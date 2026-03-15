# EPUB Extraction Audit

- Book: `kinkaku.epub`
- Seed: `20260318`
- Sample count: `4`
- Test type: `footnote`
- Granularity: `paragraph`
- Debug metadata: `on`

## Samples

### Sample 1

- Chapter / Paragraph: `5` / `76`
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

- Chapter / Paragraph: `13` / `115`
- Document: `xhtml/0012.xhtml`
- XPath: `/*/*[2]/*/*[131]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">　拱北楼は開け放たれていた。常のように、<ruby>床<rt>とこ</rt></ruby>には<ruby>円山応挙<rt>まるやまおうきょ</rt></ruby><span class="super">＊一六七</span>の軸が見える。<ruby>白檀<rt>びゃくだん</rt></ruby>を彫ったのが歳月と共に黒くなった<ruby>天竺<rt>てんじく</rt></ruby>渡りの繊巧な細工の<ruby>厨子<rt>ずし</rt></ruby>が床の間に飾ってある。左方に<ruby>利休<rt>りきゅう</rt></ruby>好みの<ruby>桑棚<rt>くわだな</rt></ruby>も見える。<ruby>襖絵<rt>ふすまえ</rt></ruby>も見える。老師の姿だけが見えないので、思わず首を生垣の上へもたげて見まわした。</p>
```

#### Extracted Text

拱北楼は開け放たれていた。常のように、床には円山応挙の軸が見える。白檀を彫ったのが歳月と共に黒くなった天竺渡りの繊巧な細工の厨子が床の間に飾ってある。左方に利休好みの桑棚も見える。襖絵も見える。老師の姿だけが見えないので、思わず首を生垣の上へもたげて見まわした。

#### CFI Roundtrip

拱北楼は開け放たれていた。常のように、床には円山応挙の軸が見える。白檀を彫ったのが歳月と共に黒くなった天竺渡りの繊巧な細工の厨子が床の間に飾ってある。左方に利休好みの桑棚も見える。襖絵も見える。老師の姿だけが見えないので、思わず首を生垣の上へもたげて見まわした。

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[131]` 拱北楼は開け放たれていた。常のように、
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[131]/*[1]` 床
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[131]` には
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[131]/*[2]` 円山応挙
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[131]` の軸が見える。
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[131]/*[4]` 白檀
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[131]` を彫ったのが歳月と共に黒くなった
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[131]/*[5]` 天竺
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[131]` 渡りの繊巧な細工の
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[131]/*[6]` 厨子
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[131]` が床の間に飾ってある。左方に
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[131]/*[7]` 利休
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[131]` 好みの
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[131]/*[8]` 桑棚
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[131]` も見える。
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[131]/*[9]` 襖絵
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[131]` も見える。老師の姿だけが見えないので、思わず首を生垣の上へもたげて見まわした。

#### Reviewer Notes

- Pending external review.

### Sample 3

- Chapter / Paragraph: `6` / `96`
- Document: `xhtml/0005.xhtml`
- XPath: `/*/*[2]/*/*[110]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">　金閣をめぐる赤松の山々は<ruby>蝉<rt>せみ</rt></ruby>の声に包まれていた。無数の見えない僧が<ruby>消災呪<rt>しょうさいしゅ</rt></ruby><span class="super">＊六〇</span>を<ruby>称<rt>とな</rt></ruby>えているかのように。「<ruby>佉佉<rt>ぎゃーぎゃー</rt></ruby>。<ruby>佉呬佉呬<rt>ぎゃーきーぎゃーきー</rt></ruby>。<ruby>吽吽<rt>うんぬん</rt></ruby>。<ruby>入嚩囉<rt>しふらー</rt>入嚩囉<rt>しふらー</rt></ruby>。<ruby>𥁊囉入嚩囉<rt>はらしふらー</rt>𥁊囉入嚩囉<rt>はらしふらー</rt></ruby>。」</p>
```

#### Extracted Text

金閣をめぐる赤松の山々は蝉の声に包まれていた。無数の見えない僧が消災呪を称えているかのように。「佉佉。佉呬佉呬。吽吽。入嚩囉入嚩囉。𥁊囉入嚩囉𥁊囉入嚩囉。」

#### CFI Roundtrip

金閣をめぐる赤松の山々は蝉の声に包まれていた。無数の見えない僧が消災呪を称えているかのように。「佉佉。佉呬佉呬。吽吽。入嚩囉入嚩囉。𥁊囉入嚩囉𥁊囉入嚩囉。」

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[110]` 金閣をめぐる赤松の山々は
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[110]/*[1]` 蝉
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[110]` の声に包まれていた。無数の見えない僧が
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[110]/*[2]` 消災呪
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[110]` を
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[110]/*[4]` 称
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[110]` えているかのように。「
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[110]/*[5]` 佉佉
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[110]` 。
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[110]/*[6]` 佉呬佉呬
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[110]` 。
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[110]/*[7]` 吽吽
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[110]` 。
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[110]/*[8]` 入嚩囉
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[110]/*[8]` 入嚩囉
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[110]` 。
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[110]/*[9]` 𥁊囉入嚩囉
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[110]/*[9]` 𥁊囉入嚩囉
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[110]` 。」

#### Reviewer Notes

- Pending external review.

### Sample 4

- Chapter / Paragraph: `14` / `74`
- Document: `xhtml/0013.xhtml`
- XPath: `/*/*[2]/*/*[88]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">　が、私の美の思い出が強まるにつれ、この暗黒は<ruby>恣<rt>ほしいま</rt></ruby>まに幻を描くことのできる下地になった。この暗いうずくまった形態のうちに、私が美と考えたものの<ruby>全貌<rt>ぜんぼう</rt></ruby>がひそんでいた。思い出の力で、美の細部はひとつひとつ闇の中からきらめき出し、きらめきは<ruby>伝播<rt>でんぱ</rt></ruby>して、ついには昼とも夜ともつかぬふしぎな時の光りの<ruby>下<rt>もと</rt></ruby>に、金閣は徐々にはっきりと目に見えるものになった。これほど完全に<ruby>細緻<rt>さいち</rt></ruby>な姿で、金閣がその<ruby>隈々<rt>くまぐま</rt></ruby>まできらめいて、私の眼前に立ち現われたことはない。私は盲人の視力をわがものにしたかのようだ。自ら発する光りで透明になった金閣は、外側からも、潮音洞の天人奏楽の天井画や、究竟頂の壁の古い<ruby>金箔<rt>きんぱく</rt></ruby>の<ruby>名残<rt>なごり</rt></ruby>をありありと見せた。金閣の繊巧な外部は、その内部とまじわった。私の目は、その構造や主題の<ruby>明瞭<rt>めいりょう</rt></ruby>な輪郭を、主題を具体化してゆく細部の丹念な繰り返しや装飾を、対比や対称の効果を、一望の下に収めることができた。法水院と潮音洞の同じ広さの二層は、微妙な相違を示しながらも、一つの深い<ruby>軒庇<rt>のきびさし</rt></ruby>のかげに守られて、いわば一双のよく似た夢、一対のよく似た快楽の記念のように重なっていた。その一つだけでは忘却に紛れそうになるものを、上下からやさしくたしかめ合い、そのために夢は現実になり、快楽は建築になったのだった。しかしそれも、第三層の究竟頂の俄かにすぼまった形が<ruby>戴<rt>いただ</rt></ruby>かれていることで、一度確かめられた現実は崩壊して、あの暗いきらびやかな時代の、<ruby>高邁<rt>こうまい</rt></ruby>な哲学に統括され、それに服するにいたるのである。そして<ruby>柿葺<rt>こけらぶき</rt></ruby><span class="super">＊一七五</span>の屋根の頂き高く、金銅の<ruby>鳳凰<rt>ほうおう</rt></ruby>が<ruby>無明<rt>むみょう</rt></ruby><span class="super">＊一七六</span>の長夜に接している。</p>
```

#### Extracted Text

が、私の美の思い出が強まるにつれ、この暗黒は恣まに幻を描くことのできる下地になった。この暗いうずくまった形態のうちに、私が美と考えたものの全貌がひそんでいた。思い出の力で、美の細部はひとつひとつ闇の中からきらめき出し、きらめきは伝播して、ついには昼とも夜ともつかぬふしぎな時の光りの下に、金閣は徐々にはっきりと目に見えるものになった。これほど完全に細緻な姿で、金閣がその隈々まできらめいて、私の眼前に立ち現われたことはない。私は盲人の視力をわがものにしたかのようだ。自ら発する光りで透明になった金閣は、外側からも、潮音洞の天人奏楽の天井画や、究竟頂の壁の古い金箔の名残をありありと見せた。金閣の繊巧な外部は、その内部とまじわった。私の目は、その構造や主題の明瞭な輪郭を、主題を具体化してゆく細部の丹念な繰り返しや装飾を、対比や対称の効果を、一望の下に収めることができた。法水院と潮音洞の同じ広さの二層は、微妙な相違を示しながらも、一つの深い軒庇のかげに守られて、いわば一双のよく似た夢、一対のよく似た快楽の記念のように重なっていた。その一つだけでは忘却に紛れそうになるものを、上下からやさしくたしかめ合い、そのために夢は現実になり、快楽は建築になったのだった。しかしそれも、第三層の究竟頂の俄かにすぼまった形が戴かれていることで、一度確かめられた現実は崩壊して、あの暗いきらびやかな時代の、高邁な哲学に統括され、それに服するにいたるのである。そして柿葺の屋根の頂き高く、金銅の鳳凰が無明の長夜に接している。

#### CFI Roundtrip

が、私の美の思い出が強まるにつれ、この暗黒は恣まに幻を描くことのできる下地になった。この暗いうずくまった形態のうちに、私が美と考えたものの全貌がひそんでいた。思い出の力で、美の細部はひとつひとつ闇の中からきらめき出し、きらめきは伝播して、ついには昼とも夜ともつかぬふしぎな時の光りの下に、金閣は徐々にはっきりと目に見えるものになった。これほど完全に細緻な姿で、金閣がその隈々まできらめいて、私の眼前に立ち現われたことはない。私は盲人の視力をわがものにしたかのようだ。自ら発する光りで透明になった金閣は、外側からも、潮音洞の天人奏楽の天井画や、究竟頂の壁の古い金箔の名残をありありと見せた。金閣の繊巧な外部は、その内部とまじわった。私の目は、その構造や主題の明瞭な輪郭を、主題を具体化してゆく細部の丹念な繰り返しや装飾を、対比や対称の効果を、一望の下に収めることができた。法水院と潮音洞の同じ広さの二層は、微妙な相違を示しながらも、一つの深い軒庇のかげに守られて、いわば一双のよく似た夢、一対のよく似た快楽の記念のように重なっていた。その一つだけでは忘却に紛れそうになるものを、上下からやさしくたしかめ合い、そのために夢は現実になり、快楽は建築になったのだった。しかしそれも、第三層の究竟頂の俄かにすぼまった形が戴かれていることで、一度確かめられた現実は崩壊して、あの暗いきらびやかな時代の、高邁な哲学に統括され、それに服するにいたるのである。そして柿葺の屋根の頂き高く、金銅の鳳凰が無明の長夜に接している。

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[88]` が、私の美の思い出が強まるにつれ、この暗黒は
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[88]/*[1]` 恣
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[88]` まに幻を描くことのできる下地になった。この暗いうずくまった形態のうちに、私が美と考えたものの
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[88]/*[2]` 全貌
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[88]` がひそんでいた。思い出の力で、美の細部はひとつひとつ闇の中からきらめき出し、きらめきは
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[88]/*[3]` 伝播
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[88]` して、ついには昼とも夜ともつかぬふしぎな時の光りの
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[88]/*[4]` 下
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[88]` に、金閣は徐々にはっきりと目に見えるものになった。これほど完全に
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[88]/*[5]` 細緻
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[88]` な姿で、金閣がその
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[88]/*[6]` 隈々
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[88]` まできらめいて、私の眼前に立ち現われたことはない。私は盲人の視力をわがものにしたかのようだ。自ら発する光りで透明になった金閣は、外側からも、潮音洞の天人奏楽の天
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[88]/*[7]` 金箔
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[88]` の
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[88]/*[8]` 名残
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[88]` をありありと見せた。金閣の繊巧な外部は、その内部とまじわった。私の目は、その構造や主題の
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[88]/*[9]` 明瞭
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[88]` な輪郭を、主題を具体化してゆく細部の丹念な繰り返しや装飾を、対比や対称の効果を、一望の下に収めることができた。法水院と潮音洞の同じ広さの二層は、微妙な相違を示し
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[88]/*[10]` 軒庇
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[88]` のかげに守られて、いわば一双のよく似た夢、一対のよく似た快楽の記念のように重なっていた。その一つだけでは忘却に紛れそうになるものを、上下からやさしくたしかめ合い
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[88]/*[11]` 戴
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[88]` かれていることで、一度確かめられた現実は崩壊して、あの暗いきらびやかな時代の、
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[88]/*[12]` 高邁
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[88]` な哲学に統括され、それに服するにいたるのである。そして
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[88]/*[13]` 柿葺
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[88]` の屋根の頂き高く、金銅の
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[88]/*[15]` 鳳凰
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[88]` が
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[88]/*[16]` 無明
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[88]` の長夜に接している。

#### Reviewer Notes

- Pending external review.

## Summary

- Total samples: `4`
- Ruby samples: `4`
- Footnote-ish samples: `4`
- Roundtrip mismatches: `0`

## Failed Samples

- None

## Suggested Fix Directions

- Inspect any roundtrip mismatch where normalized extracted text diverges from the paragraph segment.
- Review debug spans for over-skipped note links or missed ruby base text.
- Compare paragraph and sentence outputs when inline breaks appear in poetry-like XHTML.
