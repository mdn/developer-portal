#!/bin/sh

SSL_DIR=$(dirname "$0")
BASENAME="developer-portal-127-0-0-1.nip.io"
SSL_KEY="${SSL_DIR}/${BASENAME}-key.pem"
SSL_CRT="${SSL_DIR}/${BASENAME}.pem"


if [ ! -f "${SSL_KEY}" ] || [ ! -f "${SSL_CRT}" ]; then
    cfssl gencert -initca ./cfssl.json | cfssljson -bare ca -
    cfssl gencert -ca=./ca.pem -ca-key=./ca-key.pem -config=./ca-config.json -profile=server ./cfssl.json | cfssljson -bare "${BASENAME}"
else
    echo "${SSL_KEY} and ${SSL_CRT} already exists."
fi
