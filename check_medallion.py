import json
from azure_ops import arm, adb, ROOT

run_id=json.loads((ROOT/'medallion_run.json').read_text())['runId']
run=arm('GET','/pipelineruns/'+run_id)
activities=arm('POST',f'/pipelineruns/{run_id}/queryActivityruns',{'lastUpdatedAfter':'2026-11-09T00:00:00Z','lastUpdatedBefore':'2026-11-15T00:00:00Z'})
result={'run_id':run_id,'status':run['status'],'activities':[]}
for activity in activities.get('value',[]):
    row={k:activity.get(k) for k in ['activityName','activityType','status']}
    if activity.get('error',{}).get('message'): row['error']=activity['error']['message']
    output=activity.get('output') or {}
    for k in ['rowsRead','rowsCopied','runOutput','runPageUrl']:
        if k in output: row[k]=output[k]
    result['activities'].append(row)
print(json.dumps(result,indent=2))
(ROOT/'medallion_status.json').write_text(json.dumps(result,indent=2))
