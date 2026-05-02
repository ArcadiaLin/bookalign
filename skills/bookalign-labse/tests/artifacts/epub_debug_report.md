# EPUB Extraction Audit

- Book: `假面的告白-繁中.epub`
- Seed: `20260315`
- Sample count: `5`
- Test type: `mixed`
- Granularity: `paragraph`
- Debug metadata: `off`

## Samples

### Sample 1

- Chapter / Paragraph: `5` / `116`
- Document: `9789865511906-3.xhtml`
- XPath: `/*/*[2]/*[146]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">──園子早已令我難以抗拒地站在面前。見我發呆，行禮行到一半的她又再次鄭重朝我鞠躬。</p>
```

#### Extracted Text

──園子早已令我難以抗拒地站在面前。見我發呆，行禮行到一半的她又再次鄭重朝我鞠躬。

#### CFI Roundtrip

──園子早已令我難以抗拒地站在面前。見我發呆，行禮行到一半的她又再次鄭重朝我鞠躬。

#### Reviewer Notes

- Pending external review.

### Sample 2

- Chapter / Paragraph: `7` / `180`
- Document: `9789865511906-4.xhtml`
- XPath: `/*/*[2]/*[212]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">我和園子幾乎同時看手錶。</p>
```

#### Extracted Text

我和園子幾乎同時看手錶。

#### CFI Roundtrip

我和園子幾乎同時看手錶。

#### Reviewer Notes

- Pending external review.

### Sample 3

- Chapter / Paragraph: `6` / `134`
- Document: `9789865511906-3a.xhtml`
- XPath: `/*/*[2]/*[161]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">好，來拉勾！我霸氣地說。我們就這樣乍看天真無邪地拉勾，但是兒時感到的恐懼頓時重現心頭。據說拉勾之後如果爽約，那根手指就會爛<a id="GBS.0136.02"></a>掉，這種說法曾經給我幼小的心靈帶來恐懼。園子所謂的禮物，雖未明言但顯然意味著﹁求婚﹂，所以我才會恐懼。我的恐懼，是晚上不敢一個人上廁所的小孩對四周的黑暗感到的那種恐懼。</p>
```

#### Extracted Text

好，來拉勾！我霸氣地說。我們就這樣乍看天真無邪地拉勾，但是兒時感到的恐懼頓時重現心頭。據說拉勾之後如果爽約，那根手指就會爛掉，這種說法曾經給我幼小的心靈帶來恐懼。園子所謂的禮物，雖未明言但顯然意味著﹁求婚﹂，所以我才會恐懼。我的恐懼，是晚上不敢一個人上廁所的小孩對四周的黑暗感到的那種恐懼。

#### CFI Roundtrip

好，來拉勾！我霸氣地說。我們就這樣乍看天真無邪地拉勾，但是兒時感到的恐懼頓時重現心頭。據說拉勾之後如果爽約，那根手指就會爛掉，這種說法曾經給我幼小的心靈帶來恐懼。園子所謂的禮物，雖未明言但顯然意味著﹁求婚﹂，所以我才會恐懼。我的恐懼，是晚上不敢一個人上廁所的小孩對四周的黑暗感到的那種恐懼。

#### Reviewer Notes

- Pending external review.

### Sample 4

- Chapter / Paragraph: `5` / `28`
- Document: `9789865511906-3.xhtml`
- XPath: `/*/*[2]/*[34]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">我在第二章刻意一再提及 erectio penis，就是和這點有關。因為我的自我欺瞞是被這方面的無知促成的。任何小說的接吻場面都省略了關於男人 erectio 的描寫。那是理所當然，無庸贅述。性學研究書籍也省略了<span><a id="GBS.0078.05"></a>連</span>接吻時都會產生的 erectio。就我所讀到的，似乎只有在肉體交媾前，或是幻想交媾時才會發生 erectio。所以就算沒有任何慾望，到了那一刻，突然間──就像天外飛來一筆──我大概也會產生 erectio。我內心有百分之十在囁嚅：<a id="GBS.0079.01"></a>﹁不，唯有我不會發生。﹂那化為我各種形式的不安呈現。然而我在做那種惡習時可曾有過一次想起女人的某個部分？哪怕只是試驗性的！</p>
```

#### Extracted Text

我在第二章刻意一再提及 erectio penis，就是和這點有關。因為我的自我欺瞞是被這方面的無知促成的。任何小說的接吻場面都省略了關於男人 erectio 的描寫。那是理所當然，無庸贅述。性學研究書籍也省略了連接吻時都會產生的 erectio。就我所讀到的，似乎只有在肉體交媾前，或是幻想交媾時才會發生 erectio。所以就算沒有任何慾望，到了那一刻，突然間──就像天外飛來一筆──我大概也會產生 erectio。我內心有百分之十在囁嚅：﹁不，唯有我不會發生。﹂那化為我各種形式的不安呈現。然而我在做那種惡習時可曾有過一次想起女人的某個部分？哪怕只是試驗性的！

#### CFI Roundtrip

我在第二章刻意一再提及 erectio penis，就是和這點有關。因為我的自我欺瞞是被這方面的無知促成的。任何小說的接吻場面都省略了關於男人 erectio 的描寫。那是理所當然，無庸贅述。性學研究書籍也省略了連接吻時都會產生的 erectio。就我所讀到的，似乎只有在肉體交媾前，或是幻想交媾時才會發生 erectio。所以就算沒有任何慾望，到了那一刻，突然間──就像天外飛來一筆──我大概也會產生 erectio。我內心有百分之十在囁嚅：﹁不，唯有我不會發生。﹂那化為我各種形式的不安呈現。然而我在做那種惡習時可曾有過一次想起女人的某個部分？哪怕只是試驗性的！

#### Reviewer Notes

- Pending external review.

### Sample 5

- Chapter / Paragraph: `4` / `76`
- Document: `9789865511906-2.xhtml`
- XPath: `/*/*[2]/*[94]`
- Action: `BLOCK_BREAK`
- CFI roundtrip match: `yes`

#### Raw XHTML

```html
<p xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">我三步併作兩步跳過墊腳石，跟著鞋印一路走去，有些地方露出黑油油的泥土，有些地方是枯草皮，有些地方是骯髒的硬雪，有些地方是石板。於是不知不覺中，我發現自己的<a id="GBS.0043.05"></a>步伐變得和近江大步前進的方式一模一樣。</p>
```

#### Extracted Text

我三步併作兩步跳過墊腳石，跟著鞋印一路走去，有些地方露出黑油油的泥土，有些地方是枯草皮，有些地方是骯髒的硬雪，有些地方是石板。於是不知不覺中，我發現自己的步伐變得和近江大步前進的方式一模一樣。

#### CFI Roundtrip

我三步併作兩步跳過墊腳石，跟著鞋印一路走去，有些地方露出黑油油的泥土，有些地方是枯草皮，有些地方是骯髒的硬雪，有些地方是石板。於是不知不覺中，我發現自己的步伐變得和近江大步前進的方式一模一樣。

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
