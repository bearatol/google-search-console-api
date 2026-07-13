# Настройка Google Search Console API

## 1. Google Cloud

1. Открыть https://console.cloud.google.com/.
2. Создать или выбрать проект.
3. Включить **Google Search Console API**.
4. Настроить OAuth consent screen.
5. Создать OAuth Client ID типа **Desktop app**.
6. Скачать JSON с реквизитами клиента.

## 2. Файл клиента

Сохранить скачанный файл как:

```text
config/client_secret.json
```

Файл не должен попадать в Git или публиковаться.

## 3. Авторизация

Из каталога навыка выполнить:

```bash
python3 scripts/gsc.py auth
```

Команда поднимет временный callback на `127.0.0.1`, откроет Google OAuth в браузере и сохранит токен в `config/token.json`. Если браузер нельзя открыть автоматически, использовать `--no-browser` и открыть показанную ссылку вручную на том же компьютере.

Для права отправлять sitemap:

```bash
python3 scripts/gsc.py auth --scope write
```

## 4. Проверка

```bash
python3 scripts/gsc.py token-info
python3 scripts/gsc.py sites
```

Если нужного сайта нет в списке, проверить, что Google-аккаунт имеет доступ к соответствующему ресурсу Search Console.

## Используемые API

- Search Console API: https://developers.google.com/webmaster-tools
- OAuth для Desktop Apps: https://developers.google.com/identity/protocols/oauth2/native-app
- Search Analytics: https://developers.google.com/webmaster-tools/v1/searchanalytics/query
- URL Inspection: https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect

Для обычных страниц API позволяет проверить индексирование, но не отправить Request Indexing. Google Indexing API предназначен только для ограниченных типов контента, например вакансий и трансляций.
