import base64, json, pytds, certifi
from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient
from azure_ops import az, token, adb, arm, ROOT

ADF_OBJECT_ID = '64dec3f9-af47-443f-93b1-fe3a9f9145a2'
ADF_APP_ID = '8e3a1b6b-d69a-43da-85bb-58d3ee19183b'
scope = 'saleslt-medallion'

# SQL permission is restricted to reading the source schema.
with pytds.connect('keystoneade3sqlsrvr.database.windows.net',database='keystonesqldb1',access_token_callable=lambda:token('https://database.windows.net/'),cafile=certifi.where(),autocommit=True,login_timeout=60) as conn:
    cur=conn.cursor()
    import uuid
    # Azure SQL stores the client/application ID in a service principal user's SID.
    sid = uuid.UUID(ADF_APP_ID).bytes_le.hex()
    cur.execute(f"IF DATABASE_PRINCIPAL_ID('shortkart-retail-1520') IS NULL CREATE USER [shortkart-retail-1520] WITH SID=0x{sid}, TYPE=E; GRANT SELECT ON SCHEMA::SalesLT TO [shortkart-retail-1520];")
    while cur.nextset(): pass
print('SQL schema reader configured',flush=True)

key = az('storage','account','keys','list','-g','AMIT_Azure_retail','-n','adlsgenvs5')[0]['value']
blob = BlobServiceClient('https://adlsgenvs5.blob.core.windows.net',credential=key)
for container in ['bronze','silver','gold']:
    try: blob.create_container(container)
    except ResourceExistsError: pass
try:
    adb('POST','2.0/secrets/scopes/create',{'scope':scope,'scope_backend_type':'DATABRICKS'})
except RuntimeError as exc:
    if 'RESOURCE_ALREADY_EXISTS' not in str(exc): raise
adb('POST','2.0/secrets/put',{'scope':scope,'key':'storage-key','string_value':key})
adb('POST','2.0/secrets/acls/put',{'scope':scope,'principal':ADF_APP_ID,'permission':'READ'})
del key
print('Private layer containers and secret access configured',flush=True)

adb('POST','2.0/workspace/mkdirs',{'path':'/Shared/SalesLT_Medallion'})
for path in sorted((ROOT/'notebooks').glob('*.py')):
    adb('POST','2.0/workspace/import',{'path':'/Shared/SalesLT_Medallion/'+path.stem,'language':'PYTHON','format':'SOURCE','overwrite':True,'content':base64.b64encode(path.read_bytes()).decode()})
print('Three notebooks uploaded',flush=True)

def expr(value): return {'value':value,'type':'Expression'}
def ref(name,kind='DatasetReference',parameters=None):
    d={'referenceName':name,'type':kind}
    if parameters: d['parameters']=parameters
    return d
def succeeded(name): return [{'activity':name,'dependencyConditions':['Succeeded']}]
def deploy(kind,name,properties):
    body={'properties':properties}
    dest=ROOT/'adf'; dest.mkdir(exist_ok=True)
    (dest/(name+'.json')).write_text(json.dumps(body,indent=2))
    arm('PUT',f'/{kind}/{name}',body)

deploy('linkedservices','ls_saleslt_sql_mi',{
    'type':'AzureSqlDatabase','typeProperties':{
        'connectionString':'integrated security=False;encrypt=True;connection timeout=30;data source=keystoneade3sqlsrvr.database.windows.net;initial catalog=keystonesqldb1',
        'authenticationType':'SystemAssignedManagedIdentity'}})
deploy('datasets','ds_saleslt_sql',{'type':'AzureSqlTable','linkedServiceName':ref('ls_saleslt_sql_mi','LinkedServiceReference'),'typeProperties':{'schema':'SalesLT','table':'Customer'}})
deploy('datasets','ds_saleslt_raw_parquet',{'type':'Parquet','linkedServiceName':ref('ls_shopkart_adls_gen2','LinkedServiceReference'),
    'parameters':{'run_id':{'type':'String'},'table_name':{'type':'String'}},
    'typeProperties':{'location':{'type':'AzureBlobFSLocation','fileSystem':'bronze','folderPath':expr("@concat('saleslt/raw/',dataset().run_id,'/',dataset().table_name)")},'compressionCodec':'snappy'}})

metadata_query = """SELECT t.name AS TableName,
COALESCE((SELECT STRING_AGG(CAST(QUOTENAME(c.name) AS nvarchar(max)),',') WITHIN GROUP (ORDER BY ic.key_ordinal) FROM sys.indexes i JOIN sys.index_columns ic ON i.object_id=ic.object_id AND i.index_id=ic.index_id JOIN sys.columns c ON c.object_id=ic.object_id AND c.column_id=ic.column_id WHERE i.object_id=t.object_id AND i.is_primary_key=1),'') AS QuotedPrimaryKeys,
COALESCE((SELECT STRING_AGG(CAST(c.name AS nvarchar(max)),',') WITHIN GROUP (ORDER BY ic.key_ordinal) FROM sys.indexes i JOIN sys.index_columns ic ON i.object_id=ic.object_id AND i.index_id=ic.index_id JOIN sys.columns c ON c.object_id=ic.object_id AND c.column_id=ic.column_id WHERE i.object_id=t.object_id AND i.is_primary_key=1),'') AS PrimaryKeys,
'SELECT '+(SELECT STRING_AGG(CAST(CASE WHEN TYPE_NAME(c.system_type_id)='xml' THEN 'CAST('+QUOTENAME(c.name)+' AS nvarchar(max)) AS '+QUOTENAME(c.name) ELSE QUOTENAME(c.name) END AS nvarchar(max)),',') WITHIN GROUP (ORDER BY c.column_id) FROM sys.columns c WHERE c.object_id=t.object_id)+' FROM [SalesLT].'+QUOTENAME(t.name) AS SelectQuery
FROM sys.tables t WHERE t.schema_id=SCHEMA_ID('SalesLT') ORDER BY t.name"""
lookup={'name':'Discover_SalesLT_Tables','type':'Lookup','policy':{'timeout':'0.00:10:00','retry':1,'retryIntervalInSeconds':30},'typeProperties':{'source':{'type':'AzureSqlSource','sqlReaderQuery':metadata_query,'queryTimeout':'00:05:00'},'dataset':ref('ds_saleslt_sql'),'firstRowOnly':False}}
copy={'name':'Copy_SQL_Table_to_Bronze_Raw','type':'Copy','policy':{'timeout':'0.00:20:00','retry':1,'retryIntervalInSeconds':30},
    'inputs':[ref('ds_saleslt_sql')],
    'outputs':[ref('ds_saleslt_raw_parquet',parameters={'run_id':expr('@pipeline().RunId'),'table_name':expr('@item().TableName')})],
    'typeProperties':{'source':{'type':'AzureSqlSource','sqlReaderQuery':expr('@item().SelectQuery'),'queryTimeout':'00:10:00'},'sink':{'type':'ParquetSink','storeSettings':{'type':'AzureBlobFSWriteSettings'},'formatSettings':{'type':'ParquetWriteSettings'}},'enableStaging':False}}
extract={'name':'Extract_SalesLT_to_Blob','type':'ForEach','dependsOn':succeeded('Discover_SalesLT_Tables'),'typeProperties':{'items':expr("@activity('Discover_SalesLT_Tables').output.value"),'isSequential':False,'batchCount':4,'activities':[copy]}}
activities=[lookup,extract]
previous='Extract_SalesLT_to_Blob'
for name,notebook in [('Bronze','01_bronze'),('Silver','02_silver'),('Gold','03_gold')]:
    params={'run_id':expr('@pipeline().RunId')}
    if name=='Bronze': params['tables_json']=expr("@string(activity('Discover_SalesLT_Tables').output.value)")
    activities.append({'name':name+'_Notebook','type':'DatabricksNotebook','dependsOn':succeeded(previous),
        'policy':{'timeout':'0.00:30:00','retry':0,'retryIntervalInSeconds':30},
        'linkedServiceName':ref('ls_adb_retail_managed_identity','LinkedServiceReference'),
        'typeProperties':{'notebookPath':'/Shared/SalesLT_Medallion/'+notebook,'baseParameters':params}})
    previous=name+'_Notebook'
deploy('pipelines','pl_saleslt_medallion',{'description':'SalesLT SQL full snapshot → Bronze → Silver → Gold. Three separate notebook activities; immutable run folders, quality checks, and Gold Parquet exports.','concurrency':1,'activities':activities})
print('Pipeline deployed',flush=True)
print('Run configure_shared_compute.py to attach shared compute and start validation.',flush=True)
