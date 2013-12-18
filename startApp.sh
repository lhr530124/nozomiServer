NEW_RELIC_CONFIG_FILE=/data/nozomiServer/newrelic.ini newrelic-admin run-program gunicorn -w 4 -b 0.0.0.0:8080 app:app
