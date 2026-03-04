# Project Evaluation & Development Roadmap

## 1. Project Evaluation
**Concept:** Literary Translation Alignment Tool using `vecalign`.
**Verdict:** **Highly Feasible & Valuable**.

*   **Value Proposition:** Aligning professional translations (human) against originals provides significantly higher quality training data and reading experiences than AI-generated translations.
*   **Core Algorithm:** `vecalign` is an excellent choice. It handles 1-to-many and null alignments better than simple length-based methods.
*   **Critical Success Factor:** The quality of **preprocessing** (EPUB parsing and sentence segmentation) will determine 90% of the result. `vecalign` assumes clean, sentence-segmented input.

## 2. Vecalign Code Review
I have analyzed the source code (`vecalign.py`, `dp_utils.py`, `overlap.py`) from the [thompsonb/vecalign](https://github.com/thompsonb/vecalign) repository.

### A. Code Structure & Quality
*   **Core Logic:** The heavy lifting is done in `dp_utils.py` and `dp_core` (Cython). The algorithm builds a cost matrix based on cosine similarity of sentence embeddings.
*   **Performance:** It uses `Cython` for speed, which is crucial for book-length alignment. Complexity is roughly linear $O(N)$.
*   **Integration:** It is currently a CLI script that reads files. **Recommendation:** You should vendor the code (copy `dp_utils.py` and `dp_core.pyx`) and modify it to accept in-memory Numpy arrays, bypassing file I/O.

## 3. EPUB Structural Alignment Strategy (Feasibility Analysis)
Your idea to use EPUB internal structures (CFI, spine, XML tags) for pre-alignment is **highly feasible and recommended**.

### A. The "Spine" Strategy
EPUBs define a linear reading order in the `spine`.
*   **Approach:** Extract the spine from both books.
    *   *Source Spine:* `[Cover, Intro, Ch1, Ch2, ..., Back]`
    *   *Target Spine:* `[Cover, Title, Preface, Ch1, Ch2, ..., Index]`
*   **Challenge:** The number of files rarely matches perfectly (e.g., translators add prefaces, or split long chapters into `ch1_part1.html`, `ch1_part2.html`).
*   **Solution:**
    1.  **Text Concatenation:** If the spine items are granular (many small files), consider merging them into larger "super-chapters" based on TOC entries.
    2.  **Fuzzy Title Matching:** Extract headers (`<h1>`, `<h2>`) from the start of each spine item and use fuzzy string matching (e.g., Levenshtein distance on translated titles) to anchor chapters.
    3.  **Length Ratio Heuristic:** Chapter lengths usually correlate. If Source Ch1 is 5000 chars, Target Ch1 should be roughly 5000 * ratio (e.g., 1.2x for English->Chinese).

### B. CFI & XML Tags
*   **CFI (Canonical Fragment Identifier):** Useful for precise location, but fragile if the files are modified. Use it for *storing* the alignment result (e.g., "Source `/6/4[id1]` aligns to Target `/6/8[id2]`").
*   **XML IDs:** IDs in `<p id="p1">` are often preserved or generated systematically. If the source/target creation process was similar (e.g., same InDesign export), IDs might match. If not, ignore them and rely on text content.

## 4. Personal Development Roadmap (Todo)

### Phase 1: Environment & Core Aligner (PoC)
*   [ ] **Setup:** Python 3.9+, `poetry` or `pip`. Install `numpy`, `cython`, `sentence-transformers`, `EbookLib`, `beautifulsoup4`.
*   [ ] **Vendor Vecalign:** Copy `dp_utils.py`, `dp_core.pyx` locally. Create a `setup.py` to compile the Cython extension.
*   [ ] **Wrapper:** Write a Python class `VecAligner` that accepts two lists of strings (sentences), generates embeddings (using `sentence-transformers`), computes overlaps internally, and returns alignment indices.
    *   *Goal:* `aligner.align(["Hello world"], ["Bonjour le monde"])` returns `[(0, 0)]`.

### Phase 2: EPUB Inspector & Parser
*   [ ] **Structure Dumper:** Write a script to inspect an EPUB and print its `spine` and `toc` (Table of Contents).
    *   *Goal:* See if chapters correspond to single files or multiple files.
*   [ ] **Content Extractor:** Implement `EPUBParser` class using `EbookLib`.
    *   **Cleaning:** Strip HTML tags but *keep block boundaries* (p, div, br) as newlines.
    *   **Filtering:** Ignore files with < 500 characters (likely copyright/images).
*   [ ] **Segmenter:** Integrate `spaCy`, `wtpsplit` to split extracted text into sentences.

### Phase 3: The "Matcher" (Chapter Alignment)
*   [ ] **Heuristic Matcher:** Implement a logic to pair Source Files $\leftrightarrow$ Target Files.
    *   Use **File Size Correlation** (Pearson correlation of lengths).
    *   Use **Title Translation** (translate Source headers to Target lang, then fuzzy match).
*   [ ] **Visualizer:** Output a simple HTML report showing which files were paired before running sentence alignment. This is your "sanity check".

### Phase 4: Integration & Pipeline
*   [ ] **The Pipeline:**
    1.  Parse EPUBs $\to$ List of Chapters.
    2.  Match Chapters $\to$ Pairs of Text.
    3.  Segment Text $\to$ Sentences.
    4.  Align Sentences (Vecalign) $\to$ Indices.
    5.  Reconstruct $\to$ Aligned Data Structure.
*   [ ] **Output Generator:** Write the aligned data into a new EPUB or a side-by-side HTML file.

### Phase 5: Refinement
*   [ ] **Optimization:** Cache embeddings to disk (they are expensive to compute).
*   [ ] **Edge Cases:** Handle footnotes (often `<sup>` tags) – usually best to remove them for alignment, then re-insert if possible (hard) or just append.
