import time
from .models import JobReqResult, Snapshot, JobListingResult
from .services import get_data


def process_snapshots_and_summarize(jobreq_id):
    jobreq = JobReqResult.objects.get(id=jobreq_id)

    print("starting process_snapshots_and... for jobreq ", jobreq_id)
    while True:
        snapshots = Snapshot.objects.filter(jobreq_result=jobreq, ready=False)

        if not snapshots.exists():
            break  # all done

        for snapshot in snapshots:
            try:
                data = get_data(snapshot.snapshot_id)

                # still running → skip for now
                if isinstance(data, dict) and data.get("status") == "running":
                    continue

                if not data:
                    continue

                # ✅ mark ready
                snapshot.data = data
                snapshot.ready = True
                listing_source = snapshot.source
                snapshot.save()

                # ✅ create jobs
                job_objects = []

                for job in data:
                
                    if not job:
                        print("Skipping empty job:", job)
                        continue

                    title = job.get("job_title")
                    url = job.get("url")

                    # 🚨 skip invalid jobs
                    if not title or not url:
                        print("Skipping invalid job:", job)
                        continue

                    print("creating job", title)

                    job_objects.append(
                        JobListingResult(
                            jobreq_result=jobreq,
                            job_url=job.get("url"),
                            title=job.get("job_title"),
                            job_type=job.get("job_employment_type"),
                            level=job.get("job_seniority_level"),
                            summary=job.get("job_summary"),
                            salary=job.get("base_salary"),
                            posted=job.get("job_posted_date"),
                            applicants=job.get("job_num_applicants"),
                            company_name=job.get("company_name"),
                            job_location=job.get("job_location"),
                            job_function=job.get("job_function"),
                            job_industries=job.get("job_industries"),
                            company_url=job.get("company_url"),
                            source=listing_source,
                        )
                    )
                print("ready to create job listings")

                JobListingResult.objects.bulk_create(job_objects)

            except Exception as e:
                print(f"Error processing snapshot {snapshot.id}: {e}")

        # update jobreq status
        if Snapshot.objects.filter(jobreq_result=jobreq, ready=False).exists():
            jobreq.status = "processing"
        else:
            jobreq.status = "ready"

        jobreq.save()

        # ⏳ wait before polling again
        time.sleep(60)  # adjust as needed