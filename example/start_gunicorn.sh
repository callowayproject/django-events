#!/bin/bash
set -e
HOMEDIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CONF="$HOMEDIR/conf/gunicorn_conf.py"
NAME="$(basename $HOMEDIR)"
cd $HOMEDIR
source virtualenv/bin/activate
exec $HOMEDIR/virtualenv/bin/python manage.py run_gunicorn --config $CONF $@
