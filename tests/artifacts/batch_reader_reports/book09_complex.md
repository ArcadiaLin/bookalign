# EPUB Extraction Audit

- Book: `こころ (夏目 漱石, バラエティ･アートワークス) (z-library.sk, 1lib.sk, z-lib.sk).epub`
- Seed: `20261091`
- Sample count: `0`
- Test type: `complex`
- Granularity: `sentence`
- Debug metadata: `on`

## Samples

## Summary

- Total samples: `0`
- Ruby samples: `0`
- Footnote-ish samples: `0`
- Roundtrip mismatches: `0`

## Failed Samples

- None

## Suggested Fix Directions

- Inspect any roundtrip mismatch where normalized extracted text diverges from the paragraph segment.
- Review debug spans for over-skipped note links or missed ruby base text.
- Compare paragraph and sentence outputs when inline breaks appear in poetry-like XHTML.
