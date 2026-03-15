# EPUB Extraction Audit

- Book: `Jane Austen (Jane Austen) (z-library.sk, 1lib.sk, z-lib.sk).epub`
- Seed: `20261030`
- Sample count: `5`
- Test type: `normal`
- Granularity: `sentence`
- Debug metadata: `on`

## Samples

### Sample 1

- Chapter / Paragraph: `24` / `110`
- Document: `Jane_Austen_The_Complete_Illust_split_023.html`
- XPath: `/*/*[2]/*[119]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre11">Elinor said no more, and John was also for a short time silent.--His reflections ended thus.</p>
```

#### Extracted Text

Elinor said no more, and John was also for a short time silent.--His reflections ended thus.

#### Sentence Segments

- `0`: Elinor said no more, and John was also for a short time silent.
- `1`: --His reflections ended thus.

#### CFI Roundtrip

Elinor said no more, and John was also for a short time silent.--His reflections ended thus.

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[119]` Elinor said no more, and John was also for a short time silent.--His reflections

#### Reviewer Notes

- Pending external review.

### Sample 2

- Chapter / Paragraph: `20` / `333`
- Document: `Jane_Austen_The_Complete_Illust_split_019.html`
- XPath: `/*/*[2]/*[365]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre11">"Miss Bennet I am shocked and astonished. I expected to find a more reasonable young woman. But do not deceive yourself into a belief that I will ever recede. I shall not go away till you have given me the assurance I require."</p>
```

#### Extracted Text

"Miss Bennet I am shocked and astonished. I expected to find a more reasonable young woman. But do not deceive yourself into a belief that I will ever recede. I shall not go away till you have given me the assurance I require."

#### Sentence Segments

- `0`: "Miss Bennet I am shocked and astonished. I expected to find a more reasonable young woman. But do not deceive yourself into a belief that I will ever recede. I shall not go away till you have given me the assurance I require."

#### CFI Roundtrip

"Miss Bennet I am shocked and astonished. I expected to find a more reasonable young woman. But do not deceive yourself into a belief that I will ever recede. I shall not go away till you have given me the assurance I require."

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[365]` "Miss Bennet I am shocked and astonished. I expected to find a more reasonable y

#### Reviewer Notes

- Pending external review.

### Sample 3

- Chapter / Paragraph: `6` / `105`
- Document: `Jane_Austen_The_Complete_Illust_split_005.html`
- XPath: `/*/*[2]/*[187]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre11">Churchhill.</p>
```

#### Extracted Text

Churchhill.

#### Sentence Segments

- `0`: Churchhill.

#### CFI Roundtrip

Churchhill.

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[187]` Churchhill.

#### Reviewer Notes

- Pending external review.

### Sample 4

- Chapter / Paragraph: `3` / `289`
- Document: `Jane_Austen_The_Complete_Illust_split_002.html`
- XPath: `/*/*[2]/*[332]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre11">"Think of me to-morrow, my dear Emma, about four o'clock," was Mrs. Weston's parting injunction; spoken with some anxiety, and meant only for her.</p>
```

#### Extracted Text

"Think of me to-morrow, my dear Emma, about four o'clock," was Mrs. Weston's parting injunction; spoken with some anxiety, and meant only for her.

#### Sentence Segments

- `0`: "Think of me to-morrow, my dear Emma, about four o'clock," was Mrs. Weston's parting injunction; spoken with some anxiety, and meant only for her.

#### CFI Roundtrip

"Think of me to-morrow, my dear Emma, about four o'clock," was Mrs. Weston's parting injunction; spoken with some anxiety, and meant only for her.

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[332]` "Think of me to-morrow, my dear Emma, about four o'clock," was Mrs. Weston's par

#### Reviewer Notes

- Pending external review.

### Sample 5

- Chapter / Paragraph: `22` / `287`
- Document: `Jane_Austen_The_Complete_Illust_split_021.html`
- XPath: `/*/*[2]/*[320]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre11">In a firm, though cautious tone, Elinor thus began.</p>
```

#### Extracted Text

In a firm, though cautious tone, Elinor thus began.

#### Sentence Segments

- `0`: In a firm, though cautious tone, Elinor thus began.

#### CFI Roundtrip

In a firm, though cautious tone, Elinor thus began.

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[320]` In a firm, though cautious tone, Elinor thus began.

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
