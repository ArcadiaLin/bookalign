# EPUB Extraction Audit

- Book: `kinkaku.epub`
- Seed: `20261081`
- Sample count: `5`
- Test type: `complex`
- Granularity: `sentence`
- Debug metadata: `on`

## Samples

### Sample 1

- Chapter / Paragraph: `5` / `75`
- Document: `xhtml/0004.xhtml`
- XPath: `/*/*[2]/*/*[88]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">　金剛院は名高かった。それは安岡から歩いて十五分ほどの山かげにあり、<ruby>高丘<rt>たかおか</rt></ruby>親王<span class="super">＊九</span>の御手植の<ruby>栢<rt>かや</rt></ruby>や、<ruby>左甚五郎<rt>ひだりじんごろう</rt></ruby><span class="super">＊一〇</span>作と伝えられる優雅な三重塔のある<ruby>名刹<rt>めいさつ</rt></ruby><span class="super">＊一一</span>である。夏にはよく、その裏山の滝を浴びて遊んだ。</p>
```

#### Extracted Text

金剛院は名高かった。それは安岡から歩いて十五分ほどの山かげにあり、高丘親王の御手植の栢や、左甚五郎作と伝えられる優雅な三重塔のある名刹である。夏にはよく、その裏山の滝を浴びて遊んだ。

#### Sentence Segments

- `0`: 金剛院は名高かった。
- `1`: それは安岡から歩いて十五分ほどの山かげにあり、高丘親王の御手植の栢や、左甚五郎作と伝えられる優雅な三重塔のある名刹である。
- `2`: 夏にはよく、その裏山の滝を浴びて遊んだ。

#### CFI Roundtrip

金剛院は名高かった。それは安岡から歩いて十五分ほどの山かげにあり、高丘親王の御手植の栢や、左甚五郎作と伝えられる優雅な三重塔のある名刹である。夏にはよく、その裏山の滝を浴びて遊んだ。

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[88]` 金剛院は名高かった。それは安岡から歩いて十五分ほどの山かげにあり、
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[88]/*[1]` 高丘
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[88]` 親王
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[88]` の御手植の
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[88]/*[3]` 栢
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[88]` や、
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[88]/*[4]` 左甚五郎
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[88]` 作と伝えられる優雅な三重塔のある
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[88]/*[6]` 名刹
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[88]` である。夏にはよく、その裏山の滝を浴びて遊んだ。

#### Reviewer Notes

- Pending external review.

### Sample 2

- Chapter / Paragraph: `5` / `4`
- Document: `xhtml/0004.xhtml`
- XPath: `/*/*[2]/*/*[10]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">　五月の夕方など、学校からかえって、叔父の家の二階の勉強部屋から、むこうの小山を見る。若葉の山腹が西日を受けて、野の<ruby>只中<rt>ただなか</rt></ruby>に、<ruby>金屏風<rt>きんびょうぶ</rt></ruby>を建てたように見える。それを見ると私は、金閣を想像した。</p>
```

#### Extracted Text

五月の夕方など、学校からかえって、叔父の家の二階の勉強部屋から、むこうの小山を見る。若葉の山腹が西日を受けて、野の只中に、金屏風を建てたように見える。それを見ると私は、金閣を想像した。

#### Sentence Segments

- `0`: 五月の夕方など、学校からかえって、叔父の家の二階の勉強部屋から、むこうの小山を見る。
- `1`: 若葉の山腹が西日を受けて、野の只中に、金屏風を建てたように見える。
- `2`: それを見ると私は、金閣を想像した。

#### CFI Roundtrip

五月の夕方など、学校からかえって、叔父の家の二階の勉強部屋から、むこうの小山を見る。若葉の山腹が西日を受けて、野の只中に、金屏風を建てたように見える。それを見ると私は、金閣を想像した。

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[10]` 五月の夕方など、学校からかえって、叔父の家の二階の勉強部屋から、むこうの小山を見る。若葉の山腹が西日を受けて、野の
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[10]/*[1]` 只中
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[10]` に、
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[10]/*[2]` 金屏風
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[10]` を建てたように見える。それを見ると私は、金閣を想像した。

#### Reviewer Notes

- Pending external review.

### Sample 3

- Chapter / Paragraph: `12` / `78`
- Document: `xhtml/0011.xhtml`
- XPath: `/*/*[2]/*/*[97]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">　それでも私は黙ったまま彼に<ruby>対峙<rt>たいじ</rt></ruby>していた。そのとき子供たちのボールが<ruby>外<rt>そ</rt></ruby>れて、私たち二人の間へころがって来た。柏木は拾って返そうとして身をかがめかけた。意地の悪い興味が私に起り、一尺前にあるボールを、彼の内飜足がどんな風に活動して、彼の手につかませるかを見ようとした。無意識に私の目は彼の足のほうを見たらしい。柏木がこれを察した速さはほとんど神速と云ってよかった。彼はまだかがめたとも見えぬ身を起して私を見つめたが、その目には彼らしくもない冷静さを欠いた憎悪があった。</p>
```

#### Extracted Text

それでも私は黙ったまま彼に対峙していた。そのとき子供たちのボールが外れて、私たち二人の間へころがって来た。柏木は拾って返そうとして身をかがめかけた。意地の悪い興味が私に起り、一尺前にあるボールを、彼の内飜足がどんな風に活動して、彼の手につかませるかを見ようとした。無意識に私の目は彼の足のほうを見たらしい。柏木がこれを察した速さはほとんど神速と云ってよかった。彼はまだかがめたとも見えぬ身を起して私を見つめたが、その目には彼らしくもない冷静さを欠いた憎悪があった。

#### Sentence Segments

- `0`: それでも私は黙ったまま彼に対峙していた。
- `1`: そのとき子供たちのボールが外れて、私たち二人の間へころがって来た。
- `2`: 柏木は拾って返そうとして身をかがめかけた。
- `3`: 意地の悪い興味が私に起り、一尺前にあるボールを、彼の内飜足がどんな風に活動して、彼の手につかませるかを見ようとした。
- `4`: 無意識に私の目は彼の足のほうを見たらしい。
- `5`: 柏木がこれを察した速さはほとんど神速と云ってよかった。
- `6`: 彼はまだかがめたとも見えぬ身を起して私を見つめたが、その目には彼らしくもない冷静さを欠いた憎悪があった。

#### CFI Roundtrip

それでも私は黙ったまま彼に対峙していた。そのとき子供たちのボールが外れて、私たち二人の間へころがって来た。柏木は拾って返そうとして身をかがめかけた。意地の悪い興味が私に起り、一尺前にあるボールを、彼の内飜足がどんな風に活動して、彼の手につかませるかを見ようとした。無意識に私の目は彼の足のほうを見たらしい。柏木がこれを察した速さはほとんど神速と云ってよかった。彼はまだかがめたとも見えぬ身を起して私を見つめたが、その目には彼らしくもない冷静さを欠いた憎悪があった。

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[97]` それでも私は黙ったまま彼に
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[97]/*[1]` 対峙
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[97]` していた。そのとき子供たちのボールが
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[97]/*[2]` 外
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[97]` れて、私たち二人の間へころがって来た。柏木は拾って返そうとして身をかがめかけた。意地の悪い興味が私に起り、一尺前にあるボールを、彼の内飜足がどんな風に活動して、

#### Reviewer Notes

- Pending external review.

### Sample 4

- Chapter / Paragraph: `9` / `40`
- Document: `xhtml/0008.xhtml`
- XPath: `/*/*[2]/*/*[48]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">　そのとき私は彼の<ruby>詐術<rt>さじゅつ</rt></ruby>を見たように思ったのだが、わざわざああして路上に崩折れたのは、女の注意を惹くためであったのは<ruby>勿論<rt>もちろん</rt></ruby>だが、怪我の仮装で彼の内飜足を隠そうとしたのではなかったか？　しかしこの疑問は一向彼に対する<ruby>軽蔑<rt>けいべつ</rt></ruby>とはならず、むしろ親しみを増す<ruby>種子<rt>たね</rt></ruby>になった。そして私はごく青年らしい感じ方をしたのだが、彼の哲学が詐術にみちていればいるほど、それだけ彼の人生に対する誠実さが証明されるように思われたのである。</p>
```

#### Extracted Text

そのとき私は彼の詐術を見たように思ったのだが、わざわざああして路上に崩折れたのは、女の注意を惹くためであったのは勿論だが、怪我の仮装で彼の内飜足を隠そうとしたのではなかったか？ しかしこの疑問は一向彼に対する軽蔑とはならず、むしろ親しみを増す種子になった。そして私はごく青年らしい感じ方をしたのだが、彼の哲学が詐術にみちていればいるほど、それだけ彼の人生に対する誠実さが証明されるように思われたのである。

#### Sentence Segments

- `0`: そのとき私は彼の詐術を見たように思ったのだが、わざわざああして路上に崩折れたのは、女の注意を惹くためであったのは勿論だが、怪我の仮装で彼の内飜足を隠そうとしたのではなかったか？
- `1`: しかしこの疑問は一向彼に対する軽蔑とはならず、むしろ親しみを増す種子になった。
- `2`: そして私はごく青年らしい感じ方をしたのだが、彼の哲学が詐術にみちていればいるほど、それだけ彼の人生に対する誠実さが証明されるように思われたのである。

#### CFI Roundtrip

そのとき私は彼の詐術を見たように思ったのだが、わざわざああして路上に崩折れたのは、女の注意を惹くためであったのは勿論だが、怪我の仮装で彼の内飜足を隠そうとしたのではなかったか？ しかしこの疑問は一向彼に対する軽蔑とはならず、むしろ親しみを増す種子になった。そして私はごく青年らしい感じ方をしたのだが、彼の哲学が詐術にみちていればいるほど、それだけ彼の人生に対する誠実さが証明されるように思われたのである。

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[48]` そのとき私は彼の
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[48]/*[1]` 詐術
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[48]` を見たように思ったのだが、わざわざああして路上に崩折れたのは、女の注意を惹くためであったのは
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[48]/*[2]` 勿論
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[48]` だが、怪我の仮装で彼の内飜足を隠そうとしたのではなかったか？ しかしこの疑問は一向彼に対する
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[48]/*[3]` 軽蔑
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[48]` とはならず、むしろ親しみを増す
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[48]/*[4]` 種子
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[48]` になった。そして私はごく青年らしい感じ方をしたのだが、彼の哲学が詐術にみちていればいるほど、それだけ彼の人生に対する誠実さが証明されるように思われたのである。

#### Reviewer Notes

- Pending external review.

### Sample 5

- Chapter / Paragraph: `14` / `51`
- Document: `xhtml/0013.xhtml`
- XPath: `/*/*[2]/*/*[64]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">　私はその三束を抱えて、畑のかたわらを立戻った。<ruby>庫裏<rt>くり</rt></ruby>のほうはしんとしていた。料理部屋の角を曲って、執事寮の裏まで来たとき、そこの<ruby>厠<rt>かわや</rt></ruby>の窓に突然明りが射した。私はその場にうずくまった。</p>
```

#### Extracted Text

私はその三束を抱えて、畑のかたわらを立戻った。庫裏のほうはしんとしていた。料理部屋の角を曲って、執事寮の裏まで来たとき、そこの厠の窓に突然明りが射した。私はその場にうずくまった。

#### Sentence Segments

- `0`: 私はその三束を抱えて、畑のかたわらを立戻った。
- `1`: 庫裏のほうはしんとしていた。
- `2`: 料理部屋の角を曲って、執事寮の裏まで来たとき、そこの厠の窓に突然明りが射した。
- `3`: 私はその場にうずくまった。

#### CFI Roundtrip

私はその三束を抱えて、畑のかたわらを立戻った。庫裏のほうはしんとしていた。料理部屋の角を曲って、執事寮の裏まで来たとき、そこの厠の窓に突然明りが射した。私はその場にうずくまった。

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[64]` 私はその三束を抱えて、畑のかたわらを立戻った。
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[64]/*[1]` 庫裏
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[64]` のほうはしんとしていた。料理部屋の角を曲って、執事寮の裏まで来たとき、そこの
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[64]/*[2]` 厠
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[64]` の窓に突然明りが射した。私はその場にうずくまった。

#### Reviewer Notes

- Pending external review.

## Summary

- Total samples: `5`
- Ruby samples: `5`
- Footnote-ish samples: `1`
- Roundtrip mismatches: `0`

## Failed Samples

- None

## Suggested Fix Directions

- Inspect any roundtrip mismatch where normalized extracted text diverges from the paragraph segment.
- Review debug spans for over-skipped note links or missed ruby base text.
- Compare paragraph and sentence outputs when inline breaks appear in poetry-like XHTML.
