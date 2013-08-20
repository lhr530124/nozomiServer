NELIC_CONFIG_FILE=/root/NozomiEnv/newrelic.ini newrelic-admin run-program gunicorn -w 4 -b 0.0.0.0:9060 app:app
