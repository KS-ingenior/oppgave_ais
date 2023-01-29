import requests

processor_id = "0185101b-19ab-1e53-a6d7-e825d69331c4"
url = f"http://localhost:8443/nifi-api/processors/{processor_id}/run-status"
headers = {
    "Content-Type": "application/json"
}
payload = {"state": "STOPPED"}

response = requests.put(url, headers=headers, json=payload)

if response.status_code == 200:
    print("Successful PUT request")
else:
    print("PUT request failed")
