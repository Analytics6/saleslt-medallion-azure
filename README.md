# Azure SalesLT Medallion

Complete Azure SQL → Data Factory → Databricks → Bronze/Silver/Gold implementation.

- [Full architecture, configuration, deployment and operations guide](MEDALLION.md)
- [Verified run results](docs/VALIDATION.md)
- [Persisted data schemas](docs/SCHEMAS.md)
- [Notebook sources](notebooks/)
- [Data Factory definitions](adf/)

The pipeline has three separate notebook activities and a native five-minute schedule. Layer data is stored in private containers on adlsgenvs5.
