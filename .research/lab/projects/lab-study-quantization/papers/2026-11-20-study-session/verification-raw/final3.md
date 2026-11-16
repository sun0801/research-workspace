# final3 確認（編集なし，確認者）

実施: tools/render.sh で a/c を再 render（a 53 枚，c 55 枚），check_overflow.py（pptvenv の python-pptx 使用），pdftotext -layout 比較，S12(a)/S26(c) の PNG 目視．

## (1) a S12
- 出典欄: 「演習の手順: quantization_handson/README.md」 → OK
- 「演習ページ」は pptx 本文・ノート（全スライド），PDF テキストのいずれにも 0 件 → OK
- 描画（p-12.png）: 崩れ・重なりなし → OK

## (2) c S26
- 出典欄: 「本環境の実測: plot_act_dist.py の再計算（結果ログ §3 は丸めた値），比 DeiT fc2 4.26，qkv 1.83，ResNet18 1.66」→ 指定の文言を含み OK
- 図の層: make_fig_actdist_c.py は blocks.11.attn.qkv，blocks.0.mlp.fc2，layer4.1.conv2（図のタイトルとも一致）．結果ログ §3 は blocks.0.mlp.fc2（4.3）と layer4.1.conv2（1.7）を名指しし，qkv は「norm1 out 1.8〜4.1」と書くのみで blocks.11.attn.qkv の名指しはない（注意点，修正必須ではない）．
- 描画（p-26.png）: 3 パネル・出典欄とも崩れ・重なりなし → OK

## PDF 一致・overflow
- 再 render した PDF と同梱 PDF の pdftotext -layout は a・c とも完全一致（diff なし）
- check_overflow.py: a = OVERFLOW 0，c = OVERFLOW 0
