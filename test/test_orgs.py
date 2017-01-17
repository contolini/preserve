# -*- coding: utf-8 -*-
from unittest import TestCase
from unittest import mock

from preserve.orgs import (
    preserve_organization,
)


class TestCommandLine(TestCase):

    @mock.patch('preserve.orgs.list_repositories')
    @mock.patch('preserve.orgs.fork_exists')
    @mock.patch('preserve.orgs.fork_repository')
    @mock.patch('preserve.orgs.rename_repository')
    @mock.patch('preserve.orgs.update_fork')
    @mock.patch('preserve.orgs.logger')
    def test_preserve_organization_no_fork(
            self, mock_logger, mock_update_fork, mock_rename_repository,
            mock_fork_repository, mock_fork_exists, mock_list_repositories):
        """ Test preserving an org when no fork exists """
        mock_list_repositories.return_value = ['one-rep']
        mock_fork_exists.return_value = False
        mock_fork_repository.return_value = True
        mock_rename_repository.return_value = True

        preserve_organization('someone', 'myorg')

        mock_fork_repository.assert_called_with(
            'someone', 'one-rep', 'myorg')
        mock_rename_repository.assert_called_with(
            'myorg', 'one-rep', 'someone_one-rep')
        mock_update_fork.assert_not_called()

    @mock.patch('preserve.orgs.list_repositories')
    @mock.patch('preserve.orgs.fork_exists')
    @mock.patch('preserve.orgs.fork_repository')
    @mock.patch('preserve.orgs.rename_repository')
    @mock.patch('preserve.orgs.update_fork')
    @mock.patch('preserve.orgs.logger')
    def test_preserve_organization_no_fork_fork_failed(
            self, mock_logger, mock_update_fork, mock_rename_repository,
            mock_fork_repository, mock_fork_exists, mock_list_repositories):
        """ Test preserving an org when no fork exists """
        mock_list_repositories.return_value = ['one-rep']
        mock_fork_exists.return_value = False
        mock_fork_repository.return_value = False

        preserve_organization('someone', 'myorg')

        mock_fork_repository.assert_called_with(
            'someone', 'one-rep', 'myorg')
        mock_rename_repository.assert_not_called()
        mock_update_fork.assert_not_called()

        self.assertEqual(len(mock_logger.error.mock_calls), 1)

    @mock.patch('preserve.orgs.list_repositories')
    @mock.patch('preserve.orgs.fork_exists')
    @mock.patch('preserve.orgs.fork_repository')
    @mock.patch('preserve.orgs.rename_repository')
    @mock.patch('preserve.orgs.update_fork')
    @mock.patch('preserve.orgs.logger')
    def test_preserve_organization_no_fork_rename_failed(
            self, mock_logger, mock_update_fork, mock_rename_repository,
            mock_fork_repository, mock_fork_exists, mock_list_repositories):
        """ Test preserving an org when no fork exists """
        mock_list_repositories.return_value = ['one-rep']
        mock_fork_exists.return_value = False
        mock_fork_repository.return_value = True
        mock_rename_repository.return_value = False

        preserve_organization('someone', 'myorg')

        mock_fork_repository.assert_called_with(
            'someone', 'one-rep', 'myorg')
        mock_rename_repository.assert_called_with(
            'myorg', 'one-rep', 'someone_one-rep')
        mock_update_fork.assert_not_called()

        self.assertEqual(len(mock_logger.error.mock_calls), 1)

    @mock.patch('preserve.orgs.list_repositories')
    @mock.patch('preserve.orgs.fork_exists')
    @mock.patch('preserve.orgs.fork_repository')
    @mock.patch('preserve.orgs.rename_repository')
    @mock.patch('preserve.orgs.update_fork')
    @mock.patch('preserve.orgs.logger')
    def test_preserve_organization_fork_exists(
            self, mock_logger, mock_update_fork, mock_rename_repository,
            mock_fork_repository, mock_fork_exists, mock_list_repositories):
        mock_list_repositories.return_value = ['one-rep']
        mock_fork_exists.return_value = True

        preserve_organization('someone', 'myorg')

        mock_fork_repository.assert_not_called()
        mock_rename_repository.assert_not_called()
        mock_update_fork.assert_called_with(
            'someone', 'one-rep', 'myorg', 'someone_one-rep')
