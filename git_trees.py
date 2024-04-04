#!/usr/bin/env python3

import argparse
import requests

def git_trees(owner, repo, path, type, measurement, branch='master') -> None:
    """
    See https://docs.github.com/en/rest/git/trees?apiVersion=2022-11-28
    See https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api?apiVersion=2022-11-28
    See https://docs.github.com/en/rest/rate-limit/rate-limit?apiVersion=2022-11-28
    Note: The limit for unauthenticated requests is 60 requests per hour.
    Note: The limit for the tree array is 100,000 entries with a maximum size of 7 MB when using the recursive parameter.
    Print output as Line Protocol
    See https://docs.influxdata.com/influxdb/cloud/reference/syntax/line-protocol/
    """
    rate_limit_url = 'https://api.github.com/rate_limit'
    r = requests.get(rate_limit_url)
    r.raise_for_status()
    json = r.json()
    remaining = int(json["resources"]["core"]["remaining"])

    if remaining > 0:
        api_url = f'https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1'
        r = requests.get(api_url)
        r.raise_for_status()
        json = r.json()
        files = [ item["path"] for item in json["tree"] if item["path"].startswith(path) and item["path"].endswith(type)]
        count = len(files)
    else:
        count = 0

    print(f'{measurement},owner={owner},repo={repo},branch={branch},path={path} count={count}i')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--owner', required=True, help='The account owner of the repository. The name is not case sensitive')
    parser.add_argument('-r', '--repo', required=True, help='The name of the repository without the .git extension. The name is not case sensitive.')
    parser.add_argument('-p', '--path', required=True, help='The repo relative root path, e.g. schedule/yam/')
    parser.add_argument('-t', '--type', required=True, help='The file type extension, e.g. yaml')
    parser.add_argument('-m', '--measurement', required=True, help='The measurement name. Cannot begin with an underscore.')
    parser.add_argument('-b', '--branch', required=False, default='master', help='The SHA1 value or ref (branch or tag) name of the tree. Default master.')
    args = parser.parse_args()
    git_trees(owner=args.owner, repo=args.repo, path=args.path, type=args.type, measurement=args.measurement, branch=args.branch)
