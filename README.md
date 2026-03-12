# Powerbank Rental — Monorepo

Приложение для аренды павербанков через сеть зарядных станций.  
Монорепозиторий содержит три независимых проекта.

```
powerbank-project/
├── backend/            # REST API (Django + Django Ninja)
├── frontend/           # SPA (React + TypeScript + Vite)
└── stantion_emulator/  # Эмулятор станции (Python / tkinter)
```

---

## Архитектура

```
┌─────────────────┐        HTTP/JSON        ┌──────────────────┐
│    Frontend     │ ──────────────────────► │    Backend API   │
│  React + Vite   │                         │  Django + Ninja  │
└─────────────────┘                         └────────┬─────────┘
                                                     │ BasicAuth
                                            ┌────────▼──────────┐
                                            │ Stantion Emulator │
                                            │  Python / tkinter │
                                            └───────────────────┘
```

---

## Стек технологий

| Модуль             | Технологии                                                                 |
|--------------------|----------------------------------------------------------------------------|
| **Backend**        | Python 3.13, Django 5.2, Django Ninja, PostgreSQL 16 + PostGIS, Docker    |
| **Frontend**       | React 19, TypeScript, Vite, React Router, Zustand, Leaflet, Zod, RHF      |
| **Emulator**       | Python 3.13, tkinter, requests                                             |

---

## Backend

Django-приложение, предоставляющее REST API для управления станциями, аккумуляторами и арендами.

### Приложения Django

| Приложение   | Назначение                                              |
|--------------|---------------------------------------------------------|
| `users`      | Регистрация, аутентификация, профили пользователей      |
| `stantions`  | Управление зарядными станциями и слотами                |
| `rentals`    | Жизненный цикл аренды павербанка                        |
| `main`       | Общие утилиты и точка входа                             |

### Быстрый старт

```bash
cd backend

# Запуск базы данных и веб-сервера в Docker
docker compose up --build

# Применить миграции
docker compose exec web python manage.py migrate

# Создать суперпользователя
docker compose exec web python manage.py createsuperuser
```

По умолчанию API доступен на `http://localhost:8000`.  
Документация (Swagger UI): `http://localhost:8000/api/docs`.

### Переменные окружения

Скопируйте шаблон и заполните значения:

```bash
cp backend/config/.env.template backend/config/.env
```

### Тесты

```bash
cd backend
docker compose exec web pytest
```

---

## Frontend

SPA для конечного пользователя: карта станций, регистрация/авторизация, история аренд.

### Страницы

| Маршрут      | Описание                        |
|--------------|---------------------------------|
| `/login`     | Вход в аккаунт                  |
| `/register`  | Регистрация нового пользователя |
| `/`          | Карта ближайших станций (Leaflet)|
| `/rentals`   | История аренд пользователя      |

### Быстрый старт

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

### Сборка для production

```bash
npm run build      # артефакты в dist/
```

---

## Stantion Emulator

GUI-приложение на tkinter для ручного тестирования API станции.  
Позволяет настроить количество слотов, их состояние и отправить данные на сервер по BasicAuth.

### Быстрый старт

```bash
cd stantion_emulator

# Установка зависимостей (Poetry)
poetry install

# Запуск
poetry run python src/main.py
```

Или напрямую (зависимость `requests` установится автоматически):

```bash
python stantion_emulator/src/main.py
```

---

## Требования

- **Python** 3.13+
- **Node.js** 20+
- **Docker** (последняя версия) + Docker Compose
- **Poetry** (для backend и emulator)
- **pyenv** (рекомендуется для управления версиями Python)

---

## Лицензия

Учебный проект. Лицензия не определена.
