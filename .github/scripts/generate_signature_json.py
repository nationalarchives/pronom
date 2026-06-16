import json
import os
import re

import urllib.request
from datetime import datetime
from urllib.request import Request

RELEASES_API_ENDPOINT = "https://api.github.com/repos/nationalarchives/pronom/releases"


def filter_names(names: list[str], prefix: str):
    return [name for name in names if name.startswith(prefix)]


def filter_binary_files(names: list[str]):
    return filter_names(names, "DROID_SignatureFile")


def filter_container_files(names: list[str]):
    return filter_names(names, "container-signature")


def create_request(url):
    req = Request(url)
    req.add_header("Authorization", f"Bearer {os.environ["GITHUB_TOKEN"]}")
    req.add_header("Accept", "application/vnd.github+json")
    return req


def get_latest_release_names():
    url = f"{RELEASES_API_ENDPOINT}/latest"
    req = create_request(url)
    with urllib.request.urlopen(req) as response:
        return [asset["name"] for asset in json.load(response)["assets"]]


def get_all_release_names(names=None, page=1):
    if names is None:
        names = []
    url = f"{RELEASES_API_ENDPOINT}?page={page}&per_page=100"
    req = create_request(url)
    with urllib.request.urlopen(req) as response:
        releases = json.load(response)
        if len(releases) != 0:
            for release in releases:
                names.extend([asset["name"] for asset in release["assets"]])
            page += 1
            return get_all_release_names(names, page)
        else:
            return names


def get_binary_version(key):
    return key.split('_')[2].split('.')[0]


def get_container_version(key):
    return key.split('-')[2].split('.')[0]


def signature_key_to_name(key):
    version = get_binary_version(key)
    return f'DROID Signature File {version}'


def container_key_to_name(key):
    date_str = get_container_version(key)
    date_obj = datetime.strptime(date_str, "%Y%m%d")
    return date_obj.strftime("%d %B %Y")


latest_file_names = get_latest_release_names()
latest_signature_file_name = filter_binary_files(latest_file_names)[0]
latest_container_signature_file_name = filter_container_files(latest_file_names)
all_file_names = get_all_release_names()
signatures = sorted(filter_binary_files(all_file_names), key=lambda k: int(re.search(r'(\d+)', k).group(1)))
container_signatures = sorted(filter_container_files(all_file_names))
signature_names = [
    {
        "name": signature_key_to_name(sig),
        "location": f"/signatures/{sig}",
        "version": get_binary_version(sig)[1:]
    } for sig in signatures
]
container_signature_names = [
    {
        "name": container_key_to_name(sig),
        "location": f"/container-signatures/{sig}",
        "version": get_container_version(sig)
    } for sig in container_signatures
]
signature_json = {
    "latest_signature": signature_names[-1],
    "latest_container_signature": container_signature_names[-1],
    "signatures": signature_names,
    "container_signatures": container_signature_names,
}
with open("signatures.json", "w") as sig_json:
    json.dump(signature_json, sig_json, indent=2)
