import re, json, pytds, certifi, requests
from azure_ops import token, ROOT

source_path = ROOT/'source/adventureworkslt.sql'
if not source_path.exists():
    response=requests.get('https://raw.githubusercontent.com/MicrosoftLearning/dp-080-Transact-SQL/95e42b8671fe63b2942ef59d5fc1db5b0c0c4edd/Scripts/adventureworkslt.sql',timeout=120)
    response.raise_for_status()
    source_path.parent.mkdir(exist_ok=True)
    source_path.write_bytes(response.content)
script = source_path.read_text(encoding='utf-16')
batches = re.split(r'^\s*GO\s*$',script,flags=re.M|re.I)
# Target the existing database; preserve its departments table and settings.
batches = [b for b in batches if not re.search(r'\b(?:CREATE DATABASE|ALTER DATABASE|USE adventureworks)\b',b,re.I)]
with pytds.connect('keystoneade3sqlsrvr.database.windows.net',database='keystonesqldb1',access_token_callable=lambda:token('https://database.windows.net/'),cafile=certifi.where(),autocommit=False,timeout=180,login_timeout=60) as conn:
    cur=conn.cursor()
    cur.execute("SELECT COUNT(*) FROM sys.tables WHERE schema_id=SCHEMA_ID('SalesLT')")
    assert cur.fetchone()[0] == 0, 'SalesLT already populated; refusing to replace it'
    try:
        for i,batch in enumerate(batches):
            if batch.strip():
                cur.execute(batch)
                while cur.nextset(): pass
            if i%25==0: print(f'Loaded batch {i}/{len(batches)}',flush=True)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    cur.execute("SELECT t.name,SUM(p.rows) FROM sys.tables t JOIN sys.partitions p ON p.object_id=t.object_id AND p.index_id IN (0,1) WHERE t.schema_id=SCHEMA_ID('SalesLT') GROUP BY t.name ORDER BY t.name")
    counts=dict(cur.fetchall())
    (ROOT/'source_counts.json').write_text(json.dumps(counts,indent=2))
    print(json.dumps(counts,indent=2))
