"""案A（積み上げ型）のスライドを作る。
使い方: pptvenv/bin/python build_a.py   （図は先に make_figs_a.py で作る。a_data.py は quantization_handson の .venv で実行）
出力: ../2026-11-17-quantization-study-a.pptx
"""
import json
import os
import sys

from pptx.util import Emu, Pt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slidekit import (BODY_TOP, FULL_W, L_TITLEONLY, LEFT, SRC_TOP, Deck, _tag_runs)  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SS = os.path.dirname(HERE)  # papers/2026-11-20-study-session
P = os.path.dirname(os.path.dirname(os.path.dirname(SS)))  # lab-study-quantization project root... adjusted below
P = "/mnt/HDD10TB-2/aburatani/research-workspace/.research/lab/projects/lab-study-quantization"
FIG = f"{SS}/figures/a"
EXP = f"{P}/experiments/figures"
RES = "/mnt/HDD10TB-2/aburatani/quantization_handson/results"
M = json.load(open(f"{RES}/ptq_table.json"))["models"]
Q = {m: json.load(open(f"{RES}/qat_{m}.json"))["models"][m] for m in ("resnet18", "deit_tiny")}
SENS = json.load(open(f"{RES}/sensitivity.json"))

d = Deck()
_orig_notes = d._notes
d._notes = lambda s_, notes: _orig_notes(s_, notes.replace("，", "、").replace("．", "。") if notes else notes)  # ノートは「、。」（見本に合わせる）
SLIDES = []  # (番号, 節, タイトル, 分)


def reg(title, sec, minutes):
    SLIDES.append((len(d.prs.slides), sec, title, minutes))


def _wlen(t):
    return sum(1.0 if ord(c) > 0x2E80 or ord(c) in range(0x2000, 0x2400) else 0.55 for c in t)


def lead_text(s, lines, size=24, top=BODY_TOP):
    cap = 36.0 * 24 / size
    n = sum(max(1, -(-int(_wlen(t)) // int(cap))) for t in lines)
    h = int(n * size * 1.35 * 12700)
    d.textbox(s, "\n".join(lines), LEFT, top, FULL_W, h, size=size)
    return top + h + 110000


def pre_items(items):
    """数式・補助文を縦に並べる。items: ("eq", latex, size) / ("txt", text, size) / ("lab", label, latex, size)"""
    def run(s, top):
        for it in items:
            if it[0] == "eq":
                h = d.equation(s, it[1], LEFT, top, FULL_W, it[2])
                top += h + 40000
            elif it[0] == "txt":
                top = lead_text(s, [it[1]], it[2], top) - 60000
            else:  # lab: 左に見出し，右に左寄せの式
                lw = 3000000
                d.textbox(s, it[1], LEFT, top, lw, 460000, size=24)
                h = d.equation(s, it[2], LEFT + lw, top, FULL_W - lw, it[3], align="left")
                top += max(h, 460000) + 30000
        return top + 60000
    return run


def figure(title, lead, img, notes, source, sec, minutes, caption="", lead_size=24, pre=None):
    """文字は上，図は下。"""
    s = d._new(L_TITLEONLY)
    s.shapes.title.text = title
    _tag_runs(s.shapes.title.text_frame._txBody)
    top = lead_text(s, lead, lead_size) if lead else BODY_TOP
    if pre:
        top = pre(s, top)
    cap_h = 420000 if caption else 0
    bottom = SRC_TOP - 40000
    d._place_image(s, img, LEFT, top, FULL_W, bottom - top - cap_h)
    if caption:
        d.textbox(s, caption, LEFT, bottom - cap_h, FULL_W, cap_h, size=16)
    d.source(s, source)
    d._notes(s, notes)
    d.main_count += 1
    reg(title, sec, minutes)
    return s


def table(title, lead, rows, widths, notes, source, sec, minutes, size=20, row_h=560000, highlight=None, pre=None):
    s = d._new(L_TITLEONLY)
    s.shapes.title.text = title
    _tag_runs(s.shapes.title.text_frame._txBody)
    top = lead_text(s, lead) if lead else BODY_TOP
    if pre:
        top = pre(s, top)
    nr, nc = len(rows), len(rows[0])
    gf = s.shapes.add_table(nr, nc, Emu(LEFT), Emu(top), Emu(FULL_W), Emu(row_h * nr))
    t = gf.table
    tot = sum(widths)
    for i, w in enumerate(widths):
        t.columns[i].width = Emu(int(FULL_W * w / tot))
    for i, row in enumerate(rows):
        t.rows[i].height = Emu(row_h)
        for j, v in enumerate(row):
            c = t.cell(i, j)
            c.text = str(v)
            for p in c.text_frame.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(size)
                    r.font.bold = i == 0 or bool(highlight and (i, j) in highlight)
            _tag_runs(c.text_frame._txBody)
    d.source(s, source)
    d._notes(s, notes)
    d.main_count += 1
    reg(title, sec, minutes)
    return s


def bullets(title, items, notes, source, sec, minutes):
    s = d.bullets(title, items, notes=notes, source=source)
    reg(title, sec, minutes)
    return s


def section(title, sub, notes, sec, minutes):
    s = d.section(title, sub, notes=notes)
    reg(title, sec, minutes)
    return s


LOG = "結果ログ"  # 2026-11-13-quantization-study 実験ログ
S0, S1, S2, S3, S4, S5 = "0 導入", "1 数値表現と一様量子化", "2 粒度と外れ値", "3 活性と較正", "4 PTQ・QAT・手法", "5 まとめ"

# ================= 0 導入 (10分) =================
s = d.title_slide("量子化入門: 基礎から積み上げる", "油谷（名工大 玉木・丁研）\n2026-11-20 研究室勉強会",
                  notes="今日は量子化の勉強会です．量子化は初めての方を想定して，数値表現から順に積み上げます．前半は式と演習で基礎を固め，後半は PTQ と QAT，外れ値への対策，そして実際に速くなるのかを見ます．演習は手元で動かせる小さなものを四つ用意しています．90分，よろしくお願いします．")
reg("量子化入門", S0, 0.5)
section("0. 導入", "なぜ量子化するのか／今日の地図", "最初の10分で，動機と今日の進め方，そして一番大事な注意を共有します．", S0, 0.3)

bullets("今日のゴール",
        ["一様量子化を式とコードで説明する", "重みと活性の精度を CNN と ViT で測る", "自分のモデルへ移す判断基準を持つ",
         "PTQ（再学習なし）・QAT・外れ値対策", "「量子化すれば速い」とは限らない"],
        "今日のゴールは五つです．一つ目，scale と zero-point を使った一様量子化を，式とコードで説明できること．二つ目，重みだけ，重みと活性の量子化で精度がどう落ちるかを，CNN の ResNet18 と ViT の DeiT-Tiny で実際に測って読めること．三つ目，自分の動画認識や生成のモデルに移すとき，どの演算を量子化し，較正データや評価指標をどう選ぶかを判断できること．四つ目，PTQ と QAT の違いと外れ値対策の考え方を，分類表の上で位置づけられること．五つ目，量子化すれば速くなるとは限らない理由を説明できること．",
        "本日の到達目標（発表者の構成）", S0, 2.0)

bullets("なぜ量子化するのか",
        ["モデルサイズ: 8bit で FP32 の約 1/4", "電力: 8bit の移動は 32bit の 4 倍効率", "速度: 典型的に 2〜3 倍（原典の記述）",
         "実測: ResNet18 は 44.80 → 11.30 MB", "ただし本当に速くなるかは別（演習④）"],
        "動機は三つです．まずメモリ．8bit にすればモデルサイズは FP32 の約4分の1です．次に電力．8bit のデータを動かすほうが32bit の4倍効率だと白書は述べています．そして速度．典型的に2から3倍という記述があります．ここまでは原典の言い分です．私たちの環境の実測では，ResNet18 の state_dict のファイルサイズが44.80MBから11.30MBになりました．サイズは確かに約4分の1です．ただし，速くなるかどうかは別の問題で，これは演習④で確かめます．",
        "原典: 白書 [Krishnamoorthi, arXiv2018] §1／本環境の実測: 結果ログ §2-5（INT8，state_dict のファイルサイズ）", S0, 2.5)

figure("今日の積み上げ地図",
       ["基礎から順に積み上げる，演習①〜③は fake-quant，④は実際の低精度実行"],
       f"{FIG}/a-stack-map.png",
       "今日は，階段を一段ずつ上がります．数値表現，一様量子化，粒度，較正，そして手法．演習は，一様量子化で①，粒度で②，較正で③，最後に手法の章で④です．①から③は fake-quant といって，誤差を模擬するだけの演習です．④だけが実際に低ビットで動かす演習です．この違いは次のスライドで説明します．各段が前の段の上に載っているので，分からなくなったら一段戻って聞いてください．",
       "本日の構成（発表者）", S0, 2.5)

figure("fake-quant と実際の低精度実行",
       ["fake-quant の精度の結果は，高速化・省メモリと結び付けない"],
       f"{FIG}/a-fakequant-vs-real.png",
       "最初に，いちばん大事な区別をします．演習①②③は fake-quant です．値を量子化してすぐ元のスケールに戻し，計算は FP32 のまま行います．精度への影響は分かりますが，速くもならず，メモリも減りません．むしろ量子化と逆量子化の分だけ遅くなりえます．一方，演習④は実際の低精度実行で，低ビットで保存して対応する kernel で計算します．サイズ，速度，メモリが本当に変わるかを見るのはこちらです．今日の精度の数字はすべて fake-quant のものです．速度の話は④の結果だけで行います．",
       "原典: 白書 [Nagel+, arXiv2021] §2.3（量子化シミュレーション）／呼称の区別は本演習の定義", S0, 2.2)

# ================= 1 数値表現と一様量子化 (18分) =================
section("1. 数値表現と一様量子化", "演習①", "ここから18分で，量子化の中身である式を押さえます．最後に演習①で，式の動きを手元で確かめます．", S1, 0.3)

table("数値表現とビット数",
      ["量子化 = 実数を少ない数の格子点に丸めること", "n bit で区別できるビット列は 2 の n 乗個（計算）",
       "別枠: 一様でない数値形式 FP8（E4M3・E5M2）・NF4 は補足で紹介"],
      [["形式", "ビット数", "ビット列の数", "格子の間隔"],
       ["FP32", "32", "約 43 億", "不均一（浮動小数点）"],
       ["FP16", "16", "65,536", "不均一（浮動小数点）"],
       ["INT8", "8", "256", "等間隔"],
       ["INT4", "4", "16", "等間隔"]],
      [1.2, 1.2, 1.6, 2.6],
      "量子化とは，連続的な実数を，少ない数の格子点に丸めて表すことです．n ビットなら区別できるビット列は2のn乗個です．"
      "FP32 なら約43億，FP16 なら65,536，INT8 なら256，INT4 ならたったの16個です．"
      "浮動小数点は値によって間隔が違いますが，整数は等間隔です．今日の主役は，この等間隔の格子，つまり一様量子化です．"
      "FP8 や NF4 のように間隔が一様でない形式は，補足スライドに表をまとめてあります．別枠として一言だけ触れると，FP8 は指数と仮数で値を表す8ビットの浮動小数点，NF4 は正規分布の分位点から格子を作る4ビット形式で，どちらも間隔が一様ではありません．",
      "説明用の計算例（2 の n 乗，FP32 は 2 の 32 乗 ≈ 43 億）／別枠: FP8 [Micikevicius+, arXiv2022]，NF4 QLoRA [Dettmers+, NeurIPS2023]", S1, 2.2)

figure("scale と zero-point",
       [],
f"{FIG}/a-affine-grid.png",
       "一様量子化の式です．実数 x を scale s で割って丸め，zero-point z を足し，q の下限と上限にクリップします．これが量子化です．非対称なら q は 0 から 2 の b 乗マイナス1，対称で符号付きなら z をゼロにして，マイナス2の b−1 乗からプラス2の b−1 乗マイナス1です．対称のときの s は，絶対値の最大を q の上限で割ります．演習のコードはこの形です．なお q_min と q_max は整数側の範囲で，白書の q_min = −sz は実数側の限界ですから，別のものです．"
       "戻すときは，整数から z を引いて s を掛けます．z は，実数の 0 に対応する整数で，0 を誤差なく表すために使います．"
       "下の数直線は計算例です．範囲を −1.0 から 3.0，4bit とすると，s は 4 割る 15 で約 0.267，z は 4 になります．"
       "z は，実数の 0 が来る整数ですから，マイナス min を s で割って丸めて4です．x が 0.5 なら整数は 6 になり，戻すと 0.533，誤差は 0.033 で，これが丸め誤差です．原典では，s は範囲から (b − a)/(n − 1) と決めます．",
       "原典: 白書 [Nagel+, arXiv2021] §2.2 式(4)(6)(7)，整数演算のみの推論 [Jacob+, CVPR2018] §2.1 式(1)，§3 式(12)／図: 説明用の計算例（範囲 [−1.0, 3.0]，4bit）", S1, 3.0,
       pre=pre_items([
           ("eq", r"q=\operatorname{clamp}\!\left(\operatorname{round}\!\left(\dfrac{x}{s}\right)+z,\ q_{\min},\ q_{\max}\right)", 34),
           ("eq", r"\hat{x}=s\,(q-z)", 34),
           ("lab", "非対称", r"q_{\min}=0,\quad q_{\max}=2^{b}-1", 26),
           ("lab", "対称・符号付き", r"z=0,\ q_{\min}=-2^{b-1},\ q_{\max}=2^{b-1}-1,\ s=\dfrac{\max|x|}{q_{\max}}", 26),
           ("txt", "s: scale，z: zero-point（実数 0 に対応する整数），b: ビット数", 24)]))

figure("対称と非対称",
       ["対称: z = 0 に固定，非対称: z で範囲をずらし，片側の分布を無駄なく使う", "本演習: 重みは対称，活性は非対称（一般的な選択）"],
       f"{FIG}/a-sym-asym.png",
       "格子の置き方には二つあります．対称は z をゼロに固定します．計算が簡単ですが，ReLU のあとのように値が正にしかない分布では，負側の格子点が無駄になります．ここで言っているのは符号付きの対称です．符号なしの対称もあり，ReLU のあとのような片側の分布には，白書はこちらが向くと述べています．"
       "非対称は z を持つので，範囲をずらして全部の格子点を使えます．ただし z を持つぶん，追加の計算が要ります．"
       "白書は，重みは対称，活性は非対称にするのが一般的な選択だと述べていて，今日の演習もこの組み合わせです．"
       "図は計算例で，範囲 0 から 6 のデータを 4bit で表したものです．",
       "原典: 白書 [Nagel+, arXiv2021] §2.2.1，§2.4.1，§3.5／図: 説明用の計算例（4bit，範囲 0〜6）", S1, 2.2)

figure("丸め誤差とクリップ誤差",
       ["範囲を広げる: クリップ誤差は減るが，scale が増えて丸め誤差が増える", "最適な範囲は両者の折り合い（較正で決める）"],
       f"{FIG}/a-round-clip.png",
       "範囲の決め方にはトレードオフがあります．範囲を広げれば，外れた値を切る誤差，つまりクリップ誤差は減ります．しかし scale が大きくなるので，丸め誤差が増えます．逆に範囲を狭めると丸めは細かくなりますが，端の値が切れます．図は標準正規分布の4096個を4bit対称で量子化した計算例です．丸めとクリップの合計が最小になる範囲が，2.5付近にあります．この折り合いをどう決めるかが，あとで出てくる較正の中身です．",
       "原典: 白書 [Nagel+, arXiv2021] §2.2／図: 説明用の計算例（N(0,1) 4096 個，seed 0，4bit 対称，範囲 [−c, c]）", S1, 2.2)

bullets("演習の準備と動作確認",
        ["cd quantization_handson", "source .venv/bin/activate", "CPU の人は ②③ で --device cpu --threads 8（① は不要）",
         "動作確認: python ex1_tensor.py", "表が数秒で出れば準備完了"],
        "ここで演習の準備と動作確認をします．ターミナルで quantization_handson に移動し，仮想環境を有効にします．GPU がない人，使わない人は，演習②以降のコマンドに device cpu と threads 8 を付けてください．"
        "動作確認として，ex1_tensor.py を引数なしで実行します．数秒で SQNR の表が出れば準備完了です．環境は事前に作ってある前提です．詰まったら手を挙げてください．"
        "当日の配布方法が決まったら，この枚に取得手順を書き足します．",
        "演習の手順: quantization_handson/README.md", S1, 2.0)

bullets("演習①: テンソル 1 つを量子化",
        ["fake-quant（CPU，数秒）", "python ex1_tensor.py --outlier 20", "SQNR: 信号÷誤差の大きさ（dB），大きいほど良い",
         "まず外れ値なし，次に 20 を 1 つ入れる", "目安: 2 秒，手元で 2 分"],
        "演習①です．テンソルを一つ作って，ビット数と対称・非対称を変えながら誤差を見ます．CPU で数秒で終わります．誤差の指標は SQNR で，信号の大きさを量子化誤差の大きさで割ってデシベルにしたものです．大きいほど誤差が小さいことを表します．"
        "まず外れ値なしで実行して，8，6，4，3，2ビットで SQNR がどう下がるかを見てください．"
        "次に，ex1_tensor.py に outlier 20 を付けて，要素のひとつを 20 にします．同じビット数で誤差がどう変わるかを比べてください．"
        "手元で2分ほど時間を取ります．",
        "本環境の実測: 結果ログ §2-4（ex1 は CPU で 2 秒）／コード: quantization_handson/ex1_tensor.py", S1, 2.7)

figure("演習①の結果: 外れ値 1 つ",
       ["外れ値 1 つ（20）で SQNR が低下: 8bit 40.5→27.2 dB，4bit 15.5→2.6 dB"],
       f"{FIG}/a-ex1-sqnr.png",
       "演習①の結果です．青は標準正規分布の4096個，赤は同じデータの一つを20にしたものです．"
       "対称 per-tensor で，8bit では40.5dBが27.2dBに，4bit では15.5dBが2.6dBまで落ちます．"
       "理由は，範囲が外れ値で決まるので scale が大きくなり，ほかの大多数の値が粗い格子に載ってしまうからです．"
       "つまり，外れ値が一つあるだけで，全体の精度が下がる，この現象が次の章の粒度と外れ値の話につながります．"
       "これは皆さんの画面にも出た演習①の出力で，合成データの結果です．実モデルの精度ではありません．",
       "本環境の実測: 演習①の出力（結果ログ §7-1，合成データ N(0,1) 4096 個，seed 0，対称 per-tensor），実モデルの精度ではない", S1, 3.5)

# ================= 2 粒度と外れ値 (17分) =================
section("2. 粒度と外れ値", "演習②", "次は粒度です．scale を何個持つかで，精度が大きく変わることを演習②で見ます．", S2, 0.3)

figure("粒度: scale を共有する単位",
       ["per-tensor / channel / group: 細かいほど精度は上がるが，scale が増える"],
       f"{FIG}/a-granularity.png",
       "粒度とは，scale を共有する単位のことです．per-tensor はテンソル全体で一組，per-channel は出力チャネルごとに一組，per-group は，さらに入力側を64要素ずつに区切って一組持ちます．細かくするほど，値の範囲に合った scale が使えて精度は上がりますが，保存する scale が増えます．図は 4 行 8 列の模式図で，同じ色が同じ scale を共有します．本演習の per-group は，group size を64に固定しています．",
       "原典: 白書 [Nagel+, arXiv2021] §2.2.3／図: 説明用の概念図（図は 4×8 の模式図，本演習の group は 64 要素）", S2, 2.2,
       caption="図は 4×8 の模式図，本演習の group は 64 要素")

table("なぜ細かくするのか: 原典の例",
      ["重み 8bit のみ（原典，シミュレーション）: MobileNet 系は per-layer（= per-tensor）で崩れる", "値は ImageNet top-1 の精度（小数），原典の説明: BN で畳み込みカーネル間の範囲が大きく違う"],
      [["モデル", "per-layer 非対称", "per-ch 対称", "per-ch 非対称", "FP"],
       ["MobileNetV1", "0.001", "0.591", "0.704", "0.709"],
       ["MobileNetV2", "0.001", "0.698", "0.698", "0.719"],
       ["ResNet v1 50", "0.75", "0.751", "0.752", "0.752"],
       ["Inception v3", "0.78", "0.78", "0.78", "0.78"]],
      [2.0, 2.0, 1.6, 1.6, 1.2],
      "なぜ細かくするのか，原典の例を見ます．重みだけを8bitにして ImageNet の top-1 を測った結果です．"
      "MobileNet は，テンソル単位つまり per-layer，今日の言い方では per-tensor だと0.001，ほぼ0に崩れます．per-channel にすると0.704まで戻ります．"
      "一方 ResNet や Inception は per-layer でもほとんど落ちません．原典は，BN によって畳み込みカーネルごとの重みの範囲が大きく違うモデルで，"
      "per-layer が崩れると説明しています．Jacob らも，チャネル間の範囲差が100倍を超えることが単純な PTQ の失敗要因だと書いています．"
      "なお数字は原典の表記のまま，小数で示しています．",
      "原典: 白書 [Krishnamoorthi, arXiv2018] §3.1.3 Table 2（ImageNet top-1，重みのみ 8bit，シミュレーション），整数演算のみの推論 [Jacob+, CVPR2018] §3", S2, 2.3)

bullets("外れ値と細かくする代償",
        ["1 つの外れ値が全要素の精度を下げる（per-tensor）", "細かくする代償: scale の数が増える",
         "group 64・32bit の scale: 1 要素あたり 0.5 bit",
         "活性の per-channel: scale が総和の外に出せず難しい"],
        "ここまでの話をまとめます．単一の scale を持つ方式では，一つの外れ値がほかのすべての値の精度を下げます．これは LLM.int8 の論文の言葉で，演習①で見たとおりです．細かくすれば解決しますが，代償があります．scale の数が増え，メモリも増えます．QLoRA の論文の例では，32bit の scale を group size 64 で持つと，1パラメータあたり0.5bitかかります．また，活性を per-channel にすると，行列積の中で scale を外に括り出せないので，実装が難しくなります．そこで，重みは細かく，活性は per-tensor という使い分けが一般的です．",
        "原典: LLM.int8() [Dettmers+, NeurIPS2022] §3，QLoRA [Dettmers+, NeurIPS2023] §3（32/64 = 0.5 bit），白書 [Nagel+, arXiv2021] §2.4.2", S2, 2.3)

bullets("演習②: 重みだけを量子化",
        ["fake-quant で重みのみ量子化し，精度を出す", "python ex2_weight.py -m resnet18 -w 4 -g per_channel（W4 = 重み 4bit）",
         "まず 4bit で per_tensor / per_channel，余裕があれば per_group と 8bit", "目安: GPU 約 7 秒，CPU 約 13 秒（--device cpu）",
         "基準 FP32: ResNet18 93.45%，DeiT-Tiny 95.00%"],
        "演習②です．重みだけを fake-quant して，精度を測ります．まず，ResNet18 の4bit per-channel を動かしてください．"
        "W4 は重みを4ビットにするという意味です．次に，粒度を per_tensor に変えて比べます．余裕があれば per_group と8ビットも試してください．"
        "1回はGPUなら約7秒，CPUなら8スレッドで約13秒です．評価は CIFAR10 の test から seed で固定した2000枚で，"
        "FP32 の基準は ResNet18 が93.45%，DeiT-Tiny が95.00%です．各自2から3条件で十分です．CPU の人は device cpu を付けてください．",
        "本環境の実測: 結果ログ §2-3，§2-4（ResNet18 96px，DeiT-Tiny 112px，CIFAR10 test 2,000 枚，seed 0）", S2, 2.5)

figure("演習②の結果: 重みのみ",
       ["W8（重み 8bit）は ±0.3 pp 以内，W4 は per-tensor 約 29%，per-channel 90.7〜91.9%，group 92.3〜94.1%"],
       f"{EXP}/2026-11-14-slides-a-weight-only-granularity.png",
       "定量結果です．重みだけの fake-quant で，横軸がビット数，縦軸が精度，点線が FP32 です．W8 は，どの粒度でも FP32 から0.3ポイント以内で，ほぼ無劣化です．W4 になると，per-tensor は ResNet18 で29.2%，DeiT-Tiny で28.55%まで崩れます．per-channel にすると90.70%と91.90%に回復し，per-group の64ではさらに92.25%と94.05%です．3bit 以下では per-channel でも崩れ，2bit ではどの粒度でも使えません．この図は fake-quant の精度で，速度の話ではありません．",
       "本環境の実測: 結果ログ §4（fake-quant，重みのみ，eval2000，1 回の実行，精度 % の差は pp）", S2, 2.6)

table("Ablation: 最初の層は敏感",
      ["1 層だけを W4（重み 4bit，per-channel）にした精度（他の層は FP32）"],
      [["モデル／層", "FP32", "W4 のみ"],
       ["ResNet18 conv1（最初）", "93.45", "92.50"],
       ["ResNet18 fc（最後）", "93.45", "93.55"],
       ["DeiT-Tiny patch_embed（最初）", "95.00", "93.70"],
       ["DeiT-Tiny head（最後）", "95.00", "95.10"]],
      [3.6, 1.4, 1.6],
      "Ablation として，1層だけ重みを4ビットにしたときの影響を見ます．ResNet18 の最初の conv1 は92.50と，FP32の93.45から落ちます．"
      "DeiT-Tiny の最初の patch_embed も93.70に下がります．最後の層の fc と head はほとんど影響がありません．活性を4ビットにした場合も同じ傾向です（あとで見ます），"
      "入力に近い層は他より敏感だという観察です．今日の演習では最初と最後の層も量子化の対象に含めています．"
      "実際に使うときは，最初の層だけ高精度のままにする，という選択肢があります．",
      "本環境の実測: 結果ログ §3（results/sensitivity.json，fake-quant，W4 per-channel を 1 層のみ，eval2000）", S2, 2.0)

figure("DeiT-Tiny の活性: 外れ値は小さい",
       ["活性（層への入力）のチャネルごとの最大値を，大きい順に並べた図",
        "fine-tune 済み DeiT-Tiny の Linear 入力: 最大/中央値 ≤ 4.3，LLM 型の外れ値は見られない（LLM は約 20〜100 倍，原典）"],
       f"{EXP}/2026-11-14-slides-a-act-channel-absmax-deit.png",
       "最後に，ViT の活性を実際に見ます．活性とは，層への入力の値です．次の章で量子化しますが，その前に分布だけ見ておきます．"
       "図は，入力の各チャネルについて最大値を測り，大きい順に並べたものです．今回の fine-tune 済み DeiT-Tiny の Linear 入力では，最大値と中央値の比は最大でも4.3でした．"
       "LLM では，少数のチャネルが他の20倍から100倍の値になると，LLM.int8 や SmoothQuant の論文が報告しています．"
       "ResNet18 の layer4.1.conv2 は1.7ですが，これは1層の値で，全層で見ると ResNet18 の最大は5.14，layer1.0.conv2 で，DeiT より大きい層もあります．"
       "また残差ストリームは2.8から7.0でしたが，残差の足し算は FP32 のままで量子化の対象外です．"
       "ですから，ViT 一般に外れ値が小さいとは言いません．私たちの fine-tune 済み DeiT-Tiny の Linear 入力では，LLM 型の極端な外れ値が見られなかった，という限定した結論です．"
       "ViT の分布を直接扱った原典は PTQ4ViT の post-softmax と post-GELU のみで，LLM の外れ値を ViT に当てはめるのは発表者の解釈にとどめます．",
       "本環境の実測: 結果ログ §3（図は plot_act_dist.py と同じ方法，CPU）／原典: LLM.int8() [Dettmers+, NeurIPS2022] §1，SmoothQuant [Xiao+, ICML2023] §3，ViT への転用は発表者の解釈", S2, 2.8)

# ================= 3 活性と較正 (17分) =================
section("3. 活性の量子化と較正", "演習③", "活性は入力ごとに値が変わります．範囲をどう決めるか，つまり較正の話です．", S3, 0.3)

figure("較正: 活性の範囲を決める",
       ["活性は入力で変わる → 較正データで範囲を決め，固定する（静的）",
        "minmax: 最小・最大 / percentile: 99.99%（本演習の設定）/ MSE: 誤差最小",
        "minmax は外れ値で範囲が広がり，格子が粗くなる"],
       f"{FIG}/a-calib-ranges.png",
       "重みと違って，活性は入力ごとに値が変わります．そこで較正データ，今回は512枚を流して範囲を決め，評価中は固定します．これを静的な量子化といいます．"
       "範囲の決め方が三つあります．minmax は最小と最大をそのまま使うので，外れ値に弱い，percentile は分位点，今回は99.99%点で切ります．この値は本演習の設定です．"
       "MSE は，範囲を0.1倍から1.0倍の91通りに縮めて，量子化誤差が最小のものを選びます．"
       "図は合成データでの4bit非対称の計算例です．minmax は範囲が広くて MSE が0.213，MSE 法は0.027です．"
       "minmax と MSE は白書が原典です．percentile は，FP8 の論文が較正の候補として挙げているだけで，定義や99.99%は述べていません．",
       "原典: 白書 [Nagel+, arXiv2021] §3.1（minmax・MSE），FP8 [Micikevicius+, arXiv2022] §4.2（percentile は較正候補として挙げるのみ，99.99% は本演習の設定）／図: 説明用の計算例（合成データ，4bit 非対称）／較正の設定: 結果ログ §1",
       S3, 3.0)

figure("BN folding",
       ["BN を前の Conv に畳み込んでから，重みを量子化する（ResNet18）"],
       f"{FIG}/a-bn-folding.png",
       "ResNet18 では，BN を前の Conv に畳み込んでから重みを量子化します．推論では BN は固定の掛け算と足し算なので，重みとバイアスに吸収できます．式は W_fold が γ W 割る ルート σ二乗プラスイプシロンです．これは Jacob らと白書にある式です．ここで大事なのは，出力チャネルごとに違う γ と σ が重みに掛かるので，畳み込んだあとの重みは，チャネル間で範囲が大きく変わりうることです．先ほどの粒度の話と，つながっています．folding の実装は，fp64 で前後の出力差が1.8e-14（単精度では1.1e-5）であることを確認しています．",
       "原典: 整数演算のみの推論 [Jacob+, CVPR2018] §3.2 式(14)，白書 [Nagel+, arXiv2021] §2.3.1 式(11)(12)／検証: 本環境の実測: 結果ログ §2-3", S3, 2.2,
       pre=pre_items([("eq", r"W_{\mathrm{fold}}=\dfrac{\gamma\,W}{\sqrt{\sigma^{2}+\varepsilon}}", 34)]))

table("WxAy と量子化する演算",
      ["WxAy = 対象演算の重み x bit・入力活性 y bit（fake-quant）"],
      [["", "量子化する", "FP32 のまま"],
       ["ResNet18", "Conv2d・Linear の重みと入力", "BN，pooling，残差の加算"],
       ["DeiT-Tiny", "QKV・出力射影・MLP の Linear，patch_embed（Conv2d），head（Linear）", "QK^T・AV，Softmax，LayerNorm，GELU，残差"],
       ["重み", "対称・符号付き", "per-tensor / channel / group(64)"],
       ["活性", "非対称・per-tensor・静的", "較正: minmax / percentile / mse"]],
      [1.2, 3.8, 3.2],
      "WxAy という書き方を定義しておきます．対象演算の重みをxビット，入力活性をyビットにする fake-quant のことです．"
      "対象は，すべての Conv2d と Linear の重みと入力活性です．ViT では QKV 射影，出力射影，MLP の Linear に加えて，最初の patch_embed の Conv2d と最後の head の Linear も対象で，"
      "Attention の行列積や Softmax，LayerNorm，GELU，残差の足し算は FP32 のままです．"
      "重みは対称で符号付き，活性は非対称で per-tensor の静的です．活性を量子化しないときは，重みのみ x ビットと呼び，A16 という言い方は演習では使いません．",
      "本演習の設定（quantization_handson/README.md，結果ログ §1）", S3, 2.2)

bullets("演習③: 較正方法を比べる",
        ["W8 + 活性 A4 を 3 つの較正方法で比べる（DeiT-Tiny）", "python ex3_act.py -m deit_tiny -w 8 -a 4 -c minmax percentile mse",
         "余裕があれば ResNet18 や A8 でも", "目安: GPU 約 15 秒，CPU 約 30〜40 秒（--device cpu）",
         "活性の分布: python plot_act_dist.py --out act.png"],
        "演習③です．重みは8bitのままで，活性のビット数と較正方法を変えて比べます．DeiT-Tiny の A4 を，minmax，percentile，mse の三つの方法でまとめて回します．A4 は活性4ビット，W8 は重み8ビットです．"
        "GPU なら約15秒，CPU なら30から40秒です．余裕があれば ResNet18 や A8 も試して，モデルやビット数による違いを見てください．"
        "活性のチャネルごとの最大値の分布は，plot_act_dist.py の out に画像の名前を渡すと描けます．CPU で動きます．",
        "本環境の実測: 結果ログ §2-4（③ W8A8 の 3 較正方法，GPU 12 s / 16 s，CPU 27 s / 39 s）", S3, 2.5)

figure("演習③の結果: 活性と較正",
       ["A8 は較正法によらず ±0.3 pp 以内，DeiT-Tiny の A4 は 25〜71%"],
       f"{EXP}/2026-11-14-slides-a-act-calibration.png",
       "定量結果です．重み8bit per-channel に，活性を8，6，4ビットにしたときの精度です．A8 は，ResNet18 も DeiT-Tiny も，三つの較正法で FP32 から0.3ポイント以内で，ほぼ無劣化です．"
       "A4 になると差が出ます．ResNet18 は86.7から91.3の範囲で耐えますが，DeiT-Tiny は minmax が24.9，mse が47.6，percentile が71.05と，較正方法で大きく変わります．"
       "FP32 は95.00です．どの方法が良いかは，ビット数とモデルによって変わるので，決め打ちはできません．これも fake-quant の精度です．なお CPU で回すと，DeiT-Tiny の A4 は minmax が25.45，percentile が70.70と，最大0.55ポイントずれますが，順位は同じです．",
       "本環境の実測: 結果ログ §4，§7-2（fake-quant，W8 per-channel + 活性，eval2000，図は GPU の値）", S3, 2.5,
       caption="CPU で回すと DeiT-Tiny の A4 は minmax 25.45，percentile 70.70（最大 0.55 pp 差，順位は同じ）")

table("A4 の数値と，1 層だけの A4",
      ["Ablation: DeiT-Tiny で 1 層だけ A4（mse）にすると，最大 95.00 → 92.55（blocks.0.mlp.fc2）", "最初の層も A4 に敏感: ResNet18 conv1 92.05，DeiT patch_embed 93.65"],
      [["条件（A4）", "minmax", "percentile", "mse"],
       ["ResNet18 W8", "86.70", "91.30", "90.85"],
       ["ResNet18 W4", "83.80", "88.00", "88.35"],
       ["DeiT-Tiny W8", "24.90", "71.05", "47.60"],
       ["DeiT-Tiny W4", "19.90", "53.10", "28.90"]],
      [2.2, 1.5, 1.5, 1.5],
      "A4 の数値を表にします．活性を4ビットにすると，DeiT-Tiny は重みが8bitでも4bitでも較正方法で大きく変わります．ここで Ablation です．DeiT-Tiny の1層だけを A4 にすると，最大の低下は blocks.0 の mlp.fc2，GELU のあとの層で，95.00が92.55です．ほとんどの層は0.3ポイント以内です．つまり，1層ずつは小さな影響でも，全層を A4 にすると大きく崩れる，ということです．この理由はまだ検証していません．",
      "本環境の実測: 結果ログ §4，§3（1 層のみ: results/sensitivity.json）", S3, 2.5)

bullets("A4 の崩壊をどう読むか",
        ["実測: DeiT-Tiny の A4 は較正法で 25〜71%", "実測: 1 層だけなら最大 −2.45 pp",
         "実測: Linear 入力の外れ値チャネルは小さい", "解釈: 層をまたぐ誤差の累積か（未検証）",
         "原典 PTQ4ViT: post-GELU の非対称分布", "対策の方向: 較正法を比べる，敏感な層だけ 8bit に戻す（解釈）"],
        "ここまでの実測と，その読み方を分けます．実測として，DeiT-Tiny の A4 は較正法で25から71%と大きく変わる，"
        "1層だけの A4 なら，最大でも2.45ポイントの低下，そして外れ値チャネルは大きくない，という三つがあります．"
        "ここから私の解釈ですが，全層を A4 にしたときの崩れは，層をまたいだ誤差の累積と考えられます．ただし，これは検証していません．"
        "対策の方向として，較正方法を複数比べること，敏感な層だけ8ビットに戻すことが考えられます．これも解釈で，効果は測っていません．原典では PTQ4ViT が，ViT の GELU のあとの分布が非対称で，CNN の想定と違うと指摘しています．"
        "私たちの最も敏感な層が GELU のあとの fc2 だったことと整合しますが，因果は確かめていません．",
        "本環境の実測: 結果ログ §3，§4／解釈: 発表者の解釈（未検証）／原典: PTQ4ViT [Yuan+, ECCV2022] §3.2", S3, 1.8)

# ================= 4 PTQ・QAT・手法 (18分) =================
section("4. PTQ・QAT と手法", "演習④（実演）", "最後の章です．学習で精度を取り戻す QAT，外れ値への対策，そして実際に速くなるかを見ます．", S4, 0.3)

figure("PTQ と QAT",
       ["PTQ: 再学習しない，QAT: 量子化を模擬しながら学習する", "8bit は PTQ で足りることが多い，低ビットは QAT が有利（学習コスト大）"],
       f"{FIG}/a-ptq-qat.png",
       "PTQ は，学習済みモデルを再学習せずに量子化します．較正データを一度流して範囲を決めるだけです．QAT は，学習中に fake-quant を挟んで，量子化の誤差込みで重みを更新します．白書は，8bit は PTQ で足りることが多く，活性の4bit のような低ビットでは QAT が有利になりうるが，学習時間，ラベル付きデータ，ハイパーパラメータ探索のコストがかかると述べています．今日の演習で PTQ は③までに見ました．QAT は事前計算した結果を見ます．",
       "原典: 白書 [Nagel+, arXiv2021] Abstract，§4／整数演算のみの推論 [Jacob+, CVPR2018] §3（学習中の疑似量子化）", S4, 1.8)

figure("QAT の勾配: STE",
       ["⌊y⌉ は y の四捨五入，その勾配は 0 か未定義 → 逆伝播では 1 とみなす（STE）"],
f"{FIG}/a-ste.png",
       "QAT の鍵は STE，straight-through estimator です．丸めの勾配は，ほぼ至る所で0か未定義なので，そのままでは学習できません．"
       "そこで逆伝播のときだけ，丸めの勾配を1，つまり恒等とみなして通します．白書の式36です．"
       "注意として，STE の原典の Bengio らの論文は，確率的なバイナリニューロンの文脈で，量子化の丸めは扱っていません．"
       "量子化の丸めに当てはめて STE と明記しているのは，Krishnamoorthi と Nagel の白書です．Jacob らの論文は STE という語を使っていません．スライドでは，STE の原典と，量子化での使い方を分けて引用します．",
       "原典: 白書 [Nagel+, arXiv2021] §4.1 式(36)，白書 [Krishnamoorthi, arXiv2018] §3.2，STE [Bengio+, arXiv2013] §4（確率的ニューロンの文脈）", S4, 2.0,
       pre=pre_items([("eq", r"\dfrac{\partial\,\lfloor y\rceil}{\partial y}=1", 34),
                      ("txt", "STE の原典は確率的ニューロン，量子化への適用は白書", 24)]))

figure("QAT の結果（1 設定）",
       ["W4+A8，390 step，3 seed 平均: ResNet18 90.65→93.12，DeiT 91.90→93.70",
        "対照（同じ更新回数の fine-tune→PTQ）より QAT が上，1 設定のみ"],
       f"{EXP}/2026-11-14-slides-a-qat.png",
       "QAT の事前計算の結果です．W4 per-channel に A8 mse の条件で，同じ390 step，約1エポックだけ学習しています．PTQ のみだと ResNet18 が90.65，DeiT-Tiny が91.90です．QAT は3 seed の平均で，それぞれ93.1と93.7まで回復しました．比較のため，同じ回数だけ通常の fine-tune をしてから PTQ した結果は91.2と91.8で，3 seed すべてで QAT がそれを上回りました．ただし，学習率やエポック数は調整していない1設定の結果です．QAT が一般に PTQ より優れるとは言いません．fake-quant の精度です．",
       "本環境の実測: 結果ログ §5（fake-quant，3 seed 平均，学習率・epoch は未調整）", S4, 2.2)

table("外れ値対策: SmoothQuant",
      [],
      [["入力チャネル j", "1", "2", "3"],
       ["max(|X_j|)（活性）", "2", "16", "4"],
       ["max(|W_j|)（重み）", "2", "1", "4"],
       ["s_j（α = 0.5）", "1", "4", "1"],
       ["変換後 max(|X̂_j|) / max(|Ŵ_j|)", "2 / 2", "4 / 4", "4 / 4"]],
      [3.4, 1.2, 1.2, 1.2],
      "外れ値への対策の代表として SmoothQuant を見ます．活性のチャネル j を s_j で割り，重みの対応する入力チャネルに s_j を掛けます．"
      "出力は数学的に変わりませんが，活性の外れ値を重み側へ移せます．重みは per-channel にして細かく量子化できますが，活性はそれが難しいので，難しさを重みへ移します．s_j は，活性の最大値の α 乗を，重みの最大値の 1 − α 乗で割ったものです．"
      "α は移す量で，0.5が基本です．下の表は3チャネルの計算例です．活性の最大が2，16，4，重みの最大が2，1，4のとき，s は1，4，1，"
      "変換後は活性も重みも最大が2，4，4にそろいます．数値は説明用で，実測ではありません．",
      "原典: SmoothQuant [Xiao+, ICML2023] §4 式(3)(4)／数値: 説明用の計算例（α = 0.5，3 チャネル）", S4, 2.5, size=18, row_h=440000,
      pre=pre_items([("eq", r"s_j=\dfrac{\max(|X_j|)^{\alpha}}{\max(|W_j|)^{1-\alpha}}", 32),
                     ("eq", r"\hat{X}=X\operatorname{diag}(s)^{-1},\quad \hat{W}=\operatorname{diag}(s)\,W", 28),
                     ("txt", "出力は不変，活性の難しさを重みへ移す，α = 0.5 が基本", 24)]))

table("SmoothQuant の結果と，本環境",
      ["OPT-175B（原典）: 素朴な W8A8 は崩れ，SmoothQuant は FP16 に近い", "本環境の DeiT-Tiny は外れ値チャネルが小さく，直接は当てはまらない（解釈）"],
      [["手法（OPT-175B）", "7 タスク平均", "PPL（小さいほど良い）"],
       ["FP16", "66.9%", "10.99"],
       ["W8A8（素朴）", "35.5%", "93080"],
       ["LLM.int8()", "66.7%", "11.10"],
       ["SmoothQuant-O3", "66.8%", "11.17"]],
      [3.0, 2.0, 2.0],
      "SmoothQuant の原典の結果です．OPT-175B で，素朴な W8A8 は7タスクの平均が35.5%，perplexity が93,080と崩れます．LLM.int8 は66.7%，SmoothQuant のO3は66.8%で，FP16 の66.9%に近い値です．ここで大事なのは，これは LLM の外れ値チャネルへの対策だということです．私たちの DeiT-Tiny では外れ値チャネルが小さかったので，この結果が直接当てはまるとは言えません．ViT の外れ値に SmoothQuant を使う効果は，本環境では測っていません．これが私の解釈です．",
      "原典: SmoothQuant [Xiao+, ICML2023] §5.2 Table 3（PPL = perplexity，小さいほど良い）／本環境の実測: 結果ログ §3／解釈: 発表者の解釈", S4, 2.0)

table("手法の分類表",
      ["軸ごとに位置づける，詳しく扱ったのは PTQ・QAT・SmoothQuant の 3 つだけ"],
      [["軸", "例", "一言"],
       ["いつ量子化するか", "PTQ / QAT", "再学習なし / 学習中に模擬"],
       ["丸め・較正の工夫（PTQ）", "AdaRound，BRECQ，GPTQ", "丸めや誤差配分を最適化"],
       ["外れ値・スケール", "LLM.int8()，SmoothQuant，AWQ", "外れ値を別扱い / スケールで移す"],
       ["数値形式", "INT8/INT4，FP8，NF4", "格子の作り方"],
       ["量子化モデルの上の fine-tune", "QLoRA", "NF4 で凍結 + LoRA"],
       ["対象ドメイン", "PTQ4ViT，Q-Diffusion", "ViT・拡散モデルの分布に合わせる"]],
      [2.6, 2.8, 3.0],
      "最後に，今日触れなかった手法を，軸ごとに位置づけます．軸を混ぜないことが大事です．いつ量子化するかは PTQ と QAT．PTQ の丸めや較正の工夫が AdaRound，BRECQ，GPTQ．外れ値とスケールの扱いが LLM.int8，SmoothQuant，AWQ．数値形式が INT，FP8，NF4．量子化モデルの上で fine-tune するのが QLoRA．そして対象ドメインに合わせたのが，ViT の PTQ4ViT と拡散モデルの Q-Diffusion です．この中では演習で測ったのは PTQ，QAT，SmoothQuant の考え方だけで，AdaRound や GPTQ などの数値は測っていません．また，論文ごとに FP32 基準の設定が違うので，BRECQ と AdaRound の数値は同じ表に並べません．",
      "原典: 白書 [Nagel+, arXiv2021]，AdaRound [Nagel+, ICML2020]，BRECQ [Li+, ICLR2021]，GPTQ [Frantar+, ICLR2023]，LLM.int8() [Dettmers+, NeurIPS2022]，SmoothQuant [Xiao+, ICML2023]，AWQ [Lin+, MLSys2024]，QLoRA [Dettmers+, NeurIPS2023]，PTQ4ViT [Yuan+, ECCV2022]，Q-Diffusion [Li+, ICCV2023]",
      S4, 2.5, size=16, row_h=470000)

bullets("演習④: 実際の低精度実行（実演）",
        ["低ビットで保存し，kernel（計算の実装）で計算して比べる", "重みのみ INT8: 重みだけ INT8 で保存，計算前に FP へ",
         "動的 INT8: 実行時に活性も INT8 にして INT8 行列積", "FX: torch.ao の FX グラフモード INT8（Conv も対象）",
         "python ex4_lowprec.py fx_int8 / torchao / nf4"],
        "演習④です．ここから実際の低精度実行，つまり低ビットで保存して，対応する kernel，つまり計算の実装で計算する世界に入ります．"
        "用語を三つ決めます．重みのみ INT8 は，重みだけを INT8 で保存し，計算の前に FP に戻す方式です．動的 INT8 は，実行時に活性も INT8 に量子化して，INT8 の行列積を使う方式です．"
        "FX は，PyTorch の torch.ao にある FX グラフモードの量子化で，Conv も対象にできます．"
        "ResNet18 は FX の INT8，DeiT-Tiny は torchao の重みのみと動的，4bit の NF4 は ViT-Base に適用します．"
        "所要時間は20秒，85秒，11秒ですが，共有マシンが混むと torchao は約128秒かかりました．時間の都合で，皆さんが回すのは任意で，結果は事前計算したものを表示します．",
        "本環境の実測: 結果ログ §2-4，§2-5，§7-2（fx_int8 約 20 s，torchao 約 85 s（混雑時 約 128 s），nf4 約 11 s）", S4, 1.5)

table("④の結果: サイズ・速度・精度",
      ["CPU 8 スレッド，batch 32，中央値，共有マシンで雑音あり（単一マシン）"],
      [["経路", "モデル", "サイズ", "遅延 ms", "精度"],
       ["FP32", "ResNet18", "44.80 MB", "53〜55", "93.45"],
       ["INT8 FX（x86）", "ResNet18", "11.30 MB", "37〜38（約 0.69×）", "93.55"],
       ["FP32", "DeiT-Tiny", "22.04 MB", "45〜49", "95.00"],
       ["INT8 重みのみ", "DeiT-Tiny", "6.24 MB", "50〜54（約 10% 遅い）", "95.00"],
       ["INT8 動的", "DeiT-Tiny", "6.24 MB", "約 790（約 16 倍）", "94.90"]],
      [2.0, 1.6, 1.5, 2.8, 1.0],
      "実測の結果です．サイズは，ResNet18 が44.80MBから11.30MBへ約4分の1，DeiT-Tiny は22.04MBから6.24MBへ約3.5分の1に小さくなりました．速度は様々です．ResNet18 の INT8 は FP32 の約0.69倍の遅延，つまり速くなりました．DeiT-Tiny の重みのみ INT8 は10%ほど遅く，動的 INT8 は約16倍も遅くなりました．精度は，ほぼ FP32 と同じです．FP32 の基準は，量子化モデルを測ったあとに測り直した値を使っています．同じ INT8 でも，速くなる，ほぼ同じ，大きく遅いと分かれました．",
      "本環境の実測: 結果ログ §2-5（Xeon E5-2699 v3，8 スレッド，batch 32，warm-up 30 回のあと 30 回の中央値）", S4, 1.7)

bullets("速度はモデルと kernel 次第",
        ["動的 INT8 の実行時間の約 88% が aten::_int_mm", "確認できた事実: この CPU・torch 2.15 でこの kernel は速くない",
         "NF4（ViT-Base，GPU）: 保持量 165 → 43 MiB，forward の peak 0.20 → 0.07 GiB",
         "原典の高速化は GPU・専用 kernel の値", "fake-quant（①〜③）は高速化と結び付けない"],
        "では，なぜ遅いのか．動的 INT8 を torch.profiler で見ると，実行時間の約88%が aten::_int_mm，INT8の行列積に使われていました．つまり，遅いのは活性の量子化処理ではなく，この CPU とこのバージョンでの INT8 行列積の実装です．確認できたのはここまでで，他の CPU やバージョンでは変わりえます．メモリは，NF4 で ViT-Base のパラメータ保持量が165MiBから43MiB，forward の peak が0.20から0.07GiBに減りました．未学習の初期値での測定です．原典の SmoothQuant の最大1.56倍や AWQ の3倍超は，GPU と専用の kernel での値で，この実測とは混ぜません．",
        "本環境の実測: 結果ログ §2-5／原典: SmoothQuant [Xiao+, ICML2023] Abstract，AWQ [Lin+, MLSys2024] Abstract（いずれも GPU 上）", S4, 1.5)

# ================= 5 まとめ (10分) =================
section("5. 実際に使うときの判断", "まとめ・質疑", "最後の10分で，自分のモデルに移すときの判断基準と，今日のまとめです．", S5, 0.3)

table("自分のモデルに移す: 確認項目",
      ["今日の実測を根拠に，何を確認するか"],
      [["確認項目", "今日の根拠"],
       ["何を量子化するか", "最初の層は敏感（Ablation），重みのみから始める"],
       ["重みの粒度", "W4 は per-tensor で崩れ，per-channel・group で回復"],
       ["活性の較正", "A8 は差なし，A4 は較正法で大差（DeiT-Tiny）"],
       ["評価", "固定した評価セットで FP32 との差を pp で見る"],
       ["速度", "実機・kernel で測る，fake-quant は不可"]],
      [2.2, 5.6],
      "自分のモデルに移すときの確認項目を，今日の実測に結び付けてまとめます．一つ目，何を量子化するか．最初の層は敏感なので，そこを高精度に残す選択肢があります．二つ目，重みの粒度．4bit にするなら per-channel か group を考えます．三つ目，活性の較正．8bit ならどの方法でも差がなく，4bit では差が大きいので，複数を試します．四つ目，評価．較正と評価のデータを分けて固定し，FP32 との差をポイントで比べます．五つ目，速度．実機の kernel で測ります．これは今日の1モデル1データセットの結果に基づく整理で，発表者の解釈を含みます．",
      "本環境の実測: 結果ログ §2-5，§3，§4／整理は発表者の解釈", S5, 3.0, size=20)

bullets("動画・生成モデルに移すとき",
        ["動画認識（ViT 系）: ②③の手順を移せる（解釈），時間方向の分布は未測定",
         "ViT: post-softmax・GELU の分布に合わせる（PTQ4ViT）",
         "拡散: timestep ごとに活性分布が変わる → 較正データを全 timestep から取る",
         "拡散 4bit 重み: FID（小さいほど良い）は通常の PTQ で 100 超，Q-Diffusion で 5.09（FP32 は 4.22）"],
        "動画や生成のモデルに移すときの手がかりです．動画認識が ViT 系なら，今日の手順，つまり重みの粒度，活性の較正，感度の確認は移せると考えますが，時間方向の分布は測っていません．これは私の解釈です．ViT については，PTQ4ViT が post-softmax と post-GELU の分布に合わせた量子化を提案しています．拡散モデルでは，Q-Diffusion が，timestep ごとに活性の分布が変わることを課題として，全 timestep から較正データを取ります．CIFAR-10 の4bit重みで，通常の PTQ は FID が100を超えましたが，Q-Diffusion は5.09で，FP32 の4.22に近い値でした．これは原典の設定での結果です．",
        "原典: PTQ4ViT [Yuan+, ECCV2022] §3.2，Q-Diffusion [Li+, ICCV2023] §3.1，§3.3，§4.2 Table 1（CIFAR-10・DDIM）／動画への移し方は発表者の解釈", S5, 2.5)

bullets("今日のまとめ",
        ["一様量子化: s・z・ビット数，範囲は丸めとクリップの折り合い", "重み: W8 はほぼ無劣化，W4 は per-channel・group で回復",
         "活性: A8 は無劣化，DeiT-Tiny の A4 は較正法で大差", "QAT は 1 設定で効いた，一般化はしない",
         "INT8 の速度はモデルと kernel 次第"],
        "まとめです．一つ目，一様量子化は scale，zero-point，ビット数で決まり，範囲は丸め誤差とクリップ誤差の折り合いです．二つ目，重みは8bit ならほぼ無劣化で，4bit は per-tensor で崩れ，per-channel や group で回復します．三つ目，活性は8bit ならどの較正でも無劣化で，DeiT-Tiny の4bit は較正方法で大きく変わりました．四つ目，QAT は今回の1設定で効きましたが，一般化はしません．五つ目，INT8 の速度はモデルと kernel 次第で，fake-quant は高速化の証拠になりません．演習のコードは quantization_handson にあります．",
        "本環境の実測: 結果ログ §2-5，§4，§5（まとめは発表者）", S5, 2.5)

bullets("さらに学ぶ・質疑",
        ["MIT 6.5940 EfficientML.ai（Han Lab）: 講義と Lab", "CUHK CMSC5743 Mo03: PTQ・QAT・STE のスライド",
         "DeepLearning.AI × HF: Quantization in Depth", "Poznanski: ResNet18×CIFAR-10 の PTQ・QAT（Notebook）",
         "日本語: joisino「深層モデルの高速化」", "日本語: PFN「LLMと低精度数値表現」"],
        "さらに学ぶための資料です．英語では，MIT の EfficientML.ai の量子化の講義と Lab，CUHK の講義スライド，DeepLearning.AI と Hugging Face のコース，ResNet18 と CIFAR-10 で PTQ と QAT を行う Notebook があります．日本語では，joisino さんの高速化のスライドと，PFN の LLM と低精度数値表現があります．なお，これらは公開ページの記述に基づく紹介で，中身の詳細は私は確認していないものを含みます．ご質問をどうぞ．",
        "さらに学ぶ候補（既存資料の調査，ページ上の記述に基づく，内容は未確認を含む）", S5, 1.7)

n_main = len(d.prs.slides)

# ================= 補足（付録，本編外）=================
d.section("補足", "全比較表・条件の詳細", notes="ここからは補足です．質疑で必要になったときに使います．")


def rows_weight():
    rows = [["bit", "R18 tensor", "R18 chan", "R18 group", "DeiT tensor", "DeiT chan", "DeiT group"]]
    for b in (8, 6, 4, 3, 2):
        r = [str(b)]
        for m in ("resnet18", "deit_tiny"):
            for g in ("per_tensor", "per_channel", "per_group"):
                x = [e for e in M[m]["runs"] if e["table"] == "weight_only" and e["w_bits"] == b and e["granularity"] == g][0]
                r.append(f"{x['acc']:.2f}")
        rows.append(r)
    return rows


def rows_act(table_name):
    rows = [["A bit", "R18 minmax", "R18 pct", "R18 mse", "DeiT minmax", "DeiT pct", "DeiT mse"]]
    for a in (8, 6, 4, 3, 2):
        r = [str(a)]
        ok = False
        for m in ("resnet18", "deit_tiny"):
            for c in ("minmax", "percentile", "mse"):
                x = [e for e in M[m]["runs"] if e["table"] == table_name and e["a_bits"] == a and e["calib"] == c]
                r.append(f"{x[0]['acc']:.2f}" if x else "-")
                ok = ok or bool(x)
        if ok:
            rows.append(r)
    return rows


def appendix_table(title, lead, rows, widths, notes, source, size=16):
    s = d._new(L_TITLEONLY)
    s.shapes.title.text = title
    _tag_runs(s.shapes.title.text_frame._txBody)
    top = lead_text(s, [lead]) if lead else BODY_TOP
    t = s.shapes.add_table(len(rows), len(rows[0]), Emu(LEFT), Emu(top), Emu(FULL_W), Emu(440000 * len(rows))).table
    tot = sum(widths)
    for i, w in enumerate(widths):
        t.columns[i].width = Emu(int(FULL_W * w / tot))
    for i, row in enumerate(rows):
        t.rows[i].height = Emu(440000)
        for j, v in enumerate(row):
            c = t.cell(i, j)
            c.text = str(v)
            for p in c.text_frame.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(size)
                    r.font.bold = i == 0
            _tag_runs(c.text_frame._txBody)
    d.source(s, source)
    d._notes(s, notes)


appendix_table("補足: 重みのみの全比較表", "ResNet18（FP32 93.45）／DeiT-Tiny（FP32 95.00），fake-quant，eval2000", rows_weight(),
               [0.7, 1.3, 1.3, 1.3, 1.4, 1.4, 1.4],
               "重みのみの全比較表です．ビット数8，6，4，3，2と，per-tensor，per-channel，per-group 64を並べています．",
               "本環境の実測: 結果ログ §4（重みのみ，fake-quant，eval2000，1 回の実行）")
appendix_table("補足: W8 + 活性の全比較表", "重み 8bit per-channel + 活性（非対称・per-tensor・静的）", rows_act("act_w8"),
               [0.8, 1.3, 1.2, 1.2, 1.4, 1.2, 1.2],
               "重み8bit per-channel に，活性のビット数と較正方法を組み合わせた全比較表です．A4 の DeiT-Tiny の較正法の差が目立ちます．",
               "本環境の実測: 結果ログ §4（pct = percentile 99.99）")
appendix_table("補足: W4 + 活性の全比較表", "重み 4bit per-channel + 活性（非対称・per-tensor・静的）", rows_act("act_w4"),
               [0.8, 1.3, 1.2, 1.2, 1.4, 1.2, 1.2],
               "重み4bit per-channel に活性を組み合わせた表です．活性は8，6，4ビットだけ測っています．",
               "本環境の実測: 結果ログ §4（pct = percentile 99.99）")

def appendix_fp8():
    appendix_table("補足: 一様でない数値形式", "格子の間隔が一定でない形式（本編では紹介のみ）",
                   [["形式", "構成", "特徴"],
                    ["FP8 E4M3", "符号1・指数4・仮数3", "最大値 448，重み・活性向きと推奨"],
                    ["FP8 E5M2", "符号1・指数5・仮数2", "最大値 57,344，勾配向き"],
                    ["NF4", "4bit，正規分布の分位点", "非一様，0 を表せる，QLoRA で使用"]],
                   [1.3, 2.2, 3.4],
                   "一様でない数値形式の補足です．FP8 には E4M3 と E5M2 があり，符号，指数，仮数のビット数の配分が違います．E4M3 は最大値448で範囲は狭いが精度が高く，重みと活性に推奨されています．E5M2 は最大値57,344で範囲が広く，勾配向けです．NF4 は QLoRA で使われる4bit形式で，重みが正規分布に従うと仮定し，その分位点から格子を作ります．",
                   "原典: FP8 [Micikevicius+, arXiv2022] §3 Table 1，QLoRA [Dettmers+, NeurIPS2023] §3")


appendix_fp8()
q = Q
appendix_table("補足: QAT の 3 seed の数値", "W4 per-channel + A8 mse，同じ更新回数 390 step，fake-quant",
               [["モデル", "FP32", "PTQ のみ", "fine-tune→PTQ（3 seed）", "QAT（3 seed）"],
                ["ResNet18", "93.45", "90.65", " / ".join(f"{v}" for v in q["resnet18"]["finetune_then_ptq"]),
                 " / ".join(f"{v}" for v in q["resnet18"]["qat"])],
                ["DeiT-Tiny", "95.00", "91.90", " / ".join(f"{v}" for v in q["deit_tiny"]["finetune_then_ptq"]),
                 " / ".join(f"{v}" for v in q["deit_tiny"]["qat"])]],
               [1.3, 0.9, 1.2, 2.6, 2.4],
               "QAT の3 seed の個別の値です．どの seed でも QAT が上回りましたが，学習率とエポック数は調整しておらず，1設定です．",
               "本環境の実測: 結果ログ §5")

appendix_table("補足: 実験条件", "",
               [["項目", "内容"],
                ["モデル", "ResNet18（96px），DeiT-Tiny（112px），CIFAR10 で 5 epoch fine-tune"],
                ["評価・較正", "test 2,000 枚・train 512 枚（seed 0 固定），TF32 無効"],
                ["環境", "torch 2.15.0，torchao 0.18.0，Python 3.12"],
                ["速度", "Xeon E5-2699 v3，8 スレッド，batch 32，中央値"],
                ["FP32 全 10,000 枚", "ResNet18 94.29，DeiT-Tiny 95.23（参考，eval2000 は 93.45 / 95.00）"],
                ["再現性", "GPU と CPU で W8A8 などは ±0.1〜0.2 pp，DeiT A4 は最大 0.55 pp（§7-2）"]],
               [1.4, 6.0],
               "実験条件の詳細です．評価は固定した2000枚で，GPU と CPU で，W8A8 などは±0.1から0.2ポイント，DeiT-Tiny の A4 は最大0.55ポイントの違いが出ます．順位は同じです．",
               "本環境の実測: 結果ログ §1，§2，§7-2")

appendix_table("補足: 原典を読むときの注意", "",
               [["項目", "注意"],
                ["percentile", "原典は FP8 論文 §4.2 のみ（白書にはない）"],
                ["STE", "Bengio は確率的ニューロン，量子化への適用は白書"],
                ["ViT の外れ値", "直接扱う原典は PTQ4ViT のみ，LLM の外れ値は LLM の話"],
                ["BRECQ と AdaRound", "FP32 基準が違うので同じ表に載せない"],
                ["速度の数字", "原典は GPU・専用 kernel，本環境と混ぜない"]],
               [1.8, 5.6],
               "原典を読むときの注意です．percentile の較正は FP8 論文だけが述べています．STE の原典は量子化の丸めを扱っていません．ViT の外れ値を直接扱うのは PTQ4ViT だけです．BRECQ と AdaRound は FP32 の基準が違います．速度の数字は GPU の値です．",
               "原典: 引用箇所ノート 付録B")

OUT = f"{SS}/2026-11-17-quantization-study-a.pptx"
d.save(OUT)
json.dump(dict(n_main=n_main, slides=SLIDES), open(f"{SS}/figures/a/_slides.json", "w"), ensure_ascii=False, indent=1)
print(OUT, "main", n_main, "total", len(d.prs.slides))
