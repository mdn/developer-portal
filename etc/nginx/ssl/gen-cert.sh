#!/bin/sh

cfssl gencert -initca ./cfssl.json | cfssljson -bare ca -
cfssl gencert -ca=./ca.pem -ca-key=./ca-key.pem -config=./ca-config.json -profile=server ./cfssl.json | cfssljson -bare developer-portal-127-0-0-1.nip.io
