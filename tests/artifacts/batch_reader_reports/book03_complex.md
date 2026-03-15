# EPUB Extraction Audit

- Book: `Jane Austen (Jane Austen) (z-library.sk, 1lib.sk, z-lib.sk).epub`
- Seed: `20261031`
- Sample count: `5`
- Test type: `complex`
- Granularity: `sentence`
- Debug metadata: `on`

## Samples

### Sample 1

- Chapter / Paragraph: `25` / `0`
- Document: `Jane_Austen_The_Complete_Illust_split_024.html`
- XPath: `/*/*[2]/*[5]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre107"><span class="bold">Jane Austen</span> (16 December 1775-18 July 1817) was an English novelist whose works include <span class="italic">Sense and Sensibility</span>, <span class="italic">Pride and Prejudice</span>, <span class="italic">Mansfield Park</span>, <span class="italic">Emma</span>, <span class="italic">Northanger Abbey</span>, and <span class="italic">Persuasion</span>. Her social commentary and masterful use of both free indirect speech and irony eventually made Austen one of the most influential and honoured novelists in English literature. Her novels were all written and set around the Regency Era. She never married and died at age 41.</p>
```

#### Extracted Text

Jane Austen (16 December 1775-18 July 1817) was an English novelist whose works include Sense and Sensibility, Pride and Prejudice, Mansfield Park, Emma, Northanger Abbey, and Persuasion. Her social commentary and masterful use of both free indirect speech and irony eventually made Austen one of the most influential and honoured novelists in English literature. Her novels were all written and set around the Regency Era. She never married and died at age 41.

#### Sentence Segments

- `0`: Jane Austen (16 December 1775-18 July 1817) was an English novelist whose works include Sense and Sensibility, Pride and Prejudice, Mansfield Park, Emma, Northanger Abbey, and Persuasion.
- `1`: Her social commentary and masterful use of both free indirect speech and irony eventually made Austen one of the most influential and honoured novelists in English literature.
- `2`: Her novels were all written and set around the Regency Era.
- `3`: She never married and died at age 41.

#### CFI Roundtrip

Jane Austen (16 December 1775-18 July 1817) was an English novelist whose works include Sense and Sensibility, Pride and Prejudice, Mansfield Park, Emma, Northanger Abbey, and Persuasion. Her social commentary and masterful use of both free indirect speech and irony eventually made Austen one of the most influential and honoured novelists in English literature. Her novels were all written and set around the Regency Era. She never married and died at age 41.

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*[5]/*[1]` Jane Austen
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[5]` (16 December 1775-18 July 1817) was an English novelist whose works include
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[5]/*[2]` Sense and Sensibility
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[5]` ,
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[5]/*[3]` Pride and Prejudice
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[5]` ,
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[5]/*[4]` Mansfield Park
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[5]` ,
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[5]/*[5]` Emma
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[5]` ,
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[5]/*[6]` Northanger Abbey
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[5]` , and
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[5]/*[7]` Persuasion
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[5]` . Her social commentary and masterful use of both free indirect speech and irony

#### Reviewer Notes

- Pending external review.

### Sample 2

- Chapter / Paragraph: `27` / `5`
- Document: `Jane_Austen_The_Complete_Illust_split_026.html`
- XPath: `/*/*[2]/*[17]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre4">
      <span class="bold">Adobe Digital Editions .</span>
      <span class="italic">
        <span class="bold">pdf</span>
      </span>
      <span class="bold"> files</span>
    </p>
```

#### Extracted Text

Adobe Digital Editions . pdf files

#### Sentence Segments

- `0`: Adobe Digital Editions .
- `1`: pdf files

#### CFI Roundtrip

Adobe Digital Editions . pdf files

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*[17]/*[1]` Adobe Digital Editions .
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[17]/*[2]/*` pdf
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[17]/*[3]` files

#### Reviewer Notes

- Pending external review.

### Sample 3

- Chapter / Paragraph: `26` / `0`
- Document: `Jane_Austen_The_Complete_Illust_split_025.html`
- XPath: `/*/*[2]/*[6]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre8">Emma <span class="italic">Illustrations by </span><span class="bold">Hugh Thomson</span> and <span class="italic">by </span><span class="bold">Charles E. Brock</span></p>
```

#### Extracted Text

Emma Illustrations by Hugh Thomson and by Charles E. Brock

#### Sentence Segments

- `0`: Emma Illustrations by Hugh Thomson and by Charles E. Brock

#### CFI Roundtrip

Emma Illustrations by Hugh Thomson and by Charles E. Brock

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[6]` Emma
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[6]/*[1]` Illustrations by
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[6]/*[2]` Hugh Thomson
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[6]` and
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[6]/*[3]` by
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[6]/*[4]` Charles E. Brock

#### Reviewer Notes

- Pending external review.

### Sample 4

- Chapter / Paragraph: `27` / `4`
- Document: `Jane_Austen_The_Complete_Illust_split_026.html`
- XPath: `/*/*[2]/*[12]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre8">- To maximize viewing area (this is especially important for viewing illustrations), please reduce Display Margins: <span class="bold">Menu</span>&gt;<span class="bold">Options</span>&gt;<span class="bold">Margins</span>&gt;<span class="bold">Very Small</span></p>
```

#### Extracted Text

- To maximize viewing area (this is especially important for viewing illustrations), please reduce Display Margins: Menu>Options>Margins>Very Small

#### Sentence Segments

- `0`: - To maximize viewing area (this is especially important for viewing illustrations), please reduce Display Margins: Menu>Options>Margins>Very Small

#### CFI Roundtrip

- To maximize viewing area (this is especially important for viewing illustrations), please reduce Display Margins: Menu>Options>Margins>Very Small

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[12]` - To maximize viewing area (this is especially important for viewing illustratio
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[12]/*[1]` Menu
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[12]` >
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[12]/*[2]` Options
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[12]` >
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[12]/*[3]` Margins
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[12]` >
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[12]/*[4]` Very Small

#### Reviewer Notes

- Pending external review.

### Sample 5

- Chapter / Paragraph: `25` / `80`
- Document: `Jane_Austen_The_Complete_Illust_split_024.html`
- XPath: `/*/*[2]/*[79]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre30"><a href="Jane_Austen_The_Complete_Illust_split_000.html#filepos103" class="calibre5"><span class="calibre6"><span class="calibre7" style="text-decoration:underline">Go to Start</span></span></a> | This article uses material from the <a href="http://en.wikipedia.org/wiki/Jane_Austen" class="calibre5"><span class="calibre6"><span class="calibre7" style="text-decoration:underline">Wikipedia</span></span></a></p>
```

#### Extracted Text

Go to Start | This article uses material from the Wikipedia

#### Sentence Segments

- `0`: Go to Start | This article uses material from the Wikipedia

#### CFI Roundtrip

Go to Start | This article uses material from the Wikipedia

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*[79]/*[1]/*/*` Go to Start
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[79]` | This article uses material from the
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[79]/*[2]/*/*` Wikipedia

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
