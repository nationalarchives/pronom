import os
import sys

from github import Github

from github import Auth
import urllib.request
import json
import csv
from jsondiff import diff

def get_puid(format_json):
    return [i["identifierText"] for i in format_json["identifiers"] if i["identifierType"] == "PUID"][0]


def sort_by_puid(rows):
    return sorted(rows, key=lambda x: int(x[1].split("/")[1]))

def run():
    sha = sys.argv[1]
    new_version = sys.argv[2]
    auth = Auth.Token(os.environ["GITHUB_TOKEN"])

    g = Github(auth=auth)

    repo = g.get_repo("nationalarchives/pronom")

    commit = repo.get_commit(sha)

    print(commit)

    new_records = []
    new_signatures = []
    updates = []

    pulls = commit.get_pulls()

    if pulls.totalCount != 0:
        pull_title = pulls[0].title.split("\r\n")[0]
        files = list(commit.files)
        for file in commit.files:
            if file.filename.startswith("signatures/"):
                if file.status == "added":
                    with urllib.request.urlopen(file.raw_url) as added_file:
                        added_json = json.load(added_file)
                        puid = get_puid(added_json)
                        if len(added_json["internalSignatures"]) > 0 or len(added_json["containerSignatures"]) > 0:
                            new_signatures.append(["New Signature", puid, pull_title])
                    new_records.append(["New Record", puid, pull_title])
                elif file.status == "modified":
                    with urllib.request.urlopen(file.raw_url) as changed_file, urllib.request.urlopen(file.raw_url.replace(sha, "main")) as existing_file:
                        changed_json = json.load(changed_file)
                        existing_json = json.load(existing_file)
                        puid = get_puid(changed_json)
                        json_diff = json.loads(diff(existing_json, changed_json, dump=True))
                        def new_signature(key):
                            if key in json_diff:
                                return ("$insert" in json_diff[key]) or any(i for i in json_diff[key] if "signatureID" in i)
                            return False
                        if json_diff:
                            if new_signature("internalSignatures") or new_signature("containerSignatures"):
                                new_signatures.append(["New Signature", puid, pull_title])
                            updates.append(["Update", puid, pull_title])

    with open(f"changelogs/changelog-{new_version}.csv", "a") as changelog:
        writer = csv.writer(changelog)
        writer.writerows(sort_by_puid(new_records))
        writer.writerows(sort_by_puid(updates))
        writer.writerows(sort_by_puid(new_signatures))

if __name__ == "__main__":
    run()
