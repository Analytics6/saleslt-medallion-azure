# Databricks notebook source
import json
from pyspark.sql import functions as F

for name, default in [('run_id','manual'), ('tables_json','[]')]:
    dbutils.widgets.text(name, default)
run_id = dbutils.widgets.get('run_id')
tables = json.loads(dbutils.widgets.get('tables_json'))
assert tables, 'No SalesLT tables discovered; refusing an empty publication'
account = 'adlsgenvs5'
spark.conf.set(f'fs.azure.account.key.{account}.dfs.core.windows.net', dbutils.secrets.get('saleslt-medallion','storage-key'))
root = f'abfss://bronze@{account}.dfs.core.windows.net/saleslt'
counts = {}
for item in tables:
    table = item['TableName']
    source = f'{root}/raw/{run_id}/{table}'
    df = spark.read.parquet(source)
    df = df.withColumn('_ingested_at', F.current_timestamp()).withColumn('_pipeline_run_id', F.lit(run_id)).withColumn('_source_table', F.lit('SalesLT.'+table))
    path = f'{root}/snapshots/{run_id}/{table}'
    df.write.format('delta').mode('errorifexists').save(path)
    counts[table] = spark.read.format('delta').load(path).count()
    display(df.limit(5))
manifest = {'layer':'bronze','run_id':run_id,'tables':tables,'counts':counts}
dbutils.fs.put(f'{root}/manifests/{run_id}.json', json.dumps(manifest), True)
dbutils.notebook.exit(json.dumps(manifest))
