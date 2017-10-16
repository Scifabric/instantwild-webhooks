# Your API KEY in your PyBossa server
api_key = 'yourkey'
# Your PyBossa server that will be sending the notifications
endpoint = 'http://localhost:5001'
# Background jobs: disabled by default. You need Redis
enable_background_jobs = True
# Queue name: use your own name in case you're using also python-rq
queue_name = 'mywebhooks'
