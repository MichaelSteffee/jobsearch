import requests, ssl, sys
print("PYTHON:", sys.executable)
print("REQUESTS:", requests.__version__)
print("SSL:", ssl.OPENSSL_VERSION)

import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

from .models import Snapshot, JobReqResult

# Functions to search specific Job Listing Sites
# LinkedIn and Indeed

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


def search_jobs_on_indeed(jobreq_result_id: int, location: str, keyword: str, country: str = "US"):

    print("Starting search_jobs_on_indeed")
    print(os.getenv('BRIGHTDATA_API_KEY'))

    url = "https://api.brightdata.com/datasets/v3/trigger"

    headers = {
        "Authorization": f"Bearer {os.getenv('BRIGHTDATA_API_KEY')}",
        "Content-Type": "application/json",
    }

    params = {
        "dataset_id": "gd_l4dx9j9sscpvs7no2",  # <-- change this
        "include_errors": "true",
        "type": "discover_new",
        "discover_by": "keyword",
        "limit_per_input": "5"
    }

    data = [{"country":"US",
                   "domain":"indeed.com",
                   "keyword_search": keyword,
                   "location": location,
                   "date_posted":"Last 24 hours",
                   "posted_by":"",
                   "location_radius":""
        }]

    return requests.post(url, headers=headers, params=params, json=data, timeout=30)


# function to trigger individual snapshots of each job site's listings

def fetch_data_with_retry(
    jobreq_result_id,
    jobKeyword: str,
    jobLocation: str,
    jobType: str,
    jobRemote: str,
    platform: str,
    retries=3,
    delay=10
):
    print(f"Starting fetch for {platform}")

    for i in range(retries):
        try:

            if platform == "linkedin":
                response = search_jobs_on_linkedin(
                    jobreq_result_id,
                    location=jobLocation,
                    keyword=jobKeyword,
                    country="US"
                )

            elif platform == "indeed":
                response = search_jobs_on_indeed(
                    jobreq_result_id,
                    location=jobLocation,
                    keyword=jobKeyword,
                    country="US"
                )

            else:
                raise ValueError(f"Unknown platform: {platform}")

            response.raise_for_status()

            snapshot_id = response.json().get("snapshot_id")

            jobreq_result = JobReqResult.objects.get(id=jobreq_result_id)

            snapshot = Snapshot(
                snapshot_id=snapshot_id,
                ready=False,
                jobreq_result=jobreq_result,
                data={},
                source=platform,  
            )
            snapshot.save()

            return {
                "platform": platform,
                "snapshot_id": snapshot_id,
                "data": response.json(),
            }

        except requests.exceptions.RequestException as e:
            print(f"{platform} attempt {i+1} failed: {e}")

            if i < retries - 1:
                time.sleep(delay)
            else:
                raise

# Function that passes job search form data to function 
# that creates snapshots of the listing requests

def start_job_search(
    jobreq_result_id: int,
    jobKeyword: str,
    jobLocation: str,
    jobType: str,
    jobRemote: str,
    source: list[str]
):
    print(f"Sources selected: {source}")

    results = []

    if "linkedin" in source:
        print("Running LinkedIn search")
        results.append(
            fetch_data_with_retry(
                jobreq_result_id,
                jobKeyword,
                jobLocation,
                jobType,
                jobRemote,
                platform="linkedin"
            )
        )

    if "indeed" in source:
        print("Running Indeed search")
        results.append(
            fetch_data_with_retry(
                jobreq_result_id,
                jobKeyword,
                jobLocation,
                jobType,
                jobRemote,
                platform="indeed"
            )
        )

    return results

# Functions that checks the status of snpashot running on Brightdata

def is_ready(snapshot_id: str) -> bool:
    url = f'https://api.brightdata.com/datasets/v3/progress/{snapshot_id}'

    headers = {
        "Authorization": f"Bearer {os.getenv('BRIGHTDATA_API_KEY')}",
        "Content-Type": "application/json",
    }

    return requests.get(url, headers=headers).json()['status'] == 'ready'
    
# Functions that retrieves the result of completed snpashot on Brightdata

def get_data(snapshot_id: str) -> dict:
    url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}?format=json"

    headers = {
        "Authorization": f"Bearer {os.getenv('BRIGHTDATA_API_KEY')}",
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)

    response.raise_for_status()

    return response.json()
