from .models import Snapshot, JobReqResult, JobListingResult
from .services import get_data
import time


def process_snapshots_and_summarize(jobreq_result_id):
    try:
        jobreq_result = JobReqResult.objects.get(id=jobreq_result_id)
        print("TASK RUNNING", jobreq_result_id)

        jobreq_result.status = 'processing'
        jobreq_result.save()

        snapshots = Snapshot.objects.filter(jobreq_result_id=jobreq_result_id)

        # Wait for snapshots to exist
        retries = 5
        while not snapshots.exists() and retries > 0:
            print("Waiting for snapshots...")
            time.sleep(2)
            snapshots = Snapshot.objects.filter(jobreq_result_id=jobreq_result_id)
            retries -= 1

        print("SNAPSHOT COUNT:", snapshots.count())

        for snapshot in snapshots:
            # Fetch fresh data
            print("Fetching snapshot:", snapshot.snapshot_id)

            data = get_data(snapshot.snapshot_id)

            print("DATA RETURNED:", data)
            snapshot.data = data
            snapshot.ready = True
            snapshot.save()

            # 🔥 KEY CHANGE: iterate actual structured data
            jobs = data.get("jobs", [])  # adjust key if needed

            for job in jobs:
                JobListingResult.objects.create(
                    jobreq_result=jobreq_result,
                    title=job.get("title"),
                    source=snapshot.source,
                    job_url=job.get("url"),  # ✅ direct mapping
                    job_type=job.get("job_type"),
                    level=job.get("level"),
                    summary=job.get("description") or job.get("summary"),
                    salary=job.get("salary"),
                    posted=job.get("posted") or job.get("date_posted"),
                    applicants=job.get("applicants"),
                )

        jobreq_result.status = 'ready'
        jobreq_result.save()

        return f"Successfully processed Job Request result for {jobreq_result.id}"

    except Exception as e:
        print("ERROR:", str(e))
        raise