# ERP — lot record

The fields the ERP holds for an incoming lot. This is what the intake team keys today.

System of record: Thornbury ERP (Aldon 7). Owned by Supply Operations.

| Field | Type | Required | Notes |
|---|---|---|---|
| `lot_id` | text | yes | Supplier's lot or batch number, as printed |
| `material_no` | text | yes | Thornbury item code |
| `supplier_name` | text | yes | Must match an entry in the supplier master |
| `received_date` | date | yes | Set by the warehouse on receipt, not from the certificate |
| `expiry_date` | date | yes | Keyed from the certificate |
| `assay_pct` | decimal(6,3) | yes | |
| `moisture_pct` | decimal(6,3) | yes | |
| `heavy_metals_ppm` | decimal(6,3) | yes | |
| `bulk_density` | decimal(6,3) | no | |
| `status` | enum | yes | `released` · `held` · `rejected` |
| `entered_by` | user | yes | |

## Notes from the ERP team

- `expiry_date` is a required field and the ERP will not save a lot without it. Purchasing runs
  its reorder logic off this date.
- There is no field for the analytical method. There has been a request open to add one since
  March; it has not been prioritised.
- `status` defaults to `held` on creation. Setting it to `released` is a separate action.
- The ERP has a REST endpoint for lot creation. It is used by two other integrations today.
