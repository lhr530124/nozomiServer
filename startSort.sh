NEW_RELIC_CONFIG_FILE=/root/NozomiEnv/NozomiSort.ini newrelic-admin run-program gunicorn -w 1 -b 0.0.0.0:9061 app2:app
