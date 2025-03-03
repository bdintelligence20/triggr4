# Gunicorn configuration for Knowledge Hub backend

# Server socket
bind = "0.0.0.0:10000"
backlog = 2048

# Worker processes
workers = 1  # Single worker to avoid memory issues
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 2

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