# -*- coding: utf-8 -*-
from unittest import TestCase
from unittest import mock

from click.testing import CliRunner

from preserve.command_line import (
    main,
)


class TestCommandLine(TestCase):

    @mock.patch('preserve.command_line.preserve_organization')
    def test_main_just_orgs(self, mock_preserve_organization):
        runner = CliRunner()
        result = runner.invoke(main, ['someone', 'another'])
        self.assertEqual(len(mock_preserve_organization.mock_calls), 2)
        self.assertEqual(result.exit_code, 0)

    @mock.patch('preserve.command_line.preserve_organization')
    @mock.patch('preserve.command_line.logger')
    def test_main_dest_in_orgs(self, mock_logger, mock_preserve_organization):
        runner = CliRunner()
        result = runner.invoke(main, ['someone', 'myorg', '--dest-org=myorg'])
        self.assertEqual(len(mock_logger.error.mock_calls), 1)
        self.assertEqual(len(mock_preserve_organization.mock_calls), 0)
        self.assertEqual(result.exit_code, 1)
