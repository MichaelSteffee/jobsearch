import requests
from dotenv import load_dotenv

load_dotenv()

try:
    r = requests.get("https://api.brightdata.com", timeout=10)
    print("Status:", r.status_code)
except Exception as e:
    print("ERROR:", e)