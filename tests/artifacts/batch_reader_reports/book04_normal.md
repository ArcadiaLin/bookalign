# EPUB Extraction Audit

- Book: `Marianela (Benito Pérez Galdós) (z-library.sk, 1lib.sk, z-lib.sk).epub`
- Seed: `20261040`
- Sample count: `5`
- Test type: `normal`
- Granularity: `sentence`
- Debug metadata: `on`

## Samples

### Sample 1

- Chapter / Paragraph: `8` / `9`
- Document: `Text/Section0005.xhtml`
- XPath: `/*/*[2]/*[12]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">Parecía tener veinte años, y su cuerpo sólido y airoso, con admirables proporciones construido, era digno en todo de la sin igual cabeza que sustentaba. Jamás se vio incorrección más lastimosa de la Naturaleza, que la que tan acabado tipo de la humana forma representaba, recibiendo por una parte admirables dones y siendo privado por otra de la facultad que más comunica al hombre con sus semejantes y con el maravilloso conjunto de todo lo creado. Era tal la incorrección, que aquellos prodigiosos dones quedaban como inútiles, del mismo modo que si al ser creadas todas las cosas hubiéralas dejado el Hacedor a oscuras, para que no pudieran recrearse en sus propios encantos. Para que la imperfección ¡ira de Dios! fuese más manifiesta, había recibido el joven portentosa luz interior, un entendimiento de primer orden. Esto y carecer de la facultad de percibir la idea visible, que es la forma, siendo al mismo tiempo divino como un ángel, hermoso como un hombre y ciego como un vegetal, era fuerte cosa ciertamente. No comprendemos ¡ay!, el secreto de estas horrendas incorrecciones. Si lo comprendiéramos, se abrirían para nosotros las puertas que ocultan primordiales misterios del orden moral y del orden físico; comprenderíamos el inmenso misterio de la desgracia, del mal, de la muerte, y podríamos medir la perpetua sombra que sin cesar sigue al bien y a la vida.</p>
```

#### Extracted Text

Parecía tener veinte años, y su cuerpo sólido y airoso, con admirables proporciones construido, era digno en todo de la sin igual cabeza que sustentaba. Jamás se vio incorrección más lastimosa de la Naturaleza, que la que tan acabado tipo de la humana forma representaba, recibiendo por una parte admirables dones y siendo privado por otra de la facultad que más comunica al hombre con sus semejantes y con el maravilloso conjunto de todo lo creado. Era tal la incorrección, que aquellos prodigiosos dones quedaban como inútiles, del mismo modo que si al ser creadas todas las cosas hubiéralas dejado el Hacedor a oscuras, para que no pudieran recrearse en sus propios encantos. Para que la imperfección ¡ira de Dios! fuese más manifiesta, había recibido el joven portentosa luz interior, un entendimiento de primer orden. Esto y carecer de la facultad de percibir la idea visible, que es la forma, siendo al mismo tiempo divino como un ángel, hermoso como un hombre y ciego como un vegetal, era fuerte cosa ciertamente. No comprendemos ¡ay!, el secreto de estas horrendas incorrecciones. Si lo comprendiéramos, se abrirían para nosotros las puertas que ocultan primordiales misterios del orden moral y del orden físico; comprenderíamos el inmenso misterio de la desgracia, del mal, de la muerte, y podríamos medir la perpetua sombra que sin cesar sigue al bien y a la vida.

#### Sentence Segments

- `0`: Parecía tener veinte años, y su cuerpo sólido y airoso, con admirables proporciones construido, era digno en todo de la sin igual cabeza que sustentaba.
- `1`: Jamás se vio incorrección más lastimosa de la Naturaleza, que la que tan acabado tipo de la humana forma representaba, recibiendo por una parte admirables dones y siendo privado por otra de la facultad que más comunica al hombre con sus semejantes y con el maravilloso conjunto de todo lo creado.
- `2`: Era tal la incorrección, que aquellos prodigiosos dones quedaban como inútiles, del mismo modo que si al ser creadas todas las cosas hubiéralas dejado el Hacedor a oscuras, para que no pudieran recrearse en sus propios encantos.
- `3`: Para que la imperfección ¡ira de Dios! fuese más manifiesta, había recibido el joven portentosa luz interior, un entendimiento de primer orden.
- `4`: Esto y carecer de la facultad de percibir la idea visible, que es la forma, siendo al mismo tiempo divino como un ángel, hermoso como un hombre y ciego como un vegetal, era fuerte cosa ciertamente.
- `5`: No comprendemos ¡ay!, el secreto de estas horrendas incorrecciones.
- `6`: Si lo comprendiéramos, se abrirían para nosotros las puertas que ocultan primordiales misterios del orden moral y del orden físico; comprenderíamos el inmenso misterio de la desgracia, del mal, de la muerte, y podríamos medir la perpetua sombra que sin cesar sigue al bien y a la vida.

#### CFI Roundtrip

Parecía tener veinte años, y su cuerpo sólido y airoso, con admirables proporciones construido, era digno en todo de la sin igual cabeza que sustentaba. Jamás se vio incorrección más lastimosa de la Naturaleza, que la que tan acabado tipo de la humana forma representaba, recibiendo por una parte admirables dones y siendo privado por otra de la facultad que más comunica al hombre con sus semejantes y con el maravilloso conjunto de todo lo creado. Era tal la incorrección, que aquellos prodigiosos dones quedaban como inútiles, del mismo modo que si al ser creadas todas las cosas hubiéralas dejado el Hacedor a oscuras, para que no pudieran recrearse en sus propios encantos. Para que la imperfección ¡ira de Dios! fuese más manifiesta, había recibido el joven portentosa luz interior, un entendimiento de primer orden. Esto y carecer de la facultad de percibir la idea visible, que es la forma, siendo al mismo tiempo divino como un ángel, hermoso como un hombre y ciego como un vegetal, era fuerte cosa ciertamente. No comprendemos ¡ay!, el secreto de estas horrendas incorrecciones. Si lo comprendiéramos, se abrirían para nosotros las puertas que ocultan primordiales misterios del orden moral y del orden físico; comprenderíamos el inmenso misterio de la desgracia, del mal, de la muerte, y podríamos medir la perpetua sombra que sin cesar sigue al bien y a la vida.

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[12]` Parecía tener veinte años, y su cuerpo sólido y airoso, con admirables proporcio

#### Reviewer Notes

- Pending external review.

### Sample 2

- Chapter / Paragraph: `23` / `10`
- Document: `Text/Section0020.xhtml`
- XPath: `/*/*[2]/*[11]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">—Es tu prima Florentina.</p>
```

#### Extracted Text

—Es tu prima Florentina.

#### Sentence Segments

- `0`: —Es tu prima Florentina.

#### CFI Roundtrip

—Es tu prima Florentina.

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[11]` —Es tu prima Florentina.

#### Reviewer Notes

- Pending external review.

### Sample 3

- Chapter / Paragraph: `10` / `22`
- Document: `Text/Section0007.xhtml`
- XPath: `/*/*[2]/*[23]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">—No es eso, tontuela; habla de la belleza en absoluto… ¿no entenderás esto de la belleza ideal?… tampoco lo entiendes… porque has de saber que hay una belleza que no se ve ni se toca, ni se percibe con ningún sentido.</p>
```

#### Extracted Text

—No es eso, tontuela; habla de la belleza en absoluto… ¿no entenderás esto de la belleza ideal?… tampoco lo entiendes… porque has de saber que hay una belleza que no se ve ni se toca, ni se percibe con ningún sentido.

#### Sentence Segments

- `0`: —No es eso, tontuela; habla de la belleza en absoluto… ¿no entenderás esto de la belleza ideal?
- `1`: … tampoco lo entiendes… porque has de saber que hay una belleza que no se ve ni se toca, ni se percibe con ningún sentido.

#### CFI Roundtrip

—No es eso, tontuela; habla de la belleza en absoluto… ¿no entenderás esto de la belleza ideal?… tampoco lo entiendes… porque has de saber que hay una belleza que no se ve ni se toca, ni se percibe con ningún sentido.

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[23]` —No es eso, tontuela; habla de la belleza en absoluto… ¿no entenderás esto de la

#### Reviewer Notes

- Pending external review.

### Sample 4

- Chapter / Paragraph: `20` / `22`
- Document: `Text/Section0017.xhtml`
- XPath: `/*/*[2]/*[23]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">—Vamos allá, vamos al momento. No hace más que preguntar por la señora Nela. Hoy es preciso que estés allí cuando D. Teodoro le levante la venda… Es la cuarta vez… El día de la primera prueba… ¡qué día!, cuando comprendimos que mi primo había nacido a la luz, casi nos morimos de gozo. La primera cara que vio fue la mía… Vamos.</p>
```

#### Extracted Text

—Vamos allá, vamos al momento. No hace más que preguntar por la señora Nela. Hoy es preciso que estés allí cuando D. Teodoro le levante la venda… Es la cuarta vez… El día de la primera prueba… ¡qué día!, cuando comprendimos que mi primo había nacido a la luz, casi nos morimos de gozo. La primera cara que vio fue la mía… Vamos.

#### Sentence Segments

- `0`: —Vamos allá, vamos al momento.
- `1`: No hace más que preguntar por la señora Nela.
- `2`: Hoy es preciso que estés allí cuando D. Teodoro le levante la venda… Es la cuarta vez… El día de la primera prueba… ¡qué día!, cuando comprendimos que mi primo había nacido a la luz, casi nos morimos de gozo.
- `3`: La primera cara que vio fue la mía… Vamos.

#### CFI Roundtrip

—Vamos allá, vamos al momento. No hace más que preguntar por la señora Nela. Hoy es preciso que estés allí cuando D. Teodoro le levante la venda… Es la cuarta vez… El día de la primera prueba… ¡qué día!, cuando comprendimos que mi primo había nacido a la luz, casi nos morimos de gozo. La primera cara que vio fue la mía… Vamos.

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[23]` —Vamos allá, vamos al momento. No hace más que preguntar por la señora Nela. Hoy

#### Reviewer Notes

- Pending external review.

### Sample 5

- Chapter / Paragraph: `4` / `14`
- Document: `Text/Section0001.xhtml`
- XPath: `/*/*[2]/*[17]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">Moviose entonces ligero vientecillo, y Teodoro creyó sentir pasos lejanos en el fondo de aquel desconocido o supuesto abismo que ante sí tenía. Puso atención y no tardó en adquirir la certeza de que alguien andaba por allí. Levantándose, gritó:</p>
```

#### Extracted Text

Moviose entonces ligero vientecillo, y Teodoro creyó sentir pasos lejanos en el fondo de aquel desconocido o supuesto abismo que ante sí tenía. Puso atención y no tardó en adquirir la certeza de que alguien andaba por allí. Levantándose, gritó:

#### Sentence Segments

- `0`: Moviose entonces ligero vientecillo, y Teodoro creyó sentir pasos lejanos en el fondo de aquel desconocido o supuesto abismo que ante sí tenía.
- `1`: Puso atención y no tardó en adquirir la certeza de que alguien andaba por allí.
- `2`: Levantándose, gritó:

#### CFI Roundtrip

Moviose entonces ligero vientecillo, y Teodoro creyó sentir pasos lejanos en el fondo de aquel desconocido o supuesto abismo que ante sí tenía. Puso atención y no tardó en adquirir la certeza de que alguien andaba por allí. Levantándose, gritó:

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*[17]` Moviose entonces ligero vientecillo, y Teodoro creyó sentir pasos lejanos en el 

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
