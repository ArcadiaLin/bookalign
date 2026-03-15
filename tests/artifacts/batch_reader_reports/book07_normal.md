# EPUB Extraction Audit

- Book: `her.epub`
- Seed: `20261070`
- Sample count: `5`
- Test type: `normal`
- Granularity: `sentence`
- Debug metadata: `on`

## Samples

### Sample 1

- Chapter / Paragraph: `2` / `628`
- Document: `EPUB/text/ch001.xhtml`
- XPath: `/*/*[2]/*/*[11]/*[21]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre2">“你一个粗手粗脚的丑女孩，勇士会看上你？”</p>
```

#### Extracted Text

“你一个粗手粗脚的丑女孩，勇士会看上你？”

#### Sentence Segments

- `0`: “你一个粗手粗脚的丑女孩，勇士会看上你？”

#### CFI Roundtrip

“你一个粗手粗脚的丑女孩，勇士会看上你？”

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[11]/*[21]` “你一个粗手粗脚的丑女孩，勇士会看上你？”

#### Reviewer Notes

- Pending external review.

### Sample 2

- Chapter / Paragraph: `2` / `690`
- Document: `EPUB/text/ch001.xhtml`
- XPath: `/*/*[2]/*/*[12]/*[7]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre2">卓珊的父母对这场教育投资充满了期待，他们希望女儿能在学院里蜕变，靠优雅的气质成为富商的未婚妻或者子爵的夫人。</p>
```

#### Extracted Text

卓珊的父母对这场教育投资充满了期待，他们希望女儿能在学院里蜕变，靠优雅的气质成为富商的未婚妻或者子爵的夫人。

#### Sentence Segments

- `0`: 卓珊的父母对这场教育投资充满了期待，他们希望女儿能在学院里蜕变，靠优雅的气质成为富商的未婚妻或者子爵的夫人。

#### CFI Roundtrip

卓珊的父母对这场教育投资充满了期待，他们希望女儿能在学院里蜕变，靠优雅的气质成为富商的未婚妻或者子爵的夫人。

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[12]/*[7]` 卓珊的父母对这场教育投资充满了期待，他们希望女儿能在学院里蜕变，靠优雅的气质成为富商的未婚妻或者子爵的夫人。

#### Reviewer Notes

- Pending external review.

### Sample 3

- Chapter / Paragraph: `2` / `208`
- Document: `EPUB/text/ch001.xhtml`
- XPath: `/*/*[2]/*/*[6]/*[47]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre2">阿瑾回到了青青山。</p>
```

#### Extracted Text

阿瑾回到了青青山。

#### Sentence Segments

- `0`: 阿瑾回到了青青山。

#### CFI Roundtrip

阿瑾回到了青青山。

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[6]/*[47]` 阿瑾回到了青青山。

#### Reviewer Notes

- Pending external review.

### Sample 4

- Chapter / Paragraph: `2` / `81`
- Document: `EPUB/text/ch001.xhtml`
- XPath: `/*/*[2]/*/*[5]/*[40]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre2">其他凡人、妖怪都不行，甚至连一只苍蝇都飞不进去。</p>
```

#### Extracted Text

其他凡人、妖怪都不行，甚至连一只苍蝇都飞不进去。

#### Sentence Segments

- `0`: 其他凡人、妖怪都不行，甚至连一只苍蝇都飞不进去。

#### CFI Roundtrip

其他凡人、妖怪都不行，甚至连一只苍蝇都飞不进去。

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[5]/*[40]` 其他凡人、妖怪都不行，甚至连一只苍蝇都飞不进去。

#### Reviewer Notes

- Pending external review.

### Sample 5

- Chapter / Paragraph: `2` / `588`
- Document: `EPUB/text/ch001.xhtml`
- XPath: `/*/*[2]/*/*[10]/*[82]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre2">黑色的茜拉迅速变回黑色的流光，在地上扭曲出各种模样，黑色的驯鹿、黑色的侍女……</p>
```

#### Extracted Text

黑色的茜拉迅速变回黑色的流光，在地上扭曲出各种模样，黑色的驯鹿、黑色的侍女……

#### Sentence Segments

- `0`: 黑色的茜拉迅速变回黑色的流光，在地上扭曲出各种模样，黑色的驯鹿、黑色的侍女……

#### CFI Roundtrip

黑色的茜拉迅速变回黑色的流光，在地上扭曲出各种模样，黑色的驯鹿、黑色的侍女……

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[10]/*[82]` 黑色的茜拉迅速变回黑色的流光，在地上扭曲出各种模样，黑色的驯鹿、黑色的侍女……

#### Reviewer Notes

- Pending external review.

## Summary

- Total samples: `5`
- Ruby samples: `0`
- Footnote-ish samples: `0`
- Roundtrip mismatches: `0`

## Failed Samples

- None

## Suggested Fix Directions

- Inspect any roundtrip mismatch where normalized extracted text diverges from the paragraph segment.
- Review debug spans for over-skipped note links or missed ruby base text.
- Compare paragraph and sentence outputs when inline breaks appear in poetry-like XHTML.
