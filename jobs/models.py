from django.db import models
from django.contrib.auth.models import User


class JobReqResult(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('ready', 'Ready')
    ]

    title = models.CharField(max_length=256)
    status = models.CharField(max_length=64, choices=STATUS_CHOICES, default='pending')
    jobLocation = models.TextField()
    jobKeyword = models.TextField()
    jobType = models.TextField()
    jobRemote = models.TextField()

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobreq_results')


class JobListingResult(models.Model):
    title = models.CharField(max_length=1024)
    job_url = models.CharField(max_length=1024)
    company_name = models.CharField(max_length=1024, null=True, blank=True)
    job_location = models.CharField(max_length=1024, null=True, blank=True)
    job_function = models.CharField(max_length=1024, null=True, blank=True)
    job_industries = models.CharField(max_length=1024, null=True, blank=True)
    company_url = models.CharField(max_length=1024, null=True, blank=True)
    job_type = models.CharField(max_length=1024, null=True, blank=True)
    level = models.CharField(max_length=1024, null=True, blank=True)
    summary = models.CharField(max_length=1024, null=True, blank=True)
    salary = models.CharField(max_length=1024, null=True, blank=True)
    posted = models.CharField(max_length=1024, null=True, blank=True)
    applicants = models.IntegerField(null=True, blank=True)
    source = models.CharField(max_length=50) 

    jobreq_result = models.ForeignKey(JobReqResult, on_delete=models.CASCADE, related_name='job_listing_results')


class Snapshot(models.Model):
    snapshot_id = models.CharField(max_length=256)
    ready = models.BooleanField()
    data = models.JSONField()
    source = models.CharField(max_length=50) 

    jobreq_result = models.ForeignKey(JobReqResult, on_delete=models.CASCADE, related_name='snapshots')
