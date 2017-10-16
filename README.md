[![Build
Status](https://travis-ci.org/Scifabric/instantwild-webhooks.svg)](https://travis-ci.org/Scifabric/instantwild-webhooks)
[![Coverage Status](https://img.shields.io/coveralls/Scifabric/instantwild-webhooks.svg)](https://coveralls.io/r/Scifabric/instantwild-webhooks?branch=master)
## Instant Wild data analysis

This is the code that computes and gives badges to the PYBOSSA project [Instant Wild](https://instantwild.zsl.org).

The code is run when a task is completed. When a task is completed, the webhooks solution is triggered and the 
statistical analysis computed. By default each task is analyzed by 5 different people. When this happens, the
following schema is followed:

1. If the 5 first answers say that there's no animal in the picture, the task is left as completed. Else,
    1. We reset the state of the task to *ongoing* asking one extra person to contribute to the same picture
       until there are 10 contributions agreeing that there is an animal, and the animal is the same (i.e. an
       elephant) or if we got 25 answers with different solutions/options.
    2. If we have 10 people agreeing on a picture, the system gives "badges" and karma to users:
        1. If the user answered correctly, then, the karma is increased in one, else it's decreased by one (karma cannot be lower than zero).
        2. If the identified animal is an Endangered species, then, the iucn_red_list number is increased as well to reflect it.


That's all! The projec has set of tests (check the tests_analysis.py file) for checking all the available options. The next sections
explain how the PYBOSSA webhooks solution works.

### This project uses the PYBOSSA webhooks analysis tool

This very simple web module shows how you can easily analyze your PyBossa
project in real-time.

PyBossa supports webhooks, notifying via an HTTP POST request the task that has
been completed by the volunteers or users. The POST sends basically the
following data:

```

{'fired_at':,
 'project_short_name': 'project-slug',
 'project_id': 1,
 'task_id': 1,
 'result_id': 1,
 'event': 'task_completed'} 

```

The PyBossa server sends all the required information to analyze the results of
the contributions of the volunteers for a given task using
[Enki](https://github.com/PyBossa/enki).

While the main purpose of this project is to do the analysis of the results,
you can customize and fork this project to do many more things like:

 * Post to Twitter that your project has completed a task.
 * Upload the results to your DropBox folder by writing the results in a file.
 * etc.

In this specific version, the **analysis** module only shows how you can easily 
get the most voted option for an image pattern recognition project.

## Installation

To install the project all you need is run the following command (we recommend
you to use a virtual environment):

```bash
pip install -r requirements.txt
```

Now, copy the settings.py.template file to: **settings.py** and fill in the
information. Once you are done with this file, you'll be ready to run the
server.

**NOTE**: Be sure to have a PyBossa API-KEY as the analysis will be stored in the 
PyBossa results table.

**NOTE**: It requires a PyBossa server >= 1.2.0.



## Running the server

Now that you've the required libraries installed, running the server is as
simple as this:

```bash
python app.py
```

## Configuring background jobs

By default, this project has disabled the creation of queues in your system. If
you expect to have lots of contributions in your project, we recommend you to
enable them.

To support queues you will need to install in your machine a Redis server.
Then, change the flag: **enable_background_jobs** to True in your settings.py
file, and restart the server. 

*Note*: if you are already running a Redis server and queues, you can customize
the name of your queue in the settings file. Check out the config variable:
**queue_name**.

### Running the background jobs

Now that you have the project running background jobs, you need to process
them. This is very simple, in another terminal run the following command:

```bash
rqworker mywebhooks
```

*NOTE*: If you've changed the name of the queue, please, update the previous
command with your new queue name. That's all! Enjoy!!!

## LICENSE 

See COPYING file.
