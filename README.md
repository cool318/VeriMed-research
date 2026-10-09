# VeriMed (Research Edition)

This is the companion build to the research paper, kept in its own repository
so the paper and the running code never drift apart. It's a separate,
independently maintained codebase from any other VeriMed app you may be
running — the two are built for different purposes and are not meant to be
merged or compared feature-for-feature.

## Why two builds exist

VeriMed development runs along two independent tracks:

- **Your build** (own repo/deployment) — your own detection engine, your own
  design choices, your own roadmap.
- **This build** — the engine that is described, tested, and cited in the
  accompanying research paper ("Requirements Engineering for Trustworthy
  Clinical NLP Systems"). Every number in this README, and every score this
  app produces on the bundled examples, matches what the paper reports.

Neither build is "more correct" than the other — they serve different
purposes. Deploy them to separate URLs, under separate names, so there's no
ambiguity about which is which.

## What's in this build

- **Cardiology (English, synthetic)** — sentence-level grounding, the
  original published worked example (33.3% overall risk).
- **Neurology (English, synthetic)** — clause-level atomic decomposition +
  negation-aware detection.
- **Real Spanish case (CodiEsp corpus)** — genuine clinical text, not
  synthetic. CodiEsp (CLEF eHealth 2020; Miranda-Escalada, Gonzalez-Agirre
  and Krallinger, 2020), document `S1889-836X2016000100006-1`, CC-BY 4.0,
  retrieved from its original SciELO publication. Surfaces a real, severe
  failure mode: a fabricated claim scores a perfect 1.000 similarity because
  the Spanish negation word "no" is a stopword and gets stripped before
  comparison — caught correctly by the negation-aware check.
- **Auto-populated draft summaries** — paste a source note and a faithful
  extractive draft summary fills in automatically; edit it to introduce an
  error and test the detector. Analysis only runs when you click
  "Analyze Grounding" — auto-population and fabrication-checking are
  deliberately separate steps.

## Engine

TF-IDF + cosine similarity (scikit-learn), sentence- or clause-level claim
splitting, negation-aware detection (English + Spanish marker lists).
Thresholds: grounded ≥0.45, weak 0.20–0.45, unverified <0.20 — these exact
values are what the paper's worked examples use and cite.

## Running locally

```bash
pip install -r requirements.txt
python app.py
```

Open http://localhost:5050.

## Deploying (GitHub + Render, free tier)

1. Push this folder to its own GitHub repository (separate from your other
   VeriMed build).
2. On Render: New → Web Service → connect the repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`

## Known limitations (disclosed, not hidden)

- TF-IDF/cosine similarity is lexical, not semantic — see the Spanish case
  above for a concrete, severe example of what that misses.
- Negation-marker lists (English, Spanish) are small and were developed
  iteratively alongside the bundled test examples — not validated against
  an independently annotated, held-out test set.
- Only one real (non-synthetic) case included so far.
- Auto-generated draft summaries are faithful/extractive by design — they
  don't themselves demonstrate hallucination detection until edited.

## Files

- `grounding.py` — core engine (matches the paper exactly)
- `app.py` — Flask routes, including `/generate-summary` for auto-population
- `sample_data.py` — all example cases
- `templates/index.html` — UI
- `pdf_export.py` — governance-view PDF export
- `requirements.txt` — pinned dependencies
