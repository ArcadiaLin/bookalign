# EPUB Extraction Audit

- Book: `金閣寺 (三島由紀夫) (Z-Library).epub`
- Seed: `20261120`
- Sample count: `5`
- Test type: `normal`
- Granularity: `sentence`
- Debug metadata: `on`

## Samples

### Sample 1

- Chapter / Paragraph: `18` / `52`
- Document: `xhtml/0017.xhtml`
- XPath: `/*/*[2]/*/*[34]/*[2]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">十二月、『橋づくし』（文芸春秋）</p>
```

#### Extracted Text

十二月、『橋づくし』（文芸春秋）

#### Sentence Segments

- `0`: 十二月、『橋づくし』（文芸春秋）

#### CFI Roundtrip

十二月、『橋づくし』（文芸春秋）

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[34]/*[2]` 十二月、『橋づくし』（文芸春秋）

#### Reviewer Notes

- Pending external review.

### Sample 2

- Chapter / Paragraph: `11` / `22`
- Document: `xhtml/0010.xhtml`
- XPath: `/*/*[2]/*/*[32]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">　さて、私はいつのまにか犬に導かれていた。犬は見失われるかと思うと又現われた。河原町通へ抜ける道を曲った。私はこうして新京極よりもいくらか暗い電車通りの歩道へ出た。犬の姿は消えた。立止った私は<span class="em-sesame">と</span>見<span class="em-sesame">こう</span>見した。車道のきわまで出て、犬のゆくえを目でたずねていた。</p>
```

#### Extracted Text

さて、私はいつのまにか犬に導かれていた。犬は見失われるかと思うと又現われた。河原町通へ抜ける道を曲った。私はこうして新京極よりもいくらか暗い電車通りの歩道へ出た。犬の姿は消えた。立止った私はと見こう見した。車道のきわまで出て、犬のゆくえを目でたずねていた。

#### Sentence Segments

- `0`: さて、私はいつのまにか犬に導かれていた。
- `1`: 犬は見失われるかと思うと又現われた。
- `2`: 河原町通へ抜ける道を曲った。
- `3`: 私はこうして新京極よりもいくらか暗い電車通りの歩道へ出た。
- `4`: 犬の姿は消えた。
- `5`: 立止った私はと見こう見した。
- `6`: 車道のきわまで出て、犬のゆくえを目でたずねていた。

#### CFI Roundtrip

さて、私はいつのまにか犬に導かれていた。犬は見失われるかと思うと又現われた。河原町通へ抜ける道を曲った。私はこうして新京極よりもいくらか暗い電車通りの歩道へ出た。犬の姿は消えた。立止った私はと見こう見した。車道のきわまで出て、犬のゆくえを目でたずねていた。

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[32]` さて、私はいつのまにか犬に導かれていた。犬は見失われるかと思うと又現われた。河原町通へ抜ける道を曲った。私はこうして新京極よりもいくらか暗い電車通りの歩道へ出た
- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*[32]/*[1]` と
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[32]` 見
- `span` `KEEP_NORMAL` `` `/*/*[2]/*/*[32]/*[2]` こう
- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[32]` 見した。車道のきわまで出て、犬のゆくえを目でたずねていた。

#### Reviewer Notes

- Pending external review.

### Sample 3

- Chapter / Paragraph: `11` / `45`
- Document: `xhtml/0010.xhtml`
- XPath: `/*/*[2]/*/*[56]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">　そして音高く白槌を打った。方丈にひびきわたるその槌音が、私に又もや、老師の持っている権力のあらたかさを思い知らせた。</p>
```

#### Extracted Text

そして音高く白槌を打った。方丈にひびきわたるその槌音が、私に又もや、老師の持っている権力のあらたかさを思い知らせた。

#### Sentence Segments

- `0`: そして音高く白槌を打った。
- `1`: 方丈にひびきわたるその槌音が、私に又もや、老師の持っている権力のあらたかさを思い知らせた。

#### CFI Roundtrip

そして音高く白槌を打った。方丈にひびきわたるその槌音が、私に又もや、老師の持っている権力のあらたかさを思い知らせた。

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[56]` そして音高く白槌を打った。方丈にひびきわたるその槌音が、私に又もや、老師の持っている権力のあらたかさを思い知らせた。

#### Reviewer Notes

- Pending external review.

### Sample 4

- Chapter / Paragraph: `18` / `79`
- Document: `xhtml/0017.xhtml`
- XPath: `/*/*[2]/*/*[44]/*[2]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">『スタア』短編集（一月、新潮社刊）</p>
```

#### Extracted Text

『スタア』短編集（一月、新潮社刊）

#### Sentence Segments

- `0`: 『スタア』短編集（一月、新潮社刊）

#### CFI Roundtrip

『スタア』短編集（一月、新潮社刊）

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[44]/*[2]` 『スタア』短編集（一月、新潮社刊）

#### Reviewer Notes

- Pending external review.

### Sample 5

- Chapter / Paragraph: `13` / `84`
- Document: `xhtml/0012.xhtml`
- XPath: `/*/*[2]/*/*[100]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">　しかし私はそうしなかった。いきなり枕もとから、「犯罪と刑罰」をとって、女の鼻先へつきつけた。</p>
```

#### Extracted Text

しかし私はそうしなかった。いきなり枕もとから、「犯罪と刑罰」をとって、女の鼻先へつきつけた。

#### Sentence Segments

- `0`: しかし私はそうしなかった。
- `1`: いきなり枕もとから、「犯罪と刑罰」をとって、女の鼻先へつきつけた。

#### CFI Roundtrip

しかし私はそうしなかった。いきなり枕もとから、「犯罪と刑罰」をとって、女の鼻先へつきつけた。

#### Debug Spans

- `p` `BLOCK_BREAK` `paragraph` `/*/*[2]/*/*[100]` しかし私はそうしなかった。いきなり枕もとから、「犯罪と刑罰」をとって、女の鼻先へつきつけた。

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
