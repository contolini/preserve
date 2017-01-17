# -*- coding: utf-8 -*-
import logging

from preserve.github import (
    # GitHubError,
    fork_exists,
    fork_repository,
    list_repositories,
    rename_repository,
    update_fork,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def preserve_organization(org, dest_org):
    """ Preserve all public repositories for the given GitHub organization """
    logger.info("Getting repositories for " + org)

    # Get a list of that organization's repositories
    repositories = list_repositories(org)
    # repositories = ['cfgov-refresh']

    # Create forks
    for repo in repositories:
        fork_name = org + "_" + repo

        if not fork_exists(org, repo, dest_org, fork_name=fork_name):
            logger.info("\tForking " + org + '/' + repo)

            if not fork_repository(org, repo, dest_org):
                logger.error("\tError forking " + org + '/' + repo)
                continue
            logger.debug("Create Fork " + org + '/' + repo)

            if not rename_repository(dest_org, repo, fork_name):
                logger.error("\tError renaming fork " + org + '/' + repo)
                continue
            logger.debug("Renamed fork " + fork_name)

        else:
            logger.info("\tUpdating fork " + fork_name)
            update_fork(org, repo, dest_org, fork_name)
