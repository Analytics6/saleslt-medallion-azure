# Persisted layer schemas

Schemas read from the actual stored Delta Parquet data. Nullable describes the stored physical schema; quality checks enforce additional rules.

## Bronze

### Address

| Column | Physical type | Nullable |
|---|---|---|
| AddressID | int32 | True |
| AddressLine1 | string | True |
| AddressLine2 | string | True |
| City | string | True |
| StateProvince | string | True |
| CountryRegion | string | True |
| PostalCode | string | True |
| rowguid | string | True |
| ModifiedDate | timestamp[ns] | True |
| _ingested_at | timestamp[ns] | True |
| _pipeline_run_id | string | True |
| _source_table | string | True |

### Customer

| Column | Physical type | Nullable |
|---|---|---|
| CustomerID | int32 | True |
| NameStyle | bool | True |
| Title | string | True |
| FirstName | string | True |
| MiddleName | string | True |
| LastName | string | True |
| Suffix | string | True |
| CompanyName | string | True |
| SalesPerson | string | True |
| EmailAddress | string | True |
| Phone | string | True |
| PasswordHash | string | True |
| PasswordSalt | string | True |
| rowguid | string | True |
| ModifiedDate | timestamp[ns] | True |
| _ingested_at | timestamp[ns] | True |
| _pipeline_run_id | string | True |
| _source_table | string | True |

### CustomerAddress

| Column | Physical type | Nullable |
|---|---|---|
| CustomerID | int32 | True |
| AddressID | int32 | True |
| AddressType | string | True |
| rowguid | string | True |
| ModifiedDate | timestamp[ns] | True |
| _ingested_at | timestamp[ns] | True |
| _pipeline_run_id | string | True |
| _source_table | string | True |

### Product

| Column | Physical type | Nullable |
|---|---|---|
| ProductID | int32 | True |
| Name | string | True |
| ProductNumber | string | True |
| Color | string | True |
| StandardCost | decimal128(19, 4) | True |
| ListPrice | decimal128(19, 4) | True |
| Size | string | True |
| Weight | decimal128(8, 2) | True |
| ProductCategoryID | int32 | True |
| ProductModelID | int32 | True |
| SellStartDate | timestamp[ns] | True |
| SellEndDate | timestamp[ns] | True |
| DiscontinuedDate | timestamp[ns] | True |
| ThumbNailPhoto | binary | True |
| ThumbnailPhotoFileName | string | True |
| rowguid | string | True |
| ModifiedDate | timestamp[ns] | True |
| _ingested_at | timestamp[ns] | True |
| _pipeline_run_id | string | True |
| _source_table | string | True |

### ProductCategory

| Column | Physical type | Nullable |
|---|---|---|
| ProductCategoryID | int32 | True |
| ParentProductCategoryID | int32 | True |
| Name | string | True |
| rowguid | string | True |
| ModifiedDate | timestamp[ns] | True |
| _ingested_at | timestamp[ns] | True |
| _pipeline_run_id | string | True |
| _source_table | string | True |

### ProductDescription

| Column | Physical type | Nullable |
|---|---|---|
| ProductDescriptionID | int32 | True |
| Description | string | True |
| rowguid | string | True |
| ModifiedDate | timestamp[ns] | True |
| _ingested_at | timestamp[ns] | True |
| _pipeline_run_id | string | True |
| _source_table | string | True |

### ProductModel

| Column | Physical type | Nullable |
|---|---|---|
| ProductModelID | int32 | True |
| Name | string | True |
| CatalogDescription | string | True |
| rowguid | string | True |
| ModifiedDate | timestamp[ns] | True |
| _ingested_at | timestamp[ns] | True |
| _pipeline_run_id | string | True |
| _source_table | string | True |

### ProductModelProductDescription

| Column | Physical type | Nullable |
|---|---|---|
| ProductModelID | int32 | True |
| ProductDescriptionID | int32 | True |
| Culture | string | True |
| rowguid | string | True |
| ModifiedDate | timestamp[ns] | True |
| _ingested_at | timestamp[ns] | True |
| _pipeline_run_id | string | True |
| _source_table | string | True |

### SalesOrderDetail

| Column | Physical type | Nullable |
|---|---|---|
| SalesOrderID | int32 | True |
| SalesOrderDetailID | int32 | True |
| OrderQty | int32 | True |
| ProductID | int32 | True |
| UnitPrice | decimal128(19, 4) | True |
| UnitPriceDiscount | decimal128(19, 4) | True |
| LineTotal | decimal128(38, 6) | True |
| rowguid | string | True |
| ModifiedDate | timestamp[ns] | True |
| _ingested_at | timestamp[ns] | True |
| _pipeline_run_id | string | True |
| _source_table | string | True |

### SalesOrderHeader

| Column | Physical type | Nullable |
|---|---|---|
| SalesOrderID | int32 | True |
| RevisionNumber | int32 | True |
| OrderDate | timestamp[ns] | True |
| DueDate | timestamp[ns] | True |
| ShipDate | timestamp[ns] | True |
| Status | int32 | True |
| OnlineOrderFlag | bool | True |
| SalesOrderNumber | string | True |
| PurchaseOrderNumber | string | True |
| AccountNumber | string | True |
| CustomerID | int32 | True |
| ShipToAddressID | int32 | True |
| BillToAddressID | int32 | True |
| ShipMethod | string | True |
| CreditCardApprovalCode | string | True |
| SubTotal | decimal128(19, 4) | True |
| TaxAmt | decimal128(19, 4) | True |
| Freight | decimal128(19, 4) | True |
| TotalDue | decimal128(19, 4) | True |
| Comment | string | True |
| rowguid | string | True |
| ModifiedDate | timestamp[ns] | True |
| _ingested_at | timestamp[ns] | True |
| _pipeline_run_id | string | True |
| _source_table | string | True |

## Silver

### Address

| Column | Physical type | Nullable |
|---|---|---|
| AddressID | int32 | True |
| AddressLine1 | string | True |
| AddressLine2 | string | True |
| City | string | True |
| StateProvince | string | True |
| CountryRegion | string | True |
| PostalCode | string | True |
| rowguid | string | True |
| ModifiedDate | timestamp[ns] | True |
| _ingested_at | timestamp[ns] | True |
| _pipeline_run_id | string | True |
| _source_table | string | True |
| _silver_processed_at | timestamp[ns] | True |

### Customer

| Column | Physical type | Nullable |
|---|---|---|
| CustomerID | int32 | True |
| NameStyle | bool | True |
| Title | string | True |
| FirstName | string | True |
| MiddleName | string | True |
| LastName | string | True |
| Suffix | string | True |
| CompanyName | string | True |
| SalesPerson | string | True |
| EmailAddress | string | True |
| Phone | string | True |
| PasswordHash | string | True |
| PasswordSalt | string | True |
| rowguid | string | True |
| ModifiedDate | timestamp[ns] | True |
| _ingested_at | timestamp[ns] | True |
| _pipeline_run_id | string | True |
| _source_table | string | True |
| _silver_processed_at | timestamp[ns] | True |

### CustomerAddress

| Column | Physical type | Nullable |
|---|---|---|
| CustomerID | int32 | True |
| AddressID | int32 | True |
| AddressType | string | True |
| rowguid | string | True |
| ModifiedDate | timestamp[ns] | True |
| _ingested_at | timestamp[ns] | True |
| _pipeline_run_id | string | True |
| _source_table | string | True |
| _silver_processed_at | timestamp[ns] | True |

### Product

| Column | Physical type | Nullable |
|---|---|---|
| ProductID | int32 | True |
| Name | string | True |
| ProductNumber | string | True |
| Color | string | True |
| StandardCost | decimal128(19, 4) | True |
| ListPrice | decimal128(19, 4) | True |
| Size | string | True |
| Weight | decimal128(8, 2) | True |
| ProductCategoryID | int32 | True |
| ProductModelID | int32 | True |
| SellStartDate | timestamp[ns] | True |
| SellEndDate | timestamp[ns] | True |
| DiscontinuedDate | timestamp[ns] | True |
| ThumbNailPhoto | binary | True |
| ThumbnailPhotoFileName | string | True |
| rowguid | string | True |
| ModifiedDate | timestamp[ns] | True |
| _ingested_at | timestamp[ns] | True |
| _pipeline_run_id | string | True |
| _source_table | string | True |
| _silver_processed_at | timestamp[ns] | True |

### ProductCategory

| Column | Physical type | Nullable |
|---|---|---|
| ProductCategoryID | int32 | True |
| ParentProductCategoryID | int32 | True |
| Name | string | True |
| rowguid | string | True |
| ModifiedDate | timestamp[ns] | True |
| _ingested_at | timestamp[ns] | True |
| _pipeline_run_id | string | True |
| _source_table | string | True |
| _silver_processed_at | timestamp[ns] | True |

### ProductDescription

| Column | Physical type | Nullable |
|---|---|---|
| ProductDescriptionID | int32 | True |
| Description | string | True |
| rowguid | string | True |
| ModifiedDate | timestamp[ns] | True |
| _ingested_at | timestamp[ns] | True |
| _pipeline_run_id | string | True |
| _source_table | string | True |
| _silver_processed_at | timestamp[ns] | True |

### ProductModel

| Column | Physical type | Nullable |
|---|---|---|
| ProductModelID | int32 | True |
| Name | string | True |
| CatalogDescription | string | True |
| rowguid | string | True |
| ModifiedDate | timestamp[ns] | True |
| _ingested_at | timestamp[ns] | True |
| _pipeline_run_id | string | True |
| _source_table | string | True |
| _silver_processed_at | timestamp[ns] | True |

### ProductModelProductDescription

| Column | Physical type | Nullable |
|---|---|---|
| ProductModelID | int32 | True |
| ProductDescriptionID | int32 | True |
| Culture | string | True |
| rowguid | string | True |
| ModifiedDate | timestamp[ns] | True |
| _ingested_at | timestamp[ns] | True |
| _pipeline_run_id | string | True |
| _source_table | string | True |
| _silver_processed_at | timestamp[ns] | True |

### SalesOrderDetail

| Column | Physical type | Nullable |
|---|---|---|
| SalesOrderID | int32 | True |
| SalesOrderDetailID | int32 | True |
| OrderQty | int32 | True |
| ProductID | int32 | True |
| UnitPrice | decimal128(19, 4) | True |
| UnitPriceDiscount | decimal128(19, 4) | True |
| LineTotal | decimal128(38, 6) | True |
| rowguid | string | True |
| ModifiedDate | timestamp[ns] | True |
| _ingested_at | timestamp[ns] | True |
| _pipeline_run_id | string | True |
| _source_table | string | True |
| _silver_processed_at | timestamp[ns] | True |

### SalesOrderHeader

| Column | Physical type | Nullable |
|---|---|---|
| SalesOrderID | int32 | True |
| RevisionNumber | int32 | True |
| OrderDate | timestamp[ns] | True |
| DueDate | timestamp[ns] | True |
| ShipDate | timestamp[ns] | True |
| Status | int32 | True |
| OnlineOrderFlag | bool | True |
| SalesOrderNumber | string | True |
| PurchaseOrderNumber | string | True |
| AccountNumber | string | True |
| CustomerID | int32 | True |
| ShipToAddressID | int32 | True |
| BillToAddressID | int32 | True |
| ShipMethod | string | True |
| CreditCardApprovalCode | string | True |
| SubTotal | decimal128(19, 4) | True |
| TaxAmt | decimal128(19, 4) | True |
| Freight | decimal128(19, 4) | True |
| TotalDue | decimal128(19, 4) | True |
| Comment | string | True |
| rowguid | string | True |
| ModifiedDate | timestamp[ns] | True |
| _ingested_at | timestamp[ns] | True |
| _pipeline_run_id | string | True |
| _source_table | string | True |
| _silver_processed_at | timestamp[ns] | True |

## Gold

### dim_customer

| Column | Physical type | Nullable |
|---|---|---|
| CustomerID | int32 | True |
| Title | string | True |
| FirstName | string | True |
| MiddleName | string | True |
| LastName | string | True |
| Suffix | string | True |
| CompanyName | string | True |
| SalesPerson | string | True |
| EmailAddress | string | True |
| Phone | string | True |
| _pipeline_run_id | string | True |
| _gold_processed_at | timestamp[ns] | True |

### dim_date

| Column | Physical type | Nullable |
|---|---|---|
| Date | date32[day] | True |
| Year | int32 | True |
| Quarter | int32 | True |
| Month | int32 | True |
| Day | int32 | True |
| _pipeline_run_id | string | True |
| _gold_processed_at | timestamp[ns] | True |

### dim_product

| Column | Physical type | Nullable |
|---|---|---|
| ProductID | int32 | True |
| ProductName | string | True |
| ProductNumber | string | True |
| Color | string | True |
| Size | string | True |
| Weight | decimal128(8, 2) | True |
| StandardCost | decimal128(19, 4) | True |
| ListPrice | decimal128(19, 4) | True |
| ProductCategoryID | int32 | True |
| CategoryName | string | True |
| ParentCategoryName | string | True |
| ProductModelID | int32 | True |
| ModelName | string | True |
| _pipeline_run_id | string | True |
| _gold_processed_at | timestamp[ns] | True |

### fact_order

| Column | Physical type | Nullable |
|---|---|---|
| SalesOrderID | int32 | True |
| CustomerID | int32 | True |
| OrderDate | date32[day] | True |
| DueDate | date32[day] | True |
| ShipDate | date32[day] | True |
| OrderStatus | int32 | True |
| SubTotal | decimal128(19, 4) | True |
| TaxAmt | decimal128(19, 4) | True |
| Freight | decimal128(19, 4) | True |
| TotalDue | decimal128(19, 4) | True |
| _pipeline_run_id | string | True |
| _gold_processed_at | timestamp[ns] | True |

### fact_sales

| Column | Physical type | Nullable |
|---|---|---|
| SalesOrderID | int32 | True |
| SalesOrderDetailID | int32 | True |
| CustomerID | int32 | True |
| ProductID | int32 | True |
| OrderDate | date32[day] | True |
| OrderStatus | int32 | True |
| OrderQty | int32 | True |
| UnitPrice | decimal128(19, 4) | True |
| UnitPriceDiscount | decimal128(19, 4) | True |
| GrossSales | decimal128(20, 4) | True |
| DiscountAmount | decimal128(20, 4) | True |
| NetSales | decimal128(20, 4) | True |
| ShipToAddressID | int32 | True |
| BillToAddressID | int32 | True |
| _pipeline_run_id | string | True |
| _gold_processed_at | timestamp[ns] | True |

### sales_by_customer

| Column | Physical type | Nullable |
|---|---|---|
| CustomerID | int32 | True |
| Orders | int64 | True |
| Units | int64 | True |
| NetSales | decimal128(30, 4) | True |
| _pipeline_run_id | string | True |
| _gold_processed_at | timestamp[ns] | True |

### sales_by_day

| Column | Physical type | Nullable |
|---|---|---|
| OrderDate | date32[day] | True |
| Orders | int64 | True |
| Customers | int64 | True |
| Units | int64 | True |
| GrossSales | decimal128(30, 4) | True |
| DiscountAmount | decimal128(30, 4) | True |
| NetSales | decimal128(30, 4) | True |
| _pipeline_run_id | string | True |
| _gold_processed_at | timestamp[ns] | True |

### sales_by_product

| Column | Physical type | Nullable |
|---|---|---|
| ProductID | int32 | True |
| ProductName | string | True |
| CategoryName | string | True |
| Orders | int64 | True |
| Units | int64 | True |
| NetSales | decimal128(30, 4) | True |
| _pipeline_run_id | string | True |
| _gold_processed_at | timestamp[ns] | True |
