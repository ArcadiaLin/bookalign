# EPUB Extraction Audit

- Book: `Alices Adventures in Wonderland (Lewis Caroll) (z-library.sk, 1lib.sk, z-lib.sk).epub`
- Seed: `20261010`
- Sample count: `5`
- Test type: `normal`
- Granularity: `sentence`
- Debug metadata: `on`

## Samples

### Sample 1

- Chapter / Paragraph: `1` / `153`
- Document: `Alices-Adventures-in-Wonderland.xhtml`
- XPath: `/*/*[2]/*[4]/*[161]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="Paragraph---Indent">‘I don’t see,’ said the Caterpillar.</p>
```

#### Extracted Text

‘I don’t see,’ said the Caterpillar.

#### Sentence Segments

- `0`: ‘I don’t see,’ said the Caterpillar.

#### CFI Roundtrip

‘I don’t see,’ said the Caterpillar.

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[4]/*[161]` ‘I don’t see,’ said the Caterpillar.

#### Reviewer Notes

- Pending external review.

### Sample 2

- Chapter / Paragraph: `1` / `738`
- Document: `Alices-Adventures-in-Wonderland.xhtml`
- XPath: `/*/*[2]/*[4]/*[755]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="Paragraph---Indent">‘—and just take his head off outside,’ the Queen added to one of the officers: but the Hatter was out of sight before the officer could get to the door.</p>
```

#### Extracted Text

‘—and just take his head off outside,’ the Queen added to one of the officers: but the Hatter was out of sight before the officer could get to the door.

#### Sentence Segments

- `0`: ‘—and just take his head off outside,’ the Queen added to one of the officers: but the Hatter was out of sight before the officer could get to the door.

#### CFI Roundtrip

‘—and just take his head off outside,’ the Queen added to one of the officers: but the Hatter was out of sight before the officer could get to the door.

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[4]/*[755]` ‘—and just take his head off outside,’ the Queen added to one of the officers: b

#### Reviewer Notes

- Pending external review.

### Sample 3

- Chapter / Paragraph: `1` / `280`
- Document: `Alices-Adventures-in-Wonderland.xhtml`
- XPath: `/*/*[2]/*[4]/*[290]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="Paragraph---Indent">Alice glanced rather anxiously at the cook, to see if she meant to take the hint; but the cook was busily stirring the soup, and seemed not to be listening, so she went on again: ‘Twenty-four hours, I <span class="Emphasis _idGenCharOverride-1">think</span>; or is it twelve? I—’</p>
```

#### Extracted Text

Alice glanced rather anxiously at the cook, to see if she meant to take the hint; but the cook was busily stirring the soup, and seemed not to be listening, so she went on again: ‘Twenty-four hours, I think; or is it twelve? I—’

#### Sentence Segments

- `0`: Alice glanced rather anxiously at the cook, to see if she meant to take the hint; but the cook was busily stirring the soup, and seemed not to be listening, so she went on again: ‘Twenty-four hours, I think; or is it twelve? I—’

#### CFI Roundtrip

Alice glanced rather anxiously at the cook, to see if she meant to take the hint; but the cook was busily stirring the soup, and seemed not to be listening, so she went on again: ‘Twenty-four hours, I think; or is it twelve? I—’

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[4]/*[290]` Alice glanced rather anxiously at the cook, to see if she meant to take the hint
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[4]/*[290]/*` think
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[4]/*[290]` ; or is it twelve? I—’

#### Reviewer Notes

- Pending external review.

### Sample 4

- Chapter / Paragraph: `1` / `19`
- Document: `Alices-Adventures-in-Wonderland.xhtml`
- XPath: `/*/*[2]/*[4]/*[21]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="Paragraph---Indent">There were doors all round the hall, but they were all locked; and when Alice had been all the way down one side and up the other, trying every door, she walked sadly down the middle, wondering how she was ever to get out again.</p>
```

#### Extracted Text

There were doors all round the hall, but they were all locked; and when Alice had been all the way down one side and up the other, trying every door, she walked sadly down the middle, wondering how she was ever to get out again.

#### Sentence Segments

- `0`: There were doors all round the hall, but they were all locked; and when Alice had been all the way down one side and up the other, trying every door, she walked sadly down the middle, wondering how she was ever to get out again.

#### CFI Roundtrip

There were doors all round the hall, but they were all locked; and when Alice had been all the way down one side and up the other, trying every door, she walked sadly down the middle, wondering how she was ever to get out again.

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[4]/*[21]` There were doors all round the hall, but they were all locked; and when Alice ha

#### Reviewer Notes

- Pending external review.

### Sample 5

- Chapter / Paragraph: `1` / `435`
- Document: `Alices-Adventures-in-Wonderland.xhtml`
- XPath: `/*/*[2]/*[4]/*[449]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="Paragraph---Indent">‘What for?’ said the one who had spoken first.</p>
```

#### Extracted Text

‘What for?’ said the one who had spoken first.

#### Sentence Segments

- `0`: ‘What for?
- `1`: ’ said the one who had spoken first.

#### CFI Roundtrip

‘What for?’ said the one who had spoken first.

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[4]/*[449]` ‘What for?’ said the one who had spoken first.

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
