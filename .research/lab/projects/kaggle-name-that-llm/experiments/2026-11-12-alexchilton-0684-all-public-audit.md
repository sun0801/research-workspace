# Alex Chilton 0.684 All Public + What Failed Notebook audit

**(b) 試さない。** Notebook本文が報告するpublic scoreは`.684`で、現leader`.768`を超える根拠や、採用bestに対する独立OOF補完性は示されない。

- Source: [Name That LLM 0.684: All Public + What Failed](https://www.kaggle.com/code/alexchilton/name-that-llm-0-684-all-public-what-failed)
- 取得日: 2026-11-12 JST。Kaggle CLIでsource/metadataをpullして本文を読んだ。実行・提出なし。
- Notebook本文はQwen3-14B/8B・Llama3.1-8B multi-depth LoRA、Qwen embedding、DeBERTa、stylometric stack、Sinkhorn等を組み合わせた大規模ensembleと説明し、作者アカウントで2026-11-11に`.684`を得たと報告する。ここで独立検証はしていない。
- 本文は同一コードのscoreが最大`.009`揺れた実例と、他候補を重ねてscoring-runで失敗した例を挙げる。一般的な不安定性の注意にはなるが、こちらのv9 hidden rerun errorの原因特定には使えない。
- `.684`は公開首位`.768`より低く、手元bestとのcomplementarityやOOFの根拠もないため試行しない。hidden rerunエラーの個別stack traceは公開本文にもない。
