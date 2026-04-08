echo on
call conda activate jobsearch
z:
cd dev_ai/search-job-listings
python manage.py runserver
pause