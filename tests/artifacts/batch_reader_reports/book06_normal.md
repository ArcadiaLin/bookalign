# EPUB Extraction Audit

- Book: `THE ADVENTURES OF SHERLOCK HOLMES by ARTHUR CONAN DOYLE (The Adventures Of Sherlock Holmes) (z-library.sk, 1lib.sk, z-lib.sk).epub`
- Seed: `20261060`
- Sample count: `5`
- Test type: `normal`
- Granularity: `sentence`
- Debug metadata: `on`

## Samples

### Sample 1

- Chapter / Paragraph: `1` / `1380`
- Document: `Doyle, Arthur Conan - The Adventures Of Sherlock Holmes.htm`
- XPath: `/*/*[2]/*/*[1398]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="msonormal"><span><span>     </span>"You? Who are you? How could you
know anything of the matter?"</span></p>
```

#### Extracted Text

"You? Who are you? How could you know anything of the matter?"

#### Sentence Segments

- `0`: "You? Who are you? How could you know anything of the matter?"

#### CFI Roundtrip

"You? Who are you? How could you know anything of the matter?"

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*[1398]/*` "You? Who are you? How could you know anything of the matter?"

#### Reviewer Notes

- Pending external review.

### Sample 2

- Chapter / Paragraph: `1` / `243`
- Document: `Doyle, Arthur Conan - The Adventures Of Sherlock Holmes.htm`
- XPath: `/*/*[2]/*/*[245]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="msonormal"><span><span>     </span>"And the papers?" asked the
King hoarsely. "All is lost."</span></p>
```

#### Extracted Text

"And the papers?" asked the King hoarsely. "All is lost."

#### Sentence Segments

- `0`: "And the papers?" asked the King hoarsely.
- `1`: "All is lost."

#### CFI Roundtrip

"And the papers?" asked the King hoarsely. "All is lost."

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*[245]/*` "And the papers?" asked the King hoarsely. "All is lost."

#### Reviewer Notes

- Pending external review.

### Sample 3

- Chapter / Paragraph: `1` / `2432`
- Document: `Doyle, Arthur Conan - The Adventures Of Sherlock Holmes.htm`
- XPath: `/*/*[2]/*/*[2462]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="msonormal"><span><span>     </span>"And now I have a very strange
experience to tell you. I had, as you know, cut off my hair in London, and I
had placed it in a great coil at the bottom of my trunk. One evening, after the
child was in bed, I began to amuse myself by examining the furniture of my room
and by rearranging my own little things. There was an old chest of drawers in
the room, the two upper ones empty and open, the lower one locked. I had filled
the first two with my linen. and as I had still much to pack away I was naturally
annoyed at not having the use of the third drawer. It struck me that it might
have been fastened by a mere oversight, so I took out my bunch of keys and
tried to open it. The very first key fitted to perfection, and I drew the
drawer open. There was only one thing in it, but I am sure that you would never
guess what it was. It was my coil of hair.</span></p>
```

#### Extracted Text

"And now I have a very strange experience to tell you. I had, as you know, cut off my hair in London, and I had placed it in a great coil at the bottom of my trunk. One evening, after the child was in bed, I began to amuse myself by examining the furniture of my room and by rearranging my own little things. There was an old chest of drawers in the room, the two upper ones empty and open, the lower one locked. I had filled the first two with my linen. and as I had still much to pack away I was naturally annoyed at not having the use of the third drawer. It struck me that it might have been fastened by a mere oversight, so I took out my bunch of keys and tried to open it. The very first key fitted to perfection, and I drew the drawer open. There was only one thing in it, but I am sure that you would never guess what it was. It was my coil of hair.

#### Sentence Segments

- `0`: "And now I have a very strange experience to tell you.
- `1`: I had, as you know, cut off my hair in London, and I had placed it in a great coil at the bottom of my trunk.
- `2`: One evening, after the child was in bed, I began to amuse myself by examining the furniture of my room and by rearranging my own little things.
- `3`: There was an old chest of drawers in the room, the two upper ones empty and open, the lower one locked.
- `4`: I had filled the first two with my linen.
- `5`: and as I had still much to pack away I was naturally annoyed at not having the use of the third drawer.
- `6`: It struck me that it might have been fastened by a mere oversight, so I took out my bunch of keys and tried to open it.
- `7`: The very first key fitted to perfection, and I drew the drawer open.
- `8`: There was only one thing in it, but I am sure that you would never guess what it was.
- `9`: It was my coil of hair.

#### CFI Roundtrip

"And now I have a very strange experience to tell you. I had, as you know, cut off my hair in London, and I had placed it in a great coil at the bottom of my trunk. One evening, after the child was in bed, I began to amuse myself by examining the furniture of my room and by rearranging my own little things. There was an old chest of drawers in the room, the two upper ones empty and open, the lower one locked. I had filled the first two with my linen. and as I had still much to pack away I was naturally annoyed at not having the use of the third drawer. It struck me that it might have been fastened by a mere oversight, so I took out my bunch of keys and tried to open it. The very first key fitted to perfection, and I drew the drawer open. There was only one thing in it, but I am sure that you would never guess what it was. It was my coil of hair.

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*[2462]/*` "And now I have a very strange experience to tell you. I had, as you know, cut o

#### Reviewer Notes

- Pending external review.

### Sample 4

- Chapter / Paragraph: `1` / `261`
- Document: `Doyle, Arthur Conan - The Adventures Of Sherlock Holmes.htm`
- XPath: `/*/*[2]/*/*[265]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="msonormal"><span><span>     </span>"You could not possibly have come at
a better time, my dear Watson," he said cordially.</span></p>
```

#### Extracted Text

"You could not possibly have come at a better time, my dear Watson," he said cordially.

#### Sentence Segments

- `0`: "You could not possibly have come at a better time, my dear Watson," he said cordially.

#### CFI Roundtrip

"You could not possibly have come at a better time, my dear Watson," he said cordially.

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*[265]/*` "You could not possibly have come at a better time, my dear Watson," he said cor

#### Reviewer Notes

- Pending external review.

### Sample 5

- Chapter / Paragraph: `1` / `465`
- Document: `Doyle, Arthur Conan - The Adventures Of Sherlock Holmes.htm`
- XPath: `/*/*[2]/*/*[472]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="msonormal"><span><span>     </span>"But how could you guess what the
motive was?"</span></p>
```

#### Extracted Text

"But how could you guess what the motive was?"

#### Sentence Segments

- `0`: "But how could you guess what the motive was?"

#### CFI Roundtrip

"But how could you guess what the motive was?"

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*[472]/*` "But how could you guess what the motive was?"

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
