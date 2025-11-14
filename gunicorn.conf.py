# gunicorn.conf.py
import multiprocessing

# Configuración optimizada para Render.com
bind = "0.0.0.0:10000"
workers = 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2
max_requests = 500
max_requests_jitter = 50
preload_app = True

# Logs
accesslog = "-"
errorlog = "-"
loglevel = "info"

def worker_abort(worker):
    worker.log.info("worker received ABORT")