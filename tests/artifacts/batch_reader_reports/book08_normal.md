# EPUB Extraction Audit

- Book: `kinkaku.epub`
- Seed: `20261080`
- Sample count: `5`
- Test type: `normal`
- Granularity: `sentence`
- Debug metadata: `on`

## Samples

### Sample 1

- Chapter / Paragraph: `12` / `89`
- Document: `xhtml/0011.xhtml`
- XPath: `/*/*[2]/*/*[111]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">　と新入りの徒弟が言った。私は辛うじて立上った。</p>
```

#### Extracted Text

と新入りの徒弟が言った。私は辛うじて立上った。

#### Sentence Segments

- `0`: と新入りの徒弟が言った。
- `1`: 私は辛うじて立上った。

#### CFI Roundtrip

と新入りの徒弟が言った。私は辛うじて立上った。

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[111]` と新入りの徒弟が言った。私は辛うじて立上った。

#### Reviewer Notes

- Pending external review.

### Sample 2

- Chapter / Paragraph: `14` / `44`
- Document: `xhtml/0013.xhtml`
- XPath: `/*/*[2]/*/*[57]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">　老師が帰った。午後九時である。常のように四人の警備員が巡回に出た。何の異状もなかった。</p>
```

#### Extracted Text

老師が帰った。午後九時である。常のように四人の警備員が巡回に出た。何の異状もなかった。

#### Sentence Segments

- `0`: 老師が帰った。
- `1`: 午後九時である。
- `2`: 常のように四人の警備員が巡回に出た。
- `3`: 何の異状もなかった。

#### CFI Roundtrip

老師が帰った。午後九時である。常のように四人の警備員が巡回に出た。何の異状もなかった。

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[57]` 老師が帰った。午後九時である。常のように四人の警備員が巡回に出た。何の異状もなかった。

#### Reviewer Notes

- Pending external review.

### Sample 3

- Chapter / Paragraph: `18` / `42`
- Document: `xhtml/0017.xhtml`
- XPath: `/*/*[2]/*/*[30]/*[1]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">一月、戯曲『葵上』（新潮）　八月、『詩を書く少年』（文学界）</p>
```

#### Extracted Text

一月、戯曲『葵上』（新潮） 八月、『詩を書く少年』（文学界）

#### Sentence Segments

- `0`: 一月、戯曲『葵上』（新潮） 八月、『詩を書く少年』（文学界）

#### CFI Roundtrip

一月、戯曲『葵上』（新潮） 八月、『詩を書く少年』（文学界）

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[30]/*[1]` 一月、戯曲『葵上』（新潮） 八月、『詩を書く少年』（文学界）

#### Reviewer Notes

- Pending external review.

### Sample 4

- Chapter / Paragraph: `7` / `71`
- Document: `xhtml/0006.xhtml`
- XPath: `/*/*[2]/*/*[85]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">　読経のあとで、寺の者はみんな老師の居室に呼ばれ、そこで講話があった。</p>
```

#### Extracted Text

読経のあとで、寺の者はみんな老師の居室に呼ばれ、そこで講話があった。

#### Sentence Segments

- `0`: 読経のあとで、寺の者はみんな老師の居室に呼ばれ、そこで講話があった。

#### CFI Roundtrip

読経のあとで、寺の者はみんな老師の居室に呼ばれ、そこで講話があった。

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[85]` 読経のあとで、寺の者はみんな老師の居室に呼ばれ、そこで講話があった。

#### Reviewer Notes

- Pending external review.

### Sample 5

- Chapter / Paragraph: `17` / `35`
- Document: `xhtml/0016.xhtml`
- XPath: `/*/*[2]/*/*[40]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">　作者の文章は、この小説でひとつの完成に達していますが、変質者の少年にこのような立派な文章が書ける筈がないという疑問は読者の心に浮んできません。</p>
```

#### Extracted Text

作者の文章は、この小説でひとつの完成に達していますが、変質者の少年にこのような立派な文章が書ける筈がないという疑問は読者の心に浮んできません。

#### Sentence Segments

- `0`: 作者の文章は、この小説でひとつの完成に達していますが、変質者の少年にこのような立派な文章が書ける筈がないという疑問は読者の心に浮んできません。

#### CFI Roundtrip

作者の文章は、この小説でひとつの完成に達していますが、変質者の少年にこのような立派な文章が書ける筈がないという疑問は読者の心に浮んできません。

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[40]` 作者の文章は、この小説でひとつの完成に達していますが、変質者の少年にこのような立派な文章が書ける筈がないという疑問は読者の心に浮んできません。

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
