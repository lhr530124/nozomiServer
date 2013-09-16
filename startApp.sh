NELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program gunicorn -w 1 -b 0.0.0.0:9501 app:app
