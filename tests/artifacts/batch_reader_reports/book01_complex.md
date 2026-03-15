# EPUB Extraction Audit

- Book: `Alices Adventures in Wonderland (Lewis Caroll) (z-library.sk, 1lib.sk, z-lib.sk).epub`
- Seed: `20261011`
- Sample count: `5`
- Test type: `complex`
- Granularity: `sentence`
- Debug metadata: `on`

## Samples

### Sample 1

- Chapter / Paragraph: `1` / `792`
- Document: `Alices-Adventures-in-Wonderland.xhtml`
- XPath: `/*/*[2]/*[4]/*[810]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="Blockquote"><span class="Emphasis _idGenCharOverride-1">I gave her one, they gave him two, <br></br>  You gave us three or more; <br></br>They all returned from him to you, <br></br>  Though they were mine before.</span></p>
```

#### Extracted Text

I gave her one, they gave him two, You gave us three or more; They all returned from him to you, Though they were mine before.

#### Sentence Segments

- `0`: I gave her one, they gave him two, You gave us three or more; They all returned from him to you, Though they were mine before.

#### CFI Roundtrip

I gave her one, they gave him two, You gave us three or more; They all returned from him to you, Though they were mine before.

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*[4]/*[810]/*` I gave her one, they gave him two,
- `br` `INLINE_BREAK` `inline-break` `/*/*[2]/*[4]/*[810]/*/*[1]` <break>
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[4]/*[810]/*` You gave us three or more;
- `br` `INLINE_BREAK` `inline-break` `/*/*[2]/*[4]/*[810]/*/*[2]` <break>
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[4]/*[810]/*` They all returned from him to you,
- `br` `INLINE_BREAK` `inline-break` `/*/*[2]/*[4]/*[810]/*/*[3]` <break>
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[4]/*[810]/*` Though they were mine before.

#### Reviewer Notes

- Pending external review.

### Sample 2

- Chapter / Paragraph: `1` / `672`
- Document: `Alices-Adventures-in-Wonderland.xhtml`
- XPath: `/*/*[2]/*[4]/*[688]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="Blockquote"><span class="Emphasis _idGenCharOverride-1">‘Beautiful Soup! Who cares for fish, <br></br>Game, or any other dish? <br></br>Who would not give all else for two <br></br>pennyworth only of beautiful Soup? <br></br>Pennyworth only of beautiful Soup? <br></br>  Beau—ootiful Soo—oop! <br></br>  Beau—ootiful Soo—oop! <br></br>Soo—oop of the e—e—evening, <br></br>  Beautiful, beauti—FUL SOUP!’</span></p>
```

#### Extracted Text

‘Beautiful Soup! Who cares for fish, Game, or any other dish? Who would not give all else for two pennyworth only of beautiful Soup? Pennyworth only of beautiful Soup? Beau—ootiful Soo—oop! Beau—ootiful Soo—oop! Soo—oop of the e—e—evening, Beautiful, beauti—FUL SOUP!’

#### Sentence Segments

- `0`: ‘Beautiful Soup!
- `1`: Who cares for fish, Game, or any other dish?
- `2`: Who would not give all else for two pennyworth only of beautiful Soup?
- `3`: Pennyworth only of beautiful Soup?
- `4`: Beau—ootiful Soo—oop!
- `5`: Beau—ootiful Soo—oop!

#### CFI Roundtrip

‘Beautiful Soup! Who cares for fish, Game, or any other dish? Who would not give all else for two pennyworth only of beautiful Soup? Pennyworth only of beautiful Soup? Beau—ootiful Soo—oop! Beau—ootiful Soo—oop! Soo—oop of the e—e—evening, Beautiful, beauti—FUL SOUP!’

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*[4]/*[688]/*` ‘Beautiful Soup! Who cares for fish,
- `br` `INLINE_BREAK` `inline-break` `/*/*[2]/*[4]/*[688]/*/*[1]` <break>
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[4]/*[688]/*` Game, or any other dish?
- `br` `INLINE_BREAK` `inline-break` `/*/*[2]/*[4]/*[688]/*/*[2]` <break>
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[4]/*[688]/*` Who would not give all else for two
- `br` `INLINE_BREAK` `inline-break` `/*/*[2]/*[4]/*[688]/*/*[3]` <break>
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[4]/*[688]/*` pennyworth only of beautiful Soup?
- `br` `INLINE_BREAK` `inline-break` `/*/*[2]/*[4]/*[688]/*/*[4]` <break>
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[4]/*[688]/*` Pennyworth only of beautiful Soup?
- `br` `INLINE_BREAK` `inline-break` `/*/*[2]/*[4]/*[688]/*/*[5]` <break>
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[4]/*[688]/*` Beau—ootiful Soo—oop!
- `br` `INLINE_BREAK` `inline-break` `/*/*[2]/*[4]/*[688]/*/*[6]` <break>
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[4]/*[688]/*` Beau—ootiful Soo—oop!
- `br` `INLINE_BREAK` `inline-break` `/*/*[2]/*[4]/*[688]/*/*[7]` <break>
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[4]/*[688]/*` Soo—oop of the e—e—evening,
- `br` `INLINE_BREAK` `inline-break` `/*/*[2]/*[4]/*[688]/*/*[8]` <break>
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[4]/*[688]/*` Beautiful, beauti—FUL SOUP!’

#### Reviewer Notes

- Pending external review.

### Sample 3

- Chapter / Paragraph: `1` / `7`
- Document: `Alices-Adventures-in-Wonderland.xhtml`
- XPath: `/*/*[2]/*[4]/*[8]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="Blockquote ParaOverride-1"><span class="CharOverride-3">Alice! a childish story take,<br></br>And with a gentle hand<br></br>Lay it where Childhood’s dreams are twined<br></br>In Memory’s mystic band,<br></br>Like pilgrim’s withered wreath of flowers<br></br>Plucked in a far-off land.</span></p>
```

#### Extracted Text

Alice! a childish story take, And with a gentle hand Lay it where Childhood’s dreams are twined In Memory’s mystic band, Like pilgrim’s withered wreath of flowers Plucked in a far-off land.

#### Sentence Segments

- `0`: Alice! a childish story take,
- `1`: And with a gentle hand
- `2`: Lay it where Childhood’s dreams are twined
- `3`: In Memory’s mystic band,
- `4`: Like pilgrim’s withered wreath of flowers
- `5`: Plucked in a far-off land.

#### CFI Roundtrip

Alice! a childish story take, And with a gentle hand Lay it where Childhood’s dreams are twined In Memory’s mystic band, Like pilgrim’s withered wreath of flowers Plucked in a far-off land.

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*[4]/*[8]/*` Alice! a childish story take,
- `br` `INLINE_BREAK` `inline-break` `/*/*[2]/*[4]/*[8]/*/*[1]` <break>
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[4]/*[8]/*` And with a gentle hand
- `br` `INLINE_BREAK` `inline-break` `/*/*[2]/*[4]/*[8]/*/*[2]` <break>
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[4]/*[8]/*` Lay it where Childhood’s dreams are twined
- `br` `INLINE_BREAK` `inline-break` `/*/*[2]/*[4]/*[8]/*/*[3]` <break>
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[4]/*[8]/*` In Memory’s mystic band,
- `br` `INLINE_BREAK` `inline-break` `/*/*[2]/*[4]/*[8]/*/*[4]` <break>
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[4]/*[8]/*` Like pilgrim’s withered wreath of flowers
- `br` `INLINE_BREAK` `inline-break` `/*/*[2]/*[4]/*[8]/*/*[5]` <break>
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[4]/*[8]/*` Plucked in a far-off land.

#### Reviewer Notes

- Pending external review.

### Sample 4

- Chapter / Paragraph: `1` / `0`
- Document: `Alices-Adventures-in-Wonderland.xhtml`
- XPath: `/*/*[2]/*[4]/*[1]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="Blockquote ParaOverride-1"><span class="CharOverride-2">All in the Golden Afternoon</span><span class="CharOverride-3"><br></br><br></br><br></br></span></p>
```

#### Extracted Text

All in the Golden Afternoon

#### Sentence Segments

- `0`: All in the Golden Afternoon

#### CFI Roundtrip

All in the Golden Afternoon

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*[4]/*[1]/*[1]` All in the Golden Afternoon
- `br` `INLINE_BREAK` `inline-break` `/*/*[2]/*[4]/*[1]/*[2]/*[1]` <break>
- `br` `INLINE_BREAK` `inline-break` `/*/*[2]/*[4]/*[1]/*[2]/*[2]` <break>
- `br` `INLINE_BREAK` `inline-break` `/*/*[2]/*[4]/*[1]/*[2]/*[3]` <break>

#### Reviewer Notes

- Pending external review.

### Sample 5

- Chapter / Paragraph: `1` / `791`
- Document: `Alices-Adventures-in-Wonderland.xhtml`
- XPath: `/*/*[2]/*[4]/*[809]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="Blockquote"><span class="Emphasis _idGenCharOverride-1">He sent them word I had not gone <br></br>  (We know it to be true): <br></br>If she should push the matter on, <br></br>  What would become of you?</span></p>
```

#### Extracted Text

He sent them word I had not gone (We know it to be true): If she should push the matter on, What would become of you?

#### Sentence Segments

- `0`: He sent them word I had not gone (We know it to be true): If she should push the matter on, What would become of you?

#### CFI Roundtrip

He sent them word I had not gone (We know it to be true): If she should push the matter on, What would become of you?

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*[4]/*[809]/*` He sent them word I had not gone
- `br` `INLINE_BREAK` `inline-break` `/*/*[2]/*[4]/*[809]/*/*[1]` <break>
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[4]/*[809]/*` (We know it to be true):
- `br` `INLINE_BREAK` `inline-break` `/*/*[2]/*[4]/*[809]/*/*[2]` <break>
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[4]/*[809]/*` If she should push the matter on,
- `br` `INLINE_BREAK` `inline-break` `/*/*[2]/*[4]/*[809]/*/*[3]` <break>
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[4]/*[809]/*` What would become of you?

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
