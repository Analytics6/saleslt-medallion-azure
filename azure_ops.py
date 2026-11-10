import json, subprocess, requests, time
from pathlib import Path

HOST = 'https://adb-7405619275354638.18.azuredatabricks.net'
FACTORY = 'https://management.azure.com/subscriptions/c2383fdd-26a3-44a8-9d61-2c7f2e1e08bf/resourceGroups/AMIT_Azure_retail/providers/Microsoft.DataFactory/factories/shortkart-retail-1520'
ROOT = Path(__file__).parent

def az(*args):
    return json.loads(subprocess.check_output(['az.cmd', *args, '-o', 'json'], text=True))

def token(resource):
    return az('account', 'get-access-token', '--resource', resource)['accessToken']

def adb(method, path, body=None):
    r = requests.request(method, HOST+'/api/'+path, headers={'Authorization':'Bearer '+token('2ff814a6-3304-4ab8-85cb-cd0e6f879c1d')}, json=body, timeout=90)
    if not r.ok:
        raise RuntimeError(f'Databricks {r.status_code}: {r.text[:1500]}')
    return r.json() if r.content else {}

def arm(method, path, body=None):
    r = requests.request(method, FACTORY+path+('&' if '?' in path else '?')+'api-version=2018-06-01', headers={'Authorization':'Bearer '+token('https://management.azure.com/')}, json=body, timeout=90)
    if not r.ok:
        raise RuntimeError(f'ARM {r.status_code}: {r.text[:1500]}')
    return r.json() if r.content else {}
