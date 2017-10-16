# -*- coding: utf8 -*-
# This file is part of PyBossa.
#
# Copyright (C) 2015 SciFabric LTD.
#
# PyBossa is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyBossa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with PyBossa. If not, see <http://www.gnu.org/licenses/>.
"""
App package for testing PyBossa application.

This exports:
    - Test the app

"""
import json
from base import Test
from app import app
from mock import patch


class TestApp(Test):

    """Class for Testing the PyBossa application."""


    def setUp(self):
        """Setup method for configuring the tests."""
        self.app = app
        self.app.config['TESTING'] = True
        self.tc = self.app.test_client()

    def test_get_works(self):
        """Test GET method works."""
        res = self.tc.get('/')
        assert res.status_code == 200, self.ERR_MSG_200_STATUS_CODE

    @patch('settings.enable_background_jobs', False)
    @patch('app.basic')
    def test_post_works(self, mock):
        """Test POST method works."""
        res = self.tc.post('/', headers={'Content-type': 'application/json'},
                           data=json.dumps(self.payload), follow_redirects=True)
        assert mock.called
        assert res.status_code == 200, self.ERR_MSG_200_STATUS_CODE
        assert "OK" in res.data, res.data

    @patch('settings.enable_background_jobs', True)
    @patch('app.Queue')
    def test_post_works_with_queues(self, mock):
        """Test POST method works with queues."""
        res = self.tc.post('/', headers={'Content-type': 'application/json'},
                           data=json.dumps(self.payload), follow_redirects=True)
        assert mock.called
        assert res.status_code == 200, self.ERR_MSG_200_STATUS_CODE
        assert "OK" in res.data, res.data
