# EPUB Extraction Audit

- Book: `Don Quijote de la Mancha (Edicion del IV Centenario) (Spanish Edition) (Miguel de Cervantes, Real Academia Española) (z-library.sk, 1lib.sk, z-lib.sk).epub`
- Seed: `20261021`
- Sample count: `5`
- Test type: `complex`
- Granularity: `sentence`
- Debug metadata: `on`

## Samples

### Sample 1

- Chapter / Paragraph: `22` / `291`
- Document: `11_split_20.xhtml`
- XPath: `/*/*[2]/*[617]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre2">
      <span> <span class="ts3">Midnight, Central
Time, of the last day of the stated month.<span class="ts3"> <span class="ts3">A</span></span></span></span>
    </p>
```

#### Extracted Text

Midnight, Central Time, of the last day of the stated month. A

#### Sentence Segments

- `0`: Midnight, Central Time, of the last day of the stated month.
- `1`: A

#### CFI Roundtrip

Midnight, Central Time, of the last day of the stated month. A

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*[617]/*/*` Midnight, Central Time, of the last day of the stated month.
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[617]/*/*/*/*` A

#### Reviewer Notes

- Pending external review.

### Sample 2

- Chapter / Paragraph: `22` / `299`
- Document: `11_split_20.xhtml`
- XPath: `/*/*[2]/*[629]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre2">
      <span>  <span class="ts3">We produce about
two million dollars for each hour we work.<span class="ts3"> <span class="ts3">The</span></span></span></span>
    </p>
```

#### Extracted Text

We produce about two million dollars for each hour we work. The

#### Sentence Segments

- `0`: We produce about two million dollars for each hour we work.
- `1`: The

#### CFI Roundtrip

We produce about two million dollars for each hour we work. The

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*[629]/*/*` We produce about two million dollars for each hour we work.
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[629]/*/*/*/*` The

#### Reviewer Notes

- Pending external review.

### Sample 3

- Chapter / Paragraph: `8` / `243`
- Document: `11_split_6.xhtml`
- XPath: `/*/*[2]/*[261]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre2">
      <span> <span class="ts3">-Así es la verdad -respondió la doncella-, y
desde aquí adelante creo que no será menester apuntarme nada, que yo saldré a
buen puerto con mi verdadera historia. «La cual es que el rey mi padre, que se
llama Tinacrio el Sabidor, fue muy docto en esto que llaman el arte mágica, y
alcanzó por su ciencia que mi madre, que se llamaba la reina Jaramilla, había
de morir primero que él, y que de allí a poco tiempo él también había de pasar
desta vida y yo había de quedar huérfana de padre y madre. Pero decía él que no
le fatigaba tanto esto cuanto le ponía en confusión saber, por cosa muy cierta,
que un descomunal gigante, señor de una grande ínsula, que casi alinda con
nuestro reino, llamado Pandafilando de la Fosca Vista (porque es cosa
averiguada que, aunque tiene los ojos en su lugar y derechos, siempre mira al
revés, como si fuese bizco, y esto lo hace él de maligno y por poner miedo y
espanto a los que mira); digo que supo que este gigante, en sabiendo mi
orfandad, había de pasar con gran poderío sobre mi reino y me<span class="ts3"> <span class="ts3">lo había de quitar todo, sin dejarme una
pequeña aldea donde me recogiese;</span></span></span></span>
    </p>
```

#### Extracted Text

-Así es la verdad -respondió la doncella-, y desde aquí adelante creo que no será menester apuntarme nada, que yo saldré a buen puerto con mi verdadera historia. «La cual es que el rey mi padre, que se llama Tinacrio el Sabidor, fue muy docto en esto que llaman el arte mágica, y alcanzó por su ciencia que mi madre, que se llamaba la reina Jaramilla, había de morir primero que él, y que de allí a poco tiempo él también había de pasar desta vida y yo había de quedar huérfana de padre y madre. Pero decía él que no le fatigaba tanto esto cuanto le ponía en confusión saber, por cosa muy cierta, que un descomunal gigante, señor de una grande ínsula, que casi alinda con nuestro reino, llamado Pandafilando de la Fosca Vista (porque es cosa averiguada que, aunque tiene los ojos en su lugar y derechos, siempre mira al revés, como si fuese bizco, y esto lo hace él de maligno y por poner miedo y espanto a los que mira); digo que supo que este gigante, en sabiendo mi orfandad, había de pasar con gran poderío sobre mi reino y me lo había de quitar todo, sin dejarme una pequeña aldea donde me recogiese;

#### Sentence Segments

- `0`: -Así es la verdad -respondió la doncella-, y desde aquí adelante creo que no será menester apuntarme nada, que yo saldré a buen puerto con mi verdadera historia.
- `1`: «La cual es que el rey mi padre, que se llama Tinacrio el Sabidor, fue muy docto en esto que llaman el arte mágica, y alcanzó por su ciencia que mi madre, que se llamaba la reina Jaramilla, había de morir primero que él, y que de allí a poco tiempo él también había de pasar desta vida y yo había de quedar huérfana de padre y madre.
- `2`: Pero decía él que no le fatigaba tanto esto cuanto le ponía en confusión saber, por cosa muy cierta, que un descomunal gigante, señor de una grande ínsula, que casi alinda con nuestro reino, llamado Pandafilando de la Fosca Vista (porque es cosa averiguada que, aunque tiene los ojos en su lugar y derechos, siempre mira al revés, como si fuese bizco, y esto lo hace él de maligno y por poner miedo y espanto a los que mira); digo que supo que este gigante, en sabiendo mi orfandad, había de pasar con gran poderío sobre mi reino y me lo había de quitar todo, sin dejarme una pequeña aldea donde me recogiese;

#### CFI Roundtrip

-Así es la verdad -respondió la doncella-, y desde aquí adelante creo que no será menester apuntarme nada, que yo saldré a buen puerto con mi verdadera historia. «La cual es que el rey mi padre, que se llama Tinacrio el Sabidor, fue muy docto en esto que llaman el arte mágica, y alcanzó por su ciencia que mi madre, que se llamaba la reina Jaramilla, había de morir primero que él, y que de allí a poco tiempo él también había de pasar desta vida y yo había de quedar huérfana de padre y madre. Pero decía él que no le fatigaba tanto esto cuanto le ponía en confusión saber, por cosa muy cierta, que un descomunal gigante, señor de una grande ínsula, que casi alinda con nuestro reino, llamado Pandafilando de la Fosca Vista (porque es cosa averiguada que, aunque tiene los ojos en su lugar y derechos, siempre mira al revés, como si fuese bizco, y esto lo hace él de maligno y por poner miedo y espanto a los que mira); digo que supo que este gigante, en sabiendo mi orfandad, había de pasar con gran poderío sobre mi reino y me lo había de quitar todo, sin dejarme una pequeña aldea donde me recogiese;

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*[261]/*/*` -Así es la verdad -respondió la doncella-, y desde aquí adelante creo que no ser
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[261]/*/*/*/*` lo había de quitar todo, sin dejarme una pequeña aldea donde me recogiese;

#### Reviewer Notes

- Pending external review.

### Sample 4

- Chapter / Paragraph: `22` / `358`
- Document: `11_split_20.xhtml`
- XPath: `/*/*[2]/*[764]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre2">
      <span> <span class="ts3">time to the
person you received it from.<span class="ts3"> <span class="ts3">If you
received it</span></span></span></span>
    </p>
```

#### Extracted Text

time to the person you received it from. If you received it

#### Sentence Segments

- `0`: time to the person you received it from.
- `1`: If you received it

#### CFI Roundtrip

time to the person you received it from. If you received it

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*[764]/*/*` time to the person you received it from.
- `span` `KEEP_NORMAL` `` `/*/*[2]/*[764]/*/*/*/*` If you received it

#### Reviewer Notes

- Pending external review.

### Sample 5

- Chapter / Paragraph: `4` / `0`
- Document: `11_split_2.xhtml`
- XPath: `/*/*[2]/*/*[4]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre2"><span>   <span class="ts3">Yo, Juan Gallo de Andrada, escribano de
Cámara del Rey nuestro señor, de los que residen en su Consejo, certifico y doy
fe que, habiendo visto por los señores dél un libro intitulado El ingenioso
hidalgo de la Mancha, compuesto por Miguel de Cervantes Saavedra, tasaron cada
pliego del dicho libro a tres maravedís y medio; el cual tiene ochenta y tres
pliegos, que al dicho precio monta el dicho libro docientos y noventa maravedís
y medio, en que se ha de vender en papel; y dieron licencia para que a este
precio se pueda vender, y mandaron que esta tasa se ponga al principio del
dicho<span class="ts3"> <span class="ts3">libro, y no se pueda vender sin
ella. Y, para que dello conste, di la presente en Valladolid, a veinte días del
mes de deciembre de mil y seiscientos y cuatro años.</span></span></span></span></p>
```

#### Extracted Text

Yo, Juan Gallo de Andrada, escribano de Cámara del Rey nuestro señor, de los que residen en su Consejo, certifico y doy fe que, habiendo visto por los señores dél un libro intitulado El ingenioso hidalgo de la Mancha, compuesto por Miguel de Cervantes Saavedra, tasaron cada pliego del dicho libro a tres maravedís y medio; el cual tiene ochenta y tres pliegos, que al dicho precio monta el dicho libro docientos y noventa maravedís y medio, en que se ha de vender en papel; y dieron licencia para que a este precio se pueda vender, y mandaron que esta tasa se ponga al principio del dicho libro, y no se pueda vender sin ella. Y, para que dello conste, di la presente en Valladolid, a veinte días del mes de deciembre de mil y seiscientos y cuatro años.

#### Sentence Segments

- `0`: Yo, Juan Gallo de Andrada, escribano de Cámara del Rey nuestro señor, de los que residen en su Consejo, certifico y doy fe que, habiendo visto por los señores dél un libro intitulado El ingenioso hidalgo de la Mancha, compuesto por Miguel de Cervantes Saavedra, tasaron cada pliego del dicho libro a tres maravedís y medio; el cual tiene ochenta y tres pliegos, que al dicho precio monta el dicho libro docientos y noventa maravedís y medio, en que se ha de vender en papel; y dieron licencia para que a este precio se pueda vender, y mandaron que esta tasa se ponga al principio del dicho libro, y no se pueda vender sin ella.
- `1`: Y, para que dello conste, di la presente en Valladolid, a veinte días del mes de deciembre de mil y seiscientos y cuatro años.

#### CFI Roundtrip

Yo, Juan Gallo de Andrada, escribano de Cámara del Rey nuestro señor, de los que residen en su Consejo, certifico y doy fe que, habiendo visto por los señores dél un libro intitulado El ingenioso hidalgo de la Mancha, compuesto por Miguel de Cervantes Saavedra, tasaron cada pliego del dicho libro a tres maravedís y medio; el cual tiene ochenta y tres pliegos, que al dicho precio monta el dicho libro docientos y noventa maravedís y medio, en que se ha de vender en papel; y dieron licencia para que a este precio se pueda vender, y mandaron que esta tasa se ponga al principio del dicho libro, y no se pueda vender sin ella. Y, para que dello conste, di la presente en Valladolid, a veinte días del mes de deciembre de mil y seiscientos y cuatro años.

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*[4]/*/*` Yo, Juan Gallo de Andrada, escribano de Cámara del Rey nuestro señor, de los que
- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*[4]/*/*/*/*` libro, y no se pueda vender sin ella. Y, para que dello conste, di la presente e

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
