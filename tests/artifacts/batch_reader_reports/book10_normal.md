# EPUB Extraction Audit

- Book: `人間失格 (太宰 治) (z-library.sk, 1lib.sk, z-lib.sk).epub`
- Seed: `20261100`
- Sample count: `5`
- Test type: `normal`
- Granularity: `sentence`
- Debug metadata: `on`

## Samples

### Sample 1

- Chapter / Paragraph: `5` / `58`
- Document: `text/part0004.html`
- XPath: `/*/*[2]/*[3]/*[60]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre">　いつか竹一が、自分の二階へ遊びに来た時、ご持参の、一枚の原色版の口絵を得意そうに自分に見せて、そう説明しました。<br class="calibre1"></br></p>
```

#### Extracted Text

いつか竹一が、自分の二階へ遊びに来た時、ご持参の、一枚の原色版の口絵を得意そうに自分に見せて、そう説明しました。

#### Sentence Segments

- `0`: いつか竹一が、自分の二階へ遊びに来た時、ご持参の、一枚の原色版の口絵を得意そうに自分に見せて、そう説明しました。

#### CFI Roundtrip

いつか竹一が、自分の二階へ遊びに来た時、ご持参の、一枚の原色版の口絵を得意そうに自分に見せて、そう説明しました。

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[3]/*[60]` いつか竹一が、自分の二階へ遊びに来た時、ご持参の、一枚の原色版の口絵を得意そうに自分に見せて、そう説明しました。
- `br` `INLINE_BREAK` `inline-break` `/*/*[2]/*[3]/*[60]/*` <break>

#### Reviewer Notes

- Pending external review.

### Sample 2

- Chapter / Paragraph: `6` / `134`
- Document: `text/part0005.html`
- XPath: `/*/*[2]/*[5]/*[134]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre">　世間とは、いったい、何の事でしょう。人間の複数でしょうか。どこに、その世間というものの実体があるのでしょう。けれども、何しろ、強く、きびしく、こわいもの、とばかり思ってこれまで生きて来たのですが、しかし、堀木にそう言われて、ふと、<br class="calibre1"></br></p>
```

#### Extracted Text

世間とは、いったい、何の事でしょう。人間の複数でしょうか。どこに、その世間というものの実体があるのでしょう。けれども、何しろ、強く、きびしく、こわいもの、とばかり思ってこれまで生きて来たのですが、しかし、堀木にそう言われて、ふと、

#### Sentence Segments

- `0`: 世間とは、いったい、何の事でしょう。
- `1`: 人間の複数でしょうか。
- `2`: どこに、その世間というものの実体があるのでしょう。けれども、何しろ、強く、きびしく、こわいもの、とばかり思ってこれまで生きて来たのですが、しかし、堀木にそう言われて、ふと、

#### CFI Roundtrip

世間とは、いったい、何の事でしょう。人間の複数でしょうか。どこに、その世間というものの実体があるのでしょう。けれども、何しろ、強く、きびしく、こわいもの、とばかり思ってこれまで生きて来たのですが、しかし、堀木にそう言われて、ふと、

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[5]/*[134]` 世間とは、いったい、何の事でしょう。人間の複数でしょうか。どこに、その世間というものの実体があるのでしょう。けれども、何しろ、強く、きびしく、こわいもの、とばか
- `br` `INLINE_BREAK` `inline-break` `/*/*[2]/*[5]/*[134]/*` <break>

#### Reviewer Notes

- Pending external review.

### Sample 3

- Chapter / Paragraph: `6` / `120`
- Document: `text/part0005.html`
- XPath: `/*/*[2]/*[5]/*[120]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre">　自分は、何気無さそうに話頭を転じました。<br class="calibre1"></br></p>
```

#### Extracted Text

自分は、何気無さそうに話頭を転じました。

#### Sentence Segments

- `0`: 自分は、何気無さそうに話頭を転じました。

#### CFI Roundtrip

自分は、何気無さそうに話頭を転じました。

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[5]/*[120]` 自分は、何気無さそうに話頭を転じました。
- `br` `INLINE_BREAK` `inline-break` `/*/*[2]/*[5]/*[120]/*` <break>

#### Reviewer Notes

- Pending external review.

### Sample 4

- Chapter / Paragraph: `6` / `205`
- Document: `text/part0005.html`
- XPath: `/*/*[2]/*[8]/*[21]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre">正義は人生の指針たりとや？<br class="calibre1"></br></p>
```

#### Extracted Text

正義は人生の指針たりとや？

#### Sentence Segments

- `0`: 正義は人生の指針たりとや？

#### CFI Roundtrip

正義は人生の指針たりとや？

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[8]/*[21]` 正義は人生の指針たりとや？
- `br` `INLINE_BREAK` `inline-break` `/*/*[2]/*[8]/*[21]/*` <break>

#### Reviewer Notes

- Pending external review.

### Sample 5

- Chapter / Paragraph: `3` / `3`
- Document: `text/part0002.html`
- XPath: `/*/*[2]/*[2]/*[5]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre">「可愛い坊ちゃんですね」<br class="calibre1"></br></p>
```

#### Extracted Text

「可愛い坊ちゃんですね」

#### Sentence Segments

- `0`: 「可愛い坊ちゃんですね」

#### CFI Roundtrip

「可愛い坊ちゃんですね」

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[2]/*[5]` 「可愛い坊ちゃんですね」
- `br` `INLINE_BREAK` `inline-break` `/*/*[2]/*[2]/*[5]/*` <break>

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
