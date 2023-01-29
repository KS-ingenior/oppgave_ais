import requests

hostname = "localhost"
port = 8443
processor_id = "0185101b-19ab-1e53-a6d7-e825d69331c4"
processor_version = 1
clientId = "your-client-id"

url = f"http://{hostname}:{port}/nifi-api/processors/{processor_id}"

headers = {
    'Content-Type': 'application/json'
}

payload = {
    "status": {
        "runStatus": "STOPPED"
    },
    "component": {
        "state": "STOPPED",
        "id": processor_id
    },
    "id": processor_id,
    "revision": {
        "version": processor_version,
        "clientId": clientId
    }
}

response = requests.put(url, headers=headers, json=payload)

if response.status_code == 200:
    print("Processor updated successfully!")
else:
    print(f"Request failed with status code: {response.status_code}")
    print(response.text)
