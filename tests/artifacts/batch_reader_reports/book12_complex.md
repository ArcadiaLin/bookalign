# EPUB Extraction Audit

- Book: `金閣寺 (三島由紀夫) (Z-Library).epub`
- Seed: `20261121`
- Sample count: `5`
- Test type: `complex`
- Granularity: `sentence`
- Debug metadata: `on`

## Samples

### Sample 1

- Chapter / Paragraph: `12` / `59`
- Document: `xhtml/0011.xhtml`
- XPath: `/*/*[2]/*/*[74]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">　それは壮麗な山門で火に包まれるのにふさわしかった。こんなに明るい午後では、火はおそらく見えないだろう。そこでそれは<ruby>夥<rt>おびただ</rt></ruby>しい煙に巻かれ、見えない<ruby>焔<rt>ほのお</rt></ruby>が空を<ruby>舐<rt>な</rt></ruby>めるさまは、<ruby>蒼空<rt>あおぞら</rt></ruby>がただ<ruby>歪<rt>ゆが</rt></ruby>んで揺れて見えることだけでそれと知れるだろう。</p>
```

#### Extracted Text

それは壮麗な山門で火に包まれるのにふさわしかった。こんなに明るい午後では、火はおそらく見えないだろう。そこでそれは夥しい煙に巻かれ、見えない焔が空を舐めるさまは、蒼空がただ歪んで揺れて見えることだけでそれと知れるだろう。

#### Sentence Segments

- `0`: それは壮麗な山門で火に包まれるのにふさわしかった。
- `1`: こんなに明るい午後では、火はおそらく見えないだろう。
- `2`: そこでそれは夥しい煙に巻かれ、見えない焔が空を舐めるさまは、蒼空がただ歪んで揺れて見えることだけでそれと知れるだろう。

#### CFI Roundtrip

それは壮麗な山門で火に包まれるのにふさわしかった。こんなに明るい午後では、火はおそらく見えないだろう。そこでそれは夥しい煙に巻かれ、見えない焔が空を舐めるさまは、蒼空がただ歪んで揺れて見えることだけでそれと知れるだろう。

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[74]` それは壮麗な山門で火に包まれるのにふさわしかった。こんなに明るい午後では、火はおそらく見えないだろう。そこでそれは
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[74]/*[1]` 夥
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[74]` しい煙に巻かれ、見えない
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[74]/*[2]` 焔
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[74]` が空を
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[74]/*[3]` 舐
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[74]` めるさまは、
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[74]/*[4]` 蒼空
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[74]` がただ
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[74]/*[5]` 歪
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[74]` んで揺れて見えることだけでそれと知れるだろう。

#### Reviewer Notes

- Pending external review.

### Sample 2

- Chapter / Paragraph: `12` / `24`
- Document: `xhtml/0011.xhtml`
- XPath: `/*/*[2]/*/*[36]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">　母はたまたま例の制札、<ruby>若<rt>も</rt></ruby>シ<ruby>之<rt>これ</rt></ruby>ヲ犯シタル者ハ国法ニ依リ処罰セラルベシと記した制札のかたわらに立っていた。髪のおどろにみだれたさまは、門燈のあかりで、<ruby>白髪<rt>しらが</rt></ruby>が一本一本逆立っているように見えた。母の髪はそれほど白くはないのに、燈火が映えてそう見えたのである。その髪に囲まれた小さな顔は動かなかった。</p>
```

#### Extracted Text

母はたまたま例の制札、若シ之ヲ犯シタル者ハ国法ニ依リ処罰セラルベシと記した制札のかたわらに立っていた。髪のおどろにみだれたさまは、門燈のあかりで、白髪が一本一本逆立っているように見えた。母の髪はそれほど白くはないのに、燈火が映えてそう見えたのである。その髪に囲まれた小さな顔は動かなかった。

#### Sentence Segments

- `0`: 母はたまたま例の制札、若シ之ヲ犯シタル者ハ国法ニ依リ処罰セラルベシと記した制札のかたわらに立っていた。
- `1`: 髪のおどろにみだれたさまは、門燈のあかりで、白髪が一本一本逆立っているように見えた。
- `2`: 母の髪はそれほど白くはないのに、燈火が映えてそう見えたのである。
- `3`: その髪に囲まれた小さな顔は動かなかった。

#### CFI Roundtrip

母はたまたま例の制札、若シ之ヲ犯シタル者ハ国法ニ依リ処罰セラルベシと記した制札のかたわらに立っていた。髪のおどろにみだれたさまは、門燈のあかりで、白髪が一本一本逆立っているように見えた。母の髪はそれほど白くはないのに、燈火が映えてそう見えたのである。その髪に囲まれた小さな顔は動かなかった。

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[36]` 母はたまたま例の制札、
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[36]/*[1]` 若
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[36]` シ
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[36]/*[2]` 之
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[36]` ヲ犯シタル者ハ国法ニ依リ処罰セラルベシと記した制札のかたわらに立っていた。髪のおどろにみだれたさまは、門燈のあかりで、
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[36]/*[3]` 白髪
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[36]` が一本一本逆立っているように見えた。母の髪はそれほど白くはないのに、燈火が映えてそう見えたのである。その髪に囲まれた小さな顔は動かなかった。

#### Reviewer Notes

- Pending external review.

### Sample 3

- Chapter / Paragraph: `8` / `37`
- Document: `xhtml/0007.xhtml`
- XPath: `/*/*[2]/*/*[47]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">　すべては無言で行われる。私たちは黙って頭を下げる。老師はほとんどそれに応えない。そして老師と副司さんの<ruby>下駄<rt>げた</rt></ruby>の<ruby>音<rt>おと</rt></ruby>が、石だたみの上を<ruby>戞々<rt>かつかつ</rt></ruby>とわれわれから遠のいてゆく。後ろ姿が全く見えなくなるまで見送るのが、禅家の礼である。</p>
```

#### Extracted Text

すべては無言で行われる。私たちは黙って頭を下げる。老師はほとんどそれに応えない。そして老師と副司さんの下駄の音が、石だたみの上を戞々とわれわれから遠のいてゆく。後ろ姿が全く見えなくなるまで見送るのが、禅家の礼である。

#### Sentence Segments

- `0`: すべては無言で行われる。
- `1`: 私たちは黙って頭を下げる。
- `2`: 老師はほとんどそれに応えない。
- `3`: そして老師と副司さんの下駄の音が、石だたみの上を戞々とわれわれから遠のいてゆく。
- `4`: 後ろ姿が全く見えなくなるまで見送るのが、禅家の礼である。

#### CFI Roundtrip

すべては無言で行われる。私たちは黙って頭を下げる。老師はほとんどそれに応えない。そして老師と副司さんの下駄の音が、石だたみの上を戞々とわれわれから遠のいてゆく。後ろ姿が全く見えなくなるまで見送るのが、禅家の礼である。

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[47]` すべては無言で行われる。私たちは黙って頭を下げる。老師はほとんどそれに応えない。そして老師と副司さんの
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[47]/*[1]` 下駄
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[47]` の
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[47]/*[2]` 音
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[47]` が、石だたみの上を
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[47]/*[3]` 戞々
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[47]` とわれわれから遠のいてゆく。後ろ姿が全く見えなくなるまで見送るのが、禅家の礼である。

#### Reviewer Notes

- Pending external review.

### Sample 4

- Chapter / Paragraph: `5` / `33`
- Document: `xhtml/0004.xhtml`
- XPath: `/*/*[2]/*/*[42]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">　たまたま、機関学校の制服は、脱ぎすてられて、白いペンキ塗りの<ruby>柵<rt>さく</rt></ruby>にかけられていた。ズボンも、白い下着のシャツも。……それらは花々の真近で、汗ばんだ若者の<ruby>肌<rt>はだ</rt></ruby>の匂いを放っていた。<ruby>蜜蜂<rt>みつばち</rt></ruby>がまちがえて、この白くかがやいているシャツの花に羽根を休めた。金モールに飾られた制帽は、柵のひとつに、彼の頭にあったと同じように、<ruby>正<rt>ただ</rt></ruby>しく、目深に、かかっていた。彼は後輩たちに<ruby>挑<rt>いど</rt></ruby>まれて、裏の土俵へ、<ruby>角力<rt>すもう</rt></ruby>をしに行ったのである。</p>
```

#### Extracted Text

たまたま、機関学校の制服は、脱ぎすてられて、白いペンキ塗りの柵にかけられていた。ズボンも、白い下着のシャツも。……それらは花々の真近で、汗ばんだ若者の肌の匂いを放っていた。蜜蜂がまちがえて、この白くかがやいているシャツの花に羽根を休めた。金モールに飾られた制帽は、柵のひとつに、彼の頭にあったと同じように、正しく、目深に、かかっていた。彼は後輩たちに挑まれて、裏の土俵へ、角力をしに行ったのである。

#### Sentence Segments

- `0`: たまたま、機関学校の制服は、脱ぎすてられて、白いペンキ塗りの柵にかけられていた。
- `1`: ズボンも、白い下着のシャツも。
- `2`: ……それらは花々の真近で、汗ばんだ若者の肌の匂いを放っていた。
- `3`: 蜜蜂がまちがえて、この白くかがやいているシャツの花に羽根を休めた。
- `4`: 金モールに飾られた制帽は、柵のひとつに、彼の頭にあったと同じように、正しく、目深に、かかっていた。
- `5`: 彼は後輩たちに挑まれて、裏の土俵へ、角力をしに行ったのである。

#### CFI Roundtrip

たまたま、機関学校の制服は、脱ぎすてられて、白いペンキ塗りの柵にかけられていた。ズボンも、白い下着のシャツも。……それらは花々の真近で、汗ばんだ若者の肌の匂いを放っていた。蜜蜂がまちがえて、この白くかがやいているシャツの花に羽根を休めた。金モールに飾られた制帽は、柵のひとつに、彼の頭にあったと同じように、正しく、目深に、かかっていた。彼は後輩たちに挑まれて、裏の土俵へ、角力をしに行ったのである。

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[42]` たまたま、機関学校の制服は、脱ぎすてられて、白いペンキ塗りの
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[42]/*[1]` 柵
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[42]` にかけられていた。ズボンも、白い下着のシャツも。……それらは花々の真近で、汗ばんだ若者の
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[42]/*[2]` 肌
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[42]` の匂いを放っていた。
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[42]/*[3]` 蜜蜂
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[42]` がまちがえて、この白くかがやいているシャツの花に羽根を休めた。金モールに飾られた制帽は、柵のひとつに、彼の頭にあったと同じように、
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[42]/*[4]` 正
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[42]` しく、目深に、かかっていた。彼は後輩たちに
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[42]/*[5]` 挑
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[42]` まれて、裏の土俵へ、
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[42]/*[6]` 角力
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[42]` をしに行ったのである。

#### Reviewer Notes

- Pending external review.

### Sample 5

- Chapter / Paragraph: `13` / `109`
- Document: `xhtml/0012.xhtml`
- XPath: `/*/*[2]/*/*[128]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">　私は地上の物象が、こんなにも敏感に天上の色を宿しているのを、一種の感動を以て<ruby>眺<rt>なが</rt></ruby>めた。<ruby>寺内<rt>じない</rt></ruby>の緑に立ちこめている雨の<ruby>潤<rt>うるお</rt></ruby>いも、すべて天上から<ruby>享<rt>う</rt></ruby>けたものであった。それらはあたかも<ruby>恩寵<rt>おんちょう</rt></ruby>を享けたように濡れそぼち、腐敗とみずみずしさの入りまじった<ruby>香<rt>か</rt></ruby>を放っていたが、それというのも、それらは拒む<ruby>術<rt>すべ</rt></ruby>を知らないからだった。</p>
```

#### Extracted Text

私は地上の物象が、こんなにも敏感に天上の色を宿しているのを、一種の感動を以て眺めた。寺内の緑に立ちこめている雨の潤いも、すべて天上から享けたものであった。それらはあたかも恩寵を享けたように濡れそぼち、腐敗とみずみずしさの入りまじった香を放っていたが、それというのも、それらは拒む術を知らないからだった。

#### Sentence Segments

- `0`: 私は地上の物象が、こんなにも敏感に天上の色を宿しているのを、一種の感動を以て眺めた。
- `1`: 寺内の緑に立ちこめている雨の潤いも、すべて天上から享けたものであった。
- `2`: それらはあたかも恩寵を享けたように濡れそぼち、腐敗とみずみずしさの入りまじった香を放っていたが、それというのも、それらは拒む術を知らないからだった。

#### CFI Roundtrip

私は地上の物象が、こんなにも敏感に天上の色を宿しているのを、一種の感動を以て眺めた。寺内の緑に立ちこめている雨の潤いも、すべて天上から享けたものであった。それらはあたかも恩寵を享けたように濡れそぼち、腐敗とみずみずしさの入りまじった香を放っていたが、それというのも、それらは拒む術を知らないからだった。

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[128]` 私は地上の物象が、こんなにも敏感に天上の色を宿しているのを、一種の感動を以て
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[128]/*[1]` 眺
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[128]` めた。
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[128]/*[2]` 寺内
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[128]` の緑に立ちこめている雨の
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[128]/*[3]` 潤
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[128]` いも、すべて天上から
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[128]/*[4]` 享
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[128]` けたものであった。それらはあたかも
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[128]/*[5]` 恩寵
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[128]` を享けたように濡れそぼち、腐敗とみずみずしさの入りまじった
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[128]/*[6]` 香
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[128]` を放っていたが、それというのも、それらは拒む
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[128]/*[7]` 術
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[128]` を知らないからだった。

#### Reviewer Notes

- Pending external review.

## Summary

- Total samples: `5`
- Ruby samples: `5`
- Footnote-ish samples: `0`
- Roundtrip mismatches: `0`

## Failed Samples

- None

## Suggested Fix Directions

- Inspect any roundtrip mismatch where normalized extracted text diverges from the paragraph segment.
- Review debug spans for over-skipped note links or missed ruby base text.
- Compare paragraph and sentence outputs when inline breaks appear in poetry-like XHTML.
