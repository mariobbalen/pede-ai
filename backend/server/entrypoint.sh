#!/bin/sh
set -e

case "$1" in
  runserver)
    python - <<'PYEOF'
import os
import socket
import time

host = os.environ.get("RABBITMQ_HOST", "localhost")
for _ in range(30):
    try:
        socket.create_connection((host, 5672), timeout=2).close()
        break
    except OSError:
        time.sleep(1)
PYEOF
    python broker/setup.py
    python manage.py migrate --noinput
    python manage.py loaddata restaurants_seed
    exec python manage.py runserver 0.0.0.0:8000
    ;;
  consume_status)
    exec python manage.py consume_status
    ;;
  *)
    exec "$@"
    ;;
esac
