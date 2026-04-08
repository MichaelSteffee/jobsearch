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

# JobReq Details
jobreq_results = JobReqResult.objects.prefetch_related(
    'snapshots',
    'job_listing_results'
)

for jobreq_result in jobreq_results:
    snapshots = jobreq_result.snapshots.all()
    listings = jobreq_result.job_listing_results.all()

    # If none exist, Django gives you an empty queryset (this is your "outer join")
    if not snapshots:
        snapshots = [None]
if not listings:
    listings = [None]

for snapshot in snapshots:
    for listing in listings:
        print(
            jobreq_result.title,
            jobreq_result.status,
            snapshot.snapshot_id if snapshot else None,
            snapshot.ready if snapshot else None,
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