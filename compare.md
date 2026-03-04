# Comparison: ebooklib vs foliate-js

## Overview
This document evaluates and compares `ebooklib` (Python) and `foliate-js` (JavaScript) for the purpose of building an EPUB parser and aligner for the literary translation alignment project.

## 1. Library Profiles

### **ebooklib**
*   **Language:** Python
*   **Primary Use Case:** Programmatic reading, writing, and modification of EPUB files.
*   **Environment:** Backend / CLI / Scripting (perfect integration with `vecalign`).
*   **Key Capabilities:**
    *   Reads EPUB structure (spine, manifest, guide).
    *   Provides raw access to item content (HTML/XML).
    *   Supports creating new EPUBs from scratch or modifying existing ones.
    *   Handles metadata and structural elements explicitly.

### **foliate-js**
*   **Language:** JavaScript (ES Modules)
*   **Primary Use Case:** Rendering and viewing e-books in a web browser.
*   **Environment:** Frontend / Browser (requires DOM, Blob, etc.).
*   **Key Capabilities:**
    *   Parses EPUBs for display (pagination, fixed layout).
    *   Abstracts structure into a `Book` interface for navigation (`.sections`, `.toc`).
    *   Handles complex rendering logic (CFIs, overlays, search).
    *   **Limitation:** Read-only focus; modifies DOM for view, not the source file structure for saving. Harder to run in a headless script environment.

## 2. Evaluation Criteria

### A. EPUB Format Parsing & Compatibility
*   **ebooklib:** Excellent. It maps directly to the OEBPS package structure. You interact with `EpubItem`, `EpubHtml`, etc. It allows precise control over what is read and written.
*   **foliate-js:** Excellent for *rendering* compatibility (handles many formats like EPUB, MOBI, FB2). However, it abstracts the file structure to serve a UI, which might hide some low-level details needed for strict alignment.

### B. Strict Adherence & Raw Access
*   **ebooklib:** Gives you the raw bytes/string of the HTML files. You are responsible for parsing the HTML (e.g., with `BeautifulSoup`). This is ideal for extracting text exactly as it exists in the file without rendering artifacts.
*   **foliate-js:** Designed to load content into a browser View/Iframe. It handles resource resolving and sanitation. While you can access text, it is optimized for a user reading linear content, not necessarily for extracting a 1:1 structural representation for alignment.

### C. Text Manipulation & Output
*   **ebooklib:** Strong support. You can modify the content of an `EpubHtml` item and write the book back to disk. This is essential for the "Output Generator" phase (creating side-by-side EPUBs).
*   **foliate-js:** Weak support. It does not have built-in facilities to repack and save an EPUB file after modification. It uses `zip.js` for reading but is not a general-purpose EPUB editor.

## 3. Conclusion & Recommendation

**Verdict: Use `ebooklib`.**

For the specific goals of this project (extracting text for `vecalign`, aligning sentences, and potentially generating a new EPUB), `ebooklib` is the superior choice because:
1.  **Ecosystem Alignment:** It runs in Python, the same environment as the core `vecalign` algorithm.
2.  **Manipulation Capability:** It supports *writing* and *modifying* EPUBs, which is a key requirement.
3.  **Headless Execution:** It runs natively in a script/server environment without needing browser polyfills or a GUI.

`foliate-js` is an excellent library for building a *viewer* for the final aligned result, but it is not suitable for the backend processing pipeline.
