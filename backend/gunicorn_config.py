# Gunicorn configuration for Knowledge Hub backend

# Server socket
bind = "0.0.0.0:8080"
backlog = 2048

# Worker processes
workers = 2  # Increased from 1 to 2 for better concurrency
worker_class = 'sync'  # Reverted to 'sync' to avoid gevent monkey patching issues
worker_connections = 1000
timeout = 300  # Increased to 5 minutes to match Cloud Run timeout
keepalive = 2

# Get environment variables for configuration
import os
workers = int(os.environ.get('GUNICORN_WORKERS', '2'))
timeout = int(os.environ.get('GUNICORN_TIMEOUT', '300'))

# Memory management
max_requests = 1000  # Recycle workers after 1000 requests
max_requests_jitter = 200  # Add randomness to recycling
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Preload application
preload_app = True  # Load app code before forking workers

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
errorlog = '-'
loglevel = 'info'
accesslog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'knowledge-hub-api'

# Server hooks
def on_starting(server):
    server.log.info("Starting up Knowledge Hub API")

def on_exit(server):
    server.log.info("Shutting down Knowledge Hub API")

# Worker hooks
def pre_fork(server, worker):
    pass

def pre_exec(server):
    server.log.info("Forked child, re-executing")

def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    worker.log.info("Worker received INT or QUIT signal")

def worker_abort(worker):
    worker.log.info("Worker received SIGABRT signal")

def worker_exit(server, worker):
    import gc
    gc.collect()  # Explicitly trigger garbage collection
