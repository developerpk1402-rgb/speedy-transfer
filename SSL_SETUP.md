SSL setup instructions (summary)

1) Purchase and download cert
   - You said you'll buy from https://certs.securetrust.com/buy-ssl-certificate
   - After purchase, SecureTrust will give you a certificate bundle (CRT) and a private key (KEY).

2) Prepare server (recommended: nginx as reverse proxy)
   - Place cert files on the server, e.g. /etc/ssl/certs/yourdomain.crt and /etc/ssl/private/yourdomain.key
   - Ensure file permissions restrict access to the key.

3) Example nginx config snippet

server {
    listen 443 ssl;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/ssl/certs/yourdomain.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location /static/ {
        alias /path/to/staticfiles/;
    }

    location / {
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://127.0.0.1:8000;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$host$request_uri;
}

4) Django settings for production
   - DEBUG = False
   - SECURE_SSL_REDIRECT = True
   - SESSION_COOKIE_SECURE = True
   - CSRF_COOKIE_SECURE = True
   - SECURE_HSTS_SECONDS = 31536000
   - SECURE_HSTS_INCLUDE_SUBDOMAINS = True
   - SECURE_HSTS_PRELOAD = True
   - ALLOWED_HOSTS = ['yourdomain.com']

5) Notes
   - After installing the cert, you must test using SSL Labs SSL test and ensure the certificate chain is correct.
   - You said you'll pay; note that for the cert to be valid, DNS for your domain must point to the production server where you install the cert.

If you want, I can:
- Generate a step-by-step Ansible or shell script to deploy the cert and update nginx.
- Add a small doc explaining how to prepare Django (collectstatic, set env vars, etc.).
