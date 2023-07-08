# Yatube
## Описание:
Сайт для публикации дневников. Сайт предоставляет пользователям возможность создать учетную запись, публиковать записи, подписываться на любимых авторов и отмечать понравившиеся записи.

## Технологии
- Python 3.7
- Django 
- Django==2.2.16
- pytest==6.2.4
- gunicorn=20.1.0
- nginx=nginx/1.18.0

## Запуск проект локально
- Склонировать репозиторий
```bash
git clone git@github.com:MaryMash/yatube.git

```
- Создать и активировать виртуальное окружение

```python
python3.7 -m venv venv
```

```python
source venv/bin/activate
```

- Установить зависимости из файла requirements.txt

```python
python -m pip install --upgrade pip
```

```python
pip install -r requirements.txt
```

- Выполнить миграции

```python
python manage.py migrate
```

- Запустить проект

### Запуск проекта на сервере
- Создать ВМ, подключиться к серверу
- Обновить пакеты на сервере
```bash
sudo apt update
sudo apt upgrade -y
```
- Установить менеджер пакетов `pip`, утилиту для создания виртуального окружения `venv`, систему контроля версий `git`
```bash
sudo apt install python3-pip python3-venv git -y
```
- Сгенерировать ssh ключ
```bash
ssh-keygen
```
- Скопировать ключ и записать в настройки аккаунта на GitHub

```bash
cat ~/.ssh/id_rsa.pub
```

- Склонировать репозиторий на сервер

```bash
git clone git@github.com:MaryMash/yatube.git
```

- Перейти в директорию с проектом, создать и активировать виртуальное окружение, установить пакеты из `requirements.txt`

```bash
cd yatube
python3 -m venv venv
. venv/bin/activate
python -m pip install -r requirements.txt
```

- Сделать миграции

```bash
python manage.py migrate
```
- Установить пакет `gunicorn`

```bash
pip install gunicorn
```

- Создать юнит для  `gunicorn`

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

```bash
bash
[Unit]
Description=gunicorn daemon

After=network.target

[Service]
User=<username>

WorkingDirectory=/home/<username>/yatube/yatube/

ExecStart=/home/<username>/yatube/venv/bin/gunicorn --bind 127.0.0.1:8000>

[Install]
WantedBy=multi-user.target
```

- Запустить юнит

```bash
sudo systemctl start gunicorn
```

- Добавить юнит в список автозапуска операционной системы

```bash
sudo systemctl status gunicorn
```

- Проверить работоспособность запущенного демона:

```bash
sudo systemctl status gunicorn
```

- Устаносить nginx

```bash
sudo apt install nginx -y
```

- Настроить файрвол

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
sudo ufw status
```

- Проверить внесенные изменения

```bash
sudo ufw status
```

- Запустить nxinx

```bash
sudo systemctl start nginx
```

- Собрать статику

```bash
python manage.py collectstatic
```

- Перезапустить nginx

```bash
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
sudo systemctl status gunicorn
```

- Настройка конфигурации nginx

```bash
sudo nano /etc/nginx/sites-enabled/default
```

```bash
server {
    listen 80;
    server_name <ip сервера>;
    
    location /static/ {
        root /home/<имя_пользователя>/yatube/yatube/;
    }

    location /media/ {
        root /home/<имя_пользователя>/yatube/yatube/;
    }
    
    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;
    }
}
```

- Протестировать конфигурацию

```bash
sudo nginx -t
```

- Перезапустить nginx

```bash
sudo systemctl reload nginx
```

- Сайт работает можно зарегистрировать и создать посты

### Перенос базы на PostrgeSQL
Проект работает на базе SQLite. При необходимости его можно перенести на PostgreSQL

- Изменить настройки локали на ru_RU.UTF-8

```bash
sudo dpkg-reconfigure locales
sudo reboot
```

- Установить Postgres

```bash
sudo apt install postgresql postgresql-contrib -y
```

- Создать БД и пользователей

```bash
sudo -u postgres psql
CREATE DATABASE yatube;
CREATE USER yatube_user WITH ENCRYPTED PASSWORD 'xxx';
```

- Установить в виртуальное окружение драйвер для работы с postgres — psycopg2-binary:

```bash
pip install psycopg2-binary==2.8.6
```

- Записать данные для подключения в файл .env

```bash
pip install python-dotenv
```

- Внести изменения в файл setting.py

```bash
# ...директория_проекта/yatube/yatube/settings.py
from dotenv import load_dotenv

load_dotenv()

...

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT')
    }
}
```

- В директории с кодом проекта (там же, где размещены файлы settings.py и wsgi.py) создать файл `.env`, открыть его в текстовом редакторе nano и добавить настройки подключения к базе данных:

```bash
# ...директория_проекта/yatube/yatube/.env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=yatube
POSTGRES_USER=yatube_user
POSTGRES_PASSWORD=xxx
DB_HOST=127.0.0.1
DB_PORT=5432
```

- Выполнить миграции

```bash
python manage.py migrate
```

- Заполнить базу данными 

```bash
# скопировать файл с локального компьютера на сервер
scp dump.json maria_grigoryeva@<server_ip>:/home/<username>/yatube/yatube/

# на сервере удалить старые данные из базы
python3 manage.py shell  
# выполнить в открывшемся терминале:
>>> from django.contrib.contenttypes.models import ContentType
>>> ContentType.objects.all().delete()
>>> quit()

# заполнить базу данными из файла dump.json
python manage.py loaddata dump.json
```