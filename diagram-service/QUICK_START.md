# Quick Start Guide

## Команды для инициализации Git и загрузки на GitHub

### Шаг 1: Инициализация Git репозитория

```bash
cd diagram-service
git init
git add .
git commit -m "Initial commit: Complete project structure

- Project structure following best practices
- FastAPI application with analyze and generate endpoints
- Docker support (CPU and GPU modes)
- Poetry dependency management
- Comprehensive documentation
- Test scripts and examples"
```

### Шаг 2: Создание репозитория на GitHub

1. Перейдите на https://github.com/new
2. Создайте новый репозиторий с именем `diagram-service`
3. Выберите Private или Public
4. **НЕ** инициализируйте с README (у нас уже есть)

### Шаг 3: Подключение к GitHub и загрузка

**HTTPS вариант:**
```bash
git remote add origin https://github.com/ВАШ_USERNAME/diagram-service.git
git branch -M main
git push -u origin main
```

**SSH вариант (рекомендуется):**
```bash
git remote add origin git@github.com:ВАШ_USERNAME/diagram-service.git
git branch -M main
git push -u origin main
```

### Одна команда для всего (HTTPS):

```bash
cd diagram-service && git init && git add . && git commit -m "Initial commit: Complete project structure" && git branch -M main && git remote add origin https://github.com/ВАШ_USERNAME/diagram-service.git && git push -u origin main
```

---

## Быстрый запуск сервиса

### Вариант 1: Docker (рекомендуется)

```bash
cd diagram-service/docker
docker-compose up -d --build
```

Сервис будет доступен на `http://localhost:8000`

### Вариант 2: Локально с Poetry

```bash
cd diagram-service

# Установка зависимостей
poetry install

# Создание .env файла
cp .env.example .env

# Запуск сервиса
poetry run uvicorn src.api.main:app --reload
```

### Проверка работы

```bash
# Health check
curl http://localhost:8000/health

# Swagger UI
# Откройте в браузере: http://localhost:8000/docs

# Тестирование
poetry run python scripts/test_service.py
```

---

## Структура проекта

```
diagram-service/
├── src/                    # Исходный код
│   ├── api/               # FastAPI приложение
│   ├── core/              # Конфигурация, логирование, исключения
│   ├── preprocessing/     # Препроцессинг данных
│   ├── ml_pipeline/       # ML pipeline (прямая задача)
│   ├── generative_pipeline/  # Generative pipeline (обратная задача)
│   ├── postprocessing/    # Постобработка результатов
│   └── utils/             # Утилиты
├── models/                # ML модели
├── templates/             # Jinja2 шаблоны
├── tests/                 # Тесты
├── docker/                # Docker конфигурация
├── scripts/               # Вспомогательные скрипты
├── docs/                  # Документация
├── pyproject.toml         # Poetry конфигурация
├── .gitignore            # Git ignore правила
├── .env.example          # Пример переменных окружения
└── README.md             # Основная документация
```

---

## Важные файлы документации

- **README.md** - Основная документация проекта
- **PROJECT_STRUCTURE.md** - Детальная структура проекта
- **IMPLEMENTATION_PLAN.md** - План реализации по этапам
- **GIT_SETUP.md** - Подробная инструкция по Git
- **docs/API.md** - Документация API
- **docs/DEPLOYMENT.md** - Руководство по развертыванию
- **docs/ARCHITECTURE.md** - Архитектура системы

---

## Следующие шаги

1. ✅ Структура проекта создана
2. ✅ Базовое API реализовано
3. ✅ Docker конфигурация готова
4. ✅ Документация написана
5. 📝 Загрузить на GitHub (используйте команды выше)
6. 🔨 Реализовать ML компоненты:
   - YOLOv8 детектор
   - PaddleOCR интеграция
   - Graph Constructor
   - Text Parser
   - Visualizer
7. 🧪 Написать тесты
8. 🚀 Развернуть на сервере

---

## Полезные команды

```bash
# Просмотр структуры проекта
tree -L 3 -I '__pycache__|*.pyc'

# Запуск тестов
poetry run pytest tests/ -v

# Форматирование кода
poetry run black src/ tests/

# Проверка типов
poetry run mypy src/

# Просмотр логов Docker
docker logs -f diagram-service

# Остановка сервиса
docker-compose down
```
