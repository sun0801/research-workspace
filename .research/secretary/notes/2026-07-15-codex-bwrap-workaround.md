---
date: 2026-07-15
topic: codex-bwrap-workaround
type: troubleshooting
scope: research-workspace
tags: [codex, bwrap, apparmor, sandbox, workaround]
---

# Codexのbwrap障害とworkspace編集の回避手順

## 事象

通常のapply_patchやsandbox対象コマンドを実行すると、次のエラーで開始前に失敗する。

    bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted

読み取り系コマンドでも、許可済みprefixに一致するものは動く一方、未許可のsandbox実行だけが同じエラーになることがある。

## 今回確認した環境

- Ubuntu 24.04.4 LTS
- bubblewrap 0.9.0
- kernel.apparmor_restrict_unprivileged_userns = 1
- apparmor-profilesパッケージなし
- /usr/share/apparmor/extra-profiles/bwrap-userns-restrict なし
- /etc/apparmor.d/bwrap-userns-restrict なし
- apply_patchは独立スクリプトではなくCodex本体バイナリへのsymlink
- 最小bwrapテストでもuser namespaceのUID mapまたはnetwork namespaceのloopback設定に失敗

## 原因

Ubuntu 24.04でAppArmorのunprivileged user namespace制限が有効な状態に対し、Codexが利用するbwrap用AppArmor profileが導入されていない。したがって、apply_patchのパッチ内容や対象ファイルの問題ではなく、Codexのfilesystem sandbox起動層で失敗している。

## 恒久修復

sudo権限がある環境では、Codex公式manualのUbuntu 24.04向け手順に従う。

    sudo apt update
    sudo apt install apparmor-profiles apparmor-utils
    sudo install -m 0644 /usr/share/apparmor/extra-profiles/bwrap-userns-restrict /etc/apparmor.d/bwrap-userns-restrict
    sudo apparmor_parser -r /etc/apparmor.d/bwrap-userns-restrict

その後、CodexまたはIDE拡張のセッションを再起動し、bwrapとapply_patchを再テストする。

profileで解決しない場合の公式fallbackは次だが、システム全体のAppArmor保護を弱めるため、通常は使わない。

    sudo sysctl -w kernel.apparmor_restrict_unprivileged_userns=0

参考: https://learn.chatgpt.com/docs/sandboxing.md

## sudo権限がない場合の一時回避

今回のworkspaceでは、Codex tool callのsandbox escalationを使った。これはsudoやroot化ではなく、同じユーザー権限のままCodexのコマンドsandboxを一時的に外す方法である。

apply_patch自体は内部helperがbwrapを起動するため、sandbox外からapply_patchコマンドを呼んでも失敗した。そのため、既知の対象と変更内容を限定したworkspace内Markdownに対して、承認済みのperl -0pi -e fallbackを使った。

適用条件:

- workspace内の限定されたファイルだけを対象にする。
- 外部リポジトリやシステムファイルには使わない。
- 既存ファイルを丸ごと上書きしない。
- 変更前に対象範囲を読み、変更後にgit diff、git diff --check、行数、必須語を確認する。
- 新規の空ファイルにperl -0piを使う場合、空ファイルでは通常のperl -p処理が一度も走らないため、touch後にBEGINブロックなど空ファイルでも実行される方法を使う。
- これはapply_patchの代替であり、一般的な編集方法ではない。複雑なコード変更や不確実な置換には使わない。

今回の実績:

- 既存2ファイルの追記ブロックを既知のmarkerから末尾まで除去し、git diffで元に戻ったことを確認した。
- 独立brainstorm/specを新規作成し、wc、rg、末尾確認、必須項目確認を実行した。
- 外部リポジトリ、README、システム設定は変更していない。

## 再発時の診断順

1. エラーがbwrapのloopbackまたはuser namespaceか確認する。
2. Ubuntuの版、bubblewrapの版、kernel.apparmor_restrict_unprivileged_usernsを読む。
3. bwrap-userns-restrict profileの存在を確認する。
4. sudoがなければ、システム修復はせず、workspace内の限定的な文書編集だけfallbackする。
5. 外部リポジトリの実装変更は、sandbox回避だけを理由に開始しない。Implementation Gate、書き込み権限、検証方法を別途確認する。
6. sudo権限が得られたらprofileを導入し、Codexセッションを再起動してapply_patchを再テストする。
