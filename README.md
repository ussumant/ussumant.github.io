# Sumant's living site

The source for [ussumant.github.io](https://ussumant.github.io): a living record of what Sumant is building, what has shipped, and what he has learned.

## Content model

`content/site.json` is the publishing source of truth. It contains:

- stable positioning and About copy;
- the dated Now block;
- selected and archived work records;
- recent shipping-log entries;
- links and truthful stage labels.

Stages such as `Built`, `Shipped`, `Launched`, `Shared`, and `Measured` should remain distinct. A prototype or generated business concept must not be presented as an operating company.

## Build

```bash
python3 scripts/build_site.py
```

The build writes the static homepage, work archive, individual work notes, and Atom feed. Generated HTML is intentionally checked in so GitHub Pages can serve the repository without a framework or build action.

## Preview

```bash
python3 -m http.server 8765
```

Then open `http://127.0.0.1:8765`.

## Publishing loop

1. Recover a direct artifact, public link, screenshot, or measured result.
2. Add or update the evidence in the private public-work ledger.
3. Draft the corresponding `content/site.json` record with an honest stage and claim boundary.
4. Rebuild and inspect desktop and mobile renders.
5. Publish only after Sumant approves the public wording and receipts.
