NEW_RELIC_CONFIG_FILE=/root/NozomiEnv/newrelic.ini newrelic-admin run-program gunicorn -w 4 -b 0.0.0.0:9412 app:app
