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
Base package for testing PyBossa application.

This exports:
    - Test a generic class for setting up database and fixtures

"""
from app import app

# PseudoRequest = namedtuple('PseudoRequest',
#                            ['text', 'status_code', 'headers'])


class Test(object):

    """Class for Testing the PyBossa application."""

    payload = dict(fired_at=u'2014-11-17 09:49:27',
                   project_short_name=u'project',
                   project_id=1,
                   task_id=1,
                   result_id=1,
                   event=u'task_completed')

    ERR_MSG_200_STATUS_CODE = 'Status code should be 200'
    ERR_MSG_404_STATUS_CODE = 'Status code should be 404'

    def setUp(self):
        """Setup method for configuring the tests."""
        self.app = app
        self.app.config['TESTING'] = True
        self.tc = self.app.test_client()
