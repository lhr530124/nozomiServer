 NEW_RELIC_CONFIG_FILE=/data/nozomiServer/newrelicSort.ini newrelic-admin run-program gunicorn -w 2 -b 0.0.0.0:9968 app2:app
