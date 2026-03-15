# EPUB Extraction Audit

- Book: `THE ADVENTURES OF SHERLOCK HOLMES by ARTHUR CONAN DOYLE (The Adventures Of Sherlock Holmes) (z-library.sk, 1lib.sk, z-lib.sk).epub`
- Seed: `20261061`
- Sample count: `4`
- Test type: `complex`
- Granularity: `sentence`
- Debug metadata: `on`

## Samples

### Sample 1

- Chapter / Paragraph: `1` / `2313`
- Document: `Doyle, Arthur Conan - The Adventures Of Sherlock Holmes.htm`
- XPath: `/*/*[2]/*/*[2343]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="msonormal"><span><span>     </span>"DEAR MR. HOLMES:--I am very anxious
to consult you as to whether I should or should not accept a situation which
has been offered to me as governess. I shall call at half-past ten to-morrow if
I do not inconvenience you.<span>                                         </span><span> </span><span>      </span>Yours
faithfully,<span>      </span><span>   </span>VIOLET HUNTER."</span></p>
```

#### Extracted Text

"DEAR MR. HOLMES:--I am very anxious to consult you as to whether I should or should not accept a situation which has been offered to me as governess. I shall call at half-past ten to-morrow if I do not inconvenience you. Yours faithfully, VIOLET HUNTER."

#### Sentence Segments

- `0`: "DEAR MR. HOLMES:--I am very anxious to consult you as to whether I should or should not accept a situation which has been offered to me as governess. I shall call at half-past ten to-morrow if I do not inconvenience you. Yours faithfully, VIOLET HUNTER."

#### CFI Roundtrip

"DEAR MR. HOLMES:--I am very anxious to consult you as to whether I should or should not accept a situation which has been offered to me as governess. I shall call at half-past ten to-morrow if I do not inconvenience you. Yours faithfully, VIOLET HUNTER."

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*[2343]/*` "DEAR MR. HOLMES:--I am very anxious to consult you as to whether I should or sh
- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*[2343]/*` Yours faithfully,
- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*[2343]/*` VIOLET HUNTER."

#### Reviewer Notes

- Pending external review.

### Sample 2

- Chapter / Paragraph: `1` / `351`
- Document: `Doyle, Arthur Conan - The Adventures Of Sherlock Holmes.htm`
- XPath: `/*/*[2]/*/*[357]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="msonormal"><span><span>     </span><span>              </span><span>          </span>DISSOLVED.</span></p>
```

#### Extracted Text

DISSOLVED.

#### Sentence Segments

- `0`: DISSOLVED.

#### CFI Roundtrip

DISSOLVED.

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*[357]/*` DISSOLVED.

#### Reviewer Notes

- Pending external review.

### Sample 3

- Chapter / Paragraph: `1` / `1809`
- Document: `Doyle, Arthur Conan - The Adventures Of Sherlock Holmes.htm`
- XPath: `/*/*[2]/*/*[1831]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="msonormal"><span><span>     </span>"This time, at least, I did not
scorn her advice. I staggered to my feet and ran with her along the corridor
and down a winding stair. The latter led to another broad passage, and just as
we reached it we heard the sound of running feet and the shouting of two
voices, one answering the other from the floor on which<span>  </span>we were and from the one beneath. My guide
stopped and looked about her like one<span> 
</span>who is at her wit's end. Then she threw open a door which led into a
bedroom, through the window of which the moon was shining brightly.</span></p>
```

#### Extracted Text

"This time, at least, I did not scorn her advice. I staggered to my feet and ran with her along the corridor and down a winding stair. The latter led to another broad passage, and just as we reached it we heard the sound of running feet and the shouting of two voices, one answering the other from the floor on which we were and from the one beneath. My guide stopped and looked about her like one who is at her wit's end. Then she threw open a door which led into a bedroom, through the window of which the moon was shining brightly.

#### Sentence Segments

- `0`: "This time, at least, I did not scorn her advice.
- `1`: I staggered to my feet and ran with her along the corridor and down a winding stair.
- `2`: The latter led to another broad passage, and just as we reached it we heard the sound of running feet and the shouting of two voices, one answering the other from the floor on which we were and from the one beneath.
- `3`: My guide stopped and looked about her like one who is at her wit's end.
- `4`: Then she threw open a door which led into a bedroom, through the window of which the moon was shining brightly.

#### CFI Roundtrip

"This time, at least, I did not scorn her advice. I staggered to my feet and ran with her along the corridor and down a winding stair. The latter led to another broad passage, and just as we reached it we heard the sound of running feet and the shouting of two voices, one answering the other from the floor on which we were and from the one beneath. My guide stopped and looked about her like one who is at her wit's end. Then she threw open a door which led into a bedroom, through the window of which the moon was shining brightly.

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*[1831]/*` "This time, at least, I did not scorn her advice. I staggered to my feet and ran
- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*[1831]/*` we were and from the one beneath. My guide stopped and looked about her like one
- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*[1831]/*` who is at her wit's end. Then she threw open a door which led into a bedroom, th

#### Reviewer Notes

- Pending external review.

### Sample 4

- Chapter / Paragraph: `1` / `2264`
- Document: `Doyle, Arthur Conan - The Adventures Of Sherlock Holmes.htm`
- XPath: `/*/*[2]/*/*[2292]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="msonormal"><span><span>     </span>"'MY DEAREST UNCLE:--I feel that I
have brought trouble upon you, and that if I had acted differently this
terrible misfortune might never have occurred. I cannot, with this thought in
my mind, ever again be happy under your roof, and I feel that I must leave you
forever. Do not worry about my future, for that is provided for; and, above
all, do not search for me, for it will be fruitless labour and an ill-service
to me. In life or in<span>       </span><span> </span>death, I am ever your loving<span>  </span>MARY.'</span></p>
```

#### Extracted Text

"'MY DEAREST UNCLE:--I feel that I have brought trouble upon you, and that if I had acted differently this terrible misfortune might never have occurred. I cannot, with this thought in my mind, ever again be happy under your roof, and I feel that I must leave you forever. Do not worry about my future, for that is provided for; and, above all, do not search for me, for it will be fruitless labour and an ill-service to me. In life or in death, I am ever your loving MARY.'

#### Sentence Segments

- `0`: "'MY DEAREST UNCLE:--I feel that I have brought trouble upon you, and that if I had acted differently this terrible misfortune might never have occurred.
- `1`: I cannot, with this thought in my mind, ever again be happy under your roof, and I feel that I must leave you forever.
- `2`: Do not worry about my future, for that is provided for; and, above all, do not search for me, for it will be fruitless labour and an ill-service to me.
- `3`: In life or in death, I am ever your loving MARY.
- `4`: '

#### CFI Roundtrip

"'MY DEAREST UNCLE:--I feel that I have brought trouble upon you, and that if I had acted differently this terrible misfortune might never have occurred. I cannot, with this thought in my mind, ever again be happy under your roof, and I feel that I must leave you forever. Do not worry about my future, for that is provided for; and, above all, do not search for me, for it will be fruitless labour and an ill-service to me. In life or in death, I am ever your loving MARY.'

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*[2292]/*` "'MY DEAREST UNCLE:--I feel that I have brought trouble upon you, and that if I 
- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*[2292]/*` death, I am ever your loving
- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*[2292]/*` MARY.'

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
