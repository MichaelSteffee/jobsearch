from django.urls import path, include
from . import views
from .views import home_view, search_job_view, results_list_view

urlpatterns = [
    path('', home_view, name='home'),
    path('search/', search_job_view, name='search'),
    path('results/', results_list_view, name='results'),
    path('listing/<int:pk>/interest/', views.update_interest, name='update_interest'),
    path('listing/<int:pk>/applied/', views.update_applied, name='update_applied'),
    path('listing/<int:pk>/status/', views.update_status, name='update_status'),
    path("result/<int:pk>/delete/", views.delete_jobreq, name="delete_jobreq"),
]
