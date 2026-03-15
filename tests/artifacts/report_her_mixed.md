# EPUB Extraction Audit

- Book: `her.epub`
- Seed: `20260316`
- Sample count: `4`
- Test type: `mixed`
- Granularity: `sentence`
- Debug metadata: `on`

## Samples

### Sample 1

- Chapter / Paragraph: `2` / `102`
- Document: `EPUB/text/ch001.xhtml`
- XPath: `/*/*[2]/*/*[5]/*[50]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre2">阿志心里涌起一股莫名的情绪，像是愧疚，又像是恼怒。</p>
```

#### Extracted Text

阿志心里涌起一股莫名的情绪，像是愧疚，又像是恼怒。

#### Sentence Segments

- `0`: 阿志心里涌起一股莫名的情绪，像是愧疚，又像是恼怒。

#### CFI Roundtrip

阿志心里涌起一股莫名的情绪，像是愧疚，又像是恼怒。

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[5]/*[50]` 阿志心里涌起一股莫名的情绪，像是愧疚，又像是恼怒。

#### Reviewer Notes

- Pending external review.

### Sample 2

- Chapter / Paragraph: `2` / `152`
- Document: `EPUB/text/ch001.xhtml`
- XPath: `/*/*[2]/*/*[5]/*[101]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre2">“女本柔弱，为母则刚。”</p>
```

#### Extracted Text

“女本柔弱，为母则刚。”

#### Sentence Segments

- `0`: “女本柔弱，为母则刚。”

#### CFI Roundtrip

“女本柔弱，为母则刚。”

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[5]/*[101]` “女本柔弱，为母则刚。”

#### Reviewer Notes

- Pending external review.

### Sample 3

- Chapter / Paragraph: `2` / `772`
- Document: `EPUB/text/ch001.xhtml`
- XPath: `/*/*[2]/*/*[12]/*[28]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre2">她出现了幻听。</p>
```

#### Extracted Text

她出现了幻听。

#### Sentence Segments

- `0`: 她出现了幻听。

#### CFI Roundtrip

她出现了幻听。

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[12]/*[28]` 她出现了幻听。

#### Reviewer Notes

- Pending external review.

### Sample 4

- Chapter / Paragraph: `2` / `481`
- Document: `EPUB/text/ch001.xhtml`
- XPath: `/*/*[2]/*/*[9]/*[59]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre2">深渊里有什么呢？孤独妖怪到底长什么样？为什么疯子女士去了深渊还能跳着舞回来？</p>
```

#### Extracted Text

深渊里有什么呢？孤独妖怪到底长什么样？为什么疯子女士去了深渊还能跳着舞回来？

#### Sentence Segments

- `0`: 深渊里有什么呢？
- `1`: 孤独妖怪到底长什么样？
- `2`: 为什么疯子女士去了深渊还能跳着舞回来？

#### CFI Roundtrip

深渊里有什么呢？孤独妖怪到底长什么样？为什么疯子女士去了深渊还能跳着舞回来？

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[9]/*[59]` 深渊里有什么呢？孤独妖怪到底长什么样？为什么疯子女士去了深渊还能跳着舞回来？

#### Reviewer Notes

- Pending external review.

## Summary

- Total samples: `4`
- Ruby samples: `0`
- Footnote-ish samples: `0`
- Roundtrip mismatches: `0`

## Failed Samples

- None

## Suggested Fix Directions

- Inspect any roundtrip mismatch where normalized extracted text diverges from the paragraph segment.
- Review debug spans for over-skipped note links or missed ruby base text.
- Compare paragraph and sentence outputs when inline breaks appear in poetry-like XHTML.
