NELIC_CONFIG_FILE=/root/nozomiServer/nozomi.ini newrelic-admin run-program gunicorn -w 4 -b 0.0.0.0:9880 app:app
