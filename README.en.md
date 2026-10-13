# Day-Care Center Care-Density Comparison (Korea)

> A single-file web app that ranks every adult day-care center in Korea by **"how many seniors each care worker looks after"**, using one open-government dataset. No server, no login — opens on a phone.

**Live:** https://dolbomok.pages.dev · **Source:** this repo · *(Korean docs: [README.md](README.md))*

---

## The problem

When a parent is approved for long-term care in Korea, the family must choose a day-care center themselves. Seoul alone has 500+. Map apps show location and photos; center websites all say "family-like atmosphere". There is **no comparable number** — so families pick by distance or word of mouth.

## What it does

Pick a province → district. Centers appear sorted by **care-worker-to-senior ratio** (capacity ÷ care workers), lowest first, each compared against the **regional median** so a number like "1.9" is immediately readable as good or not.

- 5,346 centers · 238 districts · one dataset (National Health Insurance Service, data.go.kr #15124763)
- Built-in search, "below median only" filter, shareable deep links (`#Seoul/Gwanak-gu`)
- Flags centers open < 12 months (the metric is structurally unfair to them) instead of hiding them
- Links out to the official portal for eligibility and inspection grades — **complements** the official tool, doesn't replace it

## What I verified

- **5,346 rows cross-checked** against the source XLSX with an independent recomputation (different library, not the build code): 0 mismatches
- Found and fixed a join bug (home-care staff leaking into day-care counts), and a metric flaw (brand-new centers ranking worst) — both documented with evidence
- Compared against official inspection grades (3,243 centers): correlation −0.18 → the ratio is **independent information**, not a proxy

## Stack

Python (pandas, openpyxl) for preprocessing → one self-contained HTML (vanilla JS, embedded JSON, ~660 KB). Deployed on Cloudflare Pages. Design system documented in `디자인시스템.md` (3 colours, golden-ratio type scale, grid-only spacing, 15 px minimum for 50+ users).

## Rebuild

```bash
pip install pandas openpyxl
python tools/build_data.py data/ltc_20260610.xlsx data/day_care.json
python tools/build_html.py data/day_care.json build/index.html
python tools/verify_screen.py build/index.html data/ltc_20260610.xlsx   # full cross-check
```

Built in two days for a public-data hackathon (Oct 2026).
