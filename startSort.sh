NEW_RELIC_CONFIG_FILE=/root/nozomiServer/nozomiSort.ini newrelic-admin run-program gunicorn -k gevent -w 4 -b 0.0.0.0:9966 app2:app
