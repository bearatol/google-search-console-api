# Google Search Console API Skill

Навык для AI-агентов, который получает реальные данные Google Search Console через API и помогает анализировать поисковую эффективность сайта.

## Возможности

- OAuth 2.0 для Desktop app с read-only scope по умолчанию.
- Список доступных Search Console properties.
- Сводка по кликам, показам, CTR и средней позиции.
- Отчёты по запросам, страницам, датам, устройствам и другим измерениям.
- Просмотр и отправка sitemap с явным подтверждением.
- URL Inspection для проверки состояния страницы в индексе Google.
- Локальный кеш результатов без сторонних Python-зависимостей.

## Установка через skills CLI

```bash
npx skills add bearatol/google-search-console-api
```

После первой публичной установки репозитория через skills CLI навык автоматически сможет появиться в каталоге [skills.sh](https://skills.sh/).

## Ручная установка

Клонируйте репозиторий в каталог навыков вашего AI-агента или подключите папку как локальный skill:

```bash
git clone https://github.com/bearatol/google-search-console-api.git
cd google-search-console-api
```

Требуется Python 3.10 или новее. Сторонние Python-пакеты не нужны.

## Настройка Google API

1. Включите Google Search Console API в Google Cloud.
2. Создайте OAuth Client ID типа Desktop app.
3. Сохраните скачанный файл как `config/client_secret.json`.
4. Запустите авторизацию:

```bash
python3 scripts/gsc.py auth
```

Полная инструкция находится в [references/SETUP.md](references/SETUP.md).

## Примеры

```bash
python3 scripts/gsc.py sites
python3 scripts/gsc.py summary --site example.com
python3 scripts/gsc.py performance --site example.com --dimensions query
python3 scripts/gsc.py inspect --site example.com --url https://example.com/page
```

Все команды:

```bash
python3 scripts/gsc.py --help
```

## Безопасность

- `config/client_secret.json`, `config/token.json` и `cache/` исключены из Git.
- Токены сохраняются с правами доступа `0600`.
- Read-only scope используется по умолчанию.
- Отправка sitemap требует write scope и флаг `--confirm`.

Перед публикацией всегда проверяйте, что локальные OAuth-файлы не попали в индекс Git.

## Разработка

Запуск тестов:

```bash
python3 -B -m unittest discover -s tests -v
```

Репозиторий автоматически проверяется в GitHub Actions на поддерживаемых версиях Python.

## Лицензия

[MIT](LICENSE)
