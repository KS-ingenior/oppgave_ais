import requests

processor_id = "your_processor_id"
url = f"http://localhost:8080/nifi-api/processors/{processor_id}/run-status"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer {access_token}"
}
payload = {"state": "STOPPED"}

response = requests.put(url, headers=headers, json=payload)

if response.status_code == 200:
    print("Successful PUT request")
else:
    print("PUT request failed")
