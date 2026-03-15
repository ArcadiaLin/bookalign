# EPUB Extraction Audit

- Book: `Rimas y leyendas (Gustavo Adolfo Becquer) (z-library.sk, 1lib.sk, z-lib.sk).epub`
- Seed: `20261050`
- Sample count: `5`
- Test type: `normal`
- Granularity: `sentence`
- Debug metadata: `on`

## Samples

### Sample 1

- Chapter / Paragraph: `220` / `35`
- Document: `index_split_219.xhtml`
- XPath: `/*/*[2]/*/*/*/*[7]/*[2]/*[13]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre2"><span class="none">Los preceptos de los doctores, las lágrimas de su hija, nada había sido bastante a detenerle en el lecho.</span></p>
```

#### Extracted Text

Los preceptos de los doctores, las lágrimas de su hija, nada había sido bastante a detenerle en el lecho.

#### Sentence Segments

- `0`: Los preceptos de los doctores, las lágrimas de su hija, nada había sido bastante a detenerle en el lecho.

#### CFI Roundtrip

Los preceptos de los doctores, las lágrimas de su hija, nada había sido bastante a detenerle en el lecho.

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*/*/*[7]/*[2]/*[13]/*` Los preceptos de los doctores, las lágrimas de su hija, nada había sido bastante

#### Reviewer Notes

- Pending external review.

### Sample 2

- Chapter / Paragraph: `232` / `23`
- Document: `index_split_231.xhtml`
- XPath: `/*/*[2]/*/*/*/*[5]/*[2]/*[23]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre2"><span class="none">—¿Vosotras creéis algo de las tonterías que nos ha contado el tío Gregorio?</span></p>
```

#### Extracted Text

—¿Vosotras creéis algo de las tonterías que nos ha contado el tío Gregorio?

#### Sentence Segments

- `0`: —¿Vosotras creéis algo de las tonterías que nos ha contado el tío Gregorio?

#### CFI Roundtrip

—¿Vosotras creéis algo de las tonterías que nos ha contado el tío Gregorio?

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*/*/*[5]/*[2]/*[23]/*` —¿Vosotras creéis algo de las tonterías que nos ha contado el tío Gregorio?

#### Reviewer Notes

- Pending external review.

### Sample 3

- Chapter / Paragraph: `163` / `0`
- Document: `index_split_162.xhtml`
- XPath: `/*/*[2]/*/*/*/*/*`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<h2 xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre5" id="calibre_pb_244"> <span class="none3">— LXXIX —</span></h2>
```

#### Extracted Text

— LXXIX —

#### Sentence Segments

- `0`: — LXXIX —

#### CFI Roundtrip

— LXXIX —

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*/*/*/*/*` — LXXIX —

#### Reviewer Notes

- Pending external review.

### Sample 4

- Chapter / Paragraph: `183` / `6`
- Document: `index_split_182.xhtml`
- XPath: `/*/*[2]/*/*/*/*[2]/*[7]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre2"><span class="none2">gemidos tristes, marchitas galas</span></p>
```

#### Extracted Text

gemidos tristes, marchitas galas

#### Sentence Segments

- `0`: gemidos tristes, marchitas galas

#### CFI Roundtrip

gemidos tristes, marchitas galas

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*/*/*[2]/*[7]/*` gemidos tristes, marchitas galas

#### Reviewer Notes

- Pending external review.

### Sample 5

- Chapter / Paragraph: `142` / `10`
- Document: `index_split_141.xhtml`
- XPath: `/*/*[2]/*/*/*/*[2]/*[11]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre2"><span class="none2">mas tengo en mi tristeza una alegría…</span></p>
```

#### Extracted Text

mas tengo en mi tristeza una alegría…

#### Sentence Segments

- `0`: mas tengo en mi tristeza una alegría…

#### CFI Roundtrip

mas tengo en mi tristeza una alegría…

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*/*/*[2]/*[11]/*` mas tengo en mi tristeza una alegría…

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
