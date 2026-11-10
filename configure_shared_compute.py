import json
from azure_ops import adb,arm,ROOT

cluster_config={
    'cluster_name':'saleslt-medallion-adf',
    'spark_version':'19.x-scala2.13','node_type_id':'Standard_D4ds_v4','num_workers':0,
    'autotermination_minutes':15,
    'spark_conf':{'spark.databricks.cluster.profile':'singleNode','spark.master':'local[*, 4]'},
    'custom_tags':{'ResourceClass':'SingleNode','Project':'SalesLT-Medallion'},
    'data_security_mode':'SINGLE_USER','single_user_name':'8e3a1b6b-d69a-43da-85bb-58d3ee19183b',
    'azure_attributes':{'availability':'ON_DEMAND_AZURE','first_on_demand':1}}
existing=next((c for c in adb('GET','2.0/clusters/list').get('clusters',[]) if c['cluster_name']=='saleslt-medallion-adf'),None)
cluster={'cluster_id':existing['cluster_id']} if existing else adb('POST','2.0/clusters/create',cluster_config)
cluster_id=cluster['cluster_id']
(ROOT/'shared_compute.json').write_text(json.dumps(cluster,indent=2))
adb('PATCH','2.0/permissions/clusters/'+cluster_id,{'access_control_list':[{'service_principal_name':'8e3a1b6b-d69a-43da-85bb-58d3ee19183b','permission_level':'CAN_RESTART'}]})
ls={'properties':{'type':'AzureDatabricks','description':'Shared dedicated single-node compute for five-minute SalesLT pipeline.', 'typeProperties':{
    'domain':'https://adb-7405619275354638.18.azuredatabricks.net','authentication':'MSI',
    'workspaceResourceId':'/subscriptions/c2383fdd-26a3-44a8-9d61-2c7f2e1e08bf/resourceGroups/AMIT_Azure_retail/providers/Microsoft.Databricks/workspaces/azuredatabricks_retail_sales',
    'existingClusterId':cluster_id}}}
arm('PUT','/linkedservices/ls_saleslt_shared_compute',ls)
(ROOT/'adf/ls_saleslt_shared_compute.json').write_text(json.dumps(ls,indent=2))
if (ROOT/'medallion_run.json').exists():
    run_id=json.loads((ROOT/'medallion_run.json').read_text())['runId']
    status=arm('GET','/pipelineruns/'+run_id)['status']
    if status in ['InProgress','Queued']:
        arm('POST','/pipelineruns/'+run_id+'/cancel?isRecursive=true')
pipeline=json.loads((ROOT/'adf/pl_saleslt_medallion.json').read_text())
for activity in pipeline['properties']['activities']:
    if activity['type']=='DatabricksNotebook':
        activity['linkedServiceName']['referenceName']='ls_saleslt_shared_compute'
arm('PUT','/pipelines/pl_saleslt_medallion',pipeline)
(ROOT/'adf/pl_saleslt_medallion.json').write_text(json.dumps(pipeline,indent=2))
run=arm('POST','/pipelines/pl_saleslt_medallion/createRun',{})
(ROOT/'medallion_run.json').write_text(json.dumps(run,indent=2))
print(json.dumps({'cluster_id':cluster_id,**run}))
