---
name: google-search-console-api
description: >-
  Управление и анализ сайтов через Google Search Console API: OAuth 2.0,
  список ресурсов, поисковые запросы и страницы, клики, показы, CTR, средняя
  позиция, sitemap и URL Inspection. Использовать при упоминании Google Search
  Console API, GSC API, Search Analytics API, проверки индексации Google,
  статистики запросов Google или анализа SEO по реальным данным Google.
---

# Google Search Console API

Работать с Search Console через `scripts/gsc.py`. Использовать только стандартную библиотеку Python. Хранить OAuth-файлы локально внутри навыка и никогда не выводить токены в ответ пользователю.

## Подготовка

Перед первым вызовом прочитать [references/SETUP.md](references/SETUP.md), затем выполнить:

```bash
python3 scripts/gsc.py auth
```

По умолчанию запрашивать scope `webmasters.readonly`. Для отправки sitemap отдельно выполнить `auth --scope write`.

## Обязательный порядок анализа

1. Получить список ресурсов:
   ```bash
   python3 scripts/gsc.py sites
   ```
2. Если сайт не очевиден, попросить пользователя выбрать property.
3. Получить сводку:
   ```bash
   python3 scripts/gsc.py summary --site toolkitch.ru
   ```
4. Запустить необходимые детальные отчёты.

## Команды

```bash
# OAuth и состояние токена
python3 scripts/gsc.py auth [--scope readonly|write] [--no-browser]
python3 scripts/gsc.py token-info

# Ресурсы Search Console
python3 scripts/gsc.py sites [--no-cache]

# Сводка за последние 90 завершённых дней
python3 scripts/gsc.py summary --site toolkitch.ru [--date-from YYYY-MM-DD] [--date-to YYYY-MM-DD]

# Поисковая аналитика
python3 scripts/gsc.py performance --site toolkitch.ru --dimensions query
python3 scripts/gsc.py performance --site toolkitch.ru --dimensions page
python3 scripts/gsc.py performance --site toolkitch.ru --dimensions date,query --limit 1000
python3 scripts/gsc.py performance --site toolkitch.ru --filter device:equals:MOBILE

# Sitemap
python3 scripts/gsc.py sitemaps --site toolkitch.ru --action list
python3 scripts/gsc.py sitemaps --site toolkitch.ru --action submit \
  --sitemap-url https://toolkitch.ru/sitemap.xml --confirm

# Состояние URL в индексе Google
python3 scripts/gsc.py inspect --site toolkitch.ru --url https://toolkitch.ru/calculators/bmi
```

## Правила безопасности

- Использовать read-only scope по умолчанию.
- Не добавлять и не удалять properties.
- Не удалять sitemap.
- Отправлять sitemap только по явному запросу пользователя, с write scope и `--confirm`.
- Не обещать отправку обычной страницы на индексацию: Search Console API предоставляет URL Inspection, но не Request Indexing для обычных страниц.
- Не читать и не показывать `config/client_secret.json` и `config/token.json` без необходимости диагностики.

## Кеш и вывод

- Кеш находится в `cache/`, создаётся автоматически.
- `sites` кешируется на 24 часа, отчёты — по параметрам запроса.
- `--no-cache` принудительно получает свежие данные.
- В терминал выводится не более 30 строк; полный TSV/JSON сохраняется в кеше.
- При сравнении периодов всегда указывать точные даты и учитывать задержку финализации данных Google.

## Интерпретация

Для методики SEO-анализа использовать связанный навык `google-search-console`. В отчёте всегда разделять факты API, выводы и рекомендации. Не считать среднюю позицию точным рангом конкретного пользователя.
