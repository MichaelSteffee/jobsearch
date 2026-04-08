# code:: ipython3
import requests, ssl, sys
print("PYTHON:", sys.executable)
print("REQUESTS:", requests.__version__)
print("SSL:", ssl.OPENSSL_VERSION)

import time
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

os.getenv("BRIGHTDATA_API_KEY")

 
# code:: ipython3

    
class LLMResult:
    title: str
    prompt: str
    status: str
    owner: str

        
class Snapshot:
    def __init__(self, snapshot_id, ready=False, data=None, llm_result=None):
        self.snapshot_id = snapshot_id
        self.ready = ready
        self.data = data or {}
        self.llm_result = llm_result

    

# code:: ipython3

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def search_jobs_on_linkedin(location: str, keyword: str, country: str = "US"):
    url = "https://api.brightdata.com/datasets/v3/trigger"

    headers = {
        "Authorization": f"Bearer {os.getenv('BRIGHTDATA_API_KEY')}",
        "Content-Type": "application/json",
    }

    params = {
        "dataset_id": "gd_lpfll7v5hcqtkxl6l",
        "include_errors": "true",
        "type": "discover_new",
        "discover_by": "keyword",
        "limit_per_input": "5"
    }

    data = [{
        "location": location,
        "keyword": keyword,
        "country": country,
        "time_range": "Past month",
    }]

    response = requests.post(url, headers=headers, params=params, json=data, timeout=10)

    # Let caller handle errors
    return response

# code:: ipython3

import time
import requests

def fetch_data_with_retry(retries=3, delay=10):
    for i in range(retries):
        try:
            response = search_jobs_on_linkedin(
                location="Eureka",
                keyword="ERP Analyst",
                country="US"
            )

            response.raise_for_status()

            print("Success!")

            snapshot_id = response.json().get("snapshot_id")

            return {
                "snapshot_id": snapshot_id,
                "data": response.json()
            }

        except requests.exceptions.RequestException as e:
            print(f"Attempt {i+1} failed: {e}")

            if i < retries - 1:
                print(f"Waiting {delay} seconds...")
                time.sleep(delay)
            else:
                print("Max retries reached.")
                raise

# code:: ipython3

result = fetch_data_with_retry()

snapshot = Snapshot(
    snapshot_id=result["snapshot_id"],
    ready=False,
    data=result["data"]
)

print(snapshot.snapshot_id)
