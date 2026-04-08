import requests, ssl, sys
print("PYTHON:", sys.executable)
print("REQUESTS:", requests.__version__)
print("SSL:", ssl.OPENSSL_VERSION)

import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

from langchain.agents import create_agent
from langchain.tools import tool

from .models import Snapshot, JobReqResult

def search_jobs_on_linkedin(jobreq_result_id: int, location: str, keyword: str, country: str = "US"):
    print("Starting search_jobs_on_linkedin")
    print(os.getenv('BRIGHTDATA_API_KEY'))

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

    print("REQUEST BODY:", {
    "input": data
    })

    import certifi

    response = requests.post(
        url,
        headers=headers,
        params=params,
        json=data,
        timeout=30,
        verify=certifi.where()
    )
        # Let caller handle errors
    return response


def fetch_data_with_retry(jobreq_result_id, jobKeyword: str, jobLocation: str, jobType: str, jobRemote: str, retries=3, delay=10):
    print("Starting fetch_data_with_retry")

    for i in range(retries):
        try:
            print(f"Attempt {i} launched")
            print(os.getenv('BRIGHTDATA_API_KEY'))


            response = search_jobs_on_linkedin(
                jobreq_result_id,
                location=jobLocation,
                keyword=jobKeyword,
                country="US"
            )

            response.raise_for_status()

            print("Success!")

            snapshot_id = response.json().get("snapshot_id")

            jobreq_result = JobReqResult.objects.get(id=jobreq_result_id)

            snapshot = Snapshot(
                snapshot_id = snapshot_id,
                ready = False,
                jobreq_result = jobreq_result,
                data = {}
            )
            snapshot.save()

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


from .models import JobReqResult


def start_job_search(jobreq_result_id: int, jobKeyword: str, jobLocation: str, jobType: str, jobRemote: str, source: list[str]):

    print(f"  keyword: {jobKeyword}  location: {jobLocation}  type:  {jobType}  remote: {jobRemote}")
    print(f"Starting job search for {jobreq_result_id}")

    return fetch_data_with_retry(jobreq_result_id, jobKeyword, jobLocation, jobType, jobRemote)


""" def set_results_title(jobreq_result_id: int, title: str) -> str:
    jobreq_result = JobReqResult.objects.get(id=jobreq_result_id)
    jobreq_result.title = title
    jobreq_result.save()

    return "Success"

 """
def is_ready(snapshot_id: str) -> bool:
    url = f'https://api.brightdata.com/datasets/v3/progress/{snapshot_id}'

    headers = {
        "Authorization": f"Bearer {os.getenv('BRIGHTDATA_API_KEY')}",
        "Content-Type": "application/json",
    }

    return requests.get(url, headers=headers).json()['status'] == 'ready'
    

def get_data(snapshot_id: str) -> dict:
    url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}?format=json"

    headers = {
        "Authorization": f"Bearer {os.getenv('BRIGHTDATA_API_KEY')}",
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)

    response.raise_for_status()

    return response.json()

