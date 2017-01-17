# -*- coding: utf-8 -*-
from unittest import TestCase
from unittest import mock

from preserve.github import (
    GitHubError,
    github_api_all,
    fork_exists,
    fork_repository,
    list_repositories,
    rate_limit,
    rename_repository,
    update_fork,
)


class GitHubTestCase(TestCase):

    def setUp(self):
        import preserve.github
        preserve.github.HEADERS = {}

    @mock.patch('requests.get')
    def test_rate_limit(self, mock_requests_get):
        mock_rate_limit = mock.MagicMock()
        mock_rate_limit.json.return_value = {
            'rate': {
                'limit': 5000,
                'remaining': 4999,
                'reset': 1372700873
            }
        }
        mock_requests_get.return_value = mock_rate_limit
        response_json = rate_limit()
        self.assertEqual(response_json, (5000, 4999, 1372700873))

    @mock.patch('requests.get')
    def test_github_api_all(self, mock_requests_get):
        """ github_api_all uses the Link header in a GitHub API reasponse to
            get all paginated results for a query before returning. """
        # Mock our possible responses
        first_page = mock.MagicMock()
        first_page.status_code = 200
        first_page.json.return_value = []
        first_page.links = {
            'next': {'url': 'https://test/url?page=2', 'rel': 'next'},
            'last': {'url': '<https://test/url?page=3>', 'rel': 'last'},
        }
        second_page = mock.MagicMock()
        second_page.status_code = 200
        second_page.json.return_value = []
        second_page.links = {
            'next': {'url': 'https://test/url?page=3', 'rel': 'next'},
            'last': {'url': '<https://test/url?page=3>', 'rel': 'last'},
            'first': {'url': '<https://test/url?page=1>', 'rel': 'first'},
            'prev': {'url': '<https://test/url?page=1>', 'rel': 'prev'},
        }
        third_page = mock.MagicMock()
        third_page.status_code = 200
        third_page.json.return_value = []
        third_page.links = {
            'first': {'url': '<https://test/url?page=1>', 'rel': 'first'},
            'prev': {'url': '<https://test/url?page=2>', 'rel': 'prev'},
        }

        mock_requests_get.side_effect = [
            first_page,
            second_page,
            third_page
        ]

        github_api_all('https://test/url')
        mock_requests_get.assert_has_calls([
            mock.call('https://test/url', headers={}),
            mock.call('https://test/url?page=2', headers={}),
            mock.call('https://test/url?page=3', headers={})
        ])

    @mock.patch('requests.get')
    def test_github_api_all_404(self, mock_requests_get):
        """ github_api_all uses the Link header in a GitHub API reasponse to
            get all paginated results for a query before returning. """
        mock_error = mock.MagicMock()
        mock_error.status_code = 404
        mock_error.json.return_value = {'message': 'failure'}
        mock_requests_get.return_value = mock_error
        with self.assertRaises(GitHubError):
            github_api_all('https://test/url')

    @mock.patch('preserve.github.github_api_all')
    def test_list_repositories(self, mock_github_api_all):
        mock_github_api_all.return_value = [
            {'name': 'one-repo'},
            {'name': 'another-repo'},
        ]
        result = list_repositories('someorg')
        self.assertIn('one-repo', result)
        self.assertIn('another-repo', result)

    @mock.patch('preserve.github.github_api_all')
    def test_list_repositories_noorg(self, mock_github_api_all):
        """ Test if we are listing a user rather than an org """
        mock_github_api_all.side_effect = [
            None,
            [
                {'name': 'one-repo'},
                {'name': 'another-repo'},
            ]
        ]
        result = list_repositories('someone')
        self.assertIn('one-repo', result)
        self.assertIn('another-repo', result)

    @mock.patch('requests.get')
    def test_fork_exists(self, mock_requests_get):
        """ Test when a matching fork exists """
        existing = mock.MagicMock()
        existing.status_code = 200
        existing.json.return_value = {'fork': True}
        mock_requests_get.return_value = existing

        result = fork_exists('someone', 'one-repo', 'myorg')
        self.assertTrue(result)

    @mock.patch('requests.get')
    def test_fork_exists_not_fork(self, mock_requests_get):
        """ Test when a repo exists that's not a fork"""
        existing = mock.MagicMock()
        existing.status_code = 200
        existing.json.return_value = {'fork': False}
        mock_requests_get.return_value = existing

        with self.assertRaises(GitHubError):
            fork_exists('someone', 'one-repo', 'myorg')

    @mock.patch('requests.get')
    def test_fork_exists_doesnt(self, mock_requests_get):
        """ Test a fork doesn't exist """
        existing = mock.MagicMock()
        existing.status_code = 404
        mock_requests_get.return_value = existing

        result = fork_exists('someone', 'one-repo', 'myorg')
        self.assertFalse(result)

    @mock.patch('requests.get')
    @mock.patch('requests.post')
    def test_fork_repository(self, mock_requests_post, mock_requests_get):
        """ Test our GitHub API call to fork """
        fork_response = mock.MagicMock()
        fork_response.status_code = 202
        fork_response.json.return_value = {'message': 'Failed'}
        mock_requests_post.return_value = fork_response

        result = fork_repository('someone', 'one-repo', 'myorg')

        self.assertTrue(result)

    @mock.patch('requests.post')
    def test_fork_repository_failure(self, mock_requests_post):
        """ Test our GitHub API call to fork """
        fork_response = mock.MagicMock()
        fork_response.status_code = 400
        fork_response.json.return_value = {'message': 'Failed'}
        mock_requests_post.return_value = fork_response

        with self.assertRaises(GitHubError):
            fork_repository('someone', 'one-repo', 'myorg')

    @mock.patch('requests.post')
    def test_rename_repository(self, mock_requests_post):
        """ Test renaming repository """
        edit_response = mock.MagicMock()
        edit_response.status_code = 200
        mock_requests_post.return_value = edit_response

        result = rename_repository('myorg', 'one-repo', 'someone_one-repo')

        self.assertTrue(result)

    @mock.patch('requests.post')
    def test_rename_repository_failure(self, mock_requests_post):
        """ Test renaming repository """
        edit_response = mock.MagicMock()
        edit_response.status_code = 400
        edit_response.json.return_value = {'message': 'Failed'}
        mock_requests_post.return_value = edit_response

        with self.assertRaises(GitHubError):
            rename_repository('myorg', 'one-repo', 'someone_one-repo')

    @mock.patch('requests.get')
    @mock.patch('requests.post')
    @mock.patch('requests.patch')
    def test_update_fork_branch_exists_same_sha(self,
                                                mock_requests_patch,
                                                mock_requests_post,
                                                mock_requests_get):
        """ Test that we don't update a branch if the fork has the same sha """
        mock_upstream_branches = mock.MagicMock()
        mock_upstream_branches.status_code = 200
        mock_upstream_branches.json.return_value = [{
            "name": "master",
            "commit": {
                "sha": "6dcb09b5b57875f334f61aebed695e2e4193db5e",
            },
        }]
        mock_fork_branches = mock.MagicMock()
        mock_fork_branches.status_code = 200
        mock_fork_branches.json.return_value = [{
            "name": "master",
            "commit": {
                "sha": "6dcb09b5b57875f334f61aebed695e2e4193db5e",
            },
        }]
        mock_requests_get.side_effect = [
            mock_upstream_branches,
            mock_fork_branches
        ]

        # Because the shas are the same, we shouldn't be making any other API
        # calls
        update_fork('someone', 'one-repo', 'myorg', 'someone_one-repo')
        mock_requests_post.assert_not_called()
        mock_requests_patch.assert_not_called()

    @mock.patch('requests.get')
    @mock.patch('requests.post')
    @mock.patch('requests.patch')
    def test_update_fork_branch_exists_diff_sha(self,
                                                mock_requests_patch,
                                                mock_requests_post,
                                                mock_requests_get):
        """ Test that we update a branch if the fork has the same sha """
        mock_upstream_branches = mock.MagicMock()
        mock_upstream_branches.status_code = 200
        mock_upstream_branches.json.return_value = [{
            "name": "master",
            "commit": {
                "sha": "6dcb09b5b57875f334f61aebed695e2e4193db5e",
            },
        }]
        mock_fork_branches = mock.MagicMock()
        mock_fork_branches.status_code = 200
        mock_fork_branches.json.return_value = [{
            "name": "master",
            "commit": {
                "sha": "7fd1a60b01f91b314f59955a4e4d4e80d8edf11d",
            },
        }]
        mock_requests_get.side_effect = [
            mock_upstream_branches,
            mock_fork_branches
        ]

        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_requests_patch.return_value = mock_response

        # Because the shas are different we should be making a PATCH call
        update_fork('someone', 'one-repo', 'myorg', 'someone_one-repo')
        mock_requests_post.assert_not_called()
        mock_requests_patch.assert_has_calls([
            mock.call('https://api.github.com/repos/myorg/someone_one-repo/git/refs/heads/master',  # noqa
                      data='{"sha": "6dcb09b5b57875f334f61aebed695e2e4193db5e"}')  # noqa
        ], any_order=True)

    @mock.patch('requests.get')
    @mock.patch('requests.post')
    @mock.patch('requests.patch')
    def test_update_fork_branch_exists_diff_sha_failure(self,
                                                        mock_requests_patch,
                                                        mock_requests_post,
                                                        mock_requests_get):
        """ Test that we update a branch if the fork has the same sha """
        mock_upstream_branches = mock.MagicMock()
        mock_upstream_branches.status_code = 200
        mock_upstream_branches.json.return_value = [{
            "name": "master",
            "commit": {
                "sha": "6dcb09b5b57875f334f61aebed695e2e4193db5e",
            },
        }]
        mock_fork_branches = mock.MagicMock()
        mock_fork_branches.status_code = 200
        mock_fork_branches.json.return_value = [{
            "name": "master",
            "commit": {
                "sha": "7fd1a60b01f91b314f59955a4e4d4e80d8edf11d",
            },
        }]
        mock_requests_get.side_effect = [
            mock_upstream_branches,
            mock_fork_branches
        ]

        mock_response = mock.MagicMock()
        mock_response.status_code = 999
        mock_response.json.return_value = {'message': 'failure'}
        mock_requests_patch.return_value = mock_response

        with self.assertRaises(GitHubError):
            update_fork('someone', 'one-repo', 'myorg', 'someone_one-repo')

    @mock.patch('requests.get')
    @mock.patch('requests.post')
    @mock.patch('requests.patch')
    def test_update_fork_branch_doesnt_exist(self,
                                             mock_requests_patch,
                                             mock_requests_post,
                                             mock_requests_get):
        """ Test that we create a branch if the fork doesn't have it """
        mock_upstream_branches = mock.MagicMock()
        mock_upstream_branches.status_code = 200
        mock_upstream_branches.json.return_value = [{
            "name": "master",
            "commit": {
                "sha": "6dcb09b5b57875f334f61aebed695e2e4193db5e",
            },
        }]
        mock_fork_branches = mock.MagicMock()
        mock_fork_branches.status_code = 200
        mock_fork_branches.json.return_value = []
        mock_requests_get.side_effect = [
            mock_upstream_branches,
            mock_fork_branches
        ]

        mock_response = mock.MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'message': 'failure'}
        mock_requests_post.return_value = mock_response

        # Because the branch doesn't exist we should be making a POST call
        update_fork('someone', 'one-repo', 'myorg', 'someone_one-repo')
        mock_requests_patch.assert_not_called()
        mock_requests_post.assert_has_calls([
            mock.call('https://api.github.com/repos/myorg/someone_one-repo/git/refs',  # noqa
                      data='{"sha": "6dcb09b5b57875f334f61aebed695e2e4193db5e"}')  # noqa
        ])

    @mock.patch('requests.get')
    @mock.patch('requests.post')
    @mock.patch('requests.patch')
    def test_update_fork_branch_doesnt_exist_failure(self,
                                                     mock_requests_patch,
                                                     mock_requests_post,
                                                     mock_requests_get):
        """ Test that we create a branch if the fork doesn't have it """
        mock_upstream_branches = mock.MagicMock()
        mock_upstream_branches.status_code = 200
        mock_upstream_branches.json.return_value = [{
            "name": "master",
            "commit": {
                "sha": "6dcb09b5b57875f334f61aebed695e2e4193db5e",
            },
        }]
        mock_fork_branches = mock.MagicMock()
        mock_fork_branches.status_code = 200
        mock_fork_branches.json.return_value = []
        mock_requests_get.side_effect = [
            mock_upstream_branches,
            mock_fork_branches
        ]

        mock_response = mock.MagicMock()
        mock_response.status_code = 999
        mock_response.json.return_value = {'message': 'failure'}
        mock_requests_post.return_value = mock_response

        with self.assertRaises(GitHubError):
            update_fork('someone', 'one-repo', 'myorg', 'someone_one-repo')
