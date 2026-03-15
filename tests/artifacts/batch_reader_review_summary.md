# Batch Reader Review Summary

## Scope

- Source directory: `/home/arcadia/projs/bookalign/books`
- Books covered: 12 EPUB files
- Review mode: reader-style subjective review by sub-agents
- Sampling target per book: 5 normal paragraph samples + 5 complex nested samples
- Granularity: sentence-level extraction

Generated artifacts:

- Reports: `/home/arcadia/projs/bookalign/tests/artifacts/batch_reader_reports`
- Review manifest: `/home/arcadia/projs/bookalign/tests/artifacts/batch_reader_review_manifest.csv`
- Review results: `/home/arcadia/projs/bookalign/tests/artifacts/batch_reader_review_results.csv`

## Overall Verdict Distribution

- `pass`: 4 reports
- `mixed`: 19 reports
- `fail`: 1 report

Interpretation:

- The extractor is generally readable and stable on ordinary prose.
- The main remaining weaknesses are not random corruption; they cluster around identifiable structures:
  - dialogue / quotation splitting
  - verse / line-break handling
  - frontmatter / backmatter / metadata leakage
  - page/section number leakage in some EPUB generator styles
  - rare ruby reconstruction edge cases

## Book-Level Summary

### 1. Alice

- Normal: `mixed`
- Complex: `mixed`
- Main issues:
  - quote-boundary segmentation often feels detached
  - verse / line-broken passages are flattened into awkward single sentences

### 2. Don Quijote

- Normal: `mixed`
- Complex: `fail`
- Main issues:
  - complex samples included obvious non-body text and license-like noise
  - one sampled passage was judged structurally corrupted / merged
  - dialogue clause splitting is also slightly mechanical

### 3. Jane Austen

- Normal: `pass`
- Complex: `mixed`
- Main issues:
  - normal prose reads well
  - complex report still catches TOC / navigation / frontmatter-like extraction

### 4. Marianela

- Normal: `mixed`
- Complex: `mixed`
- Main issues:
  - chapter-heading-like samples mixed into sentence output
  - some dialogue / ellipsis passages look under-split

### 5. Rimas y leyendas

- Normal: `mixed`
- Complex: `mixed`
- Main issues:
  - dialogue rhythm around ellipses is awkward
  - verse lines are extracted as fragments or merged unnaturally

### 6. Sherlock Holmes

- Normal: `pass`
- Complex: `mixed`
- Main issues:
  - ordinary prose is good
  - some long quoted / epistolary passages are under-segmented
  - one sample isolated closing punctuation into its own segment

### 7. her.epub

- Normal: `mixed`
- Complex: `mixed`
- Main issues:
  - numeric markers like `1`, `3`, `6`, `7/8`, `2/166/3` leaked into extracted text
  - dialogue segmentation around quotes is sometimes over-split

### 8. kinkaku.epub

- Normal: `mixed`
- Complex: `pass`
- Main issues:
  - complex ruby-heavy samples read well
  - normal samples still include heading-like or glossary-like material
  - some date-like formatting shows inserted spaces

### 9. こころ

- Normal: no samples
- Complex: no samples
- Reason:
  - the EPUB is image-only in the inspected XHTML spine documents (`div > img`), so there is no extractable body text for the current text extractor

### 10. 人間失格

- Normal: `mixed`
- Complex: `mixed`
- Main issues:
  - mostly readable
  - one dangling fragment and one awkward quoted-dialogue split remain

### 11. 羅生門・鼻・芋粥

- Normal: `mixed`
- Complex: `mixed`
- Main issues:
  - separators / colophon-like text still enter extraction
  - one reviewer noted ruby/base-text surface forms that look slightly wrong or unnatural

### 12. 金閣寺 (Z-Library)

- Normal: `mixed`
- Complex: `pass`
- Main issues:
  - prose is largely clean
  - some bibliography-like or non-narrative material appears in normal samples
  - minor formatting loss around date/month expressions

## Main Patterns Across The Batch

### 1. Good

- Ruby-heavy Japanese prose is much improved overall.
- `rt/rp` noise is generally absent.
- `span.super` / footnote-marker suppression works well on the books that use it.
- CFI-backed sentence extraction remains readable on ordinary paragraphs.

### 2. Remaining Weaknesses

- Dialogue:
  - English, Spanish, and some Japanese dialogue still split awkwardly around quotes and speaker attributions.
- Verse / poetry / line-broken prose:
  - line breaks are normalized into prose-like spaces, which hurts rhythm and sentence boundaries.
- Structural filtering:
  - TOC, frontmatter, legal boilerplate, separators, glossary markers, bibliography, and publication metadata still leak into candidate paragraphs in several books.
- Numeric marker leakage:
  - some EPUBs embed page/section markers inline; these are still entering sentence output.
- Ruby edge cases:
  - most ruby is good, but a few complex literary samples still produce slightly unnatural surface forms.

## Practical Conclusion

- Current extractor quality is strong enough for ordinary prose-heavy EPUB chapters.
- It is not yet clean enough to treat all extracted block candidates as trustworthy正文 across mixed-quality public EPUBs.
- The next highest-value cleanup is not ruby anymore; it is structural-body filtering plus better sentence handling for dialogue and verse.
