"""
Gunicorn configuration file for server setup.

Including port binding, workers,logging, and request handling parameters.
"""

from multiprocessing import cpu_count

bind = "0.0.0.0:8000"

# Worker Options
workers = cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"

# Logging Options
loglevel = "info"
accesslog = "./logs/api-access.log"
errorlog = "./logs/api-error.log"

max_requests = 1000
max_requests_jitter = 100
timeout = 3600
