import io,json,decimal,datetime
import pyarrow.parquet as pq
import pytds,certifi
from azure.storage.blob import BlobServiceClient
from azure_ops import az,token,arm,ROOT

run_id=json.loads((ROOT/'medallion_run.json').read_text())['runId']
run=arm('GET','/pipelineruns/'+run_id)
assert run['status']=='Succeeded',run['status']
key=az('storage','account','keys','list','-g','AMIT_Azure_retail','-n','adlsgenvs5')[0]['value']
service=BlobServiceClient('https://adlsgenvs5.blob.core.windows.net',credential=key)
del key

def read_json(container,path):
    return json.loads(service.get_blob_client(container,path).download_blob().readall())

def read_delta(container,name):
    prefix=f'saleslt/snapshots/{run_id}/{name}/'
    client=service.get_container_client(container)
    logs=sorted(b.name for b in client.list_blobs(name_starts_with=prefix+'_delta_log/') if b.name.endswith('.json'))
    assert logs, f'Missing Delta log: {container}/{name}'
    active={}
    for path in logs:
        for line in client.download_blob(path).readall().decode().splitlines():
            item=json.loads(line)
            if 'add' in item: active[item['add']['path']]=item['add']
            if 'remove' in item: active.pop(item['remove']['path'],None)
    frames=[pq.read_table(io.BytesIO(client.download_blob(prefix+p).readall())) for p in active]
    return sum(f.num_rows for f in frames),frames

manifests={layer:read_json(layer,f'saleslt/manifests/{run_id}.json') for layer in ['bronze','silver','gold']}
with pytds.connect('keystoneade3sqlsrvr.database.windows.net',database='keystonesqldb1',access_token_callable=lambda:token('https://database.windows.net/'),cafile=certifi.where(),autocommit=True,login_timeout=60) as conn:
    cur=conn.cursor()
    cur.execute("SELECT t.name,SUM(p.rows) FROM sys.tables t JOIN sys.partitions p ON p.object_id=t.object_id AND p.index_id IN (0,1) WHERE t.schema_id=SCHEMA_ID('SalesLT') GROUP BY t.name")
    source_counts=dict(cur.fetchall())
    cur.execute('SELECT SUM(CAST(LineTotal AS decimal(20,4))) FROM SalesLT.SalesOrderDetail')
    source_net=cur.fetchone()[0]
persisted={layer:{} for layer in manifests}
schemas={layer:{} for layer in manifests}
for table,expected in source_counts.items():
    for layer in ['bronze','silver']:
        count,frames=read_delta(layer,table)
        if frames: schemas[layer][table]=[{'name':f.name,'type':str(f.type),'nullable':f.nullable} for f in frames[0].schema]
        persisted[layer][table]=count
        assert count==expected,(layer,table,count,expected)
    assert manifests['silver']['metrics'][table]['rejected_rows']==0
    assert manifests['silver']['metrics'][table]['duplicate_rows_removed']==0
gold_net=decimal.Decimal(0)
samples={}
for table,expected in manifests['gold']['counts'].items():
    count,frames=read_delta('gold',table)
    if frames: schemas['gold'][table]=[{'name':f.name,'type':str(f.type),'nullable':f.nullable} for f in frames[0].schema]
    persisted['gold'][table]=count
    assert count==expected,(table,count,expected)
    if table=='fact_sales':
        for frame in frames:
            gold_net+=sum(frame.column('NetSales').to_pylist(),decimal.Decimal(0))
    if table in ['sales_by_day','sales_by_product']:
        rows=[r for frame in frames for r in frame.to_pylist()]
        rows=sorted(rows,key=lambda r:r['NetSales'],reverse=True)
        samples[table]=rows[:10]
assert gold_net==source_net,(gold_net,source_net)
latest=read_json('gold','saleslt/latest_successful_run.json')
assert latest['run_id']==run_id
result={'run_id':run_id,'pipeline_status':run['status'],'run_start_utc':run['runStart'],'run_end_utc':run.get('runEnd'),
    'source_counts':source_counts,'persisted_counts':persisted,'silver_metrics':manifests['silver']['metrics'],
    'source_net_sales':str(source_net),'gold_net_sales':str(gold_net),'validation':'passed',
    'samples':samples}
docs=ROOT/'docs'; docs.mkdir(exist_ok=True)
(docs/'results.json').write_text(json.dumps(result,indent=2,default=str))
lines=['# Verified deployment results','',f"Manual pipeline run: `{run_id}`",'',f"Status: **{run['status']}**. Storage verification: **passed**.",'',
    f"Run start (UTC): {run['runStart']}",f"Run end (UTC): {run.get('runEnd')}",'',
    'Counts below were independently read from active Delta files in Blob Storage, using Delta transaction logs. SQL counts and line totals were queried independently.','',
    '| Source table | SQL | Bronze | Silver |','|---|---:|---:|---:|']
for t,c in sorted(source_counts.items()): lines.append(f"| {t} | {c} | {persisted['bronze'][t]} | {persisted['silver'][t]} |")
lines+=['','All Silver rejection and duplicate-removal counts were zero.','','| Gold dataset | Persisted rows |','|---|---:|']
for t,c in sorted(persisted['gold'].items()): lines.append(f'| {t} | {c} |')
lines+=['',f'Azure SQL net sales: **{source_net}**. Persisted Gold net sales: **{gold_net}**. Totals match.','',
    '## Highest-selling products','','| Product | Units | Net sales |','|---|---:|---:|']
for r in samples['sales_by_product']: lines.append(f"| {r['ProductName']} | {r['Units']} | {r['NetSales']} |")
lines+=['','See [results.json](results.json) for complete machine-readable evidence.','']
(docs/'VALIDATION.md').write_text('\n'.join(lines))
schema_lines=['# Persisted layer schemas','','Schemas read from the actual stored Delta Parquet data. Nullable describes the stored physical schema; quality checks enforce additional rules.','']
for layer,tables in schemas.items():
    schema_lines += [f'## {layer.title()}','']
    for name,fields in sorted(tables.items()):
        schema_lines += [f'### {name}','','| Column | Physical type | Nullable |','|---|---|---|']
        schema_lines += [f"| {f['name']} | {f['type']} | {f['nullable']} |" for f in fields]
        schema_lines.append('')
(docs/'SCHEMAS.md').write_text('\n'.join(schema_lines))
print(json.dumps({k:v for k,v in result.items() if k not in ['samples','silver_metrics']},indent=2))
