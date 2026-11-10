# Databricks notebook source
import json

dbutils.widgets.text("message", "Hello from Azure Data Factory")
dbutils.widgets.text("pipeline_run_id", "manual")
rows = spark.range(10).count()
assert rows == 10
result = {
    "status": "success",
    "message": dbutils.widgets.get("message"),
    "pipeline_run_id": dbutils.widgets.get("pipeline_run_id"),
    "row_count": rows,
}
print(json.dumps(result))
dbutils.notebook.exit(json.dumps(result))
