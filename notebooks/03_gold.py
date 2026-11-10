# Databricks notebook source
import json
from pyspark.sql import functions as F

dbutils.widgets.text('run_id','manual')
run_id = dbutils.widgets.get('run_id')
account = 'adlsgenvs5'
spark.conf.set(f'fs.azure.account.key.{account}.dfs.core.windows.net', dbutils.secrets.get('saleslt-medallion','storage-key'))
silver = f'abfss://silver@{account}.dfs.core.windows.net/saleslt'
gold = f'abfss://gold@{account}.dfs.core.windows.net/saleslt'
manifest = json.loads(dbutils.fs.head(f'{silver}/manifests/{run_id}.json',1048576))
for item in manifest['tables']:
    spark.read.format('delta').load(f"{silver}/snapshots/{run_id}/{item['TableName']}").createOrReplaceTempView(item['TableName'])

# Fail rather than silently lose orphaned fact records in dimensional joins.
for query in [
    'SELECT COUNT(*) FROM SalesOrderDetail d LEFT ANTI JOIN SalesOrderHeader h ON d.SalesOrderID=h.SalesOrderID',
    'SELECT COUNT(*) FROM SalesOrderDetail d LEFT ANTI JOIN Product p ON d.ProductID=p.ProductID',
    'SELECT COUNT(*) FROM SalesOrderHeader h LEFT ANTI JOIN Customer c ON h.CustomerID=c.CustomerID']:
    assert spark.sql(query).first()[0] == 0, 'Referential integrity check failed: '+query

outputs = {
 'dim_customer': spark.sql('''SELECT CustomerID, Title, FirstName, MiddleName, LastName, Suffix, CompanyName, SalesPerson, EmailAddress, Phone FROM Customer'''),
 'dim_product': spark.sql('''SELECT p.ProductID,p.Name AS ProductName,p.ProductNumber,p.Color,p.Size,p.Weight,p.StandardCost,p.ListPrice,p.ProductCategoryID,c.Name AS CategoryName,pc.Name AS ParentCategoryName,p.ProductModelID,m.Name AS ModelName FROM Product p LEFT JOIN ProductCategory c ON p.ProductCategoryID=c.ProductCategoryID LEFT JOIN ProductCategory pc ON c.ParentProductCategoryID=pc.ProductCategoryID LEFT JOIN ProductModel m ON p.ProductModelID=m.ProductModelID'''),
 'fact_sales': spark.sql('''SELECT d.SalesOrderID,d.SalesOrderDetailID,h.CustomerID,d.ProductID,CAST(h.OrderDate AS DATE) AS OrderDate,h.Status AS OrderStatus,d.OrderQty,d.UnitPrice,d.UnitPriceDiscount,CAST(d.OrderQty*d.UnitPrice AS DECIMAL(20,4)) AS GrossSales,CAST(d.OrderQty*d.UnitPrice*d.UnitPriceDiscount AS DECIMAL(20,4)) AS DiscountAmount,CAST(d.LineTotal AS DECIMAL(20,4)) AS NetSales,h.ShipToAddressID,h.BillToAddressID FROM SalesOrderDetail d JOIN SalesOrderHeader h ON d.SalesOrderID=h.SalesOrderID'''),
 'fact_order': spark.sql('''SELECT SalesOrderID,CustomerID,CAST(OrderDate AS DATE) AS OrderDate,CAST(DueDate AS DATE) AS DueDate,CAST(ShipDate AS DATE) AS ShipDate,Status AS OrderStatus,SubTotal,TaxAmt,Freight,TotalDue FROM SalesOrderHeader''')
}
outputs['fact_sales'].createOrReplaceTempView('gold_fact_sales')
outputs['dim_product'].createOrReplaceTempView('gold_dim_product')
outputs['dim_date'] = spark.sql('''SELECT DISTINCT OrderDate AS Date,year(OrderDate) AS Year,quarter(OrderDate) AS Quarter,month(OrderDate) AS Month,day(OrderDate) AS Day FROM gold_fact_sales''')
outputs['sales_by_day'] = spark.sql('''SELECT OrderDate,COUNT(DISTINCT SalesOrderID) AS Orders,COUNT(DISTINCT CustomerID) AS Customers,SUM(OrderQty) AS Units,SUM(GrossSales) AS GrossSales,SUM(DiscountAmount) AS DiscountAmount,SUM(NetSales) AS NetSales FROM gold_fact_sales GROUP BY OrderDate''')
outputs['sales_by_product'] = spark.sql('''SELECT f.ProductID,p.ProductName,p.CategoryName,COUNT(DISTINCT f.SalesOrderID) AS Orders,SUM(f.OrderQty) AS Units,SUM(f.NetSales) AS NetSales FROM gold_fact_sales f JOIN gold_dim_product p ON f.ProductID=p.ProductID GROUP BY f.ProductID,p.ProductName,p.CategoryName''')
outputs['sales_by_customer'] = spark.sql('''SELECT CustomerID,COUNT(DISTINCT SalesOrderID) AS Orders,SUM(OrderQty) AS Units,SUM(NetSales) AS NetSales FROM gold_fact_sales GROUP BY CustomerID''')
assert outputs['fact_sales'].count() == spark.table('SalesOrderDetail').count()
fact_total = outputs['fact_sales'].agg(F.sum('NetSales')).first()[0]
summary_total = outputs['sales_by_day'].agg(F.sum('NetSales')).first()[0]
assert fact_total == summary_total, 'Gold sales totals do not reconcile'
counts = {}
for name, df in outputs.items():
    df = df.withColumn('_pipeline_run_id',F.lit(run_id)).withColumn('_gold_processed_at',F.current_timestamp())
    df.write.format('delta').mode('errorifexists').save(f'{gold}/snapshots/{run_id}/{name}')
    # Parquet exports support readers without a Delta connector.
    df.write.mode('errorifexists').parquet(f'{gold}/exports/{run_id}/{name}')
    counts[name] = spark.read.format('delta').load(f'{gold}/snapshots/{run_id}/{name}').count()
    display(df.limit(10))
result = {'layer':'gold','run_id':run_id,'counts':counts,'net_sales':str(fact_total),'validation':'passed'}
dbutils.fs.put(f'{gold}/manifests/{run_id}.json',json.dumps(result),True)
# Publish only after all three layers are complete and reconciled.
dbutils.fs.put(f'{gold}/latest_successful_run.json',json.dumps(result),True)
dbutils.notebook.exit(json.dumps(result))
