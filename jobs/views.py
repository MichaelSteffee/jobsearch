from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .services import start_job_search, is_ready
from .models import JobReqResult, Snapshot, JobListingResult
from datetime import datetime

# Views for Application Pages
# Home, Job Search and Job Listing

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

# Updates to Job Listing Action Buttons and Status

from django.http import JsonResponse
from django.utils import timezone
from .models import JobListingResult

@login_required
def update_interest(request, pk):
    if request.method == "POST":
        value = request.POST.get("value")  # 'Y' or 'N'

        try:
            listing = JobListingResult.objects.get(pk=pk)
            listing.interested = value
            listing.interested_date = timezone.now().date()
            listing.save()

            return JsonResponse({
                "status": "ok",
                "value": listing.interested   # or applied/interested
            })
        except JobListingResult.DoesNotExist:
            return JsonResponse({"status": "error"}, status=404)

    return JsonResponse({"status": "invalid"}, status=400)

@login_required
def update_applied(request, pk):
    if request.method == "POST":
        value = request.POST.get("value")  # 'Y' or 'N'

        try:
            listing = JobListingResult.objects.get(pk=pk)
            listing.applied = value
            listing.applied_date = timezone.now().date()
            listing.save()

            return JsonResponse({
                "status": "ok",
                "value": listing.applied   # or applied/interested
            })
        except JobListingResult.DoesNotExist:
            return JsonResponse({"status": "error"}, status=404)

    return JsonResponse({"status": "invalid"}, status=400)

@login_required
def update_status(request, pk):
    if request.method == "POST":
        value = request.POST.get("value") 

        try:
            listing = JobListingResult.objects.get(pk=pk)
            listing.status = value
            listing.status_date = timezone.now().date()
            listing.save()

            return JsonResponse({
                "status": "ok",
                "value": listing.status   # or applied/interested
            })
        except JobListingResult.DoesNotExist:
            return JsonResponse({"status": "error"}, status=404)

    return JsonResponse({"status": "invalid"}, status=400)

# delete Job Listing Request and any Job Listings that it found

from django.views.decorators.http import require_POST

@login_required
@require_POST
def delete_jobreq(request, pk):
    try:
        result = JobReqResult.objects.get(pk=pk, owner=request.user)
        result.delete()

        return JsonResponse({"status": "ok"})
    except JobReqResult.DoesNotExist:
        return JsonResponse({"status": "error"}, status=404)
    