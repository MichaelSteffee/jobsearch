from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .services import start_job_search, is_ready
from .models import JobReqResult, Snapshot, JobListingResult
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

                import threading
                from .tasks import process_snapshots_and_summarize

                print("starting threading for jobreq_result_id ", jobreq_result.id)

                threading.Thread(
                    target=process_snapshots_and_summarize,
                    args=(jobreq_result.id,),
                    daemon=True
                ).start()

                context['result'] = result
                context['search'] = jobTitle
            except Exception as e:
                context['error'] = str(e)
    
    return render(request, 'search.html', context)
    
from django.db.models import Count, Q

@login_required
def results_list_view(request):

    print("starting results_list_view")



    results = JobReqResult.objects.filter(owner=request.user).annotate(
        total_snapshots=Count('snapshots'),
        ready_snapshots=Count('snapshots', filter=Q(snapshots__ready=True))
    ).prefetch_related('job_listing_results').order_by('-id')

    results_data = []

    for result in results:

        results_data.append({
            'result': result,
            'job_listings': result.job_listing_results.all(),
            'total_snapshots': result.total_snapshots,
            'ready_snapshots': result.ready_snapshots,
        })

    return render(request, 'jobs/results_list.html', {
        'results': results_data
    })
