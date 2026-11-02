# Учебное портфолио Python и QA

Набор учебных проектов для практики Python, ООП и тестирования. Концепция заказов используется только для обучения; полноценный проект ателье ведётся отдельно.

## Проекты

- `python_learning/oop` — упражнения по ООП и модель заказа с клиентом, позициями, количеством, статусами и расчётом стоимости.
- `api_testing` — HTTP-клиент и pytest-проверки API. Тесты с пометкой `integration` обращаются к работающему JSONPlaceholder.
- `web_scraping/books` — учебный парсер каталога Books to Scrape и тесты парсинга и загрузки страниц.

## Установка

Из корневой папки репозитория в PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Запуск тестов

Команды выполняются из корневой папки после активации окружения:

```powershell
Set-Location .\api_testing
python -m pytest -m "not integration"
python -m pytest -m integration

Set-Location ..\python_learning\oop
python -m pytest -q

Set-Location ..\..\web_scraping\books
python -m pytest -q
```

Интеграционные API-тесты требуют подключения к интернету. Остальные перечисленные тесты используют локальные данные или моки.

`result.csv` создаётся скриптом парсера и исключён из репозитория вместе с виртуальными окружениями и тестовым кэшем.