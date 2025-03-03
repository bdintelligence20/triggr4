# gunicorn_config.py
bind = "0.0.0.0:10000"
workers = 1  # Reduce to a single worker to maximize available memory
threads = 2
worker_class = 'sync'  # Use sync worker instead of gthread
worker_connections = 10  # Limit concurrent connections
timeout = 120
keepalive = 2
max_requests = 50
max_requests_jitter = 10
worker_tmp_dir = '/dev/shm'
accesslog = '-'
errorlog = '-'
loglevel = 'info'
capture_output = True
enable_stdio_inheritance = True

# Memory optimization
preload_app = False  # Don't preload app to reduce memory usage

# Function to clean up worker processes
def worker_exit(server, worker):
    import gc
    gc.collect()