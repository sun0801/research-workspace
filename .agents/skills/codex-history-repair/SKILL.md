---
name: codex-history-repair
description: Repair Codex conversations that remain listed in VS Code history but open blank, cannot be opened, fail to load, or show the Codex UI message 「別のアプリで開いています」 when selected, by safely filtering incompatible legacy rollout events and registering verified repaired copies.
---

# Codex History Repair

Use this skill when Codex past conversations are visible in the VS Code history list but open as a blank view, cannot be opened, fail during history loading, or display the message `別のアプリで開いています` in the Codex extension UI when selected from history. Treat that exact UI message as a trigger for this skill's safe diagnostic scan, especially when the affected conversation cannot be resumed normally.

The deterministic implementation is [scripts/repair_history.py](scripts/repair_history.py). Use it instead of recreating SQLite or JSONL repair logic in the conversation.

## Scope and safety

The script inspects the current Codex home at `${CODEX_HOME:-$HOME/.codex}` and verifies the live schema before acting. It expects:

- `state_5.sqlite`
- `session_index.jsonl`
- `sessions/`
- `archived_sessions/`

It repairs only history-indexed root threads whose database `history_mode` is `legacy` and whose rollout contains whole records with one of these exact top-level or payload event types:

- `custom_tool_call`
- `custom_tool_call_output`
- `patch_apply_begin`
- `patch_apply_end`
- `web_search_call`
- `web_search_end`

Do not broaden this filter to string matches inside message content. Modern `paginated` threads, child-agent threads, unindexed rollouts, recently updated threads, and rollouts held open by another process are excluded and reported.

An open-rollout result means a process currently has the rollout file open; it does not identify a separate application or a separate chat. A single VS Code Codex app-server process can hold files for several threads. Do not tell the user that another app owns a conversation based on the PID alone. If `Developer: Reload Window` does not release the rollout, re-scan and identify the process. Only terminate a verified Codex app-server after the user explicitly authorizes it, since this closes Codex sessions served by that process. Send `SIGTERM`, wait, and re-scan; do not send `SIGKILL` as a fallback.

The repair always creates a new thread. It never edits or deletes the original thread or rollout. Before creating repaired data, it makes and verifies:

- an online SQLite backup;
- a copy of `session_index.jsonl`;
- a hash-checked copy of every selected source JSONL;
- a manifest under `history-repair-backups/<timestamp>/manifest.json`.

For retained records, bytes are preserved except that exact occurrences of the old thread ID are changed to the new thread ID. Normal user/assistant messages, reasoning, function calls and outputs, command output, task events, turn context, and metadata remain. Only whole records with the six exact legacy event types are removed.

Successful prior repairs are recognized from manifests and from the normalized retained-content fingerprint of existing `(repaired)` threads. Re-running the script must not create another copy of an already verified repair. An incomplete or inconsistent prior repair fails closed for manual inspection.

Older single-thread repair manifests may have top-level `target_id`, `new_id`, and `destination` fields instead of the current `threads` list. A repaired rollout may also have since moved from `sessions/` to `archived_sessions/`, leaving the old manifest destination stale. Before treating this as an incomplete repair, inspect that specific mapping read-only:

- Confirm the manifest's `new_id` has a DB row and a current session-index entry.
- Check the old thread's current `history_mode`. If it is still `legacy`, compare its normalized retained-content fingerprint with the repaired rollout; they must match before the manifest can suppress another repair. If the old thread is already `paginated`, the repair script will skip it independently.
- Read the rollout path from that DB row and confirm it is inside `sessions/` or `archived_sessions/`.
- Confirm that rollout exists, its SHA-256 equals the manifest's `repaired_sha256`, its JSONL parses, and it contains none of the six legacy event types.
- If all checks pass, make and verify a copy of the old manifest, preserve its existing fields, and add `threads: [{"old_id": <target_id>, "new_id": <new_id>, "destination": <current DB rollout_path>}]`. Re-run the dry-run scan before applying.

If any check fails, stop for manual inspection. Do not guess a replacement path, edit SQLite, or discard the old manifest. A changed source hash alone is not conclusive if the old thread is now `paginated`; if it is still `legacy`, use the retained-content fingerprint check rather than ignoring source changes.

## Workflow

1. Run the read-only scan:

   ```bash
   python3 "${CODEX_HOME:-$HOME/.codex}/skills/codex-history-repair/scripts/repair_history.py"
   ```

2. Review the candidate, already-repaired, active/recently-skipped, and schema summaries.

3. If the user explicitly asked to repair the history, apply it:

   ```bash
   python3 "${CODEX_HOME:-$HOME/.codex}/skills/codex-history-repair/scripts/repair_history.py" --apply
   ```

   A request to diagnose or inspect alone does not authorize `--apply`. When the current request already explicitly asks for repair, do not ask for the same authorization again.

4. Confirm the final report says that SQLite integrity and foreign keys are valid, every new DB/index entry exists, all repaired JSONL records parse, no selected legacy event remains, and all originals still match their pre-repair SHA-256 hashes.

5. Ask the user to run `Developer: Reload Window` in VS Code, then open the titles ending in ` (repaired)`.

Do not remove original threads after the script succeeds. Original cleanup is a separate destructive action and requires explicit instruction after the user confirms the repaired conversations open correctly.

## Direct terminal recovery

The same two commands work from an ordinary terminal when the Codex UI cannot load. The default invocation is dry-run and changes nothing. `--apply` performs the backed-up repair. Use `--codex-home PATH` only when the affected Codex home is not `${CODEX_HOME:-$HOME/.codex}`.

If the script reports an unsupported schema, malformed JSONL, an incomplete earlier repair that cannot be verified as described above, or a live/open candidate rollout, stop and report the exact condition. Do not delete SQLite files, WAL files, caches, or the entire Codex home as a fallback.
