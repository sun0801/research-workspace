#!/usr/bin/env python3
"""Safely repair legacy Codex rollout history without modifying originals.

The default mode is a read-only scan. Pass --apply to create backed-up,
filtered copies and register them as new ``(repaired)`` threads.
"""

from __future__ import annotations

import argparse
import collections
import dataclasses
import datetime as dt
import fcntl
import hashlib
import json
import os
import pathlib
import secrets
import shutil
import sqlite3
import stat
import sys
import time
import uuid
from typing import Any, Iterable


LEGACY_TYPES = frozenset(
    {
        "custom_tool_call",
        "custom_tool_call_output",
        "patch_apply_begin",
        "patch_apply_end",
        "web_search_call",
        "web_search_end",
    }
)
REPAIRED_SUFFIX = " (repaired)"
DEFAULT_RECENT_GRACE_SECONDS = 600
MIN_FREE_BYTES = 2_000_000_000
REQUIRED_THREAD_COLUMNS = frozenset(
    {
        "id",
        "rollout_path",
        "created_at",
        "updated_at",
        "title",
        "name",
        "history_mode",
        "archived",
        "created_at_ms",
        "updated_at_ms",
        "recency_at",
        "recency_at_ms",
    }
)


class SafetyError(RuntimeError):
    """Raised when repair cannot continue without risking inconsistent state."""


@dataclasses.dataclass(frozen=True)
class Paths:
    home: pathlib.Path
    state: pathlib.Path
    index: pathlib.Path
    sessions: pathlib.Path
    archived: pathlib.Path
    backups: pathlib.Path


@dataclasses.dataclass
class RolloutScan:
    records: int
    session_meta_records: int
    target_counts: collections.Counter[str]
    source_sha256: str
    retained_fingerprint: str

    @property
    def removed_records(self) -> int:
        return sum(self.target_counts.values())


@dataclasses.dataclass
class Candidate:
    old_id: str
    title: str
    source: pathlib.Path
    row: dict[str, Any]
    scan: RolloutScan
    new_id: str | None = None
    destination: pathlib.Path | None = None
    new_ms: int | None = None
    backup: pathlib.Path | None = None
    repaired_sha256: str | None = None
    kept_records: int | None = None


@dataclasses.dataclass
class Discovery:
    candidates: list[Candidate]
    already_repaired: list[tuple[str, str]]
    skipped_open: list[tuple[str, str]]
    skipped_recent: list[tuple[str, str]]
    inventory_files: int
    db_threads: int
    index_lines: int
    index_unique_ids: int
    indexed_roots: int
    nonlegacy_indexed_roots: int
    unindexed_root_threads: int
    incomplete_manifests: list[str]


def parse_args(argv: list[str]) -> argparse.Namespace:
    default_home = pathlib.Path(
        os.environ.get("CODEX_HOME", os.path.expanduser("~/.codex"))
    )
    parser = argparse.ArgumentParser(
        description=(
            "Scan for legacy Codex history records and optionally create "
            "backed-up, verified repaired threads. Default: read-only dry-run."
        )
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="perform the repair; without this flag nothing is changed",
    )
    parser.add_argument(
        "--codex-home",
        type=pathlib.Path,
        default=default_home,
        help=f"Codex home directory (default: {default_home})",
    )
    parser.add_argument(
        "--exclude-thread-id",
        action="append",
        default=[],
        help="thread ID to exclude; may be specified more than once",
    )
    parser.add_argument(
        "--recent-grace-seconds",
        type=int,
        default=DEFAULT_RECENT_GRACE_SECONDS,
        help=(
            "skip threads updated within this many seconds "
            f"(default: {DEFAULT_RECENT_GRACE_SECONDS}; use 0 for fixtures)"
        ),
    )
    return parser.parse_args(argv)


def make_paths(home: pathlib.Path) -> Paths:
    resolved = home.expanduser().resolve()
    return Paths(
        home=resolved,
        state=resolved / "state_5.sqlite",
        index=resolved / "session_index.jsonl",
        sessions=resolved / "sessions",
        archived=resolved / "archived_sessions",
        backups=resolved / "history-repair-backups",
    )


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def exact_event_type_matches(record: dict[str, Any]) -> set[str]:
    matches: set[str] = set()
    top_type = record.get("type")
    if isinstance(top_type, str) and top_type in LEGACY_TYPES:
        matches.add(top_type)
    payload = record.get("payload")
    if isinstance(payload, dict):
        payload_type = payload.get("type")
        if isinstance(payload_type, str) and payload_type in LEGACY_TYPES:
            matches.add(payload_type)
    return matches


def scan_rollout(path: pathlib.Path, identity_id: str) -> RolloutScan:
    source_hash = hashlib.sha256()
    retained_hash = hashlib.sha256()
    counts: collections.Counter[str] = collections.Counter()
    records = 0
    session_meta_records = 0
    identity = identity_id.encode("utf-8")
    placeholder = b"<CODEX_THREAD_ID>"
    try:
        with path.open("rb") as handle:
            for line_number, raw_line in enumerate(handle, 1):
                source_hash.update(raw_line)
                try:
                    record = json.loads(raw_line)
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise SafetyError(
                        f"invalid JSONL at {path}:{line_number}: {exc}"
                    ) from exc
                if not isinstance(record, dict):
                    raise SafetyError(f"non-object JSONL record at {path}:{line_number}")
                records += 1
                if record.get("type") == "session_meta":
                    session_meta_records += 1
                matches = exact_event_type_matches(record)
                if matches:
                    counts.update(matches)
                    continue
                retained_hash.update(raw_line.replace(identity, placeholder))
    except OSError as exc:
        raise SafetyError(f"cannot read rollout {path}: {exc}") from exc
    return RolloutScan(
        records=records,
        session_meta_records=session_meta_records,
        target_counts=counts,
        source_sha256=source_hash.hexdigest(),
        retained_fingerprint=retained_hash.hexdigest(),
    )


def sqlite_ro(path: pathlib.Path) -> sqlite3.Connection:
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def validate_paths(paths: Paths) -> None:
    for path in (paths.state, paths.index, paths.sessions, paths.archived):
        if not path.exists():
            raise SafetyError(f"required Codex history path does not exist: {path}")
    if not paths.state.is_file() or not paths.index.is_file():
        raise SafetyError("state_5.sqlite and session_index.jsonl must be files")
    if not paths.sessions.is_dir() or not paths.archived.is_dir():
        raise SafetyError("sessions and archived_sessions must be directories")


def validate_schema(connection: sqlite3.Connection) -> list[str]:
    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    if integrity != "ok":
        raise SafetyError(f"state_5.sqlite integrity_check failed: {integrity}")
    tables = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    missing_tables = {"threads", "thread_spawn_edges"} - tables
    if missing_tables:
        raise SafetyError(
            "unsupported state_5.sqlite schema; missing tables: "
            + ", ".join(sorted(missing_tables))
        )
    columns = [row[1] for row in connection.execute("PRAGMA table_info(threads)")]
    missing_columns = REQUIRED_THREAD_COLUMNS - set(columns)
    if missing_columns:
        raise SafetyError(
            "unsupported threads schema; missing columns: "
            + ", ".join(sorted(missing_columns))
        )
    return columns


def load_index(path: pathlib.Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    all_entries: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise SafetyError(
                        f"invalid session_index.jsonl line {line_number}: {exc}"
                    ) from exc
                if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
                    raise SafetyError(
                        f"invalid session_index.jsonl record at line {line_number}"
                    )
                all_entries.append(entry)
    except OSError as exc:
        raise SafetyError(f"cannot read {path}: {exc}") from exc
    last_position = {entry["id"]: index for index, entry in enumerate(all_entries)}
    latest = [
        entry
        for index, entry in enumerate(all_entries)
        if last_position[entry["id"]] == index
    ]
    return all_entries, latest


def is_under(path: pathlib.Path, roots: Iterable[pathlib.Path]) -> bool:
    resolved = path.resolve()
    return any(resolved.is_relative_to(root.resolve()) for root in roots)


def detect_open_rollouts(paths: Paths) -> set[pathlib.Path]:
    """Return rollout paths currently held open by another same-user process."""
    result: set[pathlib.Path] = set()
    proc = pathlib.Path("/proc")
    if not proc.is_dir():
        return result
    uid = os.getuid()
    own_pid = os.getpid()
    for process in proc.iterdir():
        if not process.name.isdigit() or int(process.name) == own_pid:
            continue
        try:
            if process.stat().st_uid != uid:
                continue
            descriptors = process / "fd"
            for descriptor in descriptors.iterdir():
                try:
                    target_text = os.readlink(descriptor)
                except OSError:
                    continue
                if target_text.endswith(" (deleted)"):
                    target_text = target_text[: -len(" (deleted)")]
                target = pathlib.Path(target_text)
                if target.suffix != ".jsonl":
                    continue
                resolved = target.resolve()
                if is_under(resolved, (paths.sessions, paths.archived)):
                    result.add(resolved)
        except (OSError, PermissionError):
            continue
    return result


def repaired_display_title(row: sqlite3.Row, index_entry: dict[str, Any]) -> str:
    value = index_entry.get("thread_name") or row["name"] or row["title"]
    if not isinstance(value, str) or not value:
        raise SafetyError(f"thread {row['id']} has no usable title")
    return value


def inventory_jsonl(paths: Paths) -> list[pathlib.Path]:
    files = list(paths.sessions.rglob("*.jsonl"))
    files.extend(paths.archived.rglob("*.jsonl"))
    return files


def inspect_prior_manifests(
    paths: Paths,
    rows: dict[str, sqlite3.Row],
    index_ids: set[str],
) -> tuple[dict[str, str], list[str]]:
    valid: dict[str, str] = {}
    incomplete: list[str] = []
    if not paths.backups.is_dir():
        return valid, incomplete
    for manifest in sorted(paths.backups.glob("*/manifest.json")):
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            incomplete.append(f"{manifest}: unreadable manifest ({exc})")
            continue
        entries = data.get("threads")
        if not isinstance(entries, list):
            incomplete.append(f"{manifest}: missing threads list")
            continue
        manifest_valid = 0
        manifest_invalid = 0
        for entry in entries:
            if not isinstance(entry, dict):
                manifest_invalid += 1
                continue
            old_id, new_id = entry.get("old_id"), entry.get("new_id")
            destination = entry.get("destination")
            if not all(isinstance(value, str) for value in (old_id, new_id, destination)):
                manifest_invalid += 1
                continue
            row = rows.get(new_id)
            destination_path = pathlib.Path(destination)
            structurally_present = (
                row is not None
                and row["rollout_path"] == destination
                and new_id in index_ids
                and destination_path.is_file()
            )
            if not structurally_present:
                manifest_invalid += 1
                continue
            try:
                scan = scan_rollout(destination_path, new_id)
            except SafetyError:
                manifest_invalid += 1
                continue
            if scan.target_counts:
                manifest_invalid += 1
                continue
            valid[old_id] = new_id
            manifest_valid += 1
        if manifest_invalid:
            incomplete.append(
                f"{manifest}: {manifest_invalid} incomplete/inconsistent mapping(s), "
                f"{manifest_valid} valid mapping(s)"
            )
    return valid, incomplete


def discover(
    paths: Paths,
    connection: sqlite3.Connection,
    recent_grace_seconds: int,
    excluded_ids: set[str],
) -> Discovery:
    if recent_grace_seconds < 0:
        raise SafetyError("--recent-grace-seconds cannot be negative")
    all_index, latest_index = load_index(paths.index)
    rows = {row["id"]: row for row in connection.execute("SELECT * FROM threads")}
    children = {
        row[0]
        for row in connection.execute("SELECT child_thread_id FROM thread_spawn_edges")
    }
    index_ids = {entry["id"] for entry in latest_index}
    prior_repairs, incomplete_manifests = inspect_prior_manifests(
        paths, rows, index_ids
    )
    open_rollouts = detect_open_rollouts(paths)
    now_ms = int(time.time() * 1000)
    grace_ms = recent_grace_seconds * 1000

    indexed_roots = 0
    nonlegacy = 0
    unindexed_roots = sum(
        row_id not in children and row_id not in index_ids for row_id in rows
    )

    # Fingerprints provide idempotency even when a complete manifest was moved.
    repaired_fingerprints: dict[tuple[str, str], str] = {}
    for entry in latest_index:
        thread_id = entry["id"]
        row = rows.get(thread_id)
        if row is None or thread_id in children:
            continue
        display = repaired_display_title(row, entry)
        if not display.endswith(REPAIRED_SUFFIX):
            continue
        rollout = pathlib.Path(row["rollout_path"])
        if not rollout.is_file() or not is_under(rollout, (paths.sessions, paths.archived)):
            continue
        scan = scan_rollout(rollout, thread_id)
        if not scan.target_counts:
            base_title = display[: -len(REPAIRED_SUFFIX)]
            repaired_fingerprints[(base_title, scan.retained_fingerprint)] = thread_id

    candidates: list[Candidate] = []
    already_repaired: list[tuple[str, str]] = []
    skipped_open: list[tuple[str, str]] = []
    skipped_recent: list[tuple[str, str]] = []
    for entry in latest_index:
        thread_id = entry["id"]
        row = rows.get(thread_id)
        if row is None or thread_id in children:
            continue
        indexed_roots += 1
        display = repaired_display_title(row, entry)
        if display.endswith(REPAIRED_SUFFIX):
            continue
        if row["history_mode"] != "legacy":
            nonlegacy += 1
            continue
        rollout = pathlib.Path(row["rollout_path"]).resolve()
        if not rollout.is_file():
            raise SafetyError(f"indexed legacy thread has no rollout: {rollout}")
        if not is_under(rollout, (paths.sessions, paths.archived)):
            raise SafetyError(f"rollout path is outside Codex history roots: {rollout}")
        if thread_id in excluded_ids or rollout in open_rollouts:
            skipped_open.append((thread_id, display))
            continue
        updated_ms = row["updated_at_ms"] or row["updated_at"] * 1000
        if grace_ms and now_ms - int(updated_ms) < grace_ms:
            skipped_recent.append((thread_id, display))
            continue
        scan = scan_rollout(rollout, thread_id)
        if not scan.target_counts:
            continue
        prior_id = prior_repairs.get(thread_id)
        fingerprint_id = repaired_fingerprints.get(
            (display, scan.retained_fingerprint)
        )
        existing_id = prior_id or fingerprint_id
        if existing_id:
            already_repaired.append((thread_id, existing_id))
            continue
        if scan.session_meta_records < 1:
            raise SafetyError(f"legacy rollout has no session_meta record: {rollout}")
        candidates.append(
            Candidate(
                old_id=thread_id,
                title=display + REPAIRED_SUFFIX,
                source=rollout,
                row=dict(row),
                scan=scan,
            )
        )

    return Discovery(
        candidates=candidates,
        already_repaired=already_repaired,
        skipped_open=skipped_open,
        skipped_recent=skipped_recent,
        inventory_files=len(inventory_jsonl(paths)),
        db_threads=len(rows),
        index_lines=len(all_index),
        index_unique_ids=len(latest_index),
        indexed_roots=indexed_roots,
        nonlegacy_indexed_roots=nonlegacy,
        unindexed_root_threads=unindexed_roots,
        incomplete_manifests=incomplete_manifests,
    )


def uuid7(timestamp_ms: int) -> str:
    value = (
        ((timestamp_ms & ((1 << 48) - 1)) << 80)
        | (0x7 << 76)
        | (secrets.randbits(12) << 64)
        | (0b10 << 62)
        | secrets.randbits(62)
    )
    return str(uuid.UUID(int=value))


def atomic_json_write(path: pathlib.Path, value: dict[str, Any]) -> None:
    temporary = path.with_name("." + path.name + ".tmp")
    with temporary.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def update_manifest(
    manifest: pathlib.Path, report: dict[str, Any], status_value: str
) -> None:
    report["status"] = status_value
    report["status_updated_at"] = dt.datetime.now().astimezone().isoformat()
    atomic_json_write(manifest, report)


def online_sqlite_backup(source_path: pathlib.Path, destination: pathlib.Path) -> None:
    source = sqlite_ro(source_path)
    destination_connection = sqlite3.connect(destination)
    try:
        source.backup(destination_connection)
    finally:
        destination_connection.close()
        source.close()
    check = sqlite_ro(destination)
    try:
        integrity = check.execute("PRAGMA integrity_check").fetchone()[0]
    finally:
        check.close()
    if integrity != "ok":
        raise SafetyError(f"SQLite backup integrity_check failed: {integrity}")


def prepare_new_identities(
    candidates: list[Candidate], paths: Paths, existing_ids: set[str]
) -> None:
    base_ms = int(time.time() * 1000)
    local_zone = dt.datetime.now().astimezone().tzinfo
    for offset, candidate in enumerate(candidates):
        timestamp_ms = base_ms + offset
        new_id = uuid7(timestamp_ms)
        local_time = dt.datetime.fromtimestamp(timestamp_ms / 1000, tz=local_zone)
        destination = (
            paths.sessions
            / local_time.strftime("%Y/%m/%d")
            / (
                f"rollout-{local_time.strftime('%Y-%m-%dT%H-%M-%S')}-"
                f"{new_id}.jsonl"
            )
        )
        if new_id in existing_ids or destination.exists():
            raise SafetyError(f"generated thread collision: {new_id} / {destination}")
        candidate.new_id = new_id
        candidate.destination = destination
        candidate.new_ms = timestamp_ms


def create_backups(
    candidates: list[Candidate], paths: Paths, backup_dir: pathlib.Path
) -> tuple[pathlib.Path, pathlib.Path]:
    state_backup = backup_dir / "state_5.sqlite"
    index_backup = backup_dir / "session_index.jsonl"
    online_sqlite_backup(paths.state, state_backup)
    shutil.copy2(paths.index, index_backup)
    if sha256_file(paths.index) != sha256_file(index_backup):
        raise SafetyError("session_index.jsonl backup hash mismatch")
    for candidate in candidates:
        relative = candidate.source.relative_to(paths.home)
        backup = backup_dir / "original_jsonl" / relative
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(candidate.source, backup)
        if sha256_file(backup) != candidate.scan.source_sha256:
            raise SafetyError(f"rollout backup hash mismatch: {candidate.source}")
        candidate.backup = backup
    return state_backup, index_backup


def manifest_report(
    candidates: list[Candidate],
    paths: Paths,
    state_backup: pathlib.Path,
    index_backup: pathlib.Path,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "status": "backups_complete",
        "created_at": dt.datetime.now().astimezone().isoformat(),
        "codex_home": str(paths.home),
        "selection": (
            "latest session_index record for each root thread; "
            "history_mode=legacy; exact target top-level/payload event present; "
            "open and recently updated threads excluded"
        ),
        "legacy_types_removed": sorted(LEGACY_TYPES),
        "state_backup": str(state_backup),
        "index_backup": str(index_backup),
        "threads": [
            {
                "old_id": candidate.old_id,
                "new_id": candidate.new_id,
                "title": candidate.title,
                "source": str(candidate.source),
                "backup": str(candidate.backup),
                "destination": str(candidate.destination),
                "source_sha256": candidate.scan.source_sha256,
                "source_records": candidate.scan.records,
                "session_meta_records": candidate.scan.session_meta_records,
                "retained_fingerprint": candidate.scan.retained_fingerprint,
                "removed_by_type": dict(candidate.scan.target_counts),
            }
            for candidate in candidates
        ],
    }


def create_repaired_rollouts(candidates: list[Candidate]) -> None:
    for candidate in candidates:
        assert candidate.new_id is not None
        assert candidate.destination is not None
        candidate.destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = candidate.destination.with_name(
            "." + candidate.destination.name + ".tmp"
        )
        removed: collections.Counter[str] = collections.Counter()
        kept = 0
        old_bytes = candidate.old_id.encode("utf-8")
        new_bytes = candidate.new_id.encode("utf-8")
        with candidate.source.open("rb") as source, temporary.open("xb") as output:
            for line_number, raw_line in enumerate(source, 1):
                try:
                    record = json.loads(raw_line)
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise SafetyError(
                        f"source changed or became invalid at "
                        f"{candidate.source}:{line_number}: {exc}"
                    ) from exc
                matches = exact_event_type_matches(record)
                if matches:
                    removed.update(matches)
                    continue
                output.write(raw_line.replace(old_bytes, new_bytes))
                kept += 1
            output.flush()
            os.fsync(output.fileno())
        if removed != candidate.scan.target_counts:
            raise SafetyError(f"legacy event counts changed: {candidate.source}")
        expected_kept = candidate.scan.records - candidate.scan.removed_records
        if kept != expected_kept:
            raise SafetyError(f"retained record count mismatch: {candidate.source}")
        os.chmod(temporary, stat.S_IMODE(candidate.source.stat().st_mode))
        os.replace(temporary, candidate.destination)
        repaired_scan = scan_rollout(candidate.destination, candidate.new_id)
        if repaired_scan.target_counts:
            raise SafetyError(f"legacy event remains: {candidate.destination}")
        if repaired_scan.retained_fingerprint != candidate.scan.retained_fingerprint:
            raise SafetyError(
                f"non-legacy content changed unexpectedly: {candidate.destination}"
            )
        raw = candidate.destination.read_bytes()
        if old_bytes in raw or new_bytes not in raw:
            raise SafetyError(
                f"thread ID replacement validation failed: {candidate.destination}"
            )
        candidate.kept_records = kept
        candidate.repaired_sha256 = repaired_scan.source_sha256


def register_database(
    candidates: list[Candidate], paths: Paths, columns: list[str]
) -> None:
    connection = sqlite3.connect(paths.state, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA busy_timeout=30000")
    placeholders = ",".join("?" for _ in columns)
    insert = f"INSERT INTO threads ({','.join(columns)}) VALUES ({placeholders})"
    try:
        connection.execute("BEGIN IMMEDIATE")
        current_columns = [
            row[1] for row in connection.execute("PRAGMA table_info(threads)")
        ]
        if current_columns != columns:
            raise SafetyError("threads schema changed during repair")
        for candidate in candidates:
            assert candidate.new_id is not None
            assert candidate.destination is not None
            assert candidate.new_ms is not None
            current = connection.execute(
                "SELECT * FROM threads WHERE id=?", (candidate.old_id,)
            ).fetchone()
            if current is None or pathlib.Path(current["rollout_path"]).resolve() != candidate.source:
                raise SafetyError(
                    f"source thread changed during repair: {candidate.old_id}"
                )
            row = dict(current)
            timestamp_ms = candidate.new_ms
            row.update(
                {
                    "id": candidate.new_id,
                    "rollout_path": str(candidate.destination),
                    "created_at": timestamp_ms // 1000,
                    "updated_at": timestamp_ms // 1000,
                    "created_at_ms": timestamp_ms,
                    "updated_at_ms": timestamp_ms,
                    "recency_at": timestamp_ms // 1000,
                    "recency_at_ms": timestamp_ms,
                    "title": candidate.title,
                    "name": candidate.title,
                }
            )
            connection.execute(insert, [row[column] for column in columns])
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def append_index(candidates: list[Candidate], index_path: pathlib.Path) -> None:
    records: list[str] = []
    for candidate in candidates:
        assert candidate.new_id is not None
        assert candidate.new_ms is not None
        updated_at = (
            dt.datetime.fromtimestamp(candidate.new_ms / 1000, tz=dt.timezone.utc)
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z")
        )
        records.append(
            json.dumps(
                {
                    "id": candidate.new_id,
                    "thread_name": candidate.title,
                    "updated_at": updated_at,
                },
                ensure_ascii=False,
                separators=(",", ":"),
            )
            + "\n"
        )
    data = "".join(records).encode("utf-8")
    descriptor = os.open(index_path, os.O_WRONLY | os.O_APPEND)
    try:
        offset = 0
        while offset < len(data):
            offset += os.write(descriptor, data[offset:])
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def verify_applied(
    candidates: list[Candidate], paths: Paths
) -> dict[str, Any]:
    connection = sqlite_ro(paths.state)
    try:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        foreign_keys = connection.execute("PRAGMA foreign_key_check").fetchall()
        if integrity != "ok" or foreign_keys:
            raise SafetyError(
                f"post-repair SQLite validation failed: integrity={integrity}, "
                f"foreign_key_violations={len(foreign_keys)}"
            )
        for candidate in candidates:
            assert candidate.new_id is not None
            assert candidate.destination is not None
            row = connection.execute(
                "SELECT rollout_path,title,name FROM threads WHERE id=?",
                (candidate.new_id,),
            ).fetchone()
            expected = (str(candidate.destination), candidate.title, candidate.title)
            if row is None or tuple(row) != expected:
                raise SafetyError(
                    f"new database row validation failed: {candidate.new_id}"
                )
    finally:
        connection.close()
    all_index, _ = load_index(paths.index)
    index_counts = collections.Counter(entry["id"] for entry in all_index)
    for candidate in candidates:
        assert candidate.new_id is not None
        assert candidate.destination is not None
        if index_counts[candidate.new_id] != 1:
            raise SafetyError(
                f"new session index entry validation failed: {candidate.new_id}"
            )
        if sha256_file(candidate.source) != candidate.scan.source_sha256:
            raise SafetyError(f"original rollout changed: {candidate.source}")
        if candidate.backup is None or sha256_file(candidate.backup) != candidate.scan.source_sha256:
            raise SafetyError(f"original backup changed: {candidate.source}")
        repaired_scan = scan_rollout(candidate.destination, candidate.new_id)
        if repaired_scan.target_counts:
            raise SafetyError(f"legacy event remains: {candidate.destination}")
        if repaired_scan.retained_fingerprint != candidate.scan.retained_fingerprint:
            raise SafetyError(f"retained content mismatch: {candidate.destination}")
    return {
        "state_integrity_check": "ok",
        "foreign_key_violations": 0,
        "registered_threads": len(candidates),
        "index_entries_added": len(candidates),
        "originals_unchanged": True,
        "repaired_legacy_records_remaining": 0,
        "source_records_total": sum(c.scan.records for c in candidates),
        "removed_records_total": sum(c.scan.removed_records for c in candidates),
        "kept_records_total": sum(c.kept_records or 0 for c in candidates),
    }


def apply_repair(
    discovery: Discovery,
    paths: Paths,
    columns: list[str],
    existing_ids: set[str],
) -> pathlib.Path:
    if discovery.incomplete_manifests:
        details = "\n".join(f"  - {item}" for item in discovery.incomplete_manifests)
        raise SafetyError(
            "incomplete or inconsistent prior repair manifests require inspection:\n"
            + details
        )
    if not discovery.candidates:
        raise SafetyError("internal error: apply requested with no candidates")
    if shutil.disk_usage(paths.home).free < MIN_FREE_BYTES:
        raise SafetyError("less than 2 GB free; refusing to create backups")

    paths.backups.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now().astimezone().strftime("%Y%m%d-%H%M%S-%f")
    backup_dir = paths.backups / timestamp
    backup_dir.mkdir(mode=0o700)
    prepare_new_identities(discovery.candidates, paths, existing_ids)
    state_backup, index_backup = create_backups(
        discovery.candidates, paths, backup_dir
    )
    report = manifest_report(
        discovery.candidates, paths, state_backup, index_backup
    )
    manifest = backup_dir / "manifest.json"
    atomic_json_write(manifest, report)

    create_repaired_rollouts(discovery.candidates)
    for output, candidate in zip(report["threads"], discovery.candidates):
        output["kept_records"] = candidate.kept_records
        output["repaired_sha256"] = candidate.repaired_sha256
    update_manifest(manifest, report, "files_complete")

    register_database(discovery.candidates, paths, columns)
    update_manifest(manifest, report, "database_complete")

    append_index(discovery.candidates, paths.index)
    update_manifest(manifest, report, "index_complete")

    postcheck = verify_applied(discovery.candidates, paths)
    report["postcheck"] = postcheck
    report["completed_at"] = dt.datetime.now().astimezone().isoformat()
    update_manifest(manifest, report, "complete")
    return manifest


def truncate_title(title: str, width: int = 90) -> str:
    compact = " ".join(title.split())
    return compact if len(compact) <= width else compact[: width - 1] + "…"


def print_discovery(discovery: Discovery, paths: Paths) -> None:
    print("Codex history repair scan")
    print(f"  Codex home: {paths.home}")
    print(f"  JSONL inventory: {discovery.inventory_files}")
    print(f"  SQLite threads: {discovery.db_threads}")
    print(
        f"  session_index: {discovery.index_lines} lines / "
        f"{discovery.index_unique_ids} current IDs"
    )
    print(f"  Indexed root threads: {discovery.indexed_roots}")
    print(f"  Non-legacy indexed roots skipped: {discovery.nonlegacy_indexed_roots}")
    print(f"  Unindexed root threads skipped: {discovery.unindexed_root_threads}")
    print(f"  Previously repaired and verified: {len(discovery.already_repaired)}")
    print(f"  Open/explicitly excluded: {len(discovery.skipped_open)}")
    print(f"  Recently updated and skipped: {len(discovery.skipped_recent)}")
    print(f"  Repair candidates: {len(discovery.candidates)}")
    if discovery.incomplete_manifests:
        print("  WARNING: incomplete/inconsistent prior manifests:")
        for item in discovery.incomplete_manifests:
            print(f"    - {item}")
    for candidate in discovery.candidates:
        counts = ", ".join(
            f"{name}={count}"
            for name, count in sorted(candidate.scan.target_counts.items())
        )
        print(
            f"    - {candidate.old_id} | {truncate_title(candidate.title)} | "
            f"remove {candidate.scan.removed_records}: {counts}"
        )


def acquire_apply_lock(paths: Paths) -> int:
    lock_path = paths.home / ".history-repair.lock"
    descriptor = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        os.close(descriptor)
        raise SafetyError("another history repair process is already running") from exc
    return descriptor


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    paths = make_paths(args.codex_home)
    validate_paths(paths)
    connection = sqlite_ro(paths.state)
    try:
        columns = validate_schema(connection)
        rows = list(connection.execute("SELECT id FROM threads"))
        existing_ids = {row[0] for row in rows}
        excluded_ids = set(args.exclude_thread_id)
        for environment_name in ("CODEX_THREAD_ID", "CODEX_SESSION_ID"):
            value = os.environ.get(environment_name)
            if value:
                excluded_ids.add(value)
        discovery = discover(
            paths,
            connection,
            args.recent_grace_seconds,
            excluded_ids,
        )
    finally:
        connection.close()

    print_discovery(discovery, paths)
    if not discovery.candidates:
        print("No repair candidates found; no files or database records were changed.")
        return 0
    if not args.apply:
        print("Dry-run only; no files or database records were changed.")
        print("Re-run with --apply to create backups and repaired threads.")
        return 0

    lock_descriptor = acquire_apply_lock(paths)
    try:
        manifest = apply_repair(discovery, paths, columns, existing_ids)
    finally:
        os.close(lock_descriptor)
    completed = json.loads(manifest.read_text(encoding="utf-8"))
    postcheck = completed["postcheck"]
    print("Repair complete")
    print(f"  Repaired threads: {postcheck['registered_threads']}")
    print(f"  Removed legacy records: {postcheck['removed_records_total']}")
    print(f"  Retained records: {postcheck['kept_records_total']}")
    print(f"  Originals unchanged: {postcheck['originals_unchanged']}")
    print(f"  SQLite integrity: {postcheck['state_integrity_check']}")
    print(f"  Backup and manifest: {manifest.parent}")
    print("Run 'Developer: Reload Window' in VS Code, then open '(repaired)' threads.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SafetyError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
    except KeyboardInterrupt:
        print("Interrupted; originals were never modified.", file=sys.stderr)
        raise SystemExit(130)
