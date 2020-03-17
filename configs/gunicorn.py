from os import getenv
from multiprocessing import cpu_count

bind = f"0.0.0.0:{getenv('APP_PORT', '8000')}"

# Log section
if getenv('DEBUG').tolower() == "true":
    loglevel = 'debug'
else:
    loglevel = 'info'

accesslog = '-'
errorlog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s \"%(r)s\" %(s)s %(b)s \"%(f)s\" \"%(a)s\" %({X_Forwarded_For}i)s"'

# How long to keep connection alive, this should be timed
# a little less than the ELB idle timeout
keepalive = getenv('APP_GUNICORN_TIMEOUT', '118')

# NOTE: use keepalive instead of timeout
# timeout = getenv('APP_GUNICORN_TIMEOUT', '118')

if getenv('DJANGO_ENV') == 'dev':
    workers = '3'
else:
    # Automatically figure number of workers if environment is not set
    cpu = (cpu_count() * 2 + 1)
    workers = getenv('APP_GUNICORN_WORKERS', cpu)

worker_connections = getenv('APP_GUNICORN_WORKER_CONNECTIONS', '1000')
worker_class = getenv('GUNICORN_WORKER_CLASS', 'gunicorn.workers.ggevent.GeventWorker')
worker_tmp_dir = '/dev/shm'


# Called just after a worker has been forked.
def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)
