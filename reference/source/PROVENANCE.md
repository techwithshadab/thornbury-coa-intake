# Vendored controlled sources

These are copies of Thornbury documents, vendored so the derivation has a source in this repo and
the freshness gate has something to compare against. **They are copies, and a copy of a controlled
document drifts.**

| File | Upstream | Vendored on | Upstream revision at that date |
|---|---|---|---|
| `SPEC-7-revD.md` | Thornbury QMS — controlled copy held in the QMS, owned by Quality (Marisol Vega) | 2026-08-29 | Revision D, effective 1 March 2026 |
| `supplier-master.md` | Thornbury ERP supplier master, owned by IT | 2026-08-29 | as supplied at kick-off |

**Open, unresolved:** nobody has agreed how this repo learns that SPEC-7 has been revised. SPEC-7
§3.3 says a method change requires a revision and a controlled notification to suppliers; it says
nothing about notifying a downstream system. Until that is settled, a revision to SPEC-7 silently
leaves this repo asserting a withdrawn rule — which is precisely the failure SPEC-7 §4 exists to
catch. Tracked in `STATUS.md`; needs Quality to own the notification path.
