# QA — incoming lot tracker

Maintained by the Quality team, separately from the ERP. Currently a shared spreadsheet with about
14,000 rows going back four years.

| Column | Notes |
|---|---|
| `batch` | Supplier's batch number |
| `item` | Thornbury item code |
| `supplier` | Free text — spellings vary |
| `retest_due` | Taken from the certificate |
| `purity` | |
| `purity_method` | Which method the certificate stated |
| `water_content` | |
| `water_method` | Which method the certificate stated |
| `heavy_metals` | |
| `density` | |
| `conforms` | `Y` / `N` / `QUERY` |
| `reviewed_by` | QA analyst initials |
| `note` | Free text. Where the interesting information actually lives |

## Notes from QA

- `conforms = QUERY` means the analyst could not tell from the certificate alone. About 3% of rows.
  These are chased by email and the outcome usually ends up in `note` rather than in the column.
- We record the method for a reason. A result is only meaningful against the method that produced
  it, and the specification says which methods are acceptable.
- We are aware our numbers sometimes differ from what Supply Ops has in the ERP. We have not had the
  time to work out why in any systematic way.
