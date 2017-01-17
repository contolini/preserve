# -*- coding: utf-8 -*-
"""
This is a simple script that, given a user or organization on GitHub,
attmepts to use the GitHub API to do a few things:

- Get a list of that organization's repositories
- For each repository that does not have a code preserve fork, create
  a fork
- For each repository that does have a code preserve fork, update it

In this way, repositories in code preserve that are forked from a
particular user or organization are kept up-to-date, new repositories
are forked, and the code preserve forks of any repositories that may
have been deleted are left untouched.
"""
import logging
import sys

import click

from preserve.orgs import preserve_organization

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


@click.command()
@click.argument('organization', nargs=-1)
@click.option('--update', default=True, help='Update forks that already exist')
@click.option('--dest-org', default='codepreservetest',
              help='Destination organization')
def main(organization=[], update=True, dest_org='codepreservetest'):
    if dest_org in organization:
        logger.error(dest_org + " cannot be a target org")
        sys.exit(1)

    for org in organization:
        preserve_organization(org, dest_org)
