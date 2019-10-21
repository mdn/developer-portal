# SSL support for the local build

This folder will contain self-signed certificates for SSL support in local development.

They are generated/updated each time the local Docker stack is upped using `etc/nginx/ssl/generate_dev_cert.sh`

See `services:app:command` in `docker-compose.yml` for where this is hooked in.
