# Batch Reader Review Summary Round 3

## Scope

- Books reviewed: 12 EPUB files in `/home/arcadia/projs/bookalign/books`
- Sampling target: 5 `normal` + 5 `complex` sentence-level samples per book
- Review style: sub-agent reader judgment, not assertion-based checking
- Report set: `/home/arcadia/projs/bookalign/tests/artifacts/batch_reader_reports`
- Review CSV: `/home/arcadia/projs/bookalign/tests/artifacts/batch_reader_review_results_round3.csv`

## Aggregate Result

- `pass`: 4
- `mixed`: 19
- `fail`: 1
- Total reviewer findings: 45

Compared with the earlier round:

- obvious numeric-marker leakage improved on `her.epub` normal samples
- some English span-boundary word-merge issues improved in Sherlock
- some navigation / heading / author-name noise was reduced
- the remaining hard problems are now concentrated in a smaller set of structurally bad or line-break-heavy EPUB cases

## What Improved

- Standalone numeric markers between `<br>` lines are filtered more often before sentence extraction.
- Obvious Gutenberg / license-like text is reduced, though not eliminated in `Don Quijote`.
- English inline span boundaries insert spaces more safely, reducing `whichwe` / `lovingMARY`-style merges.
- CJK quoted exclamations/questions are less likely to be shattered into multiple micro-sentences.
- `br`-heavy paragraphs can now switch to line-aware splitting, which helps dialogue/verse-like blocks in healthier EPUBs.

## Remaining Problem Clusters

### 1. Structurally bad source EPUB blocks

Still visible in:

- `Don Quijote` complex
- `Jane Austen` complex
- `金閣寺 (Z-Library)` normal
- `羅生門・鼻・芋粥` normal/complex

Typical symptoms:

- backmatter / legal / navigation fragments still sampled
- bibliography / publication lines still look like candidate sentences
- glossary-like marker lines remain noisy

### 2. Dialogue / quote boundary heuristics

Still visible in:

- `Alice`
- `Marianela`
- `Rimas y leyendas`
- `Sherlock Holmes`
- `人間失格`

Typical symptoms:

- closing quote detached into its own segment
- long quoted paragraphs remain under-split
- a spoken clause plus narration is sometimes merged or split at the wrong place

### 3. Verse / line-broken prose

Still visible in:

- `Alice` complex
- `Rimas y leyendas`
- some Spanish dialogue passages with ellipses

Typical symptoms:

- lyric lines are over-split into fragments
- or compressed into prose-like units that no longer feel natural as “sentences”

### 4. Image-only / non-text EPUBs

- `こころ` still yields zero samples because the inspected spine documents are image pages rather than text XHTML.

## Book-Level Snapshot

- `Alice`: mixed. Better than before on some quote cases, but verse and quote-tail handling still weak.
- `Don Quijote`: complex still fail. Source contains enough non-body English/legal fragments that heuristics do not fully recover clean sentence candidates.
- `Jane Austen`: still mixed. Some TOC/meta leakage remains.
- `Marianela`: mixed. Main issue is under-splitting inside long quoted passages.
- `Rimas y leyendas`: mixed. Ellipsis/dialogue and verse remain difficult.
- `Sherlock Holmes`: mixed. Word-merging improved, but quote-tail loss still appears.
- `her.epub`: normal passed; complex still mixed because page-number-like lines and line-broken dialogue remain tricky.
- `kinkaku.epub`: complex pass, normal pass-ish/mildly mixed depending on sample; ruby-heavy literary prose remains one of the strongest cases.
- `こころ`: no text samples available.
- `人間失格`: mixed but generally readable; long quoted monologues still under-split.
- `羅生門・鼻・芋粥`: mixed; glossary / annotation-like entries still leak.
- `金閣寺 (Z-Library)`: mixed on normal due backmatter/meta-like lines; complex remains strong.

## Practical Boundary

At this stage the extractor is much closer to the intended boundary:

- it does not attempt semantic-perfect正文 selection
- it tries to produce alignable sentence candidates from reasonably healthy EPUB structure
- it now filters a broader class of obviously bad candidates and handles more quote/line-break patterns heuristically

The remaining failures are mostly:

- unhealthy EPUB structure
- paratext that still looks block-like
- poem/dialogue formatting that cannot be fully normalized by shallow rules alone
