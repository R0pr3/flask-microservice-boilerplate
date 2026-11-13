# TLS certificates

This directory is mounted read-only into the Nginx container at
`/etc/nginx/certs`. The files below are git-ignored and must be generated
locally — never commit private keys.

## Generate a self-signed certificate for local development

```bash
openssl req -x509 -nodes -newkey rsa:2048 -days 365 \
  -keyout nginx/certs/server.key \
  -out nginx/certs/server.crt \
  -subj "/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
```

## Production

Terminate TLS with a certificate issued by a public CA (or your internal PKI)
and place it at the same paths, or switch Nginx to a certbot-managed volume.
