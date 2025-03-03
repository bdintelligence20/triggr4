# gunicorn_config.py
bind = "0.0.0.0:8000"
workers = 2
threads = 2
worker_class = 'gthread'
worker_connections = 1000
timeout = 120
keepalive = 2
max_requests = 100
max_requests_jitter = 10
worker_tmp_dir = '/dev/shm'
accesslog = '-'
errorlog = '-'
loglevel = 'info'
capture_output = True
enable_stdio_inheritance = True

# Memory optimization
max_requests = 100  # Restart workers after this many requests
max_requests_jitter = 10  # Add randomness to the restart interval
worker_tmp_dir = '/dev/shm'  # Use RAM for temporary files

# Function to clean up worker processes
def worker_exit(server, worker):
    import gc
    gc.collect()