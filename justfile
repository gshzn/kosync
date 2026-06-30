build frontend:
    cd frontend/app/
    npm ci
    npm run build

    cd ../landing-page
    npm run build

    caddy reload --config ../Caddyfile

build client:
    cd client/
    GOOS=linux GOARCH=arm go build -o ../backend/kosync_client .

restart backend:
    systemctl --user restart kosync