from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .services import start_job_search, is_ready
from .models import JobReqResult, Snapshot, JobListingResult
from .tasks import process_snapshots_and_summarize
from datetime import datetime

def home_view(request):
    return render(request, 'jobs/home.html')
    path('', views.home_view, name='home')

@login_required
def search_job_view(request):
    context = {}

    if request.method == 'POST':

        jobKeyword = request.POST.get('jobKeyword')
        print(jobKeyword)
        jobLocation = request.POST.get('jobLocation')
        print(jobLocation)
        jobTitle = jobKeyword + " in " + jobLocation + " at " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        jobType = request.POST.get('jobType')
        jobRemote = request.POST.get('jobRemote')
        sources = request.POST.getlist("source")
        print("sources: ", sources)

        if jobKeyword and jobLocation:
            try:
                jobreq_result = JobReqResult(
                    title = jobTitle,
                    jobLocation = jobLocation,
                    jobKeyword = jobKeyword,
                    jobType = jobType,
                    jobRemote = jobRemote,
                    status = 'pending',
                    owner = request.user
                )
                jobreq_result.save()

                result = start_job_search(jobreq_result.id, jobKeyword, jobLocation, jobType, jobRemote, sources)

#                process_snapshots_and_summarize(jobreq_result.id)

                context['result'] = result
                context['search'] = jobTitle
            except Exception as e:
                context['error'] = str(e)
    
    return render(request, 'search.html', context)
    

from .services import get_data

@login_required
def results_list_view(request):
    print('starting to look for results')
    results = JobReqResult.objects.filter(owner=request.user).order_by('-id')

    for result in results:
        snapshots = Snapshot.objects.filter(jobreq_result=result)

        for snapshot in snapshots:
            print('Snapshot Found')
            
            print(snapshot.snapshot_id, " ", snapshot.ready)
            if snapshot.ready:
                continue  # already processed

            data = get_data(snapshot.snapshot_id)
            print("CHECKING SNAPSHOT:", data)

            # 🚨 Handle "not ready"
            if isinstance(data, dict) and data.get("status") == "running":
                continue

            # 🚨 Handle empty
            if not data:
                continue

            # ✅ At this point, data should be a LIST of jobs
            jobs = data
            # Mark snapshot ready
            snapshot.data = data
            snapshot.ready = True
            snapshot.save()

            for job in jobs:
                print("CHECKING JoBS: ")
                JobListingResult.objects.get_or_create(
                    jobreq_result=result,
                    job_url=job.get("url"),
                    defaults={
                        "title": job.get("job_title"),
                        "job_type": job.get("job_employment_type"),
                        "level": job.get("job_seniority_level"),
                        "summary": job.get("job_summary"),
                        "salary": job.get("base_salary"),
                        "posted": job.get("job_posted_date"),
                        "applicants": job.get("job_num_applicants"),
                        "company_name": job.get("company_name"),
                        "job_location": job.get("job_location"),
                        "job_function": job.get("job_function"),
                        "job_industries": job.get("job_industries"),
                        "company_url": job.get("company_url"),
                        "source": job.get("source")
                    }
                )

        # Update status
        if Snapshot.objects.filter(jobreq_result=result, ready=False).exists():
            result.status = 'processing'
        else:
            result.status = 'ready'
        result.save()

    # Build response data (your existing code)
    results_data = []

    for result in results:
        total_snapshots = Snapshot.objects.filter(jobreq_result_id=result.id).count()
        ready_snapshots = Snapshot.objects.filter(jobreq_result_id=result.id, ready=True).count()

        results_data.append({
            'result': result,
            'job_listings': list(result.job_listing_results.all()),
            'total_snapshots': total_snapshots,
            'ready_snapshots': ready_snapshots,
        })

    return render(request, 'jobs/results_list.html', {'results': results_data})