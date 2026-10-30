"""Small sync HTTP helper used by the Study IQ module (iq.py): server.get(url, headers=...) -> dict."""
import time
import requests


def get(url, headers=None, params=None, timeout=30, retries=3):
    last_error = None
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
            try:
                return response.json()
            except ValueError:
                return {}
        except requests.RequestException as e:
            last_error = e
            time.sleep(1 + attempt)
    raise last_error
