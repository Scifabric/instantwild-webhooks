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
try:
    import settings
except ImportError:
    import settings_testing as settings
import json
import enki
from base import Test
from analysis import basic, get_task
from mock import patch, Mock, MagicMock, call
import mock


class TestApp(Test):

    """Class for Testing the PyBossa application."""

    def _mock_response(
                self,
                status=200,
                content="CONTENT",
                json_data=None,
                raise_for_status=None):
            """
            since we typically test a bunch of different
            requests calls for a service, we are going to do
            a lot of mock responses, so its usually a good idea
            to have a helper function that builds these things
            """
            mock_resp = mock.Mock()
            # mock raise_for_status call w/optional error
            mock_resp.raise_for_status = mock.Mock()
            if raise_for_status:
                mock_resp.raise_for_status.side_effect = raise_for_status
            # set status code and content
            mock_resp.status_code = status
            mock_resp.content = content
            # add json data if provided
            if json_data:
                mock_resp.json = mock.Mock(
                    return_value=json_data
                )
            return mock_resp

    def create_task_runs_animal(self, user_id=1, user_ip=None):
        """Create task runs."""
        tr = MagicMock()
        tr.task_id=1
        tr.project_id=1
        tr.user_id=user_id
        tr.user_ip=user_ip
        tr.info = dict(answer=[{'animalCount': 1.0,
                               'speciesScientificName': 'lore',
                               'speciesCommonName': 'common',
                               'speciesID': 1}])
        return tr

    def create_task_runs_animal_wrong(self):
        """Create task runs wrong."""
        tr = MagicMock()
        tr.task_id=1
        tr.project_id=1
        tr.user_id=2
        tr.user_ip=''
        tr.info = dict(answer=[{'animalCount': 1,
                               'speciesScientificName': 'wrong',
                               'speciesCommonName': 'fatal',
                               'speciesID': 3}])
        return tr

    def create_task_runs_no_animal(self):
        """Create task runs with no animal."""
        tr = MagicMock()
        tr.task_id=1
        tr.project_id=1
        tr.user_id=3
        tr.user_ip=''
        tr.info = dict(answer=[{'animalCount': -1}])
        return tr


    def test_basic(self):
        """Test basic method works."""
        with patch('enki.Enki', autospec=True):
            enki_mock = enki.Enki(endpoint='server',
                                  api_key='api',
                                  project_short_name='project')
            print enki_mock
            enki_mock.tasks = []
            res = basic(**self.payload)
            assert enki_mock.get_tasks.called
            assert enki_mock.get_task_runs.called
            assert res == 'OK', res

    @patch('enki.pbclient', autospec=True)
    @patch('enki.Enki', autospec=True)
    def test_basic_5_taskruns(self, enki_mock, pbclient):
        """Test that with only 5 taskruns we only check for
        nan values."""
        enki_mock = enki.Enki(endpoint='server',
                              api_key='api',
                              project_short_name='project')
        task = MagicMock()
        task.id = 1
        task.project_id = 1
        task.n_answers = 5
        task.state = 'completed'
        enki_mock.tasks = [task]
        enki_mock.pbclient = pbclient
        task_runs = []
        for i in range(5):
            task_runs.append(self.create_task_runs_no_animal())
        enki_mock.task_runs = dict([(task.id,task_runs)])

        res = basic(**self.payload)
        assert res == 'The five taskruns reported no animal', res

    @patch('enki.pbclient', autospec=True)
    @patch('enki.Enki', autospec=True)
    def test_basic_4_nan_1_animal(self, enki_mock, pbclient):
        """Test 4 non animal 1 with animal."""
        enki_mock = enki.Enki(endpoint='server',
                              api_key='api',
                              project_short_name='project')
        task = MagicMock()
        task.id = 1
        task.project_id = 1
        task.n_answers = 5
        task.state = 'completed'
        pbclient.find_tasks.return_value = [task]
        enki_mock.pbclient = pbclient
        enki_mock.tasks = [task]
        task_runs = []
        for i in range(4):
            task_runs.append(self.create_task_runs_no_animal())
        task_runs.append(self.create_task_runs_animal())
        enki_mock.task_runs = dict([(task.id,task_runs)])

        res = basic(**self.payload)
        assert task.n_answers == 6, task.n_answers
        assert task.state == 'ongoing', task.state
        enki_mock.pbclient.update_task.assert_called_with(task)

    @patch('enki.pbclient', autospec=True)
    @patch('enki.Enki', autospec=True)
    def test_basic_4_nan_2_animal(self, enki_mock, pbclient):
        """Test 4 non animal 2 with animal."""
        enki_mock = enki.Enki(endpoint='server',
                              api_key='api',
                              project_short_name='project')
        task = MagicMock()
        task.id = 1
        task.project_id = 1
        task.n_answers = 6
        task.state = 'completed'
        pbclient.find_tasks.return_value = [task]
        enki_mock.pbclient = pbclient
        enki_mock.tasks = [task]
        task_runs = []
        for i in range(4):
            task_runs.append(self.create_task_runs_no_animal())
        task_runs.append(self.create_task_runs_animal())
        task_runs.append(self.create_task_runs_animal())
        enki_mock.task_runs = dict([(task.id,task_runs)])

        res = basic(**self.payload)
        assert task.n_answers == 7, task.n_answers
        enki_mock.pbclient.update_task.assert_called_with(task)


    @patch('enki.pbclient', autospec=True)
    @patch('enki.Enki', autospec=True)
    def test_basic_10_nan_2_animal(self, enki_mock, pbclient):
        """Test 10 non animal 2 with animal."""
        enki_mock = enki.Enki(endpoint='server',
                              api_key='api',
                              project_short_name='project')
        task = MagicMock()
        task.id = 1
        task.project_id = 1
        task.n_answers = 12
        task.state = 'completed'
        enki_mock.tasks = [task]
        enki_mock.pbclient = pbclient
        task_runs = []
        task_runs.append(self.create_task_runs_animal())
        task_runs.append(self.create_task_runs_animal())
        for i in range(10):
            task_runs.append(self.create_task_runs_no_animal())
        enki_mock.task_runs = dict([(task.id,task_runs)])

        res = basic(**self.payload)
        assert task.n_answers == 12, task.n_answers
        assert res == "10 taskruns reported no animal", res

    @patch('enki.pbclient', autospec=True)
    @patch('enki.Enki', autospec=True)
    def test_basic_10_nan_(self, enki_mock, pbclient):
        """Test 10 non animal."""
        enki_mock = enki.Enki(endpoint='server',
                              api_key='api',
                              project_short_name='project')
        task = MagicMock()
        task.id = 1
        task.project_id = 1
        task.n_answers = 10
        task.state = 'completed'
        enki_mock.tasks = [task]
        pbclient.update_result.return_value = '10 taskruns reported no animal'
        enki_mock.pbclient = pbclient
        task_runs = []
        for i in range(10):
            task_runs.append(self.create_task_runs_no_animal())
        enki_mock.task_runs = dict([(task.id,task_runs)])

        res = basic(**self.payload)
        assert task.n_answers == 10, task.n_answers
        assert res == "10 taskruns reported no animal", res


    @patch('enki.pbclient', autospec=True)
    @patch('enki.Enki', autospec=True)
    def test_basic_10_nan_2_animal(self, enki_mock, pbclient):
        """Test 10 non animal 2 with animal."""
        enki_mock = enki.Enki(endpoint='server',
                              api_key='api',
                              project_short_name='project')
        pbclient.update_result.return_value = '10 taskruns reported no animal'
        enki_mock.pbclient = pbclient
        task = MagicMock()
        task.id = 1
        task.project_id = 1
        task.n_answers = 12
        task.state = 'completed'
        enki_mock.tasks = [task]
        task_runs = []
        task_runs.append(self.create_task_runs_animal())
        task_runs.append(self.create_task_runs_animal())
        for i in range(10):
            task_runs.append(self.create_task_runs_no_animal())
        enki_mock.task_runs = dict([(task.id,task_runs)])

        res = basic(**self.payload)
        assert task.n_answers == 12, task.n_answers
        assert task.state == 'completed', task.state
        assert res == "10 taskruns reported no animal", res

    @patch('enki.pbclient', autospec=True)
    @patch('enki.Enki', autospec=True)
    def test_basic_9_nan_3_animal(self, enki_mock, pbclient):
        """Test 9 non animal 3 with animal."""
        enki_mock = enki.Enki(endpoint='server',
                              api_key='api',
                              project_short_name='project')
        enki_mock.pbclient = pbclient
        task = MagicMock()
        task.id = 1
        task.project_id = 1
        task.n_answers = 12
        task.state = 'completed'
        task.project_id = 1
        updated_task = MagicMock()
        updated_task.id = 1
        updated_task.project_id = 1
        updated_task.n_answers = 13
        updated_task.state = 'ongoing'
        updated_task.project_id = 1
        enki_mock.tasks = [task]
        enki_mock.pbclient.find_tasks.return_value = [task]
        enki_mock.pbclient.update_task.return_value = task
        task_runs = []
        task_runs.append(self.create_task_runs_animal())
        task_runs.append(self.create_task_runs_animal())
        task_runs.append(self.create_task_runs_animal())
        for i in range(9):
            task_runs.append(self.create_task_runs_no_animal())
        enki_mock.task_runs = dict([(task.id,task_runs)])

        res = basic(**self.payload)
        assert task.n_answers == 13, task.n_answers
        assert task.state == 'ongoing', task.state
        #assert res == "No consensus. Asking for one more answer.", res
        assert res.n_answers == 13

    @patch('analysis.requests', autospec=True)
    @patch('enki.pbclient', autospec=True)
    @patch('enki.Enki', autospec=True)
    def test_basic_10_animal(self, enki_mock, pbclient, requests_mock):
        """Test 10 animal."""
        info = [dict(info=dict(iucn_red_list_status='Endangered',
                               species='common'))]
        user_info = dict(info=dict())
        mock_response = self._mock_response(json_data=info, status=200)
        mock_response_2 = self._mock_response(json_data=user_info, status=200)

        requests_mock.get.side_effect = [mock_response, mock_response_2]

        enki_mock = enki.Enki(endpoint='server',
                              api_key='api',
                              project_short_name='project')
        enki_mock.pbclient = pbclient

        result = MagicMock()
        result.id = 1
        result.info = dict()
        enki_mock.pbclient.find_results.return_value = [result]

        task = MagicMock()
        task.id = 1
        task.project_id = 1
        task.n_answers = 10
        task.state = 'completed'
        enki_mock.tasks = [task]
        task_runs = []
        for i in range(10):
            if (i ==1):
                task_runs.append(self.create_task_runs_animal(user_id=1))
            else:
                task_runs.append(self.create_task_runs_animal(user_id=None,
                                                              user_ip=i))
        enki_mock.task_runs = dict([(task.id,task_runs)])

        res = basic(**self.payload)
        assert task.n_answers == 10, task.n_answers
        assert task.state == 'completed', task.state

    @patch('enki.pbclient', autospec=True)
    @patch('enki.Enki', autospec=True)
    def test_basic_24_animal(self, enki_mock, pbclient):
        """Test 24 animal no consensus."""
        enki_mock = enki.Enki(endpoint='server',
                              api_key='api',
                              project_short_name='project')
        task = MagicMock()
        task.id = 1
        task.project_id = 1
        task.n_answers = 24
        task.state = 'completed'

        pbclient.find_tasks.return_value = [task]
        enki_mock.pbclient = pbclient
        enki_mock.tasks = [task]
        task_runs = []
        for i in range(9):
            task_runs.append(self.create_task_runs_animal())
            task_runs.append(self.create_task_runs_no_animal())
        for i in range(6):
            task_runs.append(self.create_task_runs_animal_wrong())

        enki_mock.task_runs = dict([(task.id,task_runs)])

        res = basic(**self.payload)
        assert task.n_answers == 25, task.n_answers
        assert task.state == 'ongoing', task.state

    @patch('enki.pbclient', autospec=True)
    @patch('enki.Enki', autospec=True)
    def test_basic_25_animal(self, enki_mock, pbclient):
        """Test 25 animal no consensus."""
        enki_mock = enki.Enki(endpoint='server',
                              api_key='api',
                              project_short_name='project')
        enki_mock.pbclient = pbclient
        task = MagicMock()
        task.id = 1
        task.project_id = 1
        task.n_answers = 25
        task.state = 'completed'
        enki_mock.tasks = [task]
        task_runs = []
        for i in range(9):
            task_runs.append(self.create_task_runs_animal())
            task_runs.append(self.create_task_runs_no_animal())
        for i in range(7):
            task_runs.append(self.create_task_runs_animal_wrong())

        enki_mock.task_runs = dict([(task.id,task_runs)])

        res = basic(**self.payload)
        assert task.n_answers == 25, task.n_answers
        assert task.state == 'completed', task.state

    @patch('analysis.requests', autospec=True)
    @patch('enki.pbclient', autospec=True)
    @patch('enki.Enki', autospec=True)
    def test_basic_10_animal_consensus(self, enki_mock, pbclient,
                                       requests_mock):
        """Test 10 animal consensus."""
        info = [dict(info=dict(iucn_red_list_status='Endangered',
                               species="common"))]
        user_info = dict(info=dict())
        user_info_wrong = dict(info=dict())
        mock_response = self._mock_response(json_data=info, status=200)
        mock_response_2 = self._mock_response(json_data=user_info, status=200)
        mock_response_3 = self._mock_response(json_data=user_info_wrong, status=200)
        mock_response_4 = self._mock_response(json_data=user_info_wrong, status=200)
        requests_mock.get.side_effect = [mock_response, mock_response_2,
                                         mock_response_3, mock_response_4]

        enki_mock = enki.Enki(endpoint='server',
                              api_key='api',
                              project_short_name='project')
        enki_mock.pbclient = pbclient
        result = MagicMock()
        result.id = 1
        result.info = dict()
        enki_mock.pbclient.find_results.return_value = [result]
        task = MagicMock()
        task.id = 1
        task.project_id = 1
        task.n_answers = 11
        task.info = dict(image='url', deploymentID='deploymentID',
                         Create_time='time',
                         deploymentLocationID='deploymentLocationID')
        task.state = 'completed'
        enki_mock.tasks = [task]
        task_runs = []
        for i in range(10):
            if (i==1):
                task_runs.append(self.create_task_runs_animal(user_id=1))
            else:
                task_runs.append(self.create_task_runs_animal(user_id=None, user_ip='127.0.0.%s'
                                                              % i))
        for i in range(1):
            task_runs.append(self.create_task_runs_animal_wrong())

        for i in range(1):
            task_runs.append(self.create_task_runs_no_animal())

        enki_mock.task_runs = dict([(task.id,task_runs)])

        res = basic(**self.payload)
        assert task.n_answers == 11, task.n_answers
        assert task.state == 'completed', task.state

        answer = self.create_task_runs_animal().info['answer'][0]
        answer['animalCountStd'] = 0.0
        answer['animalCountMin'] = 1.0
        answer['animalCountMax'] = 1.0
        answer['iucn_red_list_status'] = 'Endangered'
        answer['deploymentID'] = 'deploymentID'
        answer['imageURL'] = 'url'
        answer['Create_time'] = 'time'
        answer['deploymentLocationID'] = 'deploymentLocationID'
        # del answer['speciesCommonName']
        del answer['speciesID']

        hp_url = settings.endpoint + '/api/helpingmaterial?all=1&project_id=1&info=scientific_name::' + answer['speciesScientificName'].replace(" ", '%26') + '&fulltextsearch=1'
        user_url = settings.endpoint + '/api/user/%s?api_key=%s' % (1, settings.api_key)
        user_url2 = settings.endpoint + '/api/user/%s?api_key=%s' % (2, settings.api_key)
        user_url3 = settings.endpoint + '/api/user/%s?api_key=%s' % (3, settings.api_key)
        assert requests_mock.get.mock_calls == [call(hp_url), call(user_url),
                                                call(user_url2),
                                                call(user_url3)], requests_mock.get.mock_calls
        enki_mock.pbclient.find_results.assert_called_with(all=1, project_id=1,
                                                           id=1)
        enki_mock.pbclient.update_result.assert_called_with(result)
        print result.info.values()
        print answer.values()
        assert result.info == answer, (result.info, answer)

        user_contrib_correct = dict(info=dict(species_number=1, iucn_number=1, karma=1,
                                    badges=[dict(iucn_red_list_status='Endangered',
                                                            result_id=1,
                                                            number=1)]))
        user_contrib_wrong = dict(info=dict(species_number=0, iucn_number=0, karma=0,
                                  badges=[]))

        calls = [call(user_url,
                      data=json.dumps(user_contrib_correct),
                      headers={'content-type': 'application/json'}),
                call(user_url2,
                      data=json.dumps(user_contrib_wrong),
                      headers={'content-type': 'application/json'})]

        requests_mock.put.assert_has_calls(calls)

    @patch('analysis.requests', autospec=True)
    @patch('enki.pbclient', autospec=True)
    @patch('enki.Enki', autospec=True)
    def test_basic_10_animal_consensus_karma(self, enki_mock, pbclient,
                                       requests_mock):
        """Test 10 animal consensus test karma."""
        info = [dict(info=dict(iucn_red_list_status='Endangered',
                               species='common'))]
        user_info = dict(info=dict(karma=2))
        user_info_wrong = dict(info=dict(karma=2))
        mock_response = self._mock_response(json_data=info, status=200)
        mock_response_2 = self._mock_response(json_data=user_info, status=200)
        mock_response_3 = self._mock_response(json_data=user_info_wrong, status=200)
        requests_mock.get.side_effect = [mock_response, mock_response_2,
                                         mock_response_3]

        enki_mock = enki.Enki(endpoint='server',
                              api_key='api',
                              project_short_name='project')
        enki_mock.pbclient = pbclient
        result = MagicMock()
        result.id = 1
        result.info = dict()
        enki_mock.pbclient.find_results.return_value = [result]
        task = MagicMock()
        task.id = 1
        task.project_id = 1
        task.n_answers = 11
        task.info = dict(image='url', deploymentID='deploymentID',
                         deploymentLocationID='deploymentLocationID',
                         Create_time='time')
        task.state = 'completed'
        enki_mock.tasks = [task]
        task_runs = []
        for i in range(10):
            if (i==1):
                task_runs.append(self.create_task_runs_animal(user_id=1))
            else:
                task_runs.append(self.create_task_runs_animal(user_id=None, user_ip='127.0.0.%s'
                                                              % i))
        for i in range(1):
            task_runs.append(self.create_task_runs_animal_wrong())

        enki_mock.task_runs = dict([(task.id,task_runs)])

        res = basic(**self.payload)
        assert task.n_answers == 11, task.n_answers
        assert task.state == 'completed', task.state

        answer = self.create_task_runs_animal().info['answer'][0]
        answer['animalCountStd'] = 0.0
        answer['animalCountMin'] = 1.0
        answer['animalCountMax'] = 1.0
        answer['iucn_red_list_status'] = 'Endangered'
        answer['deploymentID'] = 'deploymentID'
        answer['imageURL'] = 'url'
        answer['speciesCommonName'] = 'common'
        answer['Create_time'] = 'time'
        answer['deploymentLocationID'] = 'deploymentLocationID'
        del answer['speciesID']

        hp_url = settings.endpoint + '/api/helpingmaterial?all=1&project_id=1&info=scientific_name::' + answer['speciesScientificName'].replace(" ", '%26') + '&fulltextsearch=1'
        user_url = settings.endpoint + '/api/user/%s?api_key=%s' % (1, settings.api_key)
        user_url2 = settings.endpoint + '/api/user/%s?api_key=%s' % (2, settings.api_key)
        assert requests_mock.get.mock_calls == [call(hp_url), call(user_url),
                                                call(user_url2)]
        enki_mock.pbclient.find_results.assert_called_with(all=1, project_id=1,
                                                           id=1)
        enki_mock.pbclient.update_result.assert_called_with(result)
        print answer.keys()
        print result.info.keys()
        assert result.info == answer, (result.info, answer)

        user_contrib_correct = dict(info=dict(species_number=1, iucn_number=1, karma=3,
                                    badges=[dict(iucn_red_list_status='Endangered',
                                                            result_id=1,
                                                            number=1)]))
        user_contrib_wrong = dict(info=dict(species_number=0, iucn_number=0, karma=1,
                                  badges=[]))

        calls = [call(user_url,
                      data=json.dumps(user_contrib_correct),
                      headers={'content-type': 'application/json'}),
                call(user_url2,
                      data=json.dumps(user_contrib_wrong),
                      headers={'content-type': 'application/json'})]

        requests_mock.put.assert_has_calls(calls)

    @patch('analysis.requests', autospec=True)
    @patch('enki.pbclient', autospec=True)
    @patch('enki.Enki', autospec=True)
    def test_basic_10_animal_consensus_karma_min(self, enki_mock, pbclient,
                                       requests_mock):
        """Test 10 animal consensus test karma min is always 0."""
        info = [dict(info=dict(iucn_red_list_status='Endangered',
                               species='common'))]
        user_info = dict(info=dict(karma=2))
        user_info_wrong = dict(info={'karma': 0})
        mock_response = self._mock_response(json_data=info, status=200)
        mock_response_2 = self._mock_response(json_data=user_info, status=200)
        mock_response_3 = self._mock_response(json_data=user_info_wrong, status=200)
        requests_mock.get.side_effect = [mock_response, mock_response_2,
                                         mock_response_3]

        enki_mock = enki.Enki(endpoint='server',
                              api_key='api',
                              project_short_name='project')
        enki_mock.pbclient = pbclient
        result = MagicMock()
        result.id = 1
        result.info = dict()
        enki_mock.pbclient.find_results.return_value = [result]
        task = MagicMock()
        task.id = 1
        task.project_id = 1
        task.n_answers = 11
        task.info = dict(image='url', deploymentID='deploymentID',
                         Create_time='time',
                         deploymentLocationID='deploymentLocationID')
        task.state = 'completed'
        enki_mock.tasks = [task]
        task_runs = []
        for i in range(10):
            if (i==1):
                task_runs.append(self.create_task_runs_animal(user_id=1))
            else:
                task_runs.append(self.create_task_runs_animal(user_id=None, user_ip='127.0.0.%s'
                                                              % i))
        for i in range(1):
            task_runs.append(self.create_task_runs_animal_wrong())

        enki_mock.task_runs = dict([(task.id,task_runs)])

        res = basic(**self.payload)
        assert task.n_answers == 11, task.n_answers
        assert task.state == 'completed', task.state

        answer = self.create_task_runs_animal().info['answer'][0]
        answer['animalCountStd'] = 0.0
        answer['animalCountMin'] = 1.0
        answer['animalCountMax'] = 1.0
        answer['iucn_red_list_status'] = 'Endangered'
        answer['deploymentID'] = 'deploymentID'
        answer['imageURL'] = 'url'
        answer['Create_time'] = 'time'
        answer['deploymentLocationID'] = 'deploymentLocationID'
        answer['speciesCommonName'] = 'common'
        del answer['speciesID']

        hp_url = settings.endpoint + '/api/helpingmaterial?all=1&project_id=1&info=scientific_name::' + answer['speciesScientificName'].replace(" ", '%26') + '&fulltextsearch=1'
        user_url = settings.endpoint + '/api/user/%s?api_key=%s' % (1, settings.api_key)
        user_url2 = settings.endpoint + '/api/user/%s?api_key=%s' % (2, settings.api_key)
        assert requests_mock.get.mock_calls == [call(hp_url), call(user_url),
                                                call(user_url2)]
        enki_mock.pbclient.find_results.assert_called_with(all=1,project_id=1,
                                                           id=1)
        enki_mock.pbclient.update_result.assert_called_with(result)
        assert result.info == answer, (result.info, answer)

        user_contrib_correct = dict(info=dict(species_number=1, iucn_number=1, karma=3,
                                    badges=[dict(iucn_red_list_status='Endangered',
                                                            result_id=1,
                                                            number=1)]))
        user_contrib_wrong = dict(info=dict(species_number=0, iucn_number=0, karma=0,
                                  badges=[]))

        calls = [call(user_url,
                      data=json.dumps(user_contrib_correct),
                      headers={'content-type': 'application/json'}),
                call(user_url2,
                      data=json.dumps(user_contrib_wrong),
                      headers={'content-type': 'application/json'})]

        requests_mock.put.assert_has_calls(calls)

    @patch('analysis.requests', autospec=True)
    @patch('enki.pbclient', autospec=True)
    @patch('enki.Enki', autospec=True)
    def test_basic_10_animal_consensus_badges_work(self, enki_mock, pbclient,
                                       requests_mock):
        """Test 10 animal consensus test badges work."""
        info = [dict(info=dict(iucn_red_list_status='Endangered',
                               species='common'))]
        user_info = dict(info=dict(badges=[], karma=2))
        user_info_wrong = dict(info=dict(karma=-1))
        mock_response = self._mock_response(json_data=info, status=200)
        mock_response_2 = self._mock_response(json_data=user_info, status=200)
        mock_response_3 = self._mock_response(json_data=user_info_wrong, status=200)
        requests_mock.get.side_effect = [mock_response, mock_response_2,
                                         mock_response_3]

        enki_mock = enki.Enki(endpoint='server',
                              api_key='api',
                              project_short_name='project')
        enki_mock.pbclient = pbclient
        result = MagicMock()
        result.id = 1
        result.info = dict()
        enki_mock.pbclient.find_results.return_value = [result]
        task = MagicMock()
        task.id = 1
        task.project_id = 1
        task.n_answers = 11
        task.info = dict(image='url', deploymentID='deploymentID',
                         deploymentLocationID='deploymentLocationID',
                         Create_time='time')
        task.state = 'completed'
        enki_mock.tasks = [task]
        task_runs = []
        for i in range(10):
            if (i==1):
                task_runs.append(self.create_task_runs_animal(user_id=1))
            else:
                task_runs.append(self.create_task_runs_animal(user_id=None, user_ip='127.0.0.%s'
                                                              % i))
        for i in range(1):
            task_runs.append(self.create_task_runs_animal_wrong())

        enki_mock.task_runs = dict([(task.id,task_runs)])

        res = basic(**self.payload)
        assert task.n_answers == 11, task.n_answers
        assert task.state == 'completed', task.state

        answer = self.create_task_runs_animal().info['answer'][0]
        answer['animalCountStd'] = 0.0
        answer['animalCountMin'] = 1.0
        answer['animalCountMax'] = 1.0
        answer['iucn_red_list_status'] = 'Endangered'
        answer['deploymentID'] = 'deploymentID'
        answer['deploymentLocationID'] = 'deploymentLocationID'
        answer['Create_time'] = 'time'
        answer['imageURL'] = 'url'
        answer['speciesCommonName'] = 'common'
        del answer['speciesID']

        hp_url = settings.endpoint + '/api/helpingmaterial?all=1&project_id=1&info=scientific_name::' + answer['speciesScientificName'].replace(" ", '%26') + '&fulltextsearch=1'
        user_url = settings.endpoint + '/api/user/%s?api_key=%s' % (1, settings.api_key)
        user_url2 = settings.endpoint + '/api/user/%s?api_key=%s' % (2, settings.api_key)
        assert requests_mock.get.mock_calls == [call(hp_url), call(user_url),
                                                call(user_url2)]
        enki_mock.pbclient.find_results.assert_called_with(all=1, project_id=1,
                                                           id=1)
        enki_mock.pbclient.update_result.assert_called_with(result)
        assert result.info == answer, (result.info, answer)

        user_contrib_correct = dict(info=dict(species_number=1, iucn_number=1, karma=3,
                                    badges=[dict(iucn_red_list_status='Endangered',
                                                            result_id=1,
                                                            number=1)]))
        user_contrib_wrong = dict(info=dict(species_number=0, iucn_number=0, karma=0,
                                  badges=[]))

        calls = [call(user_url,
                      data=json.dumps(user_contrib_correct),
                      headers={'content-type': 'application/json'}),
                call(user_url2,
                      data=json.dumps(user_contrib_wrong),
                      headers={'content-type': 'application/json'})]

        requests_mock.put.assert_has_calls(calls)

    @patch('analysis.requests', autospec=True)
    @patch('enki.pbclient', autospec=True)
    @patch('enki.Enki', autospec=True)
    def test_basic_10_animal_consensus_badges_duplicates(self, enki_mock, pbclient,
                                       requests_mock):
        """Test 10 animal consensus test badges duplicates work."""
        badge = dict(iucn_red_list_status='Endangered',
                     result_id=1,
                     number=1)
        info = [dict(info=dict(iucn_red_list_status='Endangered',
                               species='common'))]
        user_info = dict(info=dict(badges=[badge], karma=2))
        user_info_wrong = dict(info=dict(karma=-1))
        mock_response = self._mock_response(json_data=info, status=200)
        mock_response_2 = self._mock_response(json_data=user_info, status=200)
        mock_response_3 = self._mock_response(json_data=user_info_wrong, status=200)
        requests_mock.get.side_effect = [mock_response, mock_response_2,
                                         mock_response_3]

        enki_mock = enki.Enki(endpoint='server',
                              api_key='api',
                              project_short_name='project')
        enki_mock.pbclient = pbclient
        result = MagicMock()
        result.id = 1
        result.info = dict()
        enki_mock.pbclient.find_results.return_value = [result]
        task = MagicMock()
        task.id = 1
        task.project_id = 1
        task.n_answers = 11
        task.info = dict(image='url', deploymentID='deploymentID',
                         deploymentLocationID='deploymentLocationID',
                         Create_time='time')
        task.state = 'completed'
        enki_mock.tasks = [task]
        task_runs = []
        for i in range(10):
            if (i==1):
                task_runs.append(self.create_task_runs_animal(user_id=1))
            else:
                task_runs.append(self.create_task_runs_animal(user_id=None, user_ip='127.0.0.%s'
                                                              % i))
        for i in range(1):
            task_runs.append(self.create_task_runs_animal_wrong())

        enki_mock.task_runs = dict([(task.id,task_runs)])

        res = basic(**self.payload)
        assert task.n_answers == 11, task.n_answers
        assert task.state == 'completed', task.state

        answer = self.create_task_runs_animal().info['answer'][0]
        answer['animalCountStd'] = 0.0
        answer['animalCountMin'] = 1.0
        answer['animalCountMax'] = 1.0
        answer['iucn_red_list_status'] = 'Endangered'
        answer['deploymentID'] = 'deploymentID'
        answer['deploymentLocationID'] = 'deploymentLocationID'
        answer['Create_time'] = 'time'
        answer['imageURL'] = 'url'
        answer['speciesCommonName'] = 'common'
        del answer['speciesID']

        hp_url = settings.endpoint + '/api/helpingmaterial?all=1&project_id=1&info=scientific_name::' + answer['speciesScientificName'].replace(" ", '%26') + '&fulltextsearch=1'
        user_url = settings.endpoint + '/api/user/%s?api_key=%s' % (1, settings.api_key)
        user_url2 = settings.endpoint + '/api/user/%s?api_key=%s' % (2, settings.api_key)
        assert requests_mock.get.mock_calls == [call(hp_url), call(user_url),
                                                call(user_url2)]
        enki_mock.pbclient.find_results.assert_called_with(all=1, project_id=1,
                                                           id=1)
        enki_mock.pbclient.update_result.assert_called_with(result)
        print result.info.values()
        print answer.values()
        assert result.info == answer, (result.info, answer)

        user_contrib_correct = dict(info=dict(species_number=1, iucn_number=1, karma=3,
                                    badges=[badge]))
        user_contrib_wrong = dict(info=dict(species_number=0, iucn_number=0, karma=0,
                                  badges=[]))

        calls = [call(user_url,
                      data=json.dumps(user_contrib_correct),
                      headers={'content-type': 'application/json'}),
                call(user_url2,
                      data=json.dumps(user_contrib_wrong),
                      headers={'content-type': 'application/json'})]

        requests_mock.put.assert_has_calls(calls)

    @patch('analysis.requests', autospec=True)
    @patch('enki.pbclient', autospec=True)
    @patch('enki.Enki', autospec=True)
    def test_basic_10_animal_consensus_badges_two_badges(self, enki_mock, pbclient,
                                       requests_mock):
        """Test 10 animal consensus test badges two badges work."""
        badge = dict(iucn_red_list_status='Endangered',
                     result_id=1,
                     number=1)
        badge2 = dict(iucn_red_list_status='Endangered',
                      result_id=2,
                      number=2)

        info = [dict(info=dict(iucn_red_list_status='Endangered',
                               species='common'))]
        user_info = dict(info=dict(badges=[badge2], karma=2))
        user_info_wrong = dict(info=dict(karma=-1))
        mock_response = self._mock_response(json_data=info, status=200)
        mock_response_2 = self._mock_response(json_data=user_info, status=200)
        mock_response_3 = self._mock_response(json_data=user_info_wrong, status=200)
        requests_mock.get.side_effect = [mock_response, mock_response_2,
                                         mock_response_3]

        enki_mock = enki.Enki(endpoint='server',
                              api_key='api',
                              project_short_name='project')
        enki_mock.pbclient = pbclient
        result = MagicMock()
        result.id = 1
        result.info = dict()
        enki_mock.pbclient.find_results.return_value = [result]
        task = MagicMock()
        task.id = 1
        task.project_id = 1
        task.n_answers = 11
        task.info = dict(image='url', deploymentID='deploymentID',
                         deploymentLocationID='deploymentLocationID',
                         Create_time='time')
        task.state = 'completed'
        enki_mock.tasks = [task]
        task_runs = []
        for i in range(10):
            if (i==1):
                task_runs.append(self.create_task_runs_animal(user_id=1))
            else:
                task_runs.append(self.create_task_runs_animal(user_id=None, user_ip='127.0.0.%s'
                                                              % i))
        for i in range(1):
            task_runs.append(self.create_task_runs_animal_wrong())

        enki_mock.task_runs = dict([(task.id,task_runs)])

        res = basic(**self.payload)
        assert task.n_answers == 11, task.n_answers
        assert task.state == 'completed', task.state

        answer = self.create_task_runs_animal().info['answer'][0]
        answer['animalCountStd'] = 0.0
        answer['animalCountMin'] = 1.0
        answer['animalCountMax'] = 1.0
        answer['iucn_red_list_status'] = 'Endangered'
        answer['deploymentID'] = 'deploymentID'
        answer['deploymentLocationID'] = 'deploymentLocationID'
        answer['Create_time'] = 'time'
        answer['imageURL'] = 'url'
        answer['speciesCommonName'] = 'common'
        del answer['speciesID']

        hp_url = settings.endpoint + '/api/helpingmaterial?all=1&project_id=1&info=scientific_name::' + answer['speciesScientificName'].replace(" ", '%26') + '&fulltextsearch=1'
        user_url = settings.endpoint + '/api/user/%s?api_key=%s' % (1, settings.api_key)
        user_url2 = settings.endpoint + '/api/user/%s?api_key=%s' % (2, settings.api_key)
        assert requests_mock.get.mock_calls == [call(hp_url), call(user_url),
                                                call(user_url2)]
        enki_mock.pbclient.find_results.assert_called_with(all=1, project_id=1,
                                                           id=1)
        enki_mock.pbclient.update_result.assert_called_with(result)
        print result.info.values()
        print answer.values()
        assert result.info == answer, (result.info, answer)

        user_contrib_correct = dict(info=dict(species_number=2, iucn_number=2, karma=3,
                                    badges=[badge2, badge]))
        user_contrib_wrong = dict(info=dict(species_number=0, iucn_number=0, karma=0,
                                  badges=[]))

        calls = [call(user_url,
                      data=json.dumps(user_contrib_correct),
                      headers={'content-type': 'application/json'}),
                call(user_url2,
                      data=json.dumps(user_contrib_wrong),
                      headers={'content-type': 'application/json'})]

        requests_mock.put.assert_has_calls(calls)

    @patch('analysis.requests', autospec=True)
    @patch('enki.pbclient', autospec=True)
    @patch('enki.Enki', autospec=True)
    def test_basic_10_animal_consensus_badges_two_badges_user_no_info(self, enki_mock, pbclient,
                                       requests_mock):
        """Test 10 animal consensus test badges two badges work for user with
        no info field."""
        badge = dict(iucn_red_list_status='Endangered',
                     result_id=1,
                     number=1)
        badge2 = dict(iucn_red_list_status='Endangered',
                      result_id=2,
                      number=2)

        info = [dict(info=dict(iucn_red_list_status='Endangered',
                               species='common'))]
        user_info = dict(info=dict(badges=[badge2], karma=2))
        user_info_wrong = dict(info=dict())
        mock_response = self._mock_response(json_data=info, status=200)
        mock_response_2 = self._mock_response(json_data=user_info, status=200)
        mock_response_3 = self._mock_response(json_data=user_info_wrong, status=200)
        requests_mock.get.side_effect = [mock_response, mock_response_2,
                                         mock_response_3]

        enki_mock = enki.Enki(endpoint='server',
                              api_key='api',
                              project_short_name='project')
        enki_mock.pbclient = pbclient
        result = MagicMock()
        result.id = 1
        result.info = dict()
        enki_mock.pbclient.find_results.return_value = [result]
        task = MagicMock()
        task.id = 1
        task.project_id = 1
        task.n_answers = 11
        task.info = dict(image='url', deploymentID='deploymentID',
                         deploymentLocationID='deploymentLocationID',
                         Create_time='time')
        task.state = 'completed'
        enki_mock.tasks = [task]
        task_runs = []
        for i in range(10):
            if (i==1):
                task_runs.append(self.create_task_runs_animal(user_id=1))
            else:
                task_runs.append(self.create_task_runs_animal(user_id=None, user_ip='127.0.0.%s'
                                                              % i))
        for i in range(1):
            task_runs.append(self.create_task_runs_animal_wrong())

        enki_mock.task_runs = dict([(task.id,task_runs)])

        res = basic(**self.payload)
        assert task.n_answers == 11, task.n_answers
        assert task.state == 'completed', task.state

        answer = self.create_task_runs_animal().info['answer'][0]
        answer['animalCountStd'] = 0.0
        answer['animalCountMin'] = 1.0
        answer['animalCountMax'] = 1.0
        answer['iucn_red_list_status'] = 'Endangered'
        answer['deploymentID'] = 'deploymentID'
        answer['deploymentLocationID'] = 'deploymentLocationID'
        answer['Create_time'] = 'time'
        answer['imageURL'] = 'url'
        answer['speciesCommonName'] = 'common'
        del answer['speciesID']

        hp_url = settings.endpoint + '/api/helpingmaterial?all=1&project_id=1&info=scientific_name::' + answer['speciesScientificName'].replace(" ", '%26') + '&fulltextsearch=1'
        user_url = settings.endpoint + '/api/user/%s?api_key=%s' % (1, settings.api_key)
        user_url2 = settings.endpoint + '/api/user/%s?api_key=%s' % (2, settings.api_key)
        assert requests_mock.get.mock_calls == [call(hp_url), call(user_url),
                                                call(user_url2)]
        enki_mock.pbclient.find_results.assert_called_with(all=1, project_id=1,
                                                           id=1)
        enki_mock.pbclient.update_result.assert_called_with(result)
        assert result.info == answer, (result.info, answer)

        user_contrib_correct = dict(info=dict(species_number=2, iucn_number=2, karma=3,
                                    badges=[badge2, badge]))
        user_contrib_wrong = dict(info=dict(species_number=0, iucn_number=0, karma=0,
                                  badges=[]))

        calls = [call(user_url,
                      data=json.dumps(user_contrib_correct),
                      headers={'content-type': 'application/json'}),
                call(user_url2,
                      data=json.dumps(user_contrib_wrong),
                      headers={'content-type': 'application/json'})]

        requests_mock.put.assert_has_calls(calls)

    @patch('enki.pbclient', autospec=True)
    def test_get_task(self, pbclient):
        """Test get_task works."""
        pbclient.find_tasks.return_value = [1]
        res = get_task(1, 1)
        assert res == 1, res
        pbclient.find_tasks.return_value = []
        res = get_task(1, 1)
        assert len(res) == 0
