NELIC_CONFIG_FILE=/root/NozomiEnv/newrelic.ini newrelic-admin run-program gunicorn -w 1 -b 0.0.0.0:9830 app:app
