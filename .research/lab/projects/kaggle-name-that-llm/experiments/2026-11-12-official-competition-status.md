---
date: 2026-11-12
project: kaggle-name-that-llm
type: official-competition-status
---

# Official competition status — 2026-11-12

確認日時: 2026-11-12 00:02 JST。Kaggle公式MCPのcompetition metadata、Timeline、Rules、Code Requirements、公開Leaderboardを確認。

- 公開Leaderboard先頭: balanced accuracy `.765`。参加チーム数: 5,496。APIのpublic leaderboard上位10件を取得。
- competition metadataのdeadlineは2027-01-14 23:59 UTC。一方、公式TimelineのFinal Submission Deadlineは2027-01-13 23:59 UTCと表示され、1日不一致。Entry Deadline / Team Merger DeadlineはTimeline上でplaceholder文字列のまま。最終判断前にKaggle画面で確認する。
- Rules: 日次最大5件提出、Final Submissionは最大2件。単一アカウントで参加・提出する条件も確認。
- Code Requirements: Notebook提出、CPU/GPUいずれも実行9時間以内、Internet無効、提出ファイル名は`submission.parquet`。
- 今回は提出直前ではないため、アカウントの当日提出数・残り枠は未確認。Kaggle CLIにcredentialがなく、`kaggle competitions submission-limits name-that-llm --json`は未実行。push・提出直前に再確認する。
- Kaggle private asset Datasetは未作成、Notebook push・Submissionも未実施。ローカルのprivate baseline asset stagingだけ完了。

## 公式情報

- [Competition overview and metadata](https://www.kaggle.com/competitions/name-that-llm)
- [Official rules](https://www.kaggle.com/competitions/name-that-llm/rules)
- [Official Code Requirements](https://www.kaggle.com/competitions/name-that-llm/code)
- [Public leaderboard](https://www.kaggle.com/competitions/name-that-llm/leaderboard)

## 2026-11-12 01:01 JST — benchmark push前の更新

Kaggle公式MCPのmetadata、Rules、Timeline、Code Requirements、public leaderboardを再取得。push直前のCLI確認で提出枠と提出履歴も確認した。

- public leaderboard首位はJames Liebelの`.765`で不変。参加チーム数は5,506（00:02時点の5,496から増加）。metadataのdeadlineは2027-01-14 23:59 UTC、Timelineは2027-01-13 23:59 UTCのため、Timelineを保守的な締切とする。
- Rulesは日次5件、Final Submission最大2件。Code RequirementsはNotebook限定、CPU/GPU各9時間以内、Internet無効、`submission.parquet`。TimelineのFinal Submission Deadlineは2027-01-13 23:59 UTC。
- `uv run --env-file ../.env kaggle competitions submission-limits name-that-llm --json`で`numAllowedNow=5`。`uv run --env-file ../.env kaggle competitions submissions name-that-llm --format json --page-size 100`は`No submissions found`。当該時点の提出数・Final選定数は0。
- `.env`を明示してCLI認証が通ることを確認。credential値は読まず、出力もしない。
- 直前にprivate baseline asset Dataset `suntree0801/name-that-llm-private-blend-assets`を作成。Kaggle MCPでversion 1、`Ready`、`is_private=true`、213,121,948 bytesを確認。公開設定は使っていない。
- ローカルKernel一覧に同じslugはなく、benchmark Notebookは`BENCHMARK_ONLY=True`、private、GPU有効、Internet無効、L4指定。Benchmark pushは未実施。次はこの設定のままpushし、実測runtime gateを確認する。

## 2026-11-12 01:39 JST — benchmark v2 push前の確認

運用改訂に従い、Notebook push直前に公式情報と提出枠を再確認。

- Leaderboard首位は`.765`で不変。チーム数は5,508（前回push前の5,506から増加）。metadata deadlineは2027-01-14 23:59 UTC、Timeline Final Submission Deadlineは2027-01-13 23:59 UTC。Timelineを保守的締切として扱う。
- Rulesは日次5件・最終選択最大2件。Code RequirementsはNotebook提出、CPU/GPU各9時間以内、Internet無効、`submission.parquet`。Data Descriptionはinteractive 3例、hidden rerun約4,000件。
- `uv run --env-file ../.env kaggle competitions submission-limits name-that-llm`は当日提出0、累積0、残り5件。
- Kaggle公式MCPのnotebook session/info/output toolは`kernels.get` permission denied。Kernelログの読取は認証済みCLI `kaggle kernels output` で行った。

## 2026-11-12 02:10 JST — benchmark v3 push前の確認

- Leaderboard首位`.765`で不変。参加チーム数5,518（前回確認5,508から増加）。metadata deadlineは1/14、Timeline Final Submission Deadlineは1/13の23:59 UTCで不一致のまま。
- Rulesは日次5件・Final選択最大2件。Code RequirementsはNotebook、9時間以内、Internet無効、`submission.parquet`。Data Descriptionのhidden rerunは約4,000件。
- CLI `kaggle competitions submission-limits name-that-llm`: 当日提出0、累積0、残り5件。Codex usage guard: 5h 88%、weekly 36%。
- private benchmark v2は誤ったcompetition pathでruntime probe前に失敗。公式path修正後のprivate v3 push直前に確認した。

## 2026-11-12 02:46 JST — benchmark v4 push前の確認

- Public leaderboard首位が`.768`（NguyenThanhNhan）に更新。前回の`.765`から上昇。チーム数は5,523（前回5,518から増加）。
- Rules/Timeline/Code Requirementsに変更なし: 最大5 submissions/day、Final最大2件、Timeline締切2027-01-13 23:59 UTC、Notebook-only、Internet無効、9時間以内、`submission.parquet`。
- CLI提出残数は5件（当日0、累積0）。Codex guardは5h残量87%、weekly 36%。
- Kaggle docsのDataset pathは一意性等によりmount pathが変わりうるため、version 3ログで見つかったprivate asset mount root不一致を受け、v4はhead fileからrootを解決する。

## 2026-11-12 03:22 JST — benchmark v5 push前の確認

- Public leaderboard首位は`.768`（NguyenThanhNhan）で不変。チーム数は5,532（前回5,523から増加）。metadata deadlineはJan 14、Timeline Final Submission DeadlineはJan 13 23:59 UTCで不一致。
- Rules/Timeline/Code Requirementsは変化なし: 日次最大5件、Final最大2件、Notebook提出、offline、9時間以内、`submission.parquet`。
- CLI提出残数は当日0・累積0・残り5件。Codex guardは5h残量85%、weekly 36%。
- v4 failureはSVC artifact 1.9.1とKaggle runtime 1.6.1の不一致。version間decision-function一致性を確かめるreference gateを加えたbenchmark-only v5をpush。

## 2026-11-12 03:58 JST — benchmark v6 push前の確認

- Leaderboard首位`.768`（NguyenThanhNhan）で不変、チーム数5,534（前回5,532から増加）。metadata deadline Jan 14、Timeline deadline Jan 13 23:59 UTCの差も継続。
- Rules/Timeline/Code Requirementsは変化なし: 日次5件、Final最大2件、Notebook-only、offline、9時間以内、`submission.parquet`。
- CLI提出枠は当日0/5、累積0。Codex guardは5h残量99%（window reset後）、weekly 36%。
- SVC cross-version probeは1.9.1対1.6.1で64×18のdecision outputsがmax abs差0.0。次のbenchmark v6 pushに先立ち、PEFTの古いtorchao optional-dispatch failureに対する条件付きworkaroundを静的検証した。

## 2026-11-12 04:34 JST — benchmark v7 push前の確認

- 当日の公式Rules、Timeline、Code Requirements、公開Leaderboard、team countを確認。Leaderboard首位`.768`、チーム数5,534。Timeline Final Submission Deadlineは2027-01-13 23:59 UTC（metadataのJan 14表記との差は継続）。Rulesは日次最大5件・Final最大2件、Code RequirementsはNotebook-only・offline・9時間以内・`submission.parquet`で不変。
- CLI提出枠は当日5件、過去提出0件。Codex guardは5h残量97%、weekly 35%。Kaggle GPU利用量は0.15h/30h。
- 続くv7 pushは提出ではなくprivate benchmark Notebook更新。remote metadataのGPU flag不一致はbenchmark logに記録し、次の軽量status pollで実行状態を確認する。

## 2026-11-12 05:20 JST — benchmark v8 push前の確認

- Public leaderboard首位`.768`（NguyenThanhNhan）、チーム数5,541。Rulesは日次最大5件・Final最大2件、Timelineの締切は2027-01-13 23:59 UTC（metadata Jan 14表記との差は継続）、Code RequirementsはNotebook-only・offline・9時間以内・`submission.parquet`。
- CLI提出可能数は5件。private asset Dataset v1は`Ready`かつprivate。Codex guardは5時間枠94%、週間35%。
- 確認直後にprivate benchmark Notebook v8をpush。詳細・remote設定・初回statusは[benchmark log](2026-11-12-baseline-benchmark-push.md)。

## 2026-11-12 06:02 JST — scored baseline v9 push前の確認

- Official MCP: public leaderboard首位`.768`（NguyenThanhNhan）、チーム数5,543。Rules: 日次5件、Final最大2件。Timeline Final deadlineは2027-01-13 23:59 UTC、metadata deadlineはJan 14のままで不一致。Code Requirements: Notebook-only、Internet無効、GPU実行9時間以内、`submission.parquet`。Data Descriptionはinteractive 3例、hidden test約4,000件。
- CLI `submission-limits`: 現在5件許可。CLI `submissions`: 過去提出なし。これらはpush直前の確認で、実際のcode submission直前にも再確認する。
- private v9 sourceはbenchmark-only switchだけ解除し、同じprivate T4×2/offline入力で全4 code cellsの静的compileを通過。v8の実測gateは2.5134時間。v9のKaggle pushはこれから。

## 2026-11-12 06:37 JST — baseline Notebook v9 submission直前の確認

- Public leaderboard首位`.768`（NguyenThanhNhan）、チーム数5,545。Rulesは日次最大5件・Final最大2件。Timeline Final deadlineは2027-01-13 23:59 UTC、metadata deadlineはJan 14と引き続き不一致。Code RequirementsはNotebook-only、Internet無効、GPU 9時間以内、`submission.parquet`。
- CLIは当日5件許可、過去提出なし。Remote version 9 metadataはprivate、GPU enabled、Internet disabled、`NvidiaTeslaT4`、所定のprivate Dataset/competition/model sources。
- v9のsample runから`submission.parquet`を取得して形式を確認し、runtime projectionは2.5303時間でgate通過。06:39 JSTにversion9をcode submissionし、ref `58251076`、残り4件。初回statusは`PENDING`でscore待ち。[実験ログ](2026-11-12-baseline-benchmark-push.md)

## 2026-11-12 07:21 JST — private v10 diagnostic push前の確認

- Official MCP: public leader`.768`（NguyenThanhNhan）、team count 5,549。Rulesは5 submissions/day・Final最大2件。Timeline締切2027-01-13 23:59 UTC、metadataはJan 14表記。Code RequirementsはNotebook-only・offline・GPU <=9h・`submission.parquet`。
- CLI提出枠: 当日1・累積1・残り4。v9 hidden rerunは既にfailedで、v10は非scored診断Notebookとしてpushするため提出枠は消費しない。
- rate guard: 5h 83%、weekly 33%。変更範囲は公開train本文を使うfull-text diagnosticのみで、baseline model/blend設定は不変。
