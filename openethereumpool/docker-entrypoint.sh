#!/bin/sh
set -e

if [[ -z $TELEGRAM_TOKEN ]]; then
	echo "A TELEGRAM_TOKEN is required to run this container."
	exit 1
fi

if [[ -z $URI_MONGODB ]]; then
	echo "A URI_MONGODB is required to run this container."
	exit 1
fi

if [[ -z $URL_POOL ]]; then
	echo "A URL_POOL is required to run this container."
	exit 1
fi

cat > conf/OpenEthereumPool.conf <<EOF
[BASIC]
tokenBot = $TELEGRAM_TOKEN
connectMongoDB = $URI_MONGODB
pathLog = log/logPool2Mine.log
fileLog = False

[API]
poolStats = $URL_POOL/api/stats
addressStats = $URL_POOL/api/accounts/
EOF

/usr/sbin/crond -b

exec "$@"
