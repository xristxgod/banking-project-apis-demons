import requests


def _get_response(method, url, data=None):
    return requests.request(method, url, json=data)
