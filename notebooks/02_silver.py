# Databricks notebook source
import json
from pyspark.sql import functions as F, Window
from pyspark.sql.types import StringType

dbutils.widgets.text('run_id','manual')
run_id = dbutils.widgets.get('run_id')
account = 'adlsgenvs5'
spark.conf.set(f'fs.azure.account.key.{account}.dfs.core.windows.net', dbutils.secrets.get('saleslt-medallion','storage-key'))
bronze = f'abfss://bronze@{account}.dfs.core.windows.net/saleslt'
silver = f'abfss://silver@{account}.dfs.core.windows.net/saleslt'
manifest = json.loads(dbutils.fs.head(f'{bronze}/manifests/{run_id}.json', 1048576))
metrics = {}
for item in manifest['tables']:
    table = item['TableName']
    df = spark.read.format('delta').load(f'{bronze}/snapshots/{run_id}/{table}')
    for field in df.schema.fields:
        if isinstance(field.dataType, StringType):
            df = df.withColumn(field.name, F.when(F.length(F.trim(F.col(field.name))) == 0, F.lit(None)).otherwise(F.trim(F.col(field.name))))
    keys = [x for x in (item.get('PrimaryKeys') or '').split(',') if x]
    invalid = F.lit(False)
    for key in keys:
        invalid = invalid | F.col(key).isNull()
    for column in ['OrderQty','UnitPrice','ListPrice','StandardCost','SubTotal','TaxAmt','Freight']:
        if column in df.columns:
            invalid = invalid | (F.col(column) < 0)
    if 'UnitPriceDiscount' in df.columns:
        invalid = invalid | (F.col('UnitPriceDiscount') < 0) | (F.col('UnitPriceDiscount') > 1)
    invalid = F.coalesce(invalid, F.lit(False))
    rejected = df.filter(invalid).withColumn('_rejection_reason', F.lit('null primary key or invalid numeric range'))
    clean = df.filter(~invalid)
    before = clean.count()
    if keys:
        order = [F.col('ModifiedDate').desc_nulls_last()] if 'ModifiedDate' in df.columns else []
        order.append(F.sha2(F.to_json(F.struct(*[F.col(c) for c in sorted(df.columns)])),256).desc())
        clean = clean.withColumn('_rn',F.row_number().over(Window.partitionBy(*keys).orderBy(*order))).filter('_rn=1').drop('_rn')
    else:
        clean = clean.dropDuplicates([c for c in clean.columns if not c.startswith('_')])
    clean = clean.withColumn('_silver_processed_at',F.current_timestamp())
    clean.write.format('delta').mode('errorifexists').save(f'{silver}/snapshots/{run_id}/{table}')
    rejected.write.format('delta').mode('errorifexists').save(f'{silver}/quarantine/{run_id}/{table}')
    metrics[table] = {'input_rows':manifest['counts'][table], 'output_rows':clean.count(), 'rejected_rows':rejected.count(), 'duplicate_rows_removed':before-clean.count()}
    assert metrics[table]['input_rows'] == metrics[table]['output_rows'] + metrics[table]['rejected_rows'] + metrics[table]['duplicate_rows_removed']
    display(clean.limit(5))
result = {'layer':'silver','run_id':run_id,'tables':manifest['tables'],'metrics':metrics}
dbutils.fs.put(f'{silver}/manifests/{run_id}.json',json.dumps(result),True)
dbutils.notebook.exit(json.dumps(result))
