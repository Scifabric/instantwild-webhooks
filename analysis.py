# -*- coding: utf8 -*-
# This file is part of PyBossa.
#
# Copyright (C) 2017 Scifabric LTD.
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

import enki
import json
try:
    import settings
except ImportError:
    import settings_testing as settings

import requests
import time
import pandas as pd
import numpy as np

# STATUS =  ['Extinct', 'Extinct in the wild', 'Critically Endangered', 'Endangered',
#             'Vulnerable', 'Near Threatened', 'Least Concern']

# NORMAL = [ 'Data deficient', 'Not evaluated']

RARE_FINDS = ['Endangered', 'Critically Endangered']

REST = ['Extinct', 'Extinct in the wild', 'Vulnerable', 'Near Threatened',
        'Least Concern', 'Data deficient', 'Not evaluated']

def give_badges(e, t, answers, result):
    topSpeciesScientific = [x['speciesScientificName'] for x in answers]
    for tr in e.task_runs[t.id]:
        if tr.user_id:
            if (len(tr.info['answer']) == 1 and
               tr.info['answer'][0]['animalCount'] == -1):
                user_answer = []
            else:
                user_answer = list(filter(lambda x: x['speciesScientificName']
                                          in topSpeciesScientific,
                                          tr.info['answer']))
            url = settings.endpoint + '/api/user/%s?api_key=%s' % (tr.user_id, settings.api_key)
            res = requests.get(url)
            contributor = res.json()

            if len(user_answer) > 0:
                print "User %s chose the good answer" % tr.user_id
                #print contributor.get('info').get('extra')
                new_badges = []
                for ua in user_answer:
                    iucn_red_list_status = filter(lambda a:
                                                  a['speciesScientificName'] ==
                                                  ua['speciesScientificName'],
                                                  answers)[0]['iucn_red_list_status']
                    badge= dict(iucn_red_list_status=iucn_red_list_status,
                                number=1,
                                result_id=result.id)
                    new_badges.append(badge)
                if contributor.get('info').get('extra'):
                    if contributor.get('info').get('extra').get('badges'):
                        current_badges = contributor.get('info').get('extra').get('badges')
                        if (len(filter(lambda b: b['result_id'] ==
                                      result.id, current_badges)) == 0):
                            contributor['info']['extra']['badges'].append(badge)
                        else:
                            print("Badge already in place")
                    else:
                        contributor['info']['extra'] = dict(badges=[badge])
                else:
                    contributor['info']['extra'] = dict(badges=[badge])
                badges = contributor['info']['extra']['badges']
                iucn_number = len(filter(lambda b: b['iucn_red_list_status'] in
                                     RARE_FINDS, badges))
                species_number = len(filter(lambda b: b['iucn_red_list_status'] in
                                        REST, badges))
                #contributor['info']['iucn_number'] = len(contributor['info']['extra']['badges'])
                contributor['info']['iucn_number'] = iucn_number
                contributor['info']['species_number'] = species_number + iucn_number
                if contributor['info'].get('karma'):
                    contributor['info']['karma'] += 1
                else:
                    contributor['info']['karma'] = 1
            else:
                print "User %s chose the wrong answer" % tr.user_id
                if contributor['info'].get('iucn_number') is None:
                    contributor['info']['iucn_number'] = 0
                if contributor['info'].get('species_number') is None:
                    contributor['info']['species_number'] = 0
                if contributor['info'].get('karma'):
                    contributor['info']['karma'] -= 1
                    if contributor['info']['karma'] < 0:
                        contributor['info']['karma'] = 0
                else:
                    contributor['info']['karma'] = 0
                if contributor['info'].get('extra') is None:
                    contributor['info']['extra'] = dict(badges=[])
            # Update contributor
            contributor.pop('n_answers', None)
            contributor.pop('rank', None)
            contributor.pop('score', None)
            contributor.pop('registered_ago', None)
            res = requests.put(url, headers={'content-type':
                                             'application/json'},
                               data=json.dumps(contributor))
            time.sleep(0)


def get_red_list_status(topSpeciesScientific):
    hp_url = settings.endpoint + '/api/helpingmaterial?all=1&info=scientific_name::' + topSpeciesScientific.replace(" ", '%26') + '&fulltextsearch=1'
    res = requests.get(hp_url)
    iucn_red_list_status = None
    if res.status_code == 200:
        data = res.json()
        if len(data) > 0:
            iucn_red_list_status = data[0]['info']['iucn_red_list_status']
    return iucn_red_list_status


def get_count_nan(df):
    vc = None
    if 'speciesID' in df.columns and 'speciesScientificName' in df.columns:
        df['speciesID'] = df['speciesID'].astype(str)
        # df['speciesScientificName'] = df['speciesScientificName'].astype(str)
        vc = df['speciesScientificName'].value_counts(dropna=False)
        # df = e.task_runs_df[t.id]
        analysis = dict(df['speciesID'].value_counts())
        # If everyone answered no animal
    return vc


def get_consensus(df, th=10):
    consensus = df.groupby('speciesScientificName').filter(lambda x: len(x) >= th)
    answer = []
    for sp, val in consensus.groupby('speciesScientificName').size().iteritems():
        animalCountDescribe = consensus.loc[consensus['speciesScientificName'] == sp,
                                            'animalCount'].describe()
        answer.append(dict(speciesScientificName=sp,
                           animalCount=animalCountDescribe['mean'],
                           animalCountStd=animalCountDescribe['std'],
                           animalCountMin=animalCountDescribe['min'],
                           animalCountMax=animalCountDescribe['max']))
    return answer

def basic(**kwargs):
    """A basic analyzer."""
    e = enki.Enki(endpoint=settings.endpoint,
                  api_key=settings.api_key,
                  project_short_name=kwargs['project_short_name'],
                  all=1)
    if kwargs['task_id']  != 95049:
        e.get_tasks(task_id=kwargs['task_id'])
        e.get_task_runs()
        labels = ['task_run_id', 'speciesID', 'speciesScientificName',
                  'speciesCommonName', 'animalCount']
        for t in e.tasks: # pragma: no cover
            data = []
            for tr in e.task_runs[t.id]:
                for datum in tr.info['answer']:
                   data.append(datum)
            df = pd.DataFrame(data)
            # If 5 first answers is nan (nothing here) mark task
            # as completed
            vc = get_count_nan(df)
            if len(e.task_runs[t.id]) == 5:
                msg = "The five taskruns reported no animal"
                if type(vc) == pd.Series and (str(vc.index[0]) == 'nan' and vc.values[0] == 5):
                    return msg
                else:
                    t.n_answers += 1
                    t.state = 'ongoing'
                    enki.pbclient.update_task(t)
                return msg
            else:
                if str(vc.index[0]) == 'nan' and vc.values[0] >= 10:
                    msg = "10 taskruns reported no animal"
                    return msg
                else:
                    answers = get_consensus(df, th=10)
                    if len(answers) == 0:
                        if len(e.task_runs[t.id]) < 25:
                            msg = "No consensus. Asking for one more answer."
                            t.n_answers += 1
                            t.state = 'ongoing'
                            enki.pbclient.update_task(t)
                            return msg
                    else:
                        for a in answers:
                            iucn_red_list_status = get_red_list_status(a['speciesScientificName'])
                            a['iucn_red_list_status'] = iucn_red_list_status
                            a['imageURL'] = t.info.get('image', None)
                            a['deploymentID'] = t.info.get('deploymentID', None)
                        result = enki.pbclient.find_results(project_id=kwargs['project_id'],
                                                            id=kwargs['result_id'])[0]
                        if len(answers) == 1:
                            result.info = answers[0]
                        if len(answers) >= 2:
                            result.info = dict(answers=answers)
                        give_badges(e, t, answers, result)
                        result = enki.pbclient.update_result(result)
                        return 'OK'
    return "OK"
