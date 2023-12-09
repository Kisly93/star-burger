#!/bin/bash

set -e
source /opt/star-burger/star-burger/.env
echo "Активация виртуального окружения..."
source /opt/star-burger/star-burger/venv/bin/activate

echo "Обновление кода из репозитория..."
git pull

echo "Установка Python зависимостей..."
pip install -r requirements.txt

echo "Установка Node.js зависимостей..."
npm ci --dev

echo "Пересбор JS-кода..."
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

echo "Пересбор статики Django..."
cd /opt/star-burger/star-burger/ && python3 ./manage.py collectstatic --noinput

echo "Накат миграций..."
python3 ./manage.py migrate --noinput

echo "Перезапуск сервисов Systemd..."
systemctl restart starburger
systemctl reload nginx.service

commit=`git rev-parse HEAD`

echo "Отправка уведомления в Rollbar..."
curl -H "X-Rollbar-Access-Token: $ROLLBAR_ACCESS_TOKEN" \
     -H "accept: application/json" \
     -H "content-type: application/json" \
     -X POST "https://api.rollbar.com/api/1/deploy" \
     -d '{
  "environment": "production",
  "revision": "'$commit'",
  "rollbar_username": "admin",
  "local_username": "admin",
  "comment": "deploy",
  "status": "succeeded"
}'
echo "Деактивация виртуального окружения..."
deactivate

echo "Деплой завершен успешно."
