import requests

hostname = "localhost"
port = 8443
processor_id = "0185101b-19ab-1e53-a6d7-e825d69331c4"

url = f"http://{hostname}:{port}/nifi-api/processors/{processor_id}"

response = requests.get(url)

if response.status_code == 200:
    processor = response.json()
    try:
        revision = processor['revision']
        client_id = revision['clientId']
        print(f"Client ID: {client_id}")
    except KeyError:
        print("Response does not contain a 'clientId' key.")
else:
    print(f"Request failed with status code: {response.status_code}")
    print(response.text)
