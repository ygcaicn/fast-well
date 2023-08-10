from __future__ import absolute_import, unicode_literals

broker_url = "redis://127.0.0.1:6379"
result_backend = "redis://127.0.0.1:6379"

accept_content = ['json']
enable_utc = False
task_serializer = 'json'
timezone = 'UTC'
task_track_started = True
worker_hijack_root_logger = False
worker_redirect_stdouts_level = 'ERROR'
result_expires = 60 * 60 * 24

