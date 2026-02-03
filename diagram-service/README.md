# Diagram Service

ML-сервис для двухстороннего преобразования диаграмм: изображение ↔ текстовое описание.

## Описание

Система представляет собой закрытый контейнеризированный ML-сервис с двумя основными функциями:

1. **Прямая задача**: Изображение диаграммы → Структурированное текстовое описание логики
2. **Обратная задача**: Текстовое описание алгоритма → Изображение диаграммы и/или код (BPMN/PlantUML)

## Технологический стек

- **Backend**: FastAPI, Python 3.10
- **ML/CV**: YOLOv8n, PaddleOCR, OpenCV
- **NLP**: spaCy, Natasha
- **Графы**: NetworkX
- **Визуализация**: Graphviz, PlantUML
- **Шаблоны**: Jinja2
- **Контейнеризация**: Docker, Docker Compose
- **Управление зависимостями**: Poetry

## Требования к системе

### Минимальные требования
- **CPU**: 4 ядра
- **RAM**: 4 GB
- **Диск**: 5 GB свободного места
- **ОС**: Linux, macOS, Windows (с Docker)

### Рекомендуемые требования (с GPU)
- **GPU**: NVIDIA с поддержкой CUDA (≥8 GB VRAM)
- **RAM**: 8 GB
- **Диск**: 10 GB свободного места

## Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/yourusername/diagram-service.git
cd diagram-service
```

### 2. Настройка окружения

Скопируйте файл с примером переменных окружения:

```bash
cp .env.example .env
```

Отредактируйте `.env` при необходимости (например, установите `DEVICE=cuda` для GPU).

### 3. Запуск через Docker (рекомендуется)

#### CPU режим

```bash
cd docker
docker-compose up --build
```

#### GPU режим

```bash
cd docker
docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up --build
```

Сервис будет доступен по адресу: `http://localhost:8000`

API документация (Swagger): `http://localhost:8000/docs`

### 4. Локальная установка (для разработки)

#### Установка Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

#### Установка зависимостей

```bash
poetry install
```

#### Загрузка моделей

```bash
poetry run python scripts/download_models.py
```

#### Запуск сервиса

```bash
poetry run uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

## Использование API

### Прямая задача: Анализ диаграммы

**Эндпоинт**: `POST /api/v1/analyze`

**Пример запроса (curl)**:

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@path/to/diagram.png"
```

**Пример запроса (Python)**:

```python
import requests

url = "http://localhost:8000/api/v1/analyze"
files = {"image": open("diagram.png", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

**Пример ответа**:

```json
{
  "task_type": "image_to_text",
  "description": "Алгоритм начинается с проверки условия...",
  "graph_representation": {
    "nodes": [
      {"id": "node_1", "type": "start", "label": "Начало", "position": [100, 50]},
      {"id": "node_2", "type": "process", "label": "Обработка данных", "position": [100, 150]}
    ],
    "edges": [
      {"source": "node_1", "target": "node_2", "label": ""}
    ]
  },
  "artifacts": {},
  "processing_time_sec": 3.45
}
```

### Обратная задача: Генерация диаграммы

**Эндпоинт**: `POST /api/v1/generate`

**Пример запроса (curl)**:

```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Начало. Проверить условие X. Если истина, выполнить действие A, иначе действие B. Конец.",
    "output_format": "image"
  }'
```

**Пример запроса (Python)**:

```python
import requests
import base64

url = "http://localhost:8000/api/v1/generate"
data = {
    "description": "Начало. Проверить условие X. Если истина, выполнить действие A, иначе действие B. Конец.",
    "output_format": "both"  # "image", "code", "both"
}
response = requests.post(url, json=data)
result = response.json()

# Сохранение изображения
if "diagram_image_base64" in result["artifacts"]:
    image_data = base64.b64decode(result["artifacts"]["diagram_image_base64"])
    with open("generated_diagram.png", "wb") as f:
        f.write(image_data)
```

**Пример ответа**:

```json
{
  "task_type": "text_to_diagram",
  "description": "Начало. Проверить условие X...",
  "graph_representation": {
    "nodes": [...],
    "edges": [...]
  },
  "artifacts": {
    "diagram_image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
    "diagram_code": "@startuml\nstart\nif (условие X?) then (да)\n  :действие A;\nelse (нет)\n  :действие B;\nendif\nstop\n@enduml"
  },
  "processing_time_sec": 2.15
}
```

## Структура проекта

Подробная структура проекта описана в [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md).

```
diagram-service/
├── src/                    # Исходный код
│   ├── api/               # FastAPI приложение
│   ├── core/              # Конфигурация, логирование
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
└── docs/                  # Документация
```

## Разработка

### Запуск тестов

```bash
poetry run pytest tests/ -v
```

### Форматирование кода

```bash
poetry run black src/ tests/
poetry run ruff check src/ tests/
```

### Проверка типов

```bash
poetry run mypy src/
```

## Конфигурация

Основные параметры настраиваются через переменные окружения в файле `.env`:

| Переменная | Описание | Значение по умолчанию |
|------------|----------|----------------------|
| `DEVICE` | Устройство для ML (cpu/cuda) | `cpu` |
| `APP_PORT` | Порт API сервера | `8000` |
| `LOG_LEVEL` | Уровень логирования | `INFO` |
| `MAX_IMAGE_SIZE` | Максимальный размер изображения | `1920` |
| `CONFIDENCE_THRESHOLD` | Порог уверенности детекции | `0.5` |

Полный список параметров см. в [`.env.example`](.env.example).

## Производительность

### Прямая задача (image → text)
- **CPU**: ~8-12 сек на изображение
- **GPU**: ~2-4 сек на изображение

### Обратная задача (text → diagram)
- **CPU/GPU**: ~2-5 сек

### Использование памяти
- **CPU режим**: ~2-3 GB RAM
- **GPU режим**: ~3-4 GB VRAM

## Ограничения

- Максимальный размер загружаемого изображения: 10 MB
- Поддерживаемые форматы изображений: PNG, JPEG, JPG
- Максимальная длина текстового описания: 5000 символов
- Поддерживаемые языки: русский, английский

## Roadmap

- [x] Базовая архитектура и API
- [x] Прямая задача (детекция + OCR)
- [x] Обратная задача (генерация диаграмм)
- [ ] Дообучение YOLOv8 на датасете диаграмм
- [ ] Поддержка циклов в графах
- [ ] Web UI (Streamlit)
- [ ] Поддержка дополнительных форматов (BPMN XML, draw.io)
- [ ] Кэширование результатов (Redis)
- [ ] Batch processing API

## Лицензия

MIT License

## Контакты

- **Автор**: Your Name
- **Email**: your.email@example.com
- **GitHub**: https://github.com/yourusername/diagram-service

## Благодарности

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- [FastAPI](https://fastapi.tiangolo.com/)
- [NetworkX](https://networkx.org/)
