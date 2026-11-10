import json,sys
from datetime import datetime,timezone,timedelta
from azure_ops import arm,ROOT

name='tr_saleslt_every_5_minutes'
action=sys.argv[1] if len(sys.argv)>1 else 'status'
if action=='start':
    # Require a completed validation before enabling the recurring workload.
    run_id=json.loads((ROOT/'medallion_run.json').read_text())['runId']
    assert arm('GET','/pipelineruns/'+run_id)['status']=='Succeeded', 'Validate the pipeline before starting its trigger'
    start=datetime.now(timezone.utc)+timedelta(minutes=1)
    start=start.replace(second=0,microsecond=0)
    body={'properties':{'description':'Run the SalesLT medallion pipeline every five minutes. Pipeline concurrency is one.',
        'type':'ScheduleTrigger','typeProperties':{'recurrence':{'frequency':'Minute','interval':5,'startTime':start.isoformat().replace('+00:00','Z'),'timeZone':'UTC'}},
        'pipelines':[{'pipelineReference':{'referenceName':'pl_saleslt_medallion','type':'PipelineReference'},'parameters':{}}]}}
    arm('PUT','/triggers/'+name,body)
    (ROOT/'adf'/f'{name}.json').write_text(json.dumps(body,indent=2))
    arm('POST','/triggers/'+name+'/start')
elif action=='stop':
    arm('POST','/triggers/'+name+'/stop')
elif action!='status':
    raise SystemExit('Usage: python configure_trigger.py [start|stop|status]')
trigger=arm('GET','/triggers/'+name)
print(json.dumps(trigger['properties'],indent=2))
(ROOT/'trigger_status.json').write_text(json.dumps(trigger['properties'],indent=2))
