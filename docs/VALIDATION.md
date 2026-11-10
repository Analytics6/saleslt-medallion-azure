# Verified deployment results

Manual pipeline run: `39a61f4e-be8e-46bb-8d15-bb3a0146556e`

Status: **Succeeded**. Storage verification: **passed**.

Run start (UTC): 2026-11-10T06:33:34.4796002Z
Run end (UTC): 2026-11-10T06:42:08.3019629Z

Counts below were independently read from active Delta files in Blob Storage, using Delta transaction logs. SQL counts and line totals were queried independently.

| Source table | SQL | Bronze | Silver |
|---|---:|---:|---:|
| Address | 450 | 450 | 450 |
| Customer | 847 | 847 | 847 |
| CustomerAddress | 417 | 417 | 417 |
| Product | 295 | 295 | 295 |
| ProductCategory | 41 | 41 | 41 |
| ProductDescription | 762 | 762 | 762 |
| ProductModel | 128 | 128 | 128 |
| ProductModelProductDescription | 762 | 762 | 762 |
| SalesOrderDetail | 542 | 542 | 542 |
| SalesOrderHeader | 32 | 32 | 32 |

All Silver rejection and duplicate-removal counts were zero.

| Gold dataset | Persisted rows |
|---|---:|
| dim_customer | 847 |
| dim_date | 1 |
| dim_product | 295 |
| fact_order | 32 |
| fact_sales | 542 |
| sales_by_customer | 32 |
| sales_by_day | 1 |
| sales_by_product | 142 |

Azure SQL net sales: **708690.1533**. Persisted Gold net sales: **708690.1533**. Totals match.

## Highest-selling products

| Product | Units | Net sales |
|---|---:|---:|
| Touring-1000 Blue, 60 | 26 | 37191.4920 |
| Mountain-200 Black, 42 | 27 | 37178.8380 |
| Road-350-W Yellow, 48 | 42 | 36486.2355 |
| Mountain-200 Black, 38 | 26 | 35801.8440 |
| Touring-1000 Yellow, 60 | 17 | 23413.4747 |
| Touring-1000 Blue, 50 | 16 | 22887.0720 |
| Mountain-200 Silver, 42 | 15 | 20879.9100 |
| Road-350-W Yellow, 40 | 20 | 20411.8800 |
| Mountain-200 Black, 46 | 14 | 19277.9160 |
| Road-350-W Yellow, 42 | 19 | 18692.5193 |

See [results.json](results.json) for complete machine-readable evidence.

## Recurring trigger

- Name: `tr_saleslt_every_5_minutes`
- Runtime state verified: **Started**
- Frequency: **every 5 minutes**
- First scheduled time: **10 November 2026, 12:14 PM IST**
- Pipeline concurrency: **1**; runs queue if processing exceeds five minutes.
- The verified cold run took approximately **8 minutes 34 seconds**.
- Temporary setup SQL firewall rules were removed after verification.

## Source code

Private repository: [Analytics6/saleslt-medallion-azure](https://github.com/Analytics6/saleslt-medallion-azure).

## First scheduled firing

The trigger fired successfully on 10 November 2026 at **12:14:01 PM IST** (06:44:01 UTC). It launched pipeline run `cbf44569-bace-4165-b548-e58dd7eb2ade`. This confirms scheduled dispatch; the complete validated manual run is reported above.
