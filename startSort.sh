NEW_RELIC_CONFIG_FILE=/root/nozomiServer/nozomiSort.ini newrelic-admin run-program gunicorn -w 4 -b 0.0.0.0:9969 app2:app
