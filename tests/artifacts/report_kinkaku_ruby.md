# EPUB Extraction Audit

- Book: `kinkaku.epub`
- Seed: `20260315`
- Sample count: `4`
- Test type: `ruby`
- Granularity: `sentence`
- Debug metadata: `on`

## Samples

### Sample 1

- Chapter / Paragraph: `14` / `20`
- Document: `xhtml/0013.xhtml`
- XPath: `/*/*[2]/*/*[29]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">　老人は何か考え事をするとき、<ruby>顎<rt>あご</rt></ruby>をうごかして、はまりのわるい総入歯をかち合わせて鳴らしていることがある。毎日同じ案内の口上を述べているが、日ましに聴きとりにくくなるようなのは入歯のせいである。が、人にすすめられても、直そうとするでもない。畑を見つめて、何か<ruby>呟<rt>つぶや</rt></ruby>いている。呟いては、又歯を鳴らし、鳴らすのを止めては又呟く。多分警報器の修繕が<ruby>捗<rt>はかど</rt></ruby>らないのをこぼしているのである。</p>
```

#### Extracted Text

老人は何か考え事をするとき、顎をうごかして、はまりのわるい総入歯をかち合わせて鳴らしていることがある。毎日同じ案内の口上を述べているが、日ましに聴きとりにくくなるようなのは入歯のせいである。が、人にすすめられても、直そうとするでもない。畑を見つめて、何か呟いている。呟いては、又歯を鳴らし、鳴らすのを止めては又呟く。多分警報器の修繕が捗らないのをこぼしているのである。

#### Sentence Segments

- `0`: 老人は何か考え事をするとき、顎をうごかして、はまりのわるい総入歯をかち合わせて鳴らしていることがある。
- `1`: 毎日同じ案内の口上を述べているが、日ましに聴きとりにくくなるようなのは入歯のせいである。
- `2`: が、人にすすめられても、直そうとするでもない。
- `3`: 畑を見つめて、何か呟いている。
- `4`: 呟いては、又歯を鳴らし、鳴らすのを止めては又呟く。
- `5`: 多分警報器の修繕が捗らないのをこぼしているのである。

#### CFI Roundtrip

老人は何か考え事をするとき、顎をうごかして、はまりのわるい総入歯をかち合わせて鳴らしていることがある。毎日同じ案内の口上を述べているが、日ましに聴きとりにくくなるようなのは入歯のせいである。が、人にすすめられても、直そうとするでもない。畑を見つめて、何か呟いている。呟いては、又歯を鳴らし、鳴らすのを止めては又呟く。多分警報器の修繕が捗らないのをこぼしているのである。

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[29]` 老人は何か考え事をするとき、
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[29]/*[1]` 顎
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[29]` をうごかして、はまりのわるい総入歯をかち合わせて鳴らしていることがある。毎日同じ案内の口上を述べているが、日ましに聴きとりにくくなるようなのは入歯のせいである。
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[29]/*[2]` 呟
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[29]` いている。呟いては、又歯を鳴らし、鳴らすのを止めては又呟く。多分警報器の修繕が
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[29]/*[3]` 捗
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[29]` らないのをこぼしているのである。

#### Reviewer Notes

- Pending external review.

### Sample 2

- Chapter / Paragraph: `13` / `40`
- Document: `xhtml/0012.xhtml`
- XPath: `/*/*[2]/*/*[49]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">　私には有為子は生前から、そういう二重の世界を自由に出入りしていたように思われる。あの悲劇的な事件のときも、彼女はこの世界を拒むかと思うと、次には又受け<ruby>容<rt>い</rt></ruby>れていた。死も有為子にとっては、かりそめの事件であったかもしれない。彼女が金剛院の<ruby>渡殿<rt>わたどの</rt></ruby>に残した血は、朝、窓をあけると同時に飛び<ruby>翔<rt>た</rt></ruby>った<ruby>蝶<rt>ちょう</rt></ruby>が、<ruby>窓枠<rt>まどわく</rt></ruby>に残して行った<ruby>鱗粉<rt>りんぷん</rt></ruby>のようなものにすぎなかったのかもしれない。</p>
```

#### Extracted Text

私には有為子は生前から、そういう二重の世界を自由に出入りしていたように思われる。あの悲劇的な事件のときも、彼女はこの世界を拒むかと思うと、次には又受け容れていた。死も有為子にとっては、かりそめの事件であったかもしれない。彼女が金剛院の渡殿に残した血は、朝、窓をあけると同時に飛び翔った蝶が、窓枠に残して行った鱗粉のようなものにすぎなかったのかもしれない。

#### Sentence Segments

- `0`: 私には有為子は生前から、そういう二重の世界を自由に出入りしていたように思われる。
- `1`: あの悲劇的な事件のときも、彼女はこの世界を拒むかと思うと、次には又受け容れていた。
- `2`: 死も有為子にとっては、かりそめの事件であったかもしれない。
- `3`: 彼女が金剛院の渡殿に残した血は、朝、窓をあけると同時に飛び翔った蝶が、窓枠に残して行った鱗粉のようなものにすぎなかったのかもしれない。

#### CFI Roundtrip

私には有為子は生前から、そういう二重の世界を自由に出入りしていたように思われる。あの悲劇的な事件のときも、彼女はこの世界を拒むかと思うと、次には又受け容れていた。死も有為子にとっては、かりそめの事件であったかもしれない。彼女が金剛院の渡殿に残した血は、朝、窓をあけると同時に飛び翔った蝶が、窓枠に残して行った鱗粉のようなものにすぎなかったのかもしれない。

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[49]` 私には有為子は生前から、そういう二重の世界を自由に出入りしていたように思われる。あの悲劇的な事件のときも、彼女はこの世界を拒むかと思うと、次には又受け
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[49]/*[1]` 容
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[49]` れていた。死も有為子にとっては、かりそめの事件であったかもしれない。彼女が金剛院の
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[49]/*[2]` 渡殿
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[49]` に残した血は、朝、窓をあけると同時に飛び
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[49]/*[3]` 翔
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[49]` った
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[49]/*[4]` 蝶
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[49]` が、
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[49]/*[5]` 窓枠
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[49]` に残して行った
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[49]/*[6]` 鱗粉
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[49]` のようなものにすぎなかったのかもしれない。

#### Reviewer Notes

- Pending external review.

### Sample 3

- Chapter / Paragraph: `12` / `70`
- Document: `xhtml/0011.xhtml`
- XPath: `/*/*[2]/*/*[82]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">　<ruby>洛中洛外<rt>らくちゅうらくがい</rt></ruby>の古い寺々が、維新以後めったに焼かれなくなったのは、こういう教養の<ruby>賜物<rt>たまもの</rt></ruby>だった。たまさかの失火はあっても、火は寸断され、細分され、管理されるにいたった。それまでは決してそうではなかった。知恩院<span class="super">＊一五〇</span>は<ruby>永享<rt>えいきょう</rt></ruby>三年に炎上し、その後何度となく火を<ruby>蒙<rt>こうむ</rt></ruby>った。南禅寺は<ruby>明徳<rt>めいとく</rt></ruby>四年に本寺の仏殿、法堂、金剛殿、大雲庵などが炎上した。<ruby>延暦寺<rt>えんりゃくじ</rt></ruby><span class="super">＊一五一</span>は<ruby>元亀<rt>げんき</rt></ruby>二年に<ruby>灰燼<rt>かいじん</rt></ruby>に帰した。<ruby>建仁寺<rt>けんにんじ</rt></ruby><span class="super">＊一五二</span>は天文二十一年に兵火に<ruby>罹<rt>かか</rt></ruby>った。三十三間堂<span class="super">＊一五三</span>は建長元年に焼亡した。本能寺<span class="super">＊一五四</span>は天正十年の兵火に焼かれた。……</p>
```

#### Extracted Text

洛中洛外の古い寺々が、維新以後めったに焼かれなくなったのは、こういう教養の賜物だった。たまさかの失火はあっても、火は寸断され、細分され、管理されるにいたった。それまでは決してそうではなかった。知恩院は永享三年に炎上し、その後何度となく火を蒙った。南禅寺は明徳四年に本寺の仏殿、法堂、金剛殿、大雲庵などが炎上した。延暦寺は元亀二年に灰燼に帰した。建仁寺は天文二十一年に兵火に罹った。三十三間堂は建長元年に焼亡した。本能寺は天正十年の兵火に焼かれた。……

#### Sentence Segments

- `0`: 洛中洛外の古い寺々が、維新以後めったに焼かれなくなったのは、こういう教養の賜物だった。
- `1`: たまさかの失火はあっても、火は寸断され、細分され、管理されるにいたった。
- `2`: それまでは決してそうではなかった。
- `3`: 知恩院は永享三年に炎上し、その後何度となく火を蒙った。
- `4`: 南禅寺は明徳四年に本寺の仏殿、法堂、金剛殿、大雲庵などが炎上した。
- `5`: 延暦寺は元亀二年に灰燼に帰した。
- `6`: 建仁寺は天文二十一年に兵火に罹った。
- `7`: 三十三間堂は建長元年に焼亡した。
- `8`: 本能寺は天正十年の兵火に焼かれた。……

#### CFI Roundtrip

洛中洛外の古い寺々が、維新以後めったに焼かれなくなったのは、こういう教養の賜物だった。たまさかの失火はあっても、火は寸断され、細分され、管理されるにいたった。それまでは決してそうではなかった。知恩院は永享三年に炎上し、その後何度となく火を蒙った。南禅寺は明徳四年に本寺の仏殿、法堂、金剛殿、大雲庵などが炎上した。延暦寺は元亀二年に灰燼に帰した。建仁寺は天文二十一年に兵火に罹った。三十三間堂は建長元年に焼亡した。本能寺は天正十年の兵火に焼かれた。……

#### Debug Spans

- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[82]/*[1]` 洛中洛外
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[82]` の古い寺々が、維新以後めったに焼かれなくなったのは、こういう教養の
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[82]/*[2]` 賜物
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[82]` だった。たまさかの失火はあっても、火は寸断され、細分され、管理されるにいたった。それまでは決してそうではなかった。知恩院
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[82]` は
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[82]/*[4]` 永享
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[82]` 三年に炎上し、その後何度となく火を
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[82]/*[5]` 蒙
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[82]` った。南禅寺は
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[82]/*[6]` 明徳
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[82]` 四年に本寺の仏殿、法堂、金剛殿、大雲庵などが炎上した。
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[82]/*[7]` 延暦寺
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[82]` は
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[82]/*[9]` 元亀
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[82]` 二年に
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[82]/*[10]` 灰燼
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[82]` に帰した。
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[82]/*[11]` 建仁寺
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[82]` は天文二十一年に兵火に
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[82]/*[13]` 罹
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[82]` った。三十三間堂
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[82]` は建長元年に焼亡した。本能寺
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[82]` は天正十年の兵火に焼かれた。……

#### Reviewer Notes

- Pending external review.

### Sample 4

- Chapter / Paragraph: `11` / `183`
- Document: `xhtml/0010.xhtml`
- XPath: `/*/*[2]/*/*[202]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">　と言い、それがみんなの結論になった。<ruby>拭<rt>ふ</rt></ruby>かれぬき<ruby>磨<rt>みが</rt></ruby>かれぬいた老人の手は、煤煙のあともなく、<ruby>根附<rt>ねつけ</rt></ruby><span class="super">＊一四一</span>のような光沢を放っていた。実際その出来合の手は、手というよりもむしろ手袋と云ったほうがよかった。</p>
```

#### Extracted Text

と言い、それがみんなの結論になった。拭かれぬき磨かれぬいた老人の手は、煤煙のあともなく、根附のような光沢を放っていた。実際その出来合の手は、手というよりもむしろ手袋と云ったほうがよかった。

#### Sentence Segments

- `0`: と言い、それがみんなの結論になった。
- `1`: 拭かれぬき磨かれぬいた老人の手は、煤煙のあともなく、根附のような光沢を放っていた。
- `2`: 実際その出来合の手は、手というよりもむしろ手袋と云ったほうがよかった。

#### CFI Roundtrip

と言い、それがみんなの結論になった。拭かれぬき磨かれぬいた老人の手は、煤煙のあともなく、根附のような光沢を放っていた。実際その出来合の手は、手というよりもむしろ手袋と云ったほうがよかった。

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[202]` と言い、それがみんなの結論になった。
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[202]/*[1]` 拭
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[202]` かれぬき
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[202]/*[2]` 磨
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[202]` かれぬいた老人の手は、煤煙のあともなく、
- `ruby` `KEEP_CHILDREN_ONLY` `ruby-base-text` `/*/*[2]/*/*[202]/*[3]` 根附
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[202]` のような光沢を放っていた。実際その出来合の手は、手というよりもむしろ手袋と云ったほうがよかった。

#### Reviewer Notes

- Pending external review.

## Summary

- Total samples: `4`
- Ruby samples: `4`
- Footnote-ish samples: `2`
- Roundtrip mismatches: `0`

## Failed Samples

- None

## Suggested Fix Directions

- Inspect any roundtrip mismatch where normalized extracted text diverges from the paragraph segment.
- Review debug spans for over-skipped note links or missed ruby base text.
- Compare paragraph and sentence outputs when inline breaks appear in poetry-like XHTML.
