import os


def num_cpus():
    if not hasattr(os, "sysconf"):
        raise RuntimeError("No sysconf detected.")
    return os.sysconf("SC_NPROCESSORS_ONLN")

INSTANCE_DIR = os.path.dirname(os.path.dirname(__file__))
INSTANCE_NAME = os.path.basename(os.path.dirname(INSTANCE_DIR))
PROJECT_DIR = os.path.dirname(INSTANCE_DIR)

if os.path.exists(os.path.join(PROJECT_DIR, 'current_deploy')):
    NAME = 'education'
    workers = num_cpus() * 2 + 1
else:
    NAME = INSTANCE_NAME

bind = "unix:///var/run/%s.sock" % NAME
pidfile = "/var/run/%s.pid" % NAME
user = "www-data"
group = "www-data"
accesslog = "/var/log/gunicorn/%s.access.log" % NAME
errorlog = "/var/log/gunicorn/%s.error.log" % NAME
proc_name = NAME
