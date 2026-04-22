from django.test import TestCase

# Create your tests here.
from .models import Snapshot, JobListingResult, JobReqResult

# Snapshot status
for snap in Snapshot.objects.all():
    print(snap.snapshot_id, snap.ready)

# JobReq status
jobreq_results = JobReqResult.objects.prefetch_related('snapshots')

for jobreq_result in jobreq_results:
    for snapshot in jobreq_result.snapshots.all():
        print(
            jobreq_result.title,
            jobreq_result.status,
            snapshot.snapshot_id,
            snapshot.ready
        )

# JobReq Listing Details
jobreq_results = JobReqResult.objects.prefetch_related(
    'snapshots',
    'job_listing_results'
)
for jobreq_result in jobreq_results:
    snapshots = jobreq_result.snapshots.all()
    listings = jobreq_result.job_listing_results.all()
    if not snapshots:
        snapshots = [None]
    if not listings:
        listings = [None]
    for snapshot in snapshots:
        for listing in listings:
            print(
                listing.interested if listing else None,
                listing.interested_date if listing else None,
                listing.applied if listing else None,
                listing.applied_date if listing else None,
                listing.status if listing else None,
                listing.status_date if listing else None,
                jobreq_result.title,
                jobreq_result.status,
                snapshot.snapshot_id if snapshot else None,
                snapshot.ready if snapshot else None,
                listing.title if listing else None,
                listing.company_name if listing else None,
            )

# JobReq Status Details
jobreq_results = JobReqResult.objects.prefetch_related(
    'snapshots',
    'job_listing_results'
)
for jobreq_result in jobreq_results:
    snapshots = jobreq_result.snapshots.all()
    listings = jobreq_result.job_listing_results.all()
#    if not snapshots:
#        snapshots = [None]
#    if not listings:
#        listings = [None]
    for snapshot in snapshots:
        for listing in listings:
            print(
                listing.interested if listing else None,
                listing.interested_date if listing else None,
                listing.applied if listing else None,
                listing.applied_date if listing else None,
                listing.status if listing else None,
                listing.status_date if listing else None,
                jobreq_result.title[0:25],
                listing.title if listing else None,
                listing.company_name if listing else None,
            )

# User Details
jobreq_results = JobReqResult.objects.select_related('owner').prefetch_related(
    'snapshots',
    'job_listing_results'
)
for jobreq_result in jobreq_results:
    print(
        jobreq_result.owner.username,   # 👈 this is what you want
        jobreq_result.title,
        jobreq_result.status
    )
    for snapshot in jobreq_result.snapshots.all():
        print("   SNAP:", snapshot.snapshot_id, snapshot.ready)
    for listing in jobreq_result.job_listing_results.all():
        print("   JOB:", listing.title, listing.company_name, listing.source)


from django.contrib.auth.models import User
user = User.objects.filter(username="tim")
user.delete()




# curl test for brigthdata
import requests
from dotenv import load_dotenv

load_dotenv()

try:
    r = requests.get("https://api.brightdata.com", timeout=10)
    print("Status:", r.status_code)
except Exception as e:
    print("ERROR:", e)



# delete 
def delete_request(req_title):
    from .models import JobReqResult
    jobReq = JobReqResult.objects.filter(title=req_title)
    jobReq.delete()

