# EPUB Extraction Audit

- Book: `Marianela (Benito Pérez Galdós) (z-library.sk, 1lib.sk, z-lib.sk).epub`
- Seed: `20261041`
- Sample count: `4`
- Test type: `complex`
- Granularity: `sentence`
- Debug metadata: `on`

## Samples

### Sample 1

- Chapter / Paragraph: `26` / `3`
- Document: `Text/autor.xhtml`
- XPath: `/*/*[2]/*[3]/*[4]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">Durante este período también escribió novelas como <i>Doña Perfecta</i> (1876) o <i>La familia de León Roch</i> (1878), obra que cierra una etapa literaria señalada por el mismo autor, quien dividió su obra novelada entre «novelas del primer período» y «novelas contemporáneas», que se inician en 1881, con la publicación de <i>La desheredada</i>. Según confesión del propio escritor, con la lectura de <i>La taberna</i>, de Zola, descubrió el naturalismo, lo cual cambió la <i>manière</i> de sus novelas, que incorporarán a partir de entonces métodos propios del naturalismo, como es la observación científica de la realidad a través, sobre todo, del análisis psicológico, aunque matizado siempre por el sentido del humor.</p>
```

#### Extracted Text

Durante este período también escribió novelas como Doña Perfecta (1876) o La familia de León Roch (1878), obra que cierra una etapa literaria señalada por el mismo autor, quien dividió su obra novelada entre «novelas del primer período» y «novelas contemporáneas», que se inician en 1881, con la publicación de La desheredada. Según confesión del propio escritor, con la lectura de La taberna, de Zola, descubrió el naturalismo, lo cual cambió la manière de sus novelas, que incorporarán a partir de entonces métodos propios del naturalismo, como es la observación científica de la realidad a través, sobre todo, del análisis psicológico, aunque matizado siempre por el sentido del humor.

#### Sentence Segments

- `0`: Durante este período también escribió novelas como Doña Perfecta (1876) o La familia de León Roch (1878), obra que cierra una etapa literaria señalada por el mismo autor, quien dividió su obra novelada entre «novelas del primer período» y «novelas contemporáneas», que se inician en 1881, con la publicación de La desheredada.
- `1`: Según confesión del propio escritor, con la lectura de La taberna, de Zola, descubrió el naturalismo, lo cual cambió la manière de sus novelas, que incorporarán a partir de entonces métodos propios del naturalismo, como es la observación científica de la realidad a través, sobre todo, del análisis psicológico, aunque matizado siempre por el sentido del humor.

#### CFI Roundtrip

Durante este período también escribió novelas como Doña Perfecta (1876) o La familia de León Roch (1878), obra que cierra una etapa literaria señalada por el mismo autor, quien dividió su obra novelada entre «novelas del primer período» y «novelas contemporáneas», que se inician en 1881, con la publicación de La desheredada. Según confesión del propio escritor, con la lectura de La taberna, de Zola, descubrió el naturalismo, lo cual cambió la manière de sus novelas, que incorporarán a partir de entonces métodos propios del naturalismo, como es la observación científica de la realidad a través, sobre todo, del análisis psicológico, aunque matizado siempre por el sentido del humor.

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[3]/*[4]` Durante este período también escribió novelas como
- `i` `KEEP_NORMAL` `keep-italic` `/*/*[2]/*[3]/*[4]/*[1]` Doña Perfecta
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[3]/*[4]` (1876) o
- `i` `KEEP_NORMAL` `keep-italic` `/*/*[2]/*[3]/*[4]/*[2]` La familia de León Roch
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[3]/*[4]` (1878), obra que cierra una etapa literaria señalada por el mismo autor, quien d
- `i` `KEEP_NORMAL` `keep-italic` `/*/*[2]/*[3]/*[4]/*[3]` La desheredada
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[3]/*[4]` . Según confesión del propio escritor, con la lectura de
- `i` `KEEP_NORMAL` `keep-italic` `/*/*[2]/*[3]/*[4]/*[4]` La taberna
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[3]/*[4]` , de Zola, descubrió el naturalismo, lo cual cambió la
- `i` `KEEP_NORMAL` `keep-italic` `/*/*[2]/*[3]/*[4]/*[5]` manière
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[3]/*[4]` de sus novelas, que incorporarán a partir de entonces métodos propios del natura

#### Reviewer Notes

- Pending external review.

### Sample 2

- Chapter / Paragraph: `25` / `9`
- Document: `Text/Section0022.xhtml`
- XPath: `/*/*[2]/*[13]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">«Lo que más sorprende en Aldeacorba es el espléndido sepulcro erigido en el cementerio, sobre la tumba de una ilustre joven, célebre en aquel país por su hermosura. <i>Doña Mariquita Manuela Téllez</i> perteneció a una de las familias más nobles y acaudaladas de Cantabria, la familia de Téllez Girón y de Trastamara. De un carácter <i>espiritual</i>, poético y algo caprichoso, tuvo el antojo (<i>take a fancy</i>) de andar por los caminos tocando la guitarra y cantando odas de Calderón, y se vestía de andrajos para confundirse con la turba de mendigos, buscones, <i>trovadores</i>, toreros, frailes, hidalgos, gitanos y <i>muleteros</i>, que en las <i>kermesas</i> forman esa abigarrada plebe española que subsiste y subsistirá siempre, independiente y pintoresca, a pesar de los <i>rails</i> y de los periódicos que han empezado a introducirse en la península occidental. El <i>abad</i> de Villamojada lloraba hablándonos de los caprichos, de las virtudes y de la belleza de la aristocrática ricahembra, la cual sabía presentarse en los saraos, fiestas y <i>cañas</i> de Madrid con el porte (<i>deportment</i>) más aristocrático. Es incalculable el número de bellos <i>romanceros</i>, sonetos y madrigales compuestos en honor de esta gentil doncella por todos los poetas españoles».</p>
```

#### Extracted Text

«Lo que más sorprende en Aldeacorba es el espléndido sepulcro erigido en el cementerio, sobre la tumba de una ilustre joven, célebre en aquel país por su hermosura. Doña Mariquita Manuela Téllez perteneció a una de las familias más nobles y acaudaladas de Cantabria, la familia de Téllez Girón y de Trastamara. De un carácter espiritual, poético y algo caprichoso, tuvo el antojo (take a fancy) de andar por los caminos tocando la guitarra y cantando odas de Calderón, y se vestía de andrajos para confundirse con la turba de mendigos, buscones, trovadores, toreros, frailes, hidalgos, gitanos y muleteros, que en las kermesas forman esa abigarrada plebe española que subsiste y subsistirá siempre, independiente y pintoresca, a pesar de los rails y de los periódicos que han empezado a introducirse en la península occidental. El abad de Villamojada lloraba hablándonos de los caprichos, de las virtudes y de la belleza de la aristocrática ricahembra, la cual sabía presentarse en los saraos, fiestas y cañas de Madrid con el porte (deportment) más aristocrático. Es incalculable el número de bellos romanceros, sonetos y madrigales compuestos en honor de esta gentil doncella por todos los poetas españoles».

#### Sentence Segments

- `0`: «Lo que más sorprende en Aldeacorba es el espléndido sepulcro erigido en el cementerio, sobre la tumba de una ilustre joven, célebre en aquel país por su hermosura. Doña Mariquita Manuela Téllez perteneció a una de las familias más nobles y acaudaladas de Cantabria, la familia de Téllez Girón y de Trastamara. De un carácter espiritual, poético y algo caprichoso, tuvo el antojo (take a fancy) de andar por los caminos tocando la guitarra y cantando odas de Calderón, y se vestía de andrajos para confundirse con la turba de mendigos, buscones, trovadores, toreros, frailes, hidalgos, gitanos y muleteros, que en las kermesas forman esa abigarrada plebe española que subsiste y subsistirá siempre, independiente y pintoresca, a pesar de los rails y de los periódicos que han empezado a introducirse en la península occidental. El abad de Villamojada lloraba hablándonos de los caprichos, de las virtudes y de la belleza de la aristocrática ricahembra, la cual sabía presentarse en los saraos, fiestas y cañas de Madrid con el porte (deportment) más aristocrático. Es incalculable el número de bellos romanceros, sonetos y madrigales compuestos en honor de esta gentil doncella por todos los poetas españoles».

#### CFI Roundtrip

«Lo que más sorprende en Aldeacorba es el espléndido sepulcro erigido en el cementerio, sobre la tumba de una ilustre joven, célebre en aquel país por su hermosura. Doña Mariquita Manuela Téllez perteneció a una de las familias más nobles y acaudaladas de Cantabria, la familia de Téllez Girón y de Trastamara. De un carácter espiritual, poético y algo caprichoso, tuvo el antojo (take a fancy) de andar por los caminos tocando la guitarra y cantando odas de Calderón, y se vestía de andrajos para confundirse con la turba de mendigos, buscones, trovadores, toreros, frailes, hidalgos, gitanos y muleteros, que en las kermesas forman esa abigarrada plebe española que subsiste y subsistirá siempre, independiente y pintoresca, a pesar de los rails y de los periódicos que han empezado a introducirse en la península occidental. El abad de Villamojada lloraba hablándonos de los caprichos, de las virtudes y de la belleza de la aristocrática ricahembra, la cual sabía presentarse en los saraos, fiestas y cañas de Madrid con el porte (deportment) más aristocrático. Es incalculable el número de bellos romanceros, sonetos y madrigales compuestos en honor de esta gentil doncella por todos los poetas españoles».

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[13]` «Lo que más sorprende en Aldeacorba es el espléndido sepulcro erigido en el ceme
- `i` `KEEP_NORMAL` `keep-italic` `/*/*[2]/*[13]/*[1]` Doña Mariquita Manuela Téllez
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[13]` perteneció a una de las familias más nobles y acaudaladas de Cantabria, la famil
- `i` `KEEP_NORMAL` `keep-italic` `/*/*[2]/*[13]/*[2]` espiritual
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[13]` , poético y algo caprichoso, tuvo el antojo (
- `i` `KEEP_NORMAL` `keep-italic` `/*/*[2]/*[13]/*[3]` take a fancy
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[13]` ) de andar por los caminos tocando la guitarra y cantando odas de Calderón, y se
- `i` `KEEP_NORMAL` `keep-italic` `/*/*[2]/*[13]/*[4]` trovadores
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[13]` , toreros, frailes, hidalgos, gitanos y
- `i` `KEEP_NORMAL` `keep-italic` `/*/*[2]/*[13]/*[5]` muleteros
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[13]` , que en las
- `i` `KEEP_NORMAL` `keep-italic` `/*/*[2]/*[13]/*[6]` kermesas
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[13]` forman esa abigarrada plebe española que subsiste y subsistirá siempre, independ
- `i` `KEEP_NORMAL` `keep-italic` `/*/*[2]/*[13]/*[7]` rails
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[13]` y de los periódicos que han empezado a introducirse en la península occidental. 
- `i` `KEEP_NORMAL` `keep-italic` `/*/*[2]/*[13]/*[8]` abad
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[13]` de Villamojada lloraba hablándonos de los caprichos, de las virtudes y de la bel
- `i` `KEEP_NORMAL` `keep-italic` `/*/*[2]/*[13]/*[9]` cañas
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[13]` de Madrid con el porte (
- `i` `KEEP_NORMAL` `keep-italic` `/*/*[2]/*[13]/*[10]` deportment
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[13]` ) más aristocrático. Es incalculable el número de bellos
- `i` `KEEP_NORMAL` `keep-italic` `/*/*[2]/*[13]/*[11]` romanceros
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[13]` , sonetos y madrigales compuestos en honor de esta gentil doncella por todos los

#### Reviewer Notes

- Pending external review.

### Sample 3

- Chapter / Paragraph: `26` / `6`
- Document: `Text/autor.xhtml`
- XPath: `/*/*[2]/*[3]/*[7]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">Un año después, coincidiendo con la publicación de una de sus obras más aplaudidas por la crítica, <i>Ángel Guerra</i>, ingresó, tras un primer intento fallido en 1883, en la Real Academia Española. Durante este período escribió algunas novelas más experimentales, en las que, en un intento extremo de realismo, utilizó íntegramente el diálogo, como en <i>Realidad</i> (1892), <i>La loca de la casa</i> (1892) y <i>El abuelo</i> (1897), algunas de ellas adaptadas también al teatro. El éxito teatral más importante, sin embargo, lo obtuvo con la representación de <i>Electra</i> (1901), obra polémica que provocó numerosas manifestaciones y protestas por su contenido anticlerical.</p>
```

#### Extracted Text

Un año después, coincidiendo con la publicación de una de sus obras más aplaudidas por la crítica, Ángel Guerra, ingresó, tras un primer intento fallido en 1883, en la Real Academia Española. Durante este período escribió algunas novelas más experimentales, en las que, en un intento extremo de realismo, utilizó íntegramente el diálogo, como en Realidad (1892), La loca de la casa (1892) y El abuelo (1897), algunas de ellas adaptadas también al teatro. El éxito teatral más importante, sin embargo, lo obtuvo con la representación de Electra (1901), obra polémica que provocó numerosas manifestaciones y protestas por su contenido anticlerical.

#### Sentence Segments

- `0`: Un año después, coincidiendo con la publicación de una de sus obras más aplaudidas por la crítica, Ángel Guerra, ingresó, tras un primer intento fallido en 1883, en la Real Academia Española.
- `1`: Durante este período escribió algunas novelas más experimentales, en las que, en un intento extremo de realismo, utilizó íntegramente el diálogo, como en Realidad (1892), La loca de la casa (1892) y El abuelo (1897), algunas de ellas adaptadas también al teatro.
- `2`: El éxito teatral más importante, sin embargo, lo obtuvo con la representación de Electra (1901), obra polémica que provocó numerosas manifestaciones y protestas por su contenido anticlerical.

#### CFI Roundtrip

Un año después, coincidiendo con la publicación de una de sus obras más aplaudidas por la crítica, Ángel Guerra, ingresó, tras un primer intento fallido en 1883, en la Real Academia Española. Durante este período escribió algunas novelas más experimentales, en las que, en un intento extremo de realismo, utilizó íntegramente el diálogo, como en Realidad (1892), La loca de la casa (1892) y El abuelo (1897), algunas de ellas adaptadas también al teatro. El éxito teatral más importante, sin embargo, lo obtuvo con la representación de Electra (1901), obra polémica que provocó numerosas manifestaciones y protestas por su contenido anticlerical.

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[3]/*[7]` Un año después, coincidiendo con la publicación de una de sus obras más aplaudid
- `i` `KEEP_NORMAL` `keep-italic` `/*/*[2]/*[3]/*[7]/*[1]` Ángel Guerra
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[3]/*[7]` , ingresó, tras un primer intento fallido en 1883, en la Real Academia Española.
- `i` `KEEP_NORMAL` `keep-italic` `/*/*[2]/*[3]/*[7]/*[2]` Realidad
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[3]/*[7]` (1892),
- `i` `KEEP_NORMAL` `keep-italic` `/*/*[2]/*[3]/*[7]/*[3]` La loca de la casa
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[3]/*[7]` (1892) y
- `i` `KEEP_NORMAL` `keep-italic` `/*/*[2]/*[3]/*[7]/*[4]` El abuelo
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[3]/*[7]` (1897), algunas de ellas adaptadas también al teatro. El éxito teatral más impor
- `i` `KEEP_NORMAL` `keep-italic` `/*/*[2]/*[3]/*[7]/*[5]` Electra
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[3]/*[7]` (1901), obra polémica que provocó numerosas manifestaciones y protestas por su c

#### Reviewer Notes

- Pending external review.

### Sample 4

- Chapter / Paragraph: `26` / `4`
- Document: `Text/autor.xhtml`
- XPath: `/*/*[2]/*[3]/*[5]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">Bajo esta nueva <i>manière</i> escribió alguna de sus obras más importantes, como <i>Fortunata y Jacinta</i>, y <i>Tristana</i>. Todas ellas forman un conjunto homogéneo en cuanto a identidad de personajes y recreación de un determinado ambiente: el Madrid de Isabel <small>II</small> y la Restauración, en el que Galdós era una personalidad importante, respetada tanto literaria como políticamente.</p>
```

#### Extracted Text

Bajo esta nueva manière escribió alguna de sus obras más importantes, como Fortunata y Jacinta, y Tristana. Todas ellas forman un conjunto homogéneo en cuanto a identidad de personajes y recreación de un determinado ambiente: el Madrid de Isabel II y la Restauración, en el que Galdós era una personalidad importante, respetada tanto literaria como políticamente.

#### Sentence Segments

- `0`: Bajo esta nueva manière escribió alguna de sus obras más importantes, como Fortunata y Jacinta, y Tristana.
- `1`: Todas ellas forman un conjunto homogéneo en cuanto a identidad de personajes y recreación de un determinado ambiente: el Madrid de Isabel II y la Restauración, en el que Galdós era una personalidad importante, respetada tanto literaria como políticamente.

#### CFI Roundtrip

Bajo esta nueva manière escribió alguna de sus obras más importantes, como Fortunata y Jacinta, y Tristana. Todas ellas forman un conjunto homogéneo en cuanto a identidad de personajes y recreación de un determinado ambiente: el Madrid de Isabel II y la Restauración, en el que Galdós era una personalidad importante, respetada tanto literaria como políticamente.

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[3]/*[5]` Bajo esta nueva
- `i` `KEEP_NORMAL` `keep-italic` `/*/*[2]/*[3]/*[5]/*[1]` manière
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[3]/*[5]` escribió alguna de sus obras más importantes, como
- `i` `KEEP_NORMAL` `keep-italic` `/*/*[2]/*[3]/*[5]/*[2]` Fortunata y Jacinta
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[3]/*[5]` , y
- `i` `KEEP_NORMAL` `keep-italic` `/*/*[2]/*[3]/*[5]/*[3]` Tristana
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[3]/*[5]` . Todas ellas forman un conjunto homogéneo en cuanto a identidad de personajes y
- `small` `KEEP_NORMAL` `` `/*/*[2]/*[3]/*[5]/*[4]` II
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[3]/*[5]` y la Restauración, en el que Galdós era una personalidad importante, respetada t

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
