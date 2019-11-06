# SSL support for the local build

This folder will contain self-signed certificates for SSL support in local development.

They are generated/updated each time the local Docker stack is upped using `etc/nginx/ssl/gen-cert.sh`

See `services:cfssl:entrypoint` in `docker-compose.yml` for where this is hooked in.
