# EPUB Extraction Audit

- Book: `Don Quijote de la Mancha (Edicion del IV Centenario) (Spanish Edition) (Miguel de Cervantes, Real Academia Española) (z-library.sk, 1lib.sk, z-lib.sk).epub`
- Seed: `20261020`
- Sample count: `5`
- Test type: `normal`
- Granularity: `sentence`
- Debug metadata: `on`

## Samples

### Sample 1

- Chapter / Paragraph: `21` / `129`
- Document: `11_split_19.xhtml`
- XPath: `/*/*[2]/*[265]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre2">
      <span>  <span class="ts3">A lo que don Quijote respondió:</span></span>
    </p>
```

#### Extracted Text

A lo que don Quijote respondió:

#### Sentence Segments

- `0`: A lo que don Quijote respondió:

#### CFI Roundtrip

A lo que don Quijote respondió:

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*[265]/*/*` A lo que don Quijote respondió:

#### Reviewer Notes

- Pending external review.

### Sample 2

- Chapter / Paragraph: `15` / `168`
- Document: `11_split_13.xhtml`
- XPath: `/*/*[2]/*/*[349]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre2"><span>  <span class="ts3">En acabando de decir su glosa don Lorenzo, se
levantó en pie don Quijote, y, en voz levantada, que parecía grito, asiendo con
su mano la derecha de don Lorenzo, dijo:</span></span></p>
```

#### Extracted Text

En acabando de decir su glosa don Lorenzo, se levantó en pie don Quijote, y, en voz levantada, que parecía grito, asiendo con su mano la derecha de don Lorenzo, dijo:

#### Sentence Segments

- `0`: En acabando de decir su glosa don Lorenzo, se levantó en pie don Quijote, y, en voz levantada, que parecía grito, asiendo con su mano la derecha de don Lorenzo, dijo:

#### CFI Roundtrip

En acabando de decir su glosa don Lorenzo, se levantó en pie don Quijote, y, en voz levantada, que parecía grito, asiendo con su mano la derecha de don Lorenzo, dijo:

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*[349]/*/*` En acabando de decir su glosa don Lorenzo, se levantó en pie don Quijote, y, en 

#### Reviewer Notes

- Pending external review.

### Sample 3

- Chapter / Paragraph: `21` / `320`
- Document: `11_split_19.xhtml`
- XPath: `/*/*[2]/*[654]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre2">
      <span>  <span class="ts3">-Déjese deso, señor -dijo Sancho-: viva la
gallina, aunque con su pepita, que hoy por ti y mañana por mí; y en estas cosas
de encuentros y porrazos no hay tomarles tiento alguno, pues el que hoy cae
puede levantarse mañana, si no es que se quiere estar en la cama; quiero decir
que se deje desmayar, sin cobrar nuevos bríos para nuevas pendencias. Y
levántese vuestra merced agora para recebir a don Gregorio, que me parece que
anda la gente alborotada, y ya debe de estar en casa.</span></span>
    </p>
```

#### Extracted Text

-Déjese deso, señor -dijo Sancho-: viva la gallina, aunque con su pepita, que hoy por ti y mañana por mí; y en estas cosas de encuentros y porrazos no hay tomarles tiento alguno, pues el que hoy cae puede levantarse mañana, si no es que se quiere estar en la cama; quiero decir que se deje desmayar, sin cobrar nuevos bríos para nuevas pendencias. Y levántese vuestra merced agora para recebir a don Gregorio, que me parece que anda la gente alborotada, y ya debe de estar en casa.

#### Sentence Segments

- `0`: -Déjese deso, señor -dijo Sancho-: viva la gallina, aunque con su pepita, que hoy por ti y mañana por mí; y en estas cosas de encuentros y porrazos no hay tomarles tiento alguno, pues el que hoy cae puede levantarse mañana, si no es que se quiere estar en la cama; quiero decir que se deje desmayar, sin cobrar nuevos bríos para nuevas pendencias.
- `1`: Y levántese vuestra merced agora para recebir a don Gregorio, que me parece que anda la gente alborotada, y ya debe de estar en casa.

#### CFI Roundtrip

-Déjese deso, señor -dijo Sancho-: viva la gallina, aunque con su pepita, que hoy por ti y mañana por mí; y en estas cosas de encuentros y porrazos no hay tomarles tiento alguno, pues el que hoy cae puede levantarse mañana, si no es que se quiere estar en la cama; quiero decir que se deje desmayar, sin cobrar nuevos bríos para nuevas pendencias. Y levántese vuestra merced agora para recebir a don Gregorio, que me parece que anda la gente alborotada, y ya debe de estar en casa.

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*[654]/*/*` -Déjese deso, señor -dijo Sancho-: viva la gallina, aunque con su pepita, que ho

#### Reviewer Notes

- Pending external review.

### Sample 4

- Chapter / Paragraph: `9` / `257`
- Document: `11_split_7.xhtml`
- XPath: `/*/*[2]/*[279]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre2">
      <span>  <span class="ts3">Poco más quedaba por leer de la novela,
cuando del caramanchón donde reposaba don Quijote salió Sancho Panza todo
alborotado, diciendo a voces:</span></span>
    </p>
```

#### Extracted Text

Poco más quedaba por leer de la novela, cuando del caramanchón donde reposaba don Quijote salió Sancho Panza todo alborotado, diciendo a voces:

#### Sentence Segments

- `0`: Poco más quedaba por leer de la novela, cuando del caramanchón donde reposaba don Quijote salió Sancho Panza todo alborotado, diciendo a voces:

#### CFI Roundtrip

Poco más quedaba por leer de la novela, cuando del caramanchón donde reposaba don Quijote salió Sancho Panza todo alborotado, diciendo a voces:

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*[279]/*/*` Poco más quedaba por leer de la novela, cuando del caramanchón donde reposaba do

#### Reviewer Notes

- Pending external review.

### Sample 5

- Chapter / Paragraph: `20` / `277`
- Document: `11_split_18.xhtml`
- XPath: `/*/*[2]/*[570]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre2">
      <span>  <span class="ts3">Tú llevas, ¡llevar impío!,</span></span>
    </p>
```

#### Extracted Text

Tú llevas, ¡llevar impío!,

#### Sentence Segments

- `0`: Tú llevas, ¡llevar impío!
- `1`: ,

#### CFI Roundtrip

Tú llevas, ¡llevar impío!,

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*[570]/*/*` Tú llevas, ¡llevar impío!,

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
