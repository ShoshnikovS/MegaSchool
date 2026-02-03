# Структура проекта diagram-service

## Папочная структура

```
diagram-service/
├── src/                              # Исходный код приложения
│   ├── api/                          # API Gateway (FastAPI)
│   │   ├── __init__.py
│   │   ├── main.py                   # Точка входа FastAPI приложения
│   │   ├── routes/                   # Эндпоинты API
│   │   │   ├── __init__.py
│   │   │   ├── analyze.py            # POST /analyze - прямая задача
│   │   │   └── generate.py           # POST /generate - обратная задача
│   │   └── models/                   # Pydantic модели для запросов/ответов
│   │       ├── __init__.py
│   │       ├── requests.py
│   │       └── responses.py
│   │
│   ├── core/                         # Ядро системы
│   │   ├── __init__.py
│   │   ├── config.py                 # Конфигурация (переменные окружения)
│   │   ├── logger.py                 # Настройка loguru
│   │   └── exceptions.py             # Кастомные исключения
│   │
│   ├── preprocessing/                # Preprocessor
│   │   ├── __init__.py
│   │   ├── image_preprocessor.py     # Нормализация изображений (OpenCV)
│   │   └── text_preprocessor.py      # Нормализация текста
│   │
│   ├── ml_pipeline/                  # ML Pipeline (прямая задача)
│   │   ├── __init__.py
│   │   ├── detector.py               # YOLOv8 детекция элементов
│   │   ├── ocr.py                    # PaddleOCR распознавание текста
│   │   ├── graph_constructor.py      # Построение графа из bbox и текста
│   │   └── semantic_interpreter.py   # Семантический анализ графа
│   │
│   ├── generative_pipeline/          # Generative Pipeline (обратная задача)
│   │   ├── __init__.py
│   │   ├── text_parser.py            # Парсинг текста в граф (spaCy/правила)
│   │   ├── visualizer.py             # Рендеринг графа в изображение (graphviz)
│   │   └── code_generator.py         # Генерация PlantUML/Mermaid кода
│   │
│   ├── postprocessing/               # Postprocessor
│   │   ├── __init__.py
│   │   ├── formatter.py              # Форматирование выходных данных
│   │   └── template_engine.py        # Jinja2 шаблоны для текстовых описаний
│   │
│   └── utils/                        # Утилиты
│       ├── __init__.py
│       ├── graph_utils.py            # Работа с NetworkX графами
│       └── image_utils.py            # Вспомогательные функции для изображений
│
├── models/                           # ML модели и веса
│   ├── yolov8/                       # YOLOv8 модели
│   │   └── .gitkeep
│   └── README.md                     # Инструкции по загрузке моделей
│
├── templates/                        # Jinja2 шаблоны
│   ├── algorithm_description.j2      # Шаблон для текстового описания
│   └── error_response.j2
│
├── tests/                            # Тесты
│   ├── __init__.py
│   ├── test_api/
│   │   ├── __init__.py
│   │   ├── test_analyze.py
│   │   └── test_generate.py
│   ├── test_ml_pipeline/
│   │   └── __init__.py
│   └── test_generative_pipeline/
│       └── __init__.py
│
├── data/                             # Данные для разработки и тестирования
│   ├── samples/                      # Примеры диаграмм
│   │   ├── input_images/
│   │   └── output_examples/
│   └── training/                     # Данные для дообучения (если нужно)
│       └── .gitkeep
│
├── docker/                           # Docker конфигурация
│   ├── Dockerfile                    # Основной Dockerfile
│   ├── Dockerfile.gpu                # Dockerfile для GPU
│   └── docker-compose.yml
│
├── scripts/                          # Вспомогательные скрипты
│   ├── download_models.py            # Скачивание предобученных моделей
│   ├── train_yolo.py                 # Дообучение YOLOv8 (опционально)
│   └── test_service.py               # Тестирование API
│
├── docs/                             # Документация
│   ├── API.md                        # Описание API эндпоинтов
│   ├── ARCHITECTURE.md               # Архитектура системы (копия)
│   └── DEPLOYMENT.md                 # Инструкции по развертыванию
│
├── .env.example                      # Пример файла переменных окружения
├── .gitignore                        # Git ignore правила
├── pyproject.toml                    # Poetry конфигурация и зависимости
├── poetry.lock                       # Зафиксированные версии зависимостей
├── README.md                         # Основная документация проекта
└── PROJECT_STRUCTURE.md              # Этот файл

```

## Принципы организации кода

### 1. Модульность
- Каждый компонент в отдельной папке
- Один файл = одна ответственность
- Избегаем дублирования кода

### 2. Именование
- Папки: lowercase с подчеркиваниями
- Файлы: lowercase с подчеркиваниями
- Классы: PascalCase
- Функции: snake_case

### 3. Зависимости между модулями
```
api → preprocessing → ml_pipeline → postprocessing
api → preprocessing → generative_pipeline → postprocessing
```

### 4. Конфигурация
- Все настройки в `src/core/config.py`
- Переменные окружения через `.env`
- Никаких хардкод значений в коде

### 5. Логирование
- Единый логгер из `src/core/logger.py`
- Структурированные логи (JSON)
- Уровни: DEBUG, INFO, WARNING, ERROR

### 6. Обработка ошибок
- Кастомные исключения в `src/core/exceptions.py`
- Централизованная обработка в FastAPI middleware
- Понятные сообщения об ошибках

## Файлы, которые НЕ нужно создавать повторно

При исправлении функционала редактируем существующие файлы, а не создаем новые:
- Если нужно исправить детектор → редактируем `src/ml_pipeline/detector.py`
- Если нужно улучшить парсер → редактируем `src/generative_pipeline/text_parser.py`
- Если нужно изменить API → редактируем соответствующий файл в `src/api/routes/`

## Порядок реализации

1. **Инфраструктура**: config, logger, exceptions
2. **API каркас**: main.py, routes с заглушками
3. **Preprocessing**: image_preprocessor, text_preprocessor
4. **ML Pipeline**: detector → ocr → graph_constructor → semantic_interpreter
5. **Generative Pipeline**: text_parser → visualizer → code_generator
6. **Postprocessing**: formatter, template_engine
7. **Интеграция**: связываем все компоненты через API
8. **Docker**: контейнеризация
9. **Документация**: README, API docs, примеры
