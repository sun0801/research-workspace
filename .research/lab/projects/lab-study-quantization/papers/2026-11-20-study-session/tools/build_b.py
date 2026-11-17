"""B案（問題駆動型）スライドの作成スクリプト．
使い方: python -I build_b.py  → ../2026-11-17-quantization-study-b.pptx
数値は結果ログ（experiments/2026-11-13-quantization-handson-results.md）と results/*.json，原典は citations ノートから．"""
import json
import os
import sys

from pptx.util import Emu

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from slidekit import BODY_TOP, FULL_W, LEFT, L_TITLEONLY, SRC_TOP, Deck, _tag_runs  # noqa: E402

SESSION = os.path.dirname(HERE)
PROJ = os.path.dirname(os.path.dirname(SESSION))
FIG = os.path.join(SESSION, "figures", "b")
EXPF = os.path.join(PROJ, "experiments", "figures")
RES = "/mnt/HDD10TB-2/aburatani/quantization_handson/results"
OUT = os.path.join(SESSION, "2026-11-17-quantization-study-b.pptx")
M = json.load(open(os.path.join(RES, "ptq_table.json")))["models"]

d = Deck()
PLAN = []  # (スライド番号, 区分, タイトル, 分)
SEC = ["導入"]
APPENDIX = False


def rec(title, mins):
    n = len(d.prs.slides)
    PLAN.append((n, SEC[0], title, mins, APPENDIX))


def T(title):
    assert len(title) <= 25, (len(title), title)
    return title


def section(title, sub, mins, notes, name):
    SEC[0] = name
    d.section(title, sub, notes=notes)
    rec(title, mins)


def bullets(title, items, mins, notes, source="", size=None):
    s = d.bullets(T(title), items, notes=notes, source=source, size=size)
    rec(title, mins)
    return s


def txt_img(title, items, img, text_h, mins, notes, source=""):
    s = d.bullets(T(title), items, notes=notes, source=source)
    ph = s.placeholders[1]
    ph.height = Emu(int(text_h * 914400))
    top = BODY_TOP + ph.height
    bottom = SRC_TOP - 50000
    d._place_image(s, img, LEFT, top, FULL_W, bottom - top)
    rec(title, mins)
    return s


def table(title, rows, mins, notes, source="", **kw):
    s = d.table(T(title), rows, notes=notes, source=source, **kw)
    rec(title, mins)
    return s


def two_col(title, left, right, mins, notes, source="", size=24):
    s = d.two_col(T(title), left=left, right=right, notes=notes, source=source, size=size)
    rec(title, mins)
    return s


def eq_slide(title, blocks, mins, notes, source="", size=None):
    """タイトルのみの枚に，文字行（"t"）と数式オブジェクト（"e"）を上から順に置く．"""
    s = d._new(L_TITLEONLY)
    s.shapes.title.text = T(title)
    _tag_runs(s.shapes.title.text_frame._txBody)
    y = BODY_TOP + 30000
    for kind, body, sz in blocks:
        if kind == "t":
            h = int(sz * 12700 * 1.5) * (body.count("\n") + 1)
            d.textbox(s, body, LEFT, y, FULL_W, h, size=sz)
        else:
            h = d.equation(s, body, LEFT, y, FULL_W, size=sz)
        y += h + 60000
    assert y < SRC_TOP, (title, y, SRC_TOP)
    d.source(s, source)
    d._notes(s, notes)
    d.main_count += 1
    rec(title, mins)
    return s


def txt_eq_img(title, item, latex, img, mins, notes, source="", eq_size=38):
    """1行の文字，その下に数式，その下に図．"""
    s = d.bullets(T(title), [item], notes=notes, source=source)
    ph = s.placeholders[1]
    ph.height = Emu(700000)
    top = BODY_TOP + 700000
    h = d.equation(s, latex, LEFT, top, FULL_W, size=eq_size)
    top += h + 40000
    bottom = SRC_TOP - 50000
    d._place_image(s, img, LEFT, top, FULL_W, bottom - top)
    rec(title, mins)
    return s


def acc(m, **cond):
    for r in M[m]["runs"]:
        if all(r[k] == v for k, v in cond.items()):
            return r["acc"]
    raise KeyError(cond)


def fmt(m, **cond):
    a = acc(m, **cond)
    return f"{a:.2f} ({a - M[m]['fp32']['eval2000']:+.2f})"


# 出典の書き方（4種のどれかを必ず書く）
SRC_MEAS = "本環境の実測"
EXP_LOG = "（結果ログ §{}）"

# ======================================================================
# 区間は spec の時間割に合わせる:
# 0-10 導入 / 10-28 概念（演習①）/ 28-45 粒度と外れ値（演習②）/ 45-62 活性と較正（演習③）/
# 62-80 PTQ・QAT(STE)・SmoothQuant・分類表＋演習④ / 80-90 まとめ
# ======================================================================
JACOB = "整数演算のみの推論 [Jacob+, CVPR2018]"
NAGEL = "白書 [Nagel+, arXiv2021]"

# ---------------- 0-10 導入 ----------------
d.title_slide("量子化入門: 困りごとから学ぶ", "油谷\n2026-11-20 研究室勉強会", notes=(
    "今日は量子化を，教科書の順ではなく，三つの困りごとから入って必要な道具を一つずつ取り出していく順番で話します。"
    "各区間の入口に「問い」を置き，10分から概念，28分から粒度と外れ値，45分から活性と較正，62分からPTQとQAT，SmoothQuant，演習④の順に進みます。"
    "演習①②③は各区間の中でその場で回します。全体で90分です。"))
rec("タイトル", 0.5)

txt_img("困りごと1: 14B が載らない", [
    "14B モデルを 16GB の GPU に載せたい",
    "FP16 の重みだけで 28GB（14B × 2 byte）",
], os.path.join(FIG, "memory_14b.png"), 1.45, 2.0, (
    "一つ目の困りごとです。140億パラメータのモデルを16GBのGPUで動かしたいとします。FP16では1パラメータ2byteなので重みだけで28GB，"
    "16GBに載りません。1パラメータを1byteにすると14GB，0.5byteつまり4bitにすると7GBです。ただしこれは重みの保存だけの計算で，"
    "計算の途中のテンソルや，文章生成のときにためるキャッシュ（KV cache）は別に必要です。この数字は説明用の計算例で，実測ではありません。"),
    "説明用の計算例: 14B × 2 / 1 / 0.5 byte（実測ではない）．重みの保存のみ．計算途中のメモリは含まない")

bullets("困りごと2: エッジで動かしたい", [
    "動画モデルを車載・ドローンなどで動かしたい",
    "メモリ・電力・遅延の制約が厳しい",
    "原典の記述: 8bit 化でサイズ 1/4",
    ("データ移動は 32bit 浮動小数点の 4 倍効率", 1),
    ("典型的に 2〜3 倍の高速化と述べている", 1),
], 1.5, (
    "二つ目はエッジ実行です。動画認識モデルを車載やドローンで動かすと，メモリも電力も遅延も厳しくなります。"
    "Krishnamoorthiの白書は，8bit化でモデルサイズが4分の1，データ移動のエネルギー効率が4倍，典型的に2〜3倍の高速化と述べています。"
    "ただしこれは原典の記述であって，今日の私たちの環境で確かめた値ではありません。次の枚で，実際に測るとどうなるかを先に見せます。"),
    "原典: 白書 [Krishnamoorthi, arXiv2018] §1（著者らの記述）．本環境の実測ではない")

s4 = table("困りごと3: 速くしたい", [
    ["INT8 の経路（CPU）", "サイズ（FP32 比）", "遅延（FP32 比）"],
    ["ResNet18・FX グラフモード", "44.80 → 11.30 MB", "約0.69倍（速い）"],
    ["DeiT-Tiny・weight-only", "22.04 → 6.24 MB", "同等〜やや遅い"],
    ["DeiT-Tiny・dynamic", "22.04 → 6.24 MB", "約16倍遅い"],
], 2.0, (
    "三つ目は速くしたいです。先に結論を一枚だけ見せます。演習④で測る実際のINT8の結果で，用語は表の下に置きました。"
    "weight-onlyは重みだけをINT8にする方式，dynamicは実行時に活性もINT8に変換する方式，FXグラフモードはPyTorchのグラフ変換でINT8にする方式で，kernelは行列積などを実際に計算するコードです。"
    "どれもサイズは3.5〜4倍小さくなりますが，ResNet18は速くなり，DeiT-Tinyのweight-onlyは同等からやや遅く，dynamicは約16倍遅くなりました。"
    "つまり量子化すれば速くなるとは限りません。モデルと演算と，それを実行するkernelに依存します。理由は演習④のところで説明します。共有マシンでの測定で雑音があります。"),
    source=f"{SRC_MEAS}（結果ログ §2-5）．実際の低精度実行，CPU 8 スレッド，batch 32，中央値",
    lead="量子化すれば速くなる？ 先に答えの一部を見る", col_widths=[5, 3, 3], size=20)
d.textbox(s4, "weight-only: 重みだけ INT8\ndynamic: 実行時に活性も INT8 に変換\nFX グラフモード: PyTorch のグラフ変換で INT8 化\nkernel: 行列積などを実際に計算するコード",
          LEFT, 4150000, FULL_W, 1500000, size=18)

table("2種類の「量子化」を区別する", [
    ["", "fake-quant（演習①②③）", "実際の低精度実行（演習④）"],
    ["値の持ち方", "量子化してすぐ元に戻す", "低ビットで格納する"],
    ["計算", "FP32 のまま", "対応する kernel"],
    ["分かること", "精度の変化", "サイズ・速度・メモリ"],
    ["得られない", "高速化・省メモリ", "—"],
], 2.5, (
    "ここで言葉を整理します。演習①②③はfake-quantです。値を量子化してすぐ元のスケールに戻し，計算はFP32のまま行います。"
    "精度への影響は分かりますが，低ビット化による高速化や省メモリは得られません。むしろ模擬の処理のぶん遅くなることもあります。"
    "演習④は実際の低精度実行で，低ビットで格納し対応するkernelで計算します。サイズ・速度・メモリが実際に変わるかを見ます。"
    "今日はこの二つを混ぜません。fake-quantの結果を高速化の話に結びつけないようにしてください。"),
    source="発表者の解釈（本演習での定義）．量子化シミュレーションは" + NAGEL + " §2.3",
    lead="精度の話と速度の話を混ぜない", col_widths=[2, 4, 4], size=20)

table("今日の流れと演習の地図", [
    ["時間", "問い", "演習"],
    ["10–28", "どう数を粗くする？ scale・誤差", "① テンソル1つ"],
    ["28–45", "4bit で崩れた．粒度と外れ値", "② 重みだけ"],
    ["45–62", "活性も量子化．較正", "③ 較正を変える"],
    ["62–80", "まだ足りない．QAT・SmoothQuant", "④ 実演，②③ 追加"],
    ["80–90", "自分のモデルに移す", "議論・質疑"],
], 1.5, (
    "今日の地図です。10分から，数をどう粗くするかを一様量子化として学び，演習①をその場で回します。28分から，4bitにしたら崩れたという問題を粒度で解き，外れ値を見て，演習②を回します。"
    "45分から活性も量子化して較正を学び，演習③を回します。62分からはまだ足りないときのQATとSmoothQuant，分類表を扱い，演習④の実演で本当に速くなるかを測ります。"
    "最後の10分は，自分のモデルに移すときの確認項目をまとめて議論します。"),
    source="演習の所要時間は結果ログ §2-4．コマンドはハンズオン README", col_widths=[1.3, 5, 4], size=20)

# ---------------- 10-28 概念 ----------------
section("1. 載せるために数を粗くする", "10–28分  問い: 14B を載せるには，数をどう粗くする？", 0.3, (
    "ここから第1節です。最初の困りごと，載らない，に答えるために，数を少ないビットで表す方法を学びます。"), "概念")

eq_slide("4bit だと値は 16 通り", [
    ("t", "b ビットで表せる値の数", 28),
    ("e", r"2^{b}", 44),
    ("t", "INT8: 256 通り，INT4: 16 通り\n連続値を 16 個の代表値に丸める\n問い: 代表値をどう置くか", 28),
], 2.0, (
    "ビット数を減らすと，表せる値の数が2のb乗に減ります。INT8で256通り，INT4で16通りです。"
    "量子化とは，連続的な値をこの少数の代表値のどれかに丸めることです。問題は，16個の代表値をどこに置くかです。"
    "最も素直なのは等間隔に置く一様量子化で，今日はこれを扱います。"),
    "説明用の計算例（2^b）．整数グリッドは" + NAGEL + " §2.2")

eq_slide("一様量子化の式", [
    ("e", r"q = \operatorname{clamp}\left(\lfloor x/s \rceil + z,\; q_{\min},\; q_{\max}\right)", 40),
    ("e", r"\hat{x} = s\,(q - z)", 40),
    ("t", "s: scale（刻み幅），z: zero-point，q: b ビット整数，⌊·⌉: 最近傍への丸め", 24),
    ("t", "z は実数の 0 に対応する整数で，これにより 0 を誤差なく表せる", 24),
    ("t", "非対称（符号なし）:", 24),
    ("e", r"q_{\min} = 0,\quad q_{\max} = 2^{b} - 1", 30),
    ("t", "対称・符号付き: z = 0", 24),
    ("e", r"q_{\min} = -2^{b-1},\quad q_{\max} = 2^{b-1} - 1", 30),
], 3.0, (
    "一様量子化の式です。実数xをsで割って丸め，zero-pointのzを足し，0から2のb乗マイナス1の範囲にクリップして整数qにします。"
    "元に戻すときは，qからzを引いてsを掛けます。sは刻み幅，zは実数の0に対応する整数で，"
    "これがあるので，ゼロパディングやReLUの0が誤差なく表せます。ここまでの式は，符号なしの整数に写す形です。"
    "重みでよく使う対称・符号付きの量子化は，zを0に固定し，整数の範囲を符号付きの，マイナス2のb−1乗から2のb−1乗マイナス1にします。4bitなら−8から7です。"
    "式はNagelらの白書の式(4)(6)と(8c)で，白書の整数x_intを，この資料ではqと書いています。演習のコードは，この式と1対1に対応しています。"),
    "原典: " + NAGEL + " §2.2 式(4)(6)，§2.2.1 式(8c)．z の役割も同 §2.2（白書の x_int = 本資料の q）")

txt_img("誤差は2種類ある", [
    "丸め誤差: 最大 s/2，クリップ誤差: 範囲の外",
    "範囲を広げると，クリップは減るが丸めは増える",
], os.path.join(FIG, "grid_round_clip.png"), 1.5, 2.5, (
    "誤差は二種類あります。範囲の中の値は代表値に丸められ，その誤差は最大で刻み幅の半分です。範囲の外の値は端にクリップされ，そのぶんの誤差が出ます。"
    "範囲を広げればクリップは減りますが，sが大きくなって丸め誤差が増えます。このトレードオフが，後で出てくる較正の中心の話です。"
    "図は4bit，範囲マイナス1から1の例で，説明のために私が描いたものです。図の両端の下端と上端は，実数の軸の上のグリッドの端で，前の枚の式にある整数のq_minやq_maxとは別のものです。白書では実数の側をq_minがマイナスsz，q_maxがs掛ける2のb乗マイナス1マイナスzと書いています。"),
    "原典: " + NAGEL + " §2.2．図は説明用の計算例（4bit，範囲 [−1, 1]）")

eq_slide("計算例: 4bit で x = 0.37", [
    ("t", "範囲 [−1, 1]，b = 4 のとき", 24),
    ("e", r"s = \frac{2}{15} \approx 0.133,\quad z = \lfloor 1/s \rceil = \lfloor 7.5 \rceil = 8", 32),
    ("t", "x = 0.37（範囲の内）: 0.37/s = 2.775 → 3，誤差 0.03（≤ s/2）", 24),
    ("e", r"q = \lfloor 0.37/s \rceil + 8 = 3 + 8 = 11,\quad \hat{x} = s\,(11 - 8) = 0.4", 30),
    ("t", "x = 1.2（範囲の外）: 17 が 15 にクリップされ，誤差 0.27", 24),
    ("e", r"q = 9 + 8 = 17 \to 15,\quad \hat{x} = s\,(15 - 8) \approx 0.933", 30),
], 2.5, (
    "数値で確かめます。範囲をマイナス1から1，4bitとすると，刻み幅sは2/15で約0.133，zero-pointはマイナスの下限を表すために1/sの7.5を丸めて8にします。"
    "x=0.37は，sで割って約2.78，丸めて3，zを足して11になり，戻すと0.4で，誤差は0.03，つまりs/2以下です。"
    "x=1.2は範囲の外で，sで割って9，zを足して17ですが，15にクリップされ，戻すと約0.933で，誤差は0.27と大きくなります。"
    "これは説明用の計算例で，実測ではありません。"),
    "説明用の計算例（実測ではない）．式は" + NAGEL + " §2.2 式(4)(6)")

txt_img("対称と非対称", [
    "対称は z = 0 で計算が軽い，非対称は表現力が高い",
    "整数の範囲: 対称・符号付き −8〜7，非対称 0〜15（4bit）",
    "一般的な選択: 重みは対称，活性は非対称",
], os.path.join(FIG, "sym_asym.png"), 2.15, 2.5, (
    "zero-pointを0に固定するのが対称量子化で，計算が軽くなります。符号付きの対称量子化では，4bitの整数は−8から7で，0を中心に左右に並びます。"
    "非対称はzero-pointを動かせるので，片側に偏った分布に合わせられますが，追加の計算が要ります。4bitの整数は0から15です。"
    "白書は，重みは対称，活性は非対称にするのが一般的としています。演習②③も同じ設定で，重みは対称・符号付き，活性は非対称・per-tensor・静的です。"
    "図は4bitのグリッドを模式的に描いたものです。"),
    "原典: " + NAGEL + " §2.2.1, §2.4.1．演習②③の設定はハンズオン README．図は模式図")

bullets("演習の準備: 環境と動作確認", [
    "cd quantization_handson",
    "source .venv/bin/activate",
    "②③で GPU が使えない・混んでいるとき: --device cpu --threads 8",
    "①は引数なしで CPU で動く（動作確認: python ex1_tensor.py）",
    "環境は事前準備（README の手順）．詰まったら隣の人か私へ",
], 1.5, (
    "演習の準備です。ハンズオンのリポジトリに入って，仮想環境を有効にします。GPUが使えない，または混んでいるときは，演習②と③のコマンドに--device cpu --threads 8を付ければCPUで動きます。演習①は引数なしでCPUで動くので，この指定は付けません。分布図のplot_act_dist.pyは--out指定だけで，既定でCPUで動きます。"
    "動作確認は次の演習①でそのまま行います。環境の作り方はREADMEにあり，事前に済ませてある前提です。詰まったら手を挙げてください。"),
    "コマンドはハンズオン README（準備・演習の節）．所要時間は結果ログ §2-4", size=24)

bullets("演習①: 1つのテンソルで試す", [
    "python ex1_tensor.py --outlier 20",
    "列: scale，zero，max|err|，MSE，SQNR[dB]",
    ("SQNR = 10 log10(信号の2乗平均 / 誤差の2乗平均)，大きいほど良い", 1),
    "見るもの: ビット数を下げたとき，外れ値を入れたときの誤差",
    "期待: 4bit 対称で MSE 0.597（SQNR 2.59 dB）",
], 2.0, (
    "ここで演習①を回します。コマンドは画面のとおりで，CPUで約2秒です。出力の列は，scale，zero-point，最大の絶対誤差，MSE，それにSQNRです。"
    "SQNRは信号の2乗平均を誤差の2乗平均で割ったものをデシベルで表したもので，大きいほど誤差が小さいという意味です。"
    "外れ値を一つ入れているので，4bitの対称ではscaleが大きくなり，MSEが0.597，SQNRが2.59デシベルまで悪化し，非対称のほうが誤差が小さく，MSEは約3分の1のはずです。"
    "1〜2分だけ時間をとります。この結果は，次の節の粒度の話につながります。"),
    "所要時間: 本環境の実測（結果ログ §2-4）．出力の例は結果ログ §7-1．コマンドはハンズオン README（演習①）", size=24)

bullets("一様でない数値形式", [
    "FP8: E4M3（最大 448），E5M2（最大 57,344）",
    ("値の間隔が一様でない浮動小数点形式", 1),
    "NF4: 正規分布の分位点から作る 4bit 形式",
    ("ブロックごとに absmax で [−1, 1] に正規化", 1),
], 1.7, (
    "別枠で，一様でない数値形式を二つ紹介します。FP8はE4M3が最大448，E5M2が最大57,344で，推奨は重みと活性にE4M3，勾配にE5M2です。"
    "NF4はQLoRAの4bit形式で，重みが0中心の正規分布に従うとみなし，標準正規分布の分位点から代表値を作ります。"
    "今日の演習はINT8とINT4の一様量子化が中心で，この二つは名前を知っておいてもらえれば十分です。"),
    "原典: FP8 [Micikevicius+, arXiv2022] §3 Table 1，NF4: QLoRA [Dettmers+, NeurIPS2023] §3")

# ---------------- 28-45 粒度と外れ値（演習②）----------------
section("2. 4bit にしたら崩れた", "28–45分  問い: 4bit で崩れるのはなぜ？ どこを細かくする？", 0.3, (
    "第2節です。重みを4bitにしたら精度が崩れた，という問題から始めます。"), "粒度・外れ値")

txt_img("4bit 重みは per-tensor で崩れる", [
    "重み 4bit（W4）で scale が層に1つ（per-tensor）",
    ("ResNet18 29.20%，DeiT-Tiny 28.55%（FP32 93.45 / 95.00）", 1),
], os.path.join(EXPF, "2026-11-14-w-only-granularity.png"), 1.5, 2.0, (
    "実測です。重みだけを量子化したfake-quantで，ビット数を8，6，4，3，2と下げます。W4は重み4bitのことです。赤のper-tensorは，層ごとにscaleを1つだけ持つ方式で，W6までは保たれますが，W4で ResNet18が29.20，"
    "DeiT-Tinyが28.55%に崩れます。FP32は93.45と95.00です。青と橙のper-channelとper-groupは，W4でもかなり保たれています。"
    "評価はCIFAR10 testの固定2,000枚，1回の実行です。"),
    f"{SRC_MEAS}" + EXP_LOG.format("4 重みのみ") + "，fake-quant，eval2000，1回の実行，重みは対称・符号付き")

txt_img("scale の持ち方を細かくする", [
    "per-tensor は 1つの scale を全体で共有",
    "チャネルごと・グループごとに scale を持つ",
    "原典の指摘: チャネル間で重みの範囲が 100 倍超違うことがある",
], os.path.join(FIG, "granularity.png"), 2.2, 2.0, (
    "なぜ崩れるのか。per-tensorは層全体で1つのscaleを共有するので，範囲の大きいチャネルに合わせると，範囲の小さいチャネルはほとんどの値が0に丸められます。"
    "Jacobらは単純なPTQの失敗要因として，出力チャネル間で重みの範囲が100倍以上違うことを挙げています。ただし，今日の2モデルでチャネル間の範囲差を測ったわけではなく，これは原典の説明です。"
    "そこでper-channelは出力チャネルごと，per-groupは入力側を64個ごとにscaleを持ちます。細かくするほど精度は上がりますが，保存するscaleが増えます。"
    "図は粒度の違いを模式的に塗り分けたものです。"),
    "原典: " + NAGEL + " §2.2.3，" + JACOB + " §3．group size 64 は本演習の設定．図は模式図")

table("W4 は回復し，W3 は落ちる", [
    ["重みのみ（fake-quant）", "per-tensor", "per-channel", "per-group(64)"],
    ["ResNet18  W4"] + [fmt("resnet18", w_bits=4, granularity=g, table="weight_only") for g in ("per_tensor", "per_channel", "per_group")],
    ["DeiT-Tiny  W4"] + [fmt("deit_tiny", w_bits=4, granularity=g, table="weight_only") for g in ("per_tensor", "per_channel", "per_group")],
    ["ResNet18  W3"] + [fmt("resnet18", w_bits=3, granularity=g, table="weight_only") for g in ("per_tensor", "per_channel", "per_group")],
    ["DeiT-Tiny  W3"] + [fmt("deit_tiny", w_bits=3, granularity=g, table="weight_only") for g in ("per_tensor", "per_channel", "per_group")],
], 2.0, (
    "数字で見ます。括弧内はFP32との差で，単位はポイントです。W4では，ResNet18がper-tensorの29.20からper-channelで90.70，per-groupで92.25に回復します。"
    "DeiT-Tinyも28.55から91.90，94.05です。ただしW3になると，per-groupでもマイナス14から17ポイント落ち，per-tensorとper-channelはほぼ崩れます。"
    "粒度を細かくすれば何でも救えるわけではありません。なお，細かい粒度ではscaleの保存分のメモリが増えます。QLoRAの原典は，32bitのscaleをブロック64ごとに持つと1パラメータあたり0.5bit増えると書いています。"),
    source=f"{SRC_MEAS}（結果ログ §4 重みのみ）．括弧内は FP32 との差 [pp]（FP32: 93.45 / 95.00）",
    lead="粒度を細かくすると回復，ただし 3bit は group でも落ちる", col_widths=[3, 3, 3, 3], size=18)

bullets("演習②: 重みだけを量子化する", [
    "まず予想: per-tensor と per-channel で何 pp 違う？",
    "python ex2_weight.py -m resnet18 -w 4 -g per_tensor",
    "同じ条件で -g per_channel も回す",
    "所要: GPU 約 7 秒，CPU 約 13 秒（1条件）",
    "CPU: --device cpu --threads 8．見るもの: FP32 との差（pp）",
], 5.7, (
    "ここで演習②を回します。重みだけを量子化して精度を出します。回す前に，4bitのper-tensorとper-channelでどれくらい差が出るか，予想してください。"
    "代表条件は2回で，1回あたりGPUで約7秒，CPUで約13秒です。見るのは，FP32との差です。さきほどの表と同じ向きになるかを確かめます。"
    "CPUの場合は--device cpu --threads 8を付けてください。3分ほど回して，結果を隣の人と見比べます。余裕があれば，ResNet18をDeiT-Tinyに変えてみてください。"),
    "所要時間: 本環境の実測（結果ログ §2-4，モデル読み込み・較正・評価を含む）．コマンドはハンズオン README", size=24)

bullets("LLM では外れ値が全層に出る", [
    "約 6.7B 以降，少数の特徴次元が最大で他の約 20 倍に",
    "全層に系統的に現れ，約 0.1% の次元に集中",
    "消すと perplexity が 600〜1000% 悪化",
    ("perplexity: 言語モデルの誤り度，小さいほど良い", 1),
    "対策の例: LLM.int8()（外れ値次元だけ 16bit）",
], 2.5, (
    "ここから外れ値の話です。LLM.int8()の論文は，6.7Bパラメータあたりから，ごく少数の特徴次元が他の最大で約20倍の大きさを全層で系統的にもつようになると報告しています。"
    "全入力特徴の約0.1%にすぎませんが，その次元をゼロにするとperplexityが600〜1000%悪化します。perplexityは言語モデルの誤り度で，小さいほど良い指標です。"
    "そこでLLM.int8()は，この外れ値の次元だけ16bitで計算し，残りの約99.9%を8bitで計算します。"
    "これはLLMの話です。では，私たちのViTにも同じ外れ値があるのかを，次の枚で測った結果で見ます。"),
    "原典: LLM.int8() [Dettmers+, NeurIPS2022] §1, §3．対象は LLM（OPT 等）．ViT の外れ値ではない")

txt_img("DeiT-Tiny に LLM型の外れ値は見えない", [
    "Linear 入力の最大/中央値は 4.3 以下（DeiT-Tiny，測定層）",
    "LLM では最大で約 20 倍（前の枚，LLM.int8()）",
], os.path.join(EXPF, "2026-11-14-act-channel-absmax-large.png"), 1.5, 2.5, (
    "この fine-tune済みDeiT-Tinyで，Linear入力のチャネルごとの最大値を調べると，最大値と中央値の比は，測った層で最大でも4.3でした。"
    "LLMでは最大で約20倍という報告でしたから，LLM型の外れ値は，このDeiT-Tinyの測った層では見えません。"
    "ResNet18のlayer4.1.conv2は1.7です。ただし，ViT一般で外れ値がないとは言っていません。測ったのはこの1つのモデルの，いくつかの層だけです。"
    "ViTの活性の分布を直接扱う原典はPTQ4ViTで，softmaxやGELUの後ろの偏りを問題にしています。この結果と，次の節のA4の崩れとのつながりは，そこで見ます。"),
    f"{SRC_MEAS}（結果ログ §3）．fine-tune 済み DeiT-Tiny の測定層のみ．LLM の約 20 倍: LLM.int8() [Dettmers+, NeurIPS2022] §1")

# ---------------- 45-62 活性と較正（演習③）----------------
section("3. 活性も量子化する", "45–62分  問い: 入力ごとに変わる活性のレンジをどう決める？", 0.3, (
    "第3節です。ここまでは重みだけでした。ここからは活性も量子化します。"), "活性・較正")

bullets("W と A: 量子化する演算", [
    "WxAy: 重み x bit，入力活性 y bit（fake-quant）",
    "対象: すべての Conv2d と Linear（最初・最後の層も）",
    "FP32 のまま: Softmax，LayerNorm，GELU，残差，Attention の行列積",
    "ResNet18 は BN を Conv に畳んでから重みを量子化",
    "活性は非対称・per-tensor・静的",
], 2.0, (
    "WxAyは，対象の演算の重みxビット，入力活性yビットという意味です。対象はすべてのConv2dとLinearで，最初と最後の層も含みます。"
    "ViTのSoftmaxやLayerNorm，GELU，残差の足し算，Attentionの行列積はFP32のままです。ResNet18ではBNをConvに畳み込んでから重みを量子化します。これは2枚あとで説明します。"
    "活性は非対称・per-tensor・静的で，較正で決めたscaleを評価中は更新しません。あくまでfake-quantで，実際のdtypeを伴うA16のような呼び方は演習では使いません。"),
    "本演習の設定（ハンズオン README）", size=24)

bullets("活性は較正でレンジを決める", [
    "静的量子化: 較正データで scale・z を先に決める",
    "較正データ: train から固定した 512 枚",
    "minmax: 最小・最大，外れ値に弱い",
    "MSE: 誤差が最小になる範囲を探索",
    "percentile: 分位点でクリップ（本演習は 99.99）",
], 2.7, (
    "活性は入力ごとに値が変わるので，較正データを数百枚流してレンジを決めます。演習では，train から固定した512枚を使います。"
    "minmaxは最小と最大をそのまま使うので，外れ値に弱いです。MSEは量子化誤差が最小になる範囲を探索します。percentileは分位点でクリップします。"
    "出典の注意ですが，minmaxとMSEはNagel白書，percentileはFP8論文が最良の較正を選ぶ候補として挙げている記述を根拠にしていて，FP8論文は定義の式までは述べていません。"
    "較正方法とパラメータは事前に決め，testの結果で選び直していません。"),
    "原典: minmax・MSE は" + NAGEL + " §3.1，percentile は FP8 [Micikevicius+, arXiv2022] §4.2．設定はハンズオン README", size=24)

eq_slide("BN を Conv に畳む", [
    ("t", "推論時の BN は，チャネルごとの掛け算と足し算", 24),
    ("e", r"\tilde{W}_{k} = \frac{\gamma_k W_k}{\sqrt{\sigma_k^{2} + \epsilon}}", 36),
    ("e", r"\tilde{b}_{k} = \beta_k - \frac{\gamma_k \mu_k}{\sqrt{\sigma_k^{2} + \epsilon}}", 36),
    ("t", "畳んだ後の重みを量子化する\nResNet18 の演習で使用（DeiT-Tiny は BN なし）", 24),
], 2.0, (
    "ResNet18では，BatchNormをConvに畳み込んでから重みを量子化します。推論時のBNは，チャネルごとの掛け算と足し算なので，Convの重みとバイアスに吸収できます。"
    "吸収した後の重みはガンマ倍で，チャネルごとに範囲が変わります。畳んだ後の重みW̃を量子化するのが大事で，畳む前の重みを量子化しても推論時の実際の重みとは違います。"
    "式はNagel白書の式(11)と(12)です。畳み込みの前後でFP32の出力の最大差は，倍精度で1.8e-14，単精度で1.1e-5で，実装の誤りではなく丸め誤差の範囲でした。DeiT-TinyにはBNがないので，この手順は要りません。"),
    "原典: " + NAGEL + " §2.3.1 式(11)(12)，" + JACOB + " §3.2．最大差は" + SRC_MEAS + "（結果ログ §2-3）", size=24)

bullets("演習③: 較正を変えて比べる", [
    "python ex3_act.py -m deit_tiny -w 8 -a 4",
    ("  -c minmax percentile mse", 1),
    "所要: GPU 約 15 秒，CPU 約 30〜40 秒（3方法まとめて）",
    "CPU では 25.45 / 70.70 / 47.60，最大 0.3〜0.55 pp ずれる（順位は同じ）",
    "分布の図: python plot_act_dist.py --out act.png（CPU 約 10 秒）",
], 6.0, (
    "ここで演習③を回します。DeiT-Tinyで，重み8bit，活性4bitのまま，較正方法をminmax，percentile，mseの3つで回します。"
    "3つまとめてGPUで約15秒，CPUで30〜40秒です。GPUでは24.9，71.05，47.6でした。CPUで回すとminmaxが25.45，percentileが70.70，mseが47.60と，最大で0.55ポイントずれますが，percentile，mse，minmaxの順位は変わりません。"
    "A4のように崩れやすい条件では，GPUとCPUで数値が少しずれることがあります。そのあと，plot_act_dist.pyで活性のチャネルごとの最大値の図を作れます。CPUで約10秒です。"
    "5分ほどとります。結果は次の枚の数値と見比べてください。"),
    "所要時間: 本環境の実測（結果ログ §2-4）．CPU の値: 同 §7-2．plot_act_dist の所要は作者の実測（CPU，約 9 秒）．コマンドは README", size=24)

table("W8A8 は較正によらずほぼ無劣化", [
    ["重み 8bit per-channel", "minmax", "percentile", "mse"],
] + [[f"{lab}  A{ab}"] + [fmt(m, w_bits=8, a_bits=ab, calib=c, table="act_w8") for c in ("minmax", "percentile", "mse")]
     for lab, m in (("ResNet18", "resnet18"), ("DeiT-Tiny", "deit_tiny")) for ab in (8, 6)], 1.5, (
    "活性の結果です。重みを8bit per-channelにして，活性を8bit，6bitにしたときの精度と，FP32との差です。"
    "A8では，ResNet18もDeiT-Tinyも，どの較正方法でもFP32との差は0.2ポイント以内です。A6でもDeiT-Tinyでマイナス1ポイント以内に収まっています。"
    "つまりW8A8は，この2モデルでは較正方法をあまり気にしなくてもほぼ無劣化です。白書も，8bitはPTQで足りることが多いと述べています。"
    "差が0.1〜0.2ポイントのものは，1回の実行の揺れの範囲です。"),
    source=f"{SRC_MEAS}（結果ログ §4）．括弧内は FP32 との差 [pp]（FP32: 93.45 / 95.00）．1回の実行",
    lead="活性: 非対称・per-tensor・静的，差は FP32 との差 [pp]", col_widths=[3, 3, 3, 3], size=18)
# 先に定義した table 呼び出しの重複を避けるため，上の1回だけを使う

txt_img("DeiT-Tiny は A4 で較正に左右される", [
    "DeiT-Tiny A4: minmax 24.9，mse 47.6，percentile 71.05",
    "ResNet18 の A4 は 86〜91% で耐える",
    "外れ値だけでは説明できない（機序は未検証の解釈）",
], os.path.join(EXPF, "2026-11-14-act-calib-a-bits.png"), 2.15, 2.5, (
    "A4まで下げると差が出ます。ResNet18は，minmaxが86.70，percentileが91.30，mseが90.85と，A4でも比較的耐えます。"
    "一方DeiT-Tinyは，minmaxで24.90，mseで47.60，percentileで71.05と，較正方法で大きく変わり，どれもFP32の95.00には届きません。"
    "前の節で見たとおり，このDeiT-TinyにはLLM型の外れ値は見えませんでした。1層だけをA4にしたときの低下も最大でマイナス2.45ポイントです。"
    "したがってA4の崩れは，層をまたいだ誤差の累積によるのではないかと私は解釈していますが，これは未検証の解釈です。"),
    f"{SRC_MEAS}（結果ログ §3, §4）．GPU の値，CPU では最大 0.55 pp ずれる（§7-2）．機序は発表者の解釈（未検証）")

# ---------------- 62-80 PTQ・QAT・SmoothQuant・分類表＋演習④ ----------------
section("4. 足りないとき・速さ", "62–80分  問い: 学習で補う？ 外れ値は？ 本当に速い？", 0.3, (
    "第4節です。PTQで足りないとき，どうするかを見て，そのあと演習④で本当に速くなるかを測ります。"), "PTQ・QAT・④")

txt_img("QAT: 量子化を含めて学習する", [
    "PTQ は再学習なし，QAT は誤差を見ながら重みを更新",
    "代償: 学習時間・ラベル付きデータ・ハイパーパラメータ探索",
], os.path.join(FIG, "qat_flow.png"), 1.6, 1.5, (
    "PTQで足りないときの手が，QATです。順伝播ではfake-quantで量子化の誤差を含めて計算し，逆伝播では重みをFP32のまま更新します。"
    "学習が終わったら，重みを実際の整数に変換して配ります。白書によると，QATは特に活性4bit以下のような低ビットで有利ですが，"
    "学習時間，ラベル付きデータ，ハイパーパラメータ探索というふつうの学習のコストがかかります。図は流れを模式的に描いたものです。"),
    "原典: " + JACOB + " §3，" + NAGEL + " §4．図は模式図")

txt_eq_img("round の勾配は STE で通す",
    "round の勾配は 0 か未定義，STE では次のようにみなして逆伝播",
    r"\frac{\partial \lfloor y \rceil}{\partial y} = 1",
    os.path.join(FIG, "ste.png"), 2.0, (
    "なぜそのまま学習できないか。丸め関数はほとんど至る所で勾配が0で，微分できないところもあり，勾配法が使えません。"
    "そこでStraight-Through Estimator，STEで，丸めの勾配を1とみなして通します。式はNagel白書の式(36)です。"
    "STEの原典はBengioらですが，そこで扱われているのは確率的なバイナリニューロンです。量子化のroundに当てはめてSTEと明記しているのは，KrishnamoorthiとNagelの白書，それにLSQです。"
    "Jacobらは，順伝播で丸めを模擬し逆伝播は通常どおり行う，と述べていますが，STEという語は使っていません。ここは書き分けておきます。"),
    "原典: " + NAGEL + " §4.1 式(36)，白書 [Krishnamoorthi, arXiv2018] §3.2．STE の原典 [Bengio+, arXiv2013] は確率的ニューロンの文脈")

txt_img("W4A8 では QAT が PTQ を上回った", [
    "ResNet18: PTQ 90.65 → QAT 93.1（3 seed 平均）",
    "DeiT-Tiny: PTQ 91.90 → QAT 93.7",
    ("fine-tune→PTQ: 同じ更新回数の通常の fine-tune のあと PTQ", 1),
], os.path.join(EXPF, "2026-11-14-qat-vs-ptq.png"), 2.0, 2.0, (
    "実測です。重み4bit per-channel，活性8bit mseで，QATは約1エポックぶんの390ステップ，3つのseedで学習しました。"
    "ResNet18はPTQのみの90.65からQATの93.1で約+2.5ポイント，DeiT-Tinyは91.90から93.7で約+1.8ポイントです。同じ更新回数だけ通常のfine-tuneをしてからPTQした91.2，91.8と比べても，3つのseedすべてでQATが上回りました。"
    "ただし，これは1つの設定，W4A8，短い学習，1つのデータセットでの観察です。学習率やエポック数は調整していません。QATが一般にPTQより優れるという主張はしません。"),
    f"{SRC_MEAS}" + EXP_LOG.format("5") + "，1設定（学習率・epoch 未調整），3 seed 平均，一般化しない，fake-quant")

eq_slide("SmoothQuant: 難しさを重みへ移す", [
    ("t", "活性の各チャネル j を係数 s で割り，重みの入力チャネル j に s を掛ける", 24),
    ("e", r"s_j = \frac{\max(|X_j|)^{\alpha}}{\max(|W_j|)^{1-\alpha}}", 38),
    ("t", "X: 活性，W: 重み，j: チャネル番号（式の s の添字も j）\nα: 移す量，OPT・BLOOM では 0.5 が基本\n較正データで s を求め，変換はオフライン", 24),
], 2.5, (
    "外れ値への対策の一つがSmoothQuantです。活性のチャネルjをs_jで割り，重みの対応する入力チャネルにs_jを掛けると，線形層の出力は数学的に変わりません。"
    "このとき活性の外れ値が小さくなり，そのぶん重みが少し難しくなる，つまり量子化の難しさを活性から重みへ移します。"
    "s_jは活性と重みの最大値から式(4)で決め，アルファが移す量を決めます。0.5が基本で，外れ値が多いモデルでは大きくします。"
    "較正サンプルでsを求め，変換は事前に済ませるので，実行時の追加コストはありません。式はSmoothQuant論文の式(4)です。Xは活性，Wは重み，jはチャネル番号です。"
    "前の節で見たように，DeiT-Tinyでは外れ値チャネルが目立たなかったので，SmoothQuantがDeiT-Tinyで効くかどうかは測っていません。原典の数値はLLMでのものです。"),
    "原典: SmoothQuant [Xiao+, ICML2023] §4 式(3)(4)．α = 0.5 は OPT・BLOOM での記述")

table("SmoothQuant で W8A8 が崩れない", [
    ["OPT-175B", "7タスク平均", "WikiText ppl（小さいほど良い）"],
    ["FP16", "66.9%", "10.99"],
    ["W8A8（素朴）", "35.5%", "93080"],
    ["LLM.int8()", "66.7%", "11.10"],
    ["SmoothQuant-O3", "66.8%", "11.17"],
], 1.2, (
    "効果です。OPT-175Bで，素朴にW8A8にすると，7タスク平均が35.5%，perplexityが93080とほぼ崩壊します。"
    "SmoothQuantはO3の設定で66.8%，perplexity 11.17と，FP16の66.9%，10.99にほぼ並びます。LLM.int8()も同等です。"
    "これはOPT-175Bという巨大なLLMでの原典の数値で，私たちのDeiT-Tinyの実測とは条件が違います。"),
    source="原典: SmoothQuant [Xiao+, ICML2023] §5.2 Table 3（OPT-175B），本環境の実測ではない",
    lead="LLM（OPT-175B）での原典の数値，素朴な W8A8 は崩壊", col_widths=[4, 3, 4], size=20)

table("分類表: 手法の位置づけ", [
    ["軸", "例", "一言"],
    ["いつ量子化するか", "PTQ / QAT", "再学習なし / 学習で補う"],
    ["丸め・較正の工夫", "AdaRound，BRECQ，GPTQ", "丸め方・再構成で誤差を減らす"],
    ["外れ値・スケール", "LLM.int8()，SmoothQuant，AWQ", "別扱い / 等価変換 / 重要なチャネルを保護"],
    ["数値形式", "INT8/INT4，FP8，NF4", "一様 / 非一様"],
    ["量子化モデルでの学習", "QLoRA", "NF4 で凍結した重み + LoRA"],
    ["対象ドメイン", "PTQ4ViT，Q-Diffusion", "ViT・拡散モデル向け（補足）"],
], 1.5, (
    "分類表です。軸を混ぜないために，いつ量子化するか，丸め・較正の工夫，外れ値・スケールの扱い，数値形式，量子化モデルの上での学習，対象ドメインの6つに分けています。"
    "AdaRoundとBRECQとGPTQは重みの丸め方や再構成で誤差を減らす手法です。LLM.int8()とSmoothQuantとAWQは外れ値やスケールの扱いです。"
    "詳しく扱ったのはPTQとQAT，それからSmoothQuantだけで，ほかはこの表で位置づけだけ確認してください。PTQ4ViTとQ-Diffusionは補足に1枚あります。AdaRoundとBRECQの数値は基準のFP32が違うので，並べて比べていません。"),
    source="原典: GPTQ [Frantar+, ICLR2023]，AWQ [Lin+, MLSys2024]，AdaRound [Nagel+, ICML2020]，BRECQ [Li+, ICLR2021]，QLoRA [Dettmers+, NeurIPS2023]",
    col_widths=[3, 4, 5], size=18)

table("演習④: 実際の INT8 を測る", [
    ["経路（CPU）", "サイズ", "遅延 ms/batch32", "精度"],
    ["ResNet18 FP32（測り直し）", "44.80 MB", "53〜55", "93.45%"],
    ["ResNet18 INT8（FX）", "11.30 MB", "37〜38", "93.55%"],
    ["DeiT-Tiny FP32（測り直し）", "22.04 MB", "45〜49", "95.00%"],
    ["DeiT-Tiny INT8 weight-only", "6.24 MB", "50〜54", "95.00%"],
    ["DeiT-Tiny INT8 dynamic", "6.24 MB", "約790", "94.90%"],
], 3.0, (
    "演習④の実演です。これは実際の低精度実行で，fake-quantではありません。CPU 8スレッド，batch 32で，ウォームアップ30回のあと30回測った中央値です。"
    "ResNet18のINT8はサイズが約4分の1で，遅延は約0.69倍と速くなりました。DeiT-Tinyは，weight-onlyでサイズは3.5分の1ですが遅延は同等かやや遅く，dynamicは約790ミリ秒とFP32の約16倍遅くなりました。"
    "FP32は，量子化したモデルを測ったあとで測り直した値を基準にしています。実行にはfx_int8で約20秒，torchaoで85秒から2分かかるので，ここでは事前に測った結果を見せます。共有マシンで雑音もあります。"),
    source=f"{SRC_MEAS}（結果ログ §2-5，§7-2）．ResNet18: torch.ao FX x86，DeiT-Tiny: torchao．5〜6回の実行，共有マシン",
    col_widths=[4.2, 2, 2.6, 1.8], size=18)

bullets("INT8 でも遅くなることがある", [
    "ResNet18（Conv を含む）: 約 0.69 倍で速い",
    "DeiT-Tiny weight-only: 同等〜やや遅い",
    "dynamic は約 16 倍遅い",
    ("時間の約 88% が aten::_int_mm（profiler）", 1),
    "分かったのは「この CPU・この版で kernel が速くない」まで",
], 2.0, (
    "なぜ遅くなるのか。dynamic INT8をtorch.profilerで見ると，実行時間の約88%がaten::_int_mm，INT8の行列積に使われていました。"
    "つまり遅いのは活性を量子化する処理ではなく，このCPUと，torch 2.15でのINT8行列積のkernelです。"
    "確認できたのは，このkernelが速くないところまでで，他のCPUや他のバージョンでは結果が変わりえます。"
    "量子化すれば速くなるとは限らず，モデル・演算・kernelで決まるので，速度は必ず対象の環境で測る必要があります。"),
    f"{SRC_MEAS}（結果ログ §2-5）．torch 2.15，CPU．他の CPU・版では変わりうる，原因の一般化はしない", size=24)

table("演習②③: 追加の条件を回す", [
    ["演習", "追加の条件（-m 以降）", "所要の目安（1条件）"],
    ["②", "-m deit_tiny -w 4 -g per_group", "GPU 約6秒 / CPU 約13秒"],
    ["③", "-m resnet18 -w 8 -a 4 -c minmax percentile mse", "GPU 約12秒 / CPU 約27秒（3方法）"],
    ["③", "-m deit_tiny -w 8 -a 6 -c minmax percentile mse", "GPU 約16秒 / CPU 約39秒（3方法）"],
], 2.0, (
    "ここで2分，演習②と③を追加の条件で回します。②はDeiT-Tinyのper-group，③はResNet18のA4と，DeiT-TinyのA6です。"
    "所要時間は，②が1条件でGPU約6秒，CPU約13秒，③は3つの較正方法まとめてGPU 12〜16秒，CPU 27〜39秒です。"
    "全比較表は付録にあります。先ほどの結果と見比べて，8bitなら較正を気にしなくてよいこと，4bitでは較正でも決まることを確かめてください。"),
    source=f"所要の目安: {SRC_MEAS}（結果ログ §2-4，②は per-channel，③は W8A8 の値）．コマンドは README．fake-quant",
    lead="CPU は最大 0.3〜0.55 pp ずれる，順位を見る", col_widths=[1.6, 6, 4], size=18)

# ---------------- 80-90 まとめ ----------------
section("5. まとめ", "80–90分  議論・判断基準・質疑", 0.2, (
    "最後の10分です。自分のモデルに移すときの議論と確認項目，今日の困りごとへの答えをまとめます。"), "まとめ")

bullets("議論: 自分のモデルに移すなら", [
    "動画・生成モデルで，どの演算を量子化する？",
    "較正データは何を使う？ 評価指標は？",
    "欲しいのは速度？ メモリ？ 精度の維持？",
    "隣の人と 2 分話してから共有",
], 3.0, (
    "最後に議論です。皆さんの動画認識や生成のモデルに移すとしたら，どの演算を量子化するか，較正データには何を使うか，評価は分類精度でよいのか，FIDなど別の指標か，"
    "そして欲しいのは速度かメモリか，を隣の人と2分ほど話してください。そのあと数人に共有してもらいます。"
    "拡散モデルのように，時間方向で分布が変わるモデルでは，較正データの取り方が変わるかもしれません。Q-Diffusionがその例で，補足に1枚あります。"),
    "議論のための問い（発表者作成）．原典・実測ではない")

bullets("自分のモデルに移す確認項目", [
    "① 目的: メモリ・速度・精度の維持のどれか",
    "② 対象: どの演算を量子化するか（最初・最後の層は）",
    ("ViT: softmax・GELU 後は特別扱い，拡散: timestep ごとに較正", 1),
    "③ 較正: データと方法（minmax・percentile・MSE）",
    "④ 評価: 同じデータで FP32 との差を見る",
    "⑤ 実機: 速度は対象のハードウェアで測る",
], 2.5, (
    "確認項目を五つにまとめます。目的，対象，較正，評価，実機です。目的がメモリならfake-quantではなく実際の低ビット格納が要ります。"
    "対象は，今日のように全Conv2dとLinearとするのか，最初と最後の層は残すのかを決めます。ViTではsoftmaxやGELUの後ろの分布が偏るのでPTQ4ViTのように別扱いし，拡散モデルではtimestepごとに分布が変わるのでQ-Diffusionのように全timestepから較正します。どちらも補足に1枚あります。較正はデータと方法を事前に決め，testで選び直さないこと。"
    "評価は同じデータでFP32との差を見ること。速度は，今日の演習④のように，モデルとkernelで変わるので，対象のハードウェアで測ることです。"
    "これは今日の実測と原典から私が整理した確認項目です。"),
    "発表者の解釈（本日の実測と原典からの整理）", size=24)

table("困りごと → 今日の答え", [
    ["困りごと", "今日の答え", "根拠"],
    ["14B が載らない", "重みを INT8・4bit に（28→14→7 GB）", "計算例"],
    ["エッジで動かしたい", "8bit でサイズ 1/4（原典）．速さは実機で測る", "原典・実測"],
    ["4bit で崩れた", "per-channel・group で W4 は 91〜94%", "実測"],
    ["活性も量子化", "W8A8 は無劣化，A4 は較正に左右される", "実測"],
    ["まだ足りない", "QAT（W4A8，PTQ のみ比 +1.8〜2.5 pp）", "実測"],
    ["速くしたい", "モデル・kernel 次第．実機で測る", "実測"],
], 1.5, (
    "三つの困りごとと，その先で出てきた問題への答えを並べます。載らない問題は，重みをINT8や4bitにすると28から14，7ギガに減る，という計算例。"
    "エッジは，原典は8bitでサイズ4分の1と述べますが，速さは実機で測る必要があります。4bitで崩れる問題は，per-channelやper-groupで91から94%に回復する実測。"
    "活性も量子化する場合，W8A8は無劣化で，A4は較正で大きく変わる実測。足りないときはQATで，W4A8の1設定ではPTQのみに比べてResNet18で2.5，DeiT-Tinyで1.8ポイント上でしたが，一般化はしません。"
    "速くしたいは，モデルとkernel次第なので，実機で測るという実測です。"),
    source="各枚の出典のとおり（計算例: 14B × 2/1/0.5 byte，実測: 結果ログ §2-5, §3〜§5）",
    col_widths=[2.5, 5.5, 2], size=18)

two_col("言えること・言えないこと", [
    "**言えること",
    "W8A8 はこの 2 モデルでほぼ無劣化",
    "W4 は粒度で回復する",
    "INT8 はサイズが 1/3.5〜1/4",
], [
    "**言えないこと",
    "QAT が一般に PTQ より良い",
    "fake-quant の精度 = 高速化",
    "A4 の崩れの原因は外れ値",
], 1.5, (
    "最後に，言えることと言えないことを分けます。言えるのは，この2モデルでW8A8がほぼ無劣化だったこと，W4が粒度で回復したこと，INT8でサイズが約3.5〜4分の1になったことです。"
    "言えないのは，QATが一般にPTQより良いということ，fake-quantの精度が高速化を意味するということ，A4の崩れの原因が外れ値だということです。"
    "最後のものは，実測では外れ値が見えなかったので，未検証の解釈にとどまります。"),
    source=f"{SRC_MEAS}（結果ログ §2-5, §3〜§5）．言えないことは発表者の解釈（未検証を含む）")

bullets("さらに学ぶ資料・質疑", [
    "MIT 6.5940 EfficientML.ai（量子化の講義と Lab）",
    "Quantization in Depth（DeepLearning.AI × HF）",
    "joisino「深層モデルの高速化」（日本語）",
    "白書 [Nagel+, arXiv2021]，ハンズオン README",
    "質疑",
], 1.3, (
    "さらに学ぶための資料です。MITのEfficientML.aiには量子化の講義と演習があります。DeepLearning.AIのQuantization in Depthは線形量子化を自作して学べます。"
    "日本語では，joisinoさんの深層モデルの高速化のスライドが読みやすいです。原典としては，Nagelらの白書が全体像に向いています。"
    "今日のハンズオンはquantization_handsonのREADMEから再現できます。質問があればどうぞ。"),
    "出典: 既存資料の調査（existing-materials §6）．MIT・Quantization in Depth の中身は一部未確認", size=24)

# ---------------- 付録 ----------------
APPENDIX = True
SEC[0] = "付録"
d.section("付録", "全比較表・補足", notes="付録です。質問が出たときに使います。")
rec("付録", 0)


def w_table(model, title):
    rows = [["bit", "per-tensor", "per-channel", "per-group(64)"]]
    for b in (8, 6, 4, 3, 2):
        rows.append([f"W{b}"] + [fmt(model, w_bits=b, granularity=g, table="weight_only")
                                  for g in ("per_tensor", "per_channel", "per_group")])
    d.table(title, rows, notes="重みだけを量子化した全比較表です。括弧内はFP32との差で，W6までは粒度によらずほぼ同じ，W4以下で差が出ます。",
            source=f"{SRC_MEAS}（結果ログ §4 重みのみ）．括弧内は FP32 ({M[model]['fp32']['eval2000']:.2f}%) との差 [pp]，1回の実行",
            col_widths=[1.5, 3, 3, 3], size=18)
    rec(title, 0)


def a_table(model, title):
    rows = [["活性 bit", "minmax", "percentile(99.99)", "mse"]]
    for b in (8, 6, 4, 3, 2):
        rows.append([f"A{b}"] + [fmt(model, w_bits=8, a_bits=b, calib=c, table="act_w8")
                                  for c in ("minmax", "percentile", "mse")])
    d.table(title, rows, notes="重み8bit per-channelに活性を足した全比較表です。A8とA6は較正によらずほぼ同じで，A4以下で較正の差が出ます。",
            source=f"{SRC_MEAS}（結果ログ §4）．重み 8bit per-channel，括弧内は FP32 ({M[model]['fp32']['eval2000']:.2f}%) との差 [pp]",
            col_widths=[1.5, 3, 3, 3], size=18)
    rec(title, 0)


w_table("resnet18", "全比較: ResNet18 重みのみ")
w_table("deit_tiny", "全比較: DeiT-Tiny 重みのみ")
a_table("resnet18", "全比較: ResNet18 の活性")
a_table("deit_tiny", "全比較: DeiT-Tiny の活性")
d.bullets("層ごとの感度（1層だけ量子化）", [
    "DeiT-Tiny: A4 の最大低下は blocks.0.mlp.fc2（GELU 後）",
    ("95.00 → 92.55，ほとんどの層は −0.3 pp 以内", 1),
    "入力に近い層は敏感",
    ("ResNet18 conv1: W4 92.5%，A4 92.05%（FP32 93.45%）", 1),
    ("DeiT-Tiny patch_embed: W4 93.7%，A4 93.65%", 1),
], notes="1層だけ量子化したときの感度です。全層をA4にしたときの崩れは，層をまたいだ誤差の累積とみられますが，未検証の解釈です。",
    source=f"{SRC_MEAS}（結果ログ §3，results/sensitivity.json）．1層だけの量子化")
rec("層ごとの感度（1層だけ量子化）", 0)
d.bullets("NF4: 実際の 4bit のメモリ", [
    "timm ViT-Base の Linear のみ NF4（bitsandbytes）",
    "パラメータ保持量: FP16 165 MiB → NF4 43 MiB",
    "forward（batch 8）の peak: 0.20 → 0.07 GiB",
    "重みは未学習の初期値，精度は測っていない",
], notes="実際の4bit（NF4）でのメモリです。GPU0で測り，精度は測っていません。",
    source=f"{SRC_MEAS}（結果ログ §2-5）．実際の低精度実行（GPU0 A4000），torch.cuda.max_memory_allocated")
rec("NF4: 実際の 4bit のメモリ", 0)
d.bullets("原典の高速化は専用 kernel の話", [
    "GPTQ: OPT-175B 3bit で 3.24 倍（A100）",
    ("FP16 は 5 GPU，3bit は 1 GPU の遅延比", 1),
    ("重みを都度 dequantize する専用 kernel", 1),
    "SmoothQuant: 最大 1.56 倍，メモリ約半分",
    "AWQ: GPU で 3 倍超（TinyChat）",
    "LLM.int8(): 小さいモデルでは遅くなりうる",
], notes="原典の高速化はGPU上の専用kernelでの値で，演習④の実測とは別です。GPTQの3.24倍は，FP16を5GPU，3bitを1GPUで動かした1トークンの遅延の比です。",
    source="原典: GPTQ [Frantar+, ICLR2023] Table 6，SmoothQuant [Xiao+, ICML2023]，AWQ [Lin+, MLSys2024]，LLM.int8() [Dettmers+, NeurIPS2022] §3.4（GPU）", size=24)
rec("原典の高速化は専用 kernel の話", 0)
d.bullets("ViT・拡散モデルへの移し方", [
    "ViT: softmax 後・GELU 後の分布が偏る → PTQ4ViT",
    ("ViT-S/224 の W8A8 で低下 0.38 pp", 1),
    "拡散: timestep ごとに活性分布が変わる",
    ("全 timestep から較正データを取る（Q-Diffusion）", 1),
    ("CIFAR-10 の 4bit 重みで FID 5.09（FP32 は 4.22）", 1),
], notes="ViTでは，softmaxの後ろは0付近に偏り，GELUの後ろは非対称な分布になります。PTQ4ViTはその分布に合わせます。拡散モデルでは，timestepごとに活性分布が変わるので，Q-Diffusionは全timestepから較正データを取ります。どちらも原典の数値で，演習の条件とは別です。",
    source="原典: PTQ4ViT [Yuan+, ECCV2022] §3.2 Table 1（ImageNet），Q-Diffusion [Li+, ICCV2023] §3.1 Table 1（CIFAR-10）．本演習の条件とは別", size=24)
rec("ViT・拡散モデルへの移し方", 0)


# 文の区切りの「．」は「，」にそろえる（スライド上の文字のみ．ノートは対象外）
def _fix_punct(prs):
    def runs(shape):
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                yield from p.runs
        if getattr(shape, "has_table", False) and shape.has_table:
            for row in shape.table.rows:
                for c in row.cells:
                    for p in c.text_frame.paragraphs:
                        yield from p.runs
    for sl in prs.slides:
        for sh in sl.shapes:
            for r in runs(sh):
                if "．" in r.text:
                    r.text = r.text.replace("．", "，")


_fix_punct(d.prs)


def _fix_notes(prs):
    for sl in prs.slides:
        if sl.has_notes_slide:
            for p in sl.notes_slide.notes_text_frame.paragraphs:
                for r in p.runs:
                    r.text = r.text.replace("，", "、").replace("．", "。")


_fix_notes(d.prs)
d.save(OUT)

main = [p for p in PLAN if not p[4]]
total = sum(p[3] for p in main)
print("本編", len(main), "枚．合計", round(total, 2), "分．全", len(d.prs.slides), "枚")
sec_sum = {}
for n, sec, t, m, ap in main:
    sec_sum[sec] = round(sec_sum.get(sec, 0) + m, 2)
print(sec_sum)
with open(os.path.join(HERE, "_timetable_b.md"), "w") as f:
    f.write("| 枚 | 区分 | タイトル | 分 |\n|---|---|---|---|\n")
    for n, sec, t, m, ap in PLAN:
        f.write(f"| {n} | {sec} | {t} | {m if not ap else '付録'} |\n")
    f.write(f"\n本編 {len(main)} 枚，合計 {total:g} 分\n")
