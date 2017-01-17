# -*- coding: utf-8 -*-
import json
import os
import requests

GITHUB_API_URL = 'https://api.github.com'
HEADERS = {}
ACCESS_TOKEN = os.environ.get('GITHUB_API_TOKEN', None)
if ACCESS_TOKEN is not None:
    HEADERS['Authorization'] = 'token ' + ACCESS_TOKEN


class GitHubError(Exception):
    pass


def rate_limit():
    """ Check GitHub rate limit """
    rate_limit_url = '/'.join([GITHUB_API_URL, 'rate_limit'])
    response = requests.get(rate_limit_url, headers=HEADERS)
    response_json = response.json()
    limit = response_json['rate']['limit']
    remaining = response_json['rate']['remaining']
    reset = response_json['rate']['reset']
    return (limit, remaining, reset)


def github_api_all(url):
    """
    Fetch all results, not simply the first page of results, for the given URL.
    """
    # Get our initial response
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise GitHubError(response.json()['message'])

    response_json = response.json()
    while 'next' in response.links:
        # While we have a 'next' link, fetch it and add its response to the
        # json object.
        response = requests.get(response.links['next']['url'], headers=HEADERS)
        response_json += response.json()

    return response_json


def list_repositories(user_or_org):
    """ List a user/org's repositories """
    # First see if we were given a user or an organization. Assume org first.
    repos_url = '/'.join([GITHUB_API_URL, 'orgs', user_or_org, 'repos'])
    response_json = github_api_all(repos_url)

    if response_json is None:
        # If we didn't successfully get an org, let's try a user
        repos_url = '/'.join([GITHUB_API_URL, 'users', user_or_org, 'repos'])
        response_json = github_api_all(repos_url)

    repositories = [r['name'] for r in response_json]
    return repositories


def fork_exists(origin_user, origin_repository,
                destination_org, fork_name=None):
    """ Check if a fork exists for an org """
    if fork_name is None:
        fork_name = origin_repository

    # Check to see if we already have a fork of this repository
    existing_url = '/'.join([
        GITHUB_API_URL,
        'repos',
        destination_org,
        fork_name
    ])
    existing_response = requests.get(existing_url, headers=HEADERS)
    if existing_response.status_code == 200:
        if existing_response.json()['fork'] is True:
            return True
        raise GitHubError(fork_name + ' already exists and is not a fork')
    return False


def fork_repository(origin_user, origin_repository, destination_org):
    """ Fork an origin user/org's repository to an org. """
    # Fork the repository
    fork_url = '/'.join([
        GITHUB_API_URL,
        'repos',
        origin_user,
        origin_repository,
        'forks?org=' + destination_org
    ])
    fork_response = requests.post(fork_url, headers=HEADERS)
    if fork_response.status_code != 202:
        raise GitHubError(fork_response.json()['message'])

    return True


def rename_repository(user_or_org, old_name, new_name):
    """ Rename a repository """
    # Rename the repository
    edit_url = '/'.join([
        GITHUB_API_URL,
        'repos',
        user_or_org,
        old_name,
    ])
    parameters = json.dumps({'name': new_name})
    edit_response = requests.post(edit_url, headers=HEADERS, data=parameters)
    if edit_response.status_code != 200:
        raise GitHubError(edit_response.json()['message'])

    return True


def update_fork(origin_user, origin_repository, fork_user, fork_repository):
    """ Update a fork or an origin user/org's repository """
    # http://stackoverflow.com/a/27762278/2877583

    # Get a list of branches in the origin
    upstream_branches_url = '/'.join([
        GITHUB_API_URL,
        'repos',
        origin_user,
        origin_repository,
        'branches',
    ])
    upstream_branches_json = github_api_all(upstream_branches_url)
    upstream_branches = [(b['name'], b['commit']['sha'])
                         for b in upstream_branches_json]

    # Get a list of fork branches, so we know whether to update the branch or
    # create a new one
    fork_branches_url = '/'.join([
        GITHUB_API_URL,
        'repos',
        fork_user,
        fork_repository,
        'branches',
    ])
    fork_branches_json = github_api_all(fork_branches_url)
    fork_branches = {b['name']: b['commit']['sha'] for b in fork_branches_json}

    for branch, commit in upstream_branches:
        parameters = {'sha': commit}

        if branch in fork_branches:
            if fork_branches[branch] == commit:
                continue

            # This is an update to an existing branch
            patch_url = '/'.join([
                GITHUB_API_URL,
                'repos',
                fork_user,
                fork_repository,
                'git', 'refs', 'heads',
                branch
            ])
            response = requests.patch(patch_url, data=json.dumps(parameters))
            if response.status_code != 200:
                raise GitHubError(response.json()['message'])

        else:
            # This is a new branch
            post_url = '/'.join([
                GITHUB_API_URL,
                'repos',
                fork_user,
                fork_repository,
                'git', 'refs'
            ])
            response = requests.post(post_url, data=json.dumps(parameters))
            if response.status_code != 201:
                raise GitHubError(response.json()['message'])
