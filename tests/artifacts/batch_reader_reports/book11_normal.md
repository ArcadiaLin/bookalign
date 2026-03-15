# EPUB Extraction Audit

- Book: `羅生門・鼻・芋粥 (角川文庫) (芥川 龍之介) (z-library.sk, 1lib.sk, z-lib.sk).epub`
- Seed: `20261110`
- Sample count: `5`
- Test type: `normal`
- Granularity: `sentence`
- Debug metadata: `on`

## Samples

### Sample 1

- Chapter / Paragraph: `20` / `0`
- Document: `text/part0014_split_005.html`
- XPath: `/*/*[2]/*/*/*/*[1]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<h2 xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="min-110per_" id="calibre_pb_5">　　　　五</h2>
```

#### Extracted Text

五

#### Sentence Segments

- `0`: 五

#### CFI Roundtrip

五

#### Debug Spans

- `h2` `BLOCK_BREAK` `heading-2` `/*/*[2]/*/*/*/*[1]` 五

#### Reviewer Notes

- Pending external review.

### Sample 2

- Chapter / Paragraph: `13` / `7`
- Document: `text/part0012.html`
- XPath: `/*/*[2]/*/*/*[1]/*[10]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre">　──君、梅幸というのはなんだね。<br class="calibre1"></br></p>
```

#### Extracted Text

──君、梅幸というのはなんだね。

#### Sentence Segments

- `0`: ──君、梅幸というのはなんだね。

#### CFI Roundtrip

──君、梅幸というのはなんだね。

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*/*[1]/*[10]` ──君、梅幸というのはなんだね。
- `br` `INLINE_BREAK` `inline-break` `/*/*[2]/*/*/*[1]/*[10]/*` <break>

#### Reviewer Notes

- Pending external review.

### Sample 3

- Chapter / Paragraph: `35` / `0`
- Document: `text/part0021_split_005.html`
- XPath: `/*/*[2]/*/*/*/*[1]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<h2 xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="min-110per_" id="calibre_pb_5">　　　　鼻</h2>
```

#### Extracted Text

鼻

#### Sentence Segments

- `0`: 鼻

#### CFI Roundtrip

鼻

#### Debug Spans

- `h2` `BLOCK_BREAK` `heading-2` `/*/*[2]/*/*/*/*[1]` 鼻

#### Reviewer Notes

- Pending external review.

### Sample 4

- Chapter / Paragraph: `51` / `5`
- Document: `text/part0024.html`
- XPath: `/*/*[2]/*/*/*[3]/*[5]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre"><span class="min-085per">〒102-8078　東京都千代田区富士見2-13-3</span><br class="calibre1"></br></p>
```

#### Extracted Text

〒102-8078 東京都千代田区富士見2-13-3

#### Sentence Segments

- `0`: 〒102-8078 東京都千代田区富士見2-13-3

#### CFI Roundtrip

〒102-8078 東京都千代田区富士見2-13-3

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*/*[3]/*[5]/*[1]` 〒102-8078 東京都千代田区富士見2-13-3
- `br` `INLINE_BREAK` `inline-break` `/*/*[2]/*/*/*[3]/*[5]/*[2]` <break>

#### Reviewer Notes

- Pending external review.

### Sample 5

- Chapter / Paragraph: `2` / `5`
- Document: `text/part0001.html`
- XPath: `/*/*[2]/*/*/*/*[8]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre">本文中に「＊」が付されている箇所には注釈があります。その箇所を選択すると、該当する注釈が表示されます。</p>
```

#### Extracted Text

本文中に「＊」が付されている箇所には注釈があります。その箇所を選択すると、該当する注釈が表示されます。

#### Sentence Segments

- `0`: 本文中に「＊」が付されている箇所には注釈があります。
- `1`: その箇所を選択すると、該当する注釈が表示されます。

#### CFI Roundtrip

本文中に「＊」が付されている箇所には注釈があります。その箇所を選択すると、該当する注釈が表示されます。

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*/*/*[8]` 本文中に「＊」が付されている箇所には注釈があります。その箇所を選択すると、該当する注釈が表示されます。

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
