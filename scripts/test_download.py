import requests

url = 'http://127.0.0.1:8000/reconcile?download=true'
files = {
    'plan_file': open('tests/samples/plan.xlsx','rb'),
    'actual_file': open('tests/samples/actual.xlsx','rb'),
    'prescription_file': open('tests/samples/prescription.xlsx','rb'),
}

resp = requests.post(url, files=files)
print('status', resp.status_code, 'content-type', resp.headers.get('content-type'))
with open('tests/samples/download-test.xlsx', 'wb') as f:
    f.write(resp.content)
print('download size', len(resp.content))
print('first bytes', resp.content[:10])
