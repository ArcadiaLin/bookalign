# EPUB Extraction Audit

- Book: `Rimas y leyendas (Gustavo Adolfo Becquer) (z-library.sk, 1lib.sk, z-lib.sk).epub`
- Seed: `20261051`
- Sample count: `5`
- Test type: `complex`
- Granularity: `sentence`
- Debug metadata: `on`

## Samples

### Sample 1

- Chapter / Paragraph: `244` / `7`
- Document: `index_split_243.xhtml`
- XPath: `/*/*[2]/*/*/*/*[7]/*[2]/*[2]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre2"><span class="none">No busquéis su explicación en los </span><span class="none2">Vedas</span><span class="none">, testimonios de las locuras de nuestros mayores, ni en los </span><span class="none2">Puranas</span><span class="none">, donde vestidos con las deslumbradoras galas de la poesía, se acumulan disparates sobre disparates acerca de su origen.</span></p>
```

#### Extracted Text

No busquéis su explicación en los Vedas, testimonios de las locuras de nuestros mayores, ni en los Puranas, donde vestidos con las deslumbradoras galas de la poesía, se acumulan disparates sobre disparates acerca de su origen.

#### Sentence Segments

- `0`: No busquéis su explicación en los Vedas, testimonios de las locuras de nuestros mayores, ni en los Puranas, donde vestidos con las deslumbradoras galas de la poesía, se acumulan disparates sobre disparates acerca de su origen.

#### CFI Roundtrip

No busquéis su explicación en los Vedas, testimonios de las locuras de nuestros mayores, ni en los Puranas, donde vestidos con las deslumbradoras galas de la poesía, se acumulan disparates sobre disparates acerca de su origen.

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*/*/*[7]/*[2]/*[2]/*[1]` No busquéis su explicación en los
- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*/*/*[7]/*[2]/*[2]/*[2]` Vedas
- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*/*/*[7]/*[2]/*[2]/*[3]` , testimonios de las locuras de nuestros mayores, ni en los
- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*/*/*[7]/*[2]/*[2]/*[4]` Puranas
- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*/*/*[7]/*[2]/*[2]/*[5]` , donde vestidos con las deslumbradoras galas de la poesía, se acumulan disparat

#### Reviewer Notes

- Pending external review.

### Sample 2

- Chapter / Paragraph: `226` / `4`
- Document: `index_split_225.xhtml`
- XPath: `/*/*[2]/*/*/*/*[3]/*[5]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre2">Consecuente con mi manía, repasé los cuadernos, y lo primero que me llamó la atención fue que, aunque en la última página había esta palabra latina, tan vulgar en todas las obras, <span class="none2">finis</span><span class="none">, la verdad era que el </span><span class="none2">Miserere</span><span class="none"> no estaba terminado, porque la música no alcanzaba sino hasta el décimo versículo.</span></p>
```

#### Extracted Text

Consecuente con mi manía, repasé los cuadernos, y lo primero que me llamó la atención fue que, aunque en la última página había esta palabra latina, tan vulgar en todas las obras, finis, la verdad era que el Miserere no estaba terminado, porque la música no alcanzaba sino hasta el décimo versículo.

#### Sentence Segments

- `0`: Consecuente con mi manía, repasé los cuadernos, y lo primero que me llamó la atención fue que, aunque en la última página había esta palabra latina, tan vulgar en todas las obras, finis, la verdad era que el Miserere no estaba terminado, porque la música no alcanzaba sino hasta el décimo versículo.

#### CFI Roundtrip

Consecuente con mi manía, repasé los cuadernos, y lo primero que me llamó la atención fue que, aunque en la última página había esta palabra latina, tan vulgar en todas las obras, finis, la verdad era que el Miserere no estaba terminado, porque la música no alcanzaba sino hasta el décimo versículo.

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*/*/*[3]/*[5]` Consecuente con mi manía, repasé los cuadernos, y lo primero que me llamó la ate
- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*/*/*[3]/*[5]/*[1]` finis
- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*/*/*[3]/*[5]/*[2]` , la verdad era que el
- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*/*/*[3]/*[5]/*[3]` Miserere
- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*/*/*[3]/*[5]/*[4]` no estaba terminado, porque la música no alcanzaba sino hasta el décimo versícul

#### Reviewer Notes

- Pending external review.

### Sample 3

- Chapter / Paragraph: `220` / `18`
- Document: `index_split_219.xhtml`
- XPath: `/*/*[2]/*/*/*/*[5]/*[2]/*[7]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre2"><span class="none">Pero vamos, vecina, vamos a la iglesia, antes que se ponga de bote en bote… que algunas noches como ésta suele llenarse de modo que no cabe ni un grano de trigo… Buena ganga tienen las monjas con su organista… ¿Cuándo se ha visto el convento tan favorecido como ahora?… De las otras comunidades, puedo decir que le han hecho a Maese Pérez proposiciones magníficas; verdad que nada tiene de extraño, pues hasta el señor arzobispo le ha ofrecido montes de oro por llevarle a la catedral… Pero él, nada… Primero dejaría la vida que abandonar su órgano favorito… ¿No conocéis a maese Pérez? Verdad es que sois nueva en el barrio… Pues es un santo varón; pobre, sí, pero limosnero cual no otro… Sin más parientes que su hija ni más amigo que su órgano, pasa su vida entera en velar por la inocencia de la una y componer los registros del otro… ¡Cuidado que el órgano es viejo!… Pues nada, él se da tal maña en arreglarlo y cuidarlo, que suena que es una maravilla… Como le conoce de tal modo, que a tientas… porque no sé si os lo he dicho, pero el pobre señor es ciego de nacimiento… Y ¡con qué paciencia lleva su desgracia!… Cuando le preguntan que cuánto daría por ver, responde: </span><span class="none2">Mucho, pero no tanto como creéis, porque tengo esperanzas. ¿Esperanzas de ver? Sí, y muy pronto</span><span class="none"> —añade sonriéndose como un ángel—; </span><span class="none2">ya cuento setenta y seis años; por muy larga que sea mi vida, pronto veré a Dios…</span>.</p>
```

#### Extracted Text

Pero vamos, vecina, vamos a la iglesia, antes que se ponga de bote en bote… que algunas noches como ésta suele llenarse de modo que no cabe ni un grano de trigo… Buena ganga tienen las monjas con su organista… ¿Cuándo se ha visto el convento tan favorecido como ahora?… De las otras comunidades, puedo decir que le han hecho a Maese Pérez proposiciones magníficas; verdad que nada tiene de extraño, pues hasta el señor arzobispo le ha ofrecido montes de oro por llevarle a la catedral… Pero él, nada… Primero dejaría la vida que abandonar su órgano favorito… ¿No conocéis a maese Pérez? Verdad es que sois nueva en el barrio… Pues es un santo varón; pobre, sí, pero limosnero cual no otro… Sin más parientes que su hija ni más amigo que su órgano, pasa su vida entera en velar por la inocencia de la una y componer los registros del otro… ¡Cuidado que el órgano es viejo!… Pues nada, él se da tal maña en arreglarlo y cuidarlo, que suena que es una maravilla… Como le conoce de tal modo, que a tientas… porque no sé si os lo he dicho, pero el pobre señor es ciego de nacimiento… Y ¡con qué paciencia lleva su desgracia!… Cuando le preguntan que cuánto daría por ver, responde: Mucho, pero no tanto como creéis, porque tengo esperanzas. ¿Esperanzas de ver? Sí, y muy pronto —añade sonriéndose como un ángel—; ya cuento setenta y seis años; por muy larga que sea mi vida, pronto veré a Dios….

#### Sentence Segments

- `0`: Pero vamos, vecina, vamos a la iglesia, antes que se ponga de bote en bote… que algunas noches como ésta suele llenarse de modo que no cabe ni un grano de trigo… Buena ganga tienen las monjas con su organista… ¿Cuándo se ha visto el convento tan favorecido como ahora?
- `1`: … De las otras comunidades, puedo decir que le han hecho a Maese Pérez proposiciones magníficas; verdad que nada tiene de extraño, pues hasta el señor arzobispo le ha ofrecido montes de oro por llevarle a la catedral… Pero él, nada… Primero dejaría la vida que abandonar su órgano favorito… ¿No conocéis a maese Pérez?
- `2`: Verdad es que sois nueva en el barrio… Pues es un santo varón; pobre, sí, pero limosnero cual no otro… Sin más parientes que su hija ni más amigo que su órgano, pasa su vida entera en velar por la inocencia de la una y componer los registros del otro… ¡Cuidado que el órgano es viejo!
- `3`: … Pues nada, él se da tal maña en arreglarlo y cuidarlo, que suena que es una maravilla… Como le conoce de tal modo, que a tientas… porque no sé si os lo he dicho, pero el pobre señor es ciego de nacimiento… Y ¡con qué paciencia lleva su desgracia!
- `4`: … Cuando le preguntan que cuánto daría por ver, responde: Mucho, pero no tanto como creéis, porque tengo esperanzas.
- `5`: ¿Esperanzas de ver?
- `6`: Sí, y muy pronto —añade sonriéndose como un ángel—; ya cuento setenta y seis años; por muy larga que sea mi vida, pronto veré a Dios….

#### CFI Roundtrip

Pero vamos, vecina, vamos a la iglesia, antes que se ponga de bote en bote… que algunas noches como ésta suele llenarse de modo que no cabe ni un grano de trigo… Buena ganga tienen las monjas con su organista… ¿Cuándo se ha visto el convento tan favorecido como ahora?… De las otras comunidades, puedo decir que le han hecho a Maese Pérez proposiciones magníficas; verdad que nada tiene de extraño, pues hasta el señor arzobispo le ha ofrecido montes de oro por llevarle a la catedral… Pero él, nada… Primero dejaría la vida que abandonar su órgano favorito… ¿No conocéis a maese Pérez? Verdad es que sois nueva en el barrio… Pues es un santo varón; pobre, sí, pero limosnero cual no otro… Sin más parientes que su hija ni más amigo que su órgano, pasa su vida entera en velar por la inocencia de la una y componer los registros del otro… ¡Cuidado que el órgano es viejo!… Pues nada, él se da tal maña en arreglarlo y cuidarlo, que suena que es una maravilla… Como le conoce de tal modo, que a tientas… porque no sé si os lo he dicho, pero el pobre señor es ciego de nacimiento… Y ¡con qué paciencia lleva su desgracia!… Cuando le preguntan que cuánto daría por ver, responde: Mucho, pero no tanto como creéis, porque tengo esperanzas. ¿Esperanzas de ver? Sí, y muy pronto —añade sonriéndose como un ángel—; ya cuento setenta y seis años; por muy larga que sea mi vida, pronto veré a Dios….

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*/*/*[5]/*[2]/*[7]/*[1]` Pero vamos, vecina, vamos a la iglesia, antes que se ponga de bote en bote… que 
- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*/*/*[5]/*[2]/*[7]/*[2]` Mucho, pero no tanto como creéis, porque tengo esperanzas. ¿Esperanzas de ver? S
- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*/*/*[5]/*[2]/*[7]/*[3]` —añade sonriéndose como un ángel—;
- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*/*/*[5]/*[2]/*[7]/*[4]` ya cuento setenta y seis años; por muy larga que sea mi vida, pronto veré a Dios
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*/*/*[5]/*[2]/*[7]` .

#### Reviewer Notes

- Pending external review.

### Sample 4

- Chapter / Paragraph: `226` / `17`
- Document: `index_split_225.xhtml`
- XPath: `/*/*[2]/*/*/*/*[5]/*[2]/*[10]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre2"><span class="none">—¿No dije? —murmuró el campesino; y luego prosiguió con una entonación misteriosa—. Ese </span><span class="none2">Miserere</span><span class="none">, que sólo oyen por casualidad los que como yo andan día y noche tras el ganado por entre breñas y peñascales, es toda una historia; una historia muy antigua, pero tan verdadera como al parecer increíble. Es el caso, que en lo más fragoso de esas cordilleras, de montañas que limitan el horizonte del valle, en el fondo del cual se halla la abadía, hubo hace ya muchos años, ¡qué digo muchos años!, muchos siglos, un monasterio famoso; monasterio que, a lo que parece, edificó a sus expensas un señor con los bienes que había de legar a su hijo, al cual desheredó al morir, en pena de sus maldades. Hasta aquí todo fue bueno; pero es el caso que este hijo, que, por lo que se verá más adelante, debió de ser de la piel del diablo, si no era el mismo diablo en persona, sabedor de que sus bienes estaban en poder de los religiosos, y de que su castillo se había transformado en iglesia, reunió a unos cuantos bandoleros, camaradas suyos en la vida de perdición que emprendiera al abandonar la casa de sus padres, y una noche de Jueves Santo, en que los monjes se hallaban en el coro, y en el punto y hora en que iban a comenzar o habían comenzado el </span><span class="none2">Miserere</span><span class="none">, pusieron fuego al monasterio, saquearon la iglesia, y a éste quiero, a aquél no, se dice que no dejaron fraile con vida. Después de esta atrocidad, se marcharon los bandidos y su instigador con ellos, adonde no se sabe, a los profundos tal vez. Las llamas redujeron el monasterio a escombros; de la iglesia aún quedan en pie las ruinas sobre el cóncavo peñón, de donde nace la cascada, que, después de estrellarse de peña en peña, forma el riachuelo que viene a bañar los muros de esta abadía.</span></p>
```

#### Extracted Text

—¿No dije? —murmuró el campesino; y luego prosiguió con una entonación misteriosa—. Ese Miserere, que sólo oyen por casualidad los que como yo andan día y noche tras el ganado por entre breñas y peñascales, es toda una historia; una historia muy antigua, pero tan verdadera como al parecer increíble. Es el caso, que en lo más fragoso de esas cordilleras, de montañas que limitan el horizonte del valle, en el fondo del cual se halla la abadía, hubo hace ya muchos años, ¡qué digo muchos años!, muchos siglos, un monasterio famoso; monasterio que, a lo que parece, edificó a sus expensas un señor con los bienes que había de legar a su hijo, al cual desheredó al morir, en pena de sus maldades. Hasta aquí todo fue bueno; pero es el caso que este hijo, que, por lo que se verá más adelante, debió de ser de la piel del diablo, si no era el mismo diablo en persona, sabedor de que sus bienes estaban en poder de los religiosos, y de que su castillo se había transformado en iglesia, reunió a unos cuantos bandoleros, camaradas suyos en la vida de perdición que emprendiera al abandonar la casa de sus padres, y una noche de Jueves Santo, en que los monjes se hallaban en el coro, y en el punto y hora en que iban a comenzar o habían comenzado el Miserere, pusieron fuego al monasterio, saquearon la iglesia, y a éste quiero, a aquél no, se dice que no dejaron fraile con vida. Después de esta atrocidad, se marcharon los bandidos y su instigador con ellos, adonde no se sabe, a los profundos tal vez. Las llamas redujeron el monasterio a escombros; de la iglesia aún quedan en pie las ruinas sobre el cóncavo peñón, de donde nace la cascada, que, después de estrellarse de peña en peña, forma el riachuelo que viene a bañar los muros de esta abadía.

#### Sentence Segments

- `0`: —¿No dije?
- `1`: —murmuró el campesino; y luego prosiguió con una entonación misteriosa—.
- `2`: Ese Miserere, que sólo oyen por casualidad los que como yo andan día y noche tras el ganado por entre breñas y peñascales, es toda una historia; una historia muy antigua, pero tan verdadera como al parecer increíble.
- `3`: Es el caso, que en lo más fragoso de esas cordilleras, de montañas que limitan el horizonte del valle, en el fondo del cual se halla la abadía, hubo hace ya muchos años, ¡qué digo muchos años!, muchos siglos, un monasterio famoso; monasterio que, a lo que parece, edificó a sus expensas un señor con los bienes que había de legar a su hijo, al cual desheredó al morir, en pena de sus maldades.
- `4`: Hasta aquí todo fue bueno; pero es el caso que este hijo, que, por lo que se verá más adelante, debió de ser de la piel del diablo, si no era el mismo diablo en persona, sabedor de que sus bienes estaban en poder de los religiosos, y de que su castillo se había transformado en iglesia, reunió a unos cuantos bandoleros, camaradas suyos en la vida de perdición que emprendiera al abandonar la casa de sus padres, y una noche de Jueves Santo, en que los monjes se hallaban en el coro, y en el punto y hora en que iban a comenzar o habían comenzado el Miserere, pusieron fuego al monasterio, saquearon la iglesia, y a éste quiero, a aquél no, se dice que no dejaron fraile con vida.
- `5`: Después de esta atrocidad, se marcharon los bandidos y su instigador con ellos, adonde no se sabe, a los profundos tal vez.
- `6`: Las llamas redujeron el monasterio a escombros; de la iglesia aún quedan en pie las ruinas sobre el cóncavo peñón, de donde nace la cascada, que, después de estrellarse de peña en peña, forma el riachuelo que viene a bañar los muros de esta abadía.

#### CFI Roundtrip

—¿No dije? —murmuró el campesino; y luego prosiguió con una entonación misteriosa—. Ese Miserere, que sólo oyen por casualidad los que como yo andan día y noche tras el ganado por entre breñas y peñascales, es toda una historia; una historia muy antigua, pero tan verdadera como al parecer increíble. Es el caso, que en lo más fragoso de esas cordilleras, de montañas que limitan el horizonte del valle, en el fondo del cual se halla la abadía, hubo hace ya muchos años, ¡qué digo muchos años!, muchos siglos, un monasterio famoso; monasterio que, a lo que parece, edificó a sus expensas un señor con los bienes que había de legar a su hijo, al cual desheredó al morir, en pena de sus maldades. Hasta aquí todo fue bueno; pero es el caso que este hijo, que, por lo que se verá más adelante, debió de ser de la piel del diablo, si no era el mismo diablo en persona, sabedor de que sus bienes estaban en poder de los religiosos, y de que su castillo se había transformado en iglesia, reunió a unos cuantos bandoleros, camaradas suyos en la vida de perdición que emprendiera al abandonar la casa de sus padres, y una noche de Jueves Santo, en que los monjes se hallaban en el coro, y en el punto y hora en que iban a comenzar o habían comenzado el Miserere, pusieron fuego al monasterio, saquearon la iglesia, y a éste quiero, a aquél no, se dice que no dejaron fraile con vida. Después de esta atrocidad, se marcharon los bandidos y su instigador con ellos, adonde no se sabe, a los profundos tal vez. Las llamas redujeron el monasterio a escombros; de la iglesia aún quedan en pie las ruinas sobre el cóncavo peñón, de donde nace la cascada, que, después de estrellarse de peña en peña, forma el riachuelo que viene a bañar los muros de esta abadía.

#### Debug Spans

- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*/*/*[5]/*[2]/*[10]/*[1]` —¿No dije? —murmuró el campesino; y luego prosiguió con una entonación misterios
- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*/*/*[5]/*[2]/*[10]/*[2]` Miserere
- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*/*/*[5]/*[2]/*[10]/*[3]` , que sólo oyen por casualidad los que como yo andan día y noche tras el ganado 
- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*/*/*[5]/*[2]/*[10]/*[4]` Miserere
- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*/*/*[5]/*[2]/*[10]/*[5]` , pusieron fuego al monasterio, saquearon la iglesia, y a éste quiero, a aquél n

#### Reviewer Notes

- Pending external review.

### Sample 5

- Chapter / Paragraph: `226` / `27`
- Document: `index_split_225.xhtml`
- XPath: `/*/*[2]/*/*/*/*[5]/*[2]/*[20]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" class="calibre2">—¿A dónde voy? A oír esa maravillosa música, a oír el grande, el verdadero <span class="none2">Miserere</span><span class="none">, el </span><span class="none2">Miserere</span><span class="none"> de los que vuelven al mundo después de muertos, y saben lo que es morir en el pecado.</span></p>
```

#### Extracted Text

—¿A dónde voy? A oír esa maravillosa música, a oír el grande, el verdadero Miserere, el Miserere de los que vuelven al mundo después de muertos, y saben lo que es morir en el pecado.

#### Sentence Segments

- `0`: —¿A dónde voy?
- `1`: A oír esa maravillosa música, a oír el grande, el verdadero Miserere, el Miserere de los que vuelven al mundo después de muertos, y saben lo que es morir en el pecado.

#### CFI Roundtrip

—¿A dónde voy? A oír esa maravillosa música, a oír el grande, el verdadero Miserere, el Miserere de los que vuelven al mundo después de muertos, y saben lo que es morir en el pecado.

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*/*/*[5]/*[2]/*[20]` —¿A dónde voy? A oír esa maravillosa música, a oír el grande, el verdadero
- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*/*/*[5]/*[2]/*[20]/*[1]` Miserere
- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*/*/*[5]/*[2]/*[20]/*[2]` , el
- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*/*/*[5]/*[2]/*[20]/*[3]` Miserere
- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*/*/*[5]/*[2]/*[20]/*[4]` de los que vuelven al mundo después de muertos, y saben lo que es morir en el pe

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
