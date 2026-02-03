# Детальный план реализации diagram-service

## Этап 1: Подготовка инфраструктуры (День 1)

### 1.1 Создание структуры проекта
- [x] Создать документацию структуры проекта
- [ ] Создать все необходимые папки
- [ ] Создать пустые `__init__.py` файлы

### 1.2 Конфигурационные файлы
- [ ] `pyproject.toml` - Poetry конфигурация с зависимостями
- [ ] `.gitignore` - правила игнорирования
- [ ] `.env.example` - пример переменных окружения
- [ ] `models/README.md` - инструкции по загрузке моделей

### 1.3 Базовые модули ядра
- [ ] `src/core/config.py` - загрузка конфигурации из .env
- [ ] `src/core/logger.py` - настройка loguru
- [ ] `src/core/exceptions.py` - кастомные исключения

## Этап 2: API Gateway (День 1-2)

### 2.1 Pydantic модели
- [ ] `src/api/models/requests.py`:
  - `AnalyzeRequest` (image: base64/multipart)
  - `GenerateRequest` (description: str, format: str)
- [ ] `src/api/models/responses.py`:
  - `UnifiedResponse` (task_type, description, graph, artifacts, time)
  - `ErrorResponse`

### 2.2 FastAPI приложение
- [ ] `src/api/main.py`:
  - Инициализация FastAPI
  - Middleware для логирования
  - Обработчик исключений
  - CORS настройки
  - Health check эндпоинт `/health`

### 2.3 Эндпоинты
- [ ] `src/api/routes/analyze.py`:
  - `POST /analyze` - прямая задача
  - Валидация входных данных
  - Вызов ML pipeline
  - Возврат унифицированного ответа
- [ ] `src/api/routes/generate.py`:
  - `POST /generate` - обратная задача
  - Валидация текстового описания
  - Вызов generative pipeline
  - Возврат изображения и/или кода

## Этап 3: Preprocessing (День 2)

### 3.1 Препроцессинг изображений
- [ ] `src/preprocessing/image_preprocessor.py`:
  - Класс `ImagePreprocessor`
  - Декодирование base64/multipart
  - Нормализация размера (max 1920x1080)
  - Конвертация в RGB
  - Улучшение контраста (CLAHE)
  - Удаление шума (bilateral filter)

### 3.2 Препроцессинг текста
- [ ] `src/preprocessing/text_preprocessor.py`:
  - Класс `TextPreprocessor`
  - Очистка текста от лишних символов
  - Нормализация пробелов
  - Базовая токенизация

## Этап 4: ML Pipeline - Прямая задача (День 2-3)

### 4.1 Детекция элементов
- [ ] `src/ml_pipeline/detector.py`:
  - Класс `DiagramDetector`
  - Загрузка YOLOv8n модели
  - Метод `detect(image) -> List[BBox]`
  - Фильтрация по confidence threshold
  - Поддержка CPU/GPU режима

### 4.2 OCR распознавание
- [ ] `src/ml_pipeline/ocr.py`:
  - Класс `TextRecognizer`
  - Инициализация PaddleOCR (ru+en)
  - Метод `recognize(image, bboxes) -> Dict[bbox_id, text]`
  - Обработка повернутого текста

### 4.3 Построение графа
- [ ] `src/ml_pipeline/graph_constructor.py`:
  - Класс `GraphConstructor`
  - Создание NetworkX графа из bbox
  - Определение связей по геометрии:
    - Вертикальные связи (сверху-вниз)
    - Горизонтальные связи (слева-направо)
    - Стрелки и линии связи
  - Метод `construct(bboxes, texts) -> nx.DiGraph`

### 4.4 Семантический интерпретатор
- [ ] `src/ml_pipeline/semantic_interpreter.py`:
  - Класс `SemanticInterpreter`
  - Классификация типов узлов:
    - Start/End (овалы)
    - Process (прямоугольники)
    - Decision (ромбы)
    - Data (параллелограммы)
  - Определение логики переходов
  - Метод `interpret(graph) -> StructuredGraph`

## Этап 5: Generative Pipeline - Обратная задача (День 3-4)

### 5.1 Парсинг текста
- [ ] `src/generative_pipeline/text_parser.py`:
  - Класс `TextToGraphParser`
  - Rule-based парсинг:
    - Извлечение шагов (регулярные выражения)
    - Определение условий (if/else/while)
    - Извлечение связей между шагами
  - Опционально: spaCy для NER
  - Метод `parse(text) -> GraphStructure`

### 5.2 Визуализация графа
- [ ] `src/generative_pipeline/visualizer.py`:
  - Класс `GraphVisualizer`
  - Рендеринг через graphviz:
    - Настройка стилей узлов по типам
    - Настройка стрелок и меток
    - Layout алгоритм (dot, neato)
  - Метод `render(graph) -> bytes` (PNG)
  - Поддержка разных размеров

### 5.3 Генерация кода диаграмм
- [ ] `src/generative_pipeline/code_generator.py`:
  - Класс `DiagramCodeGenerator`
  - Генерация PlantUML кода
  - Генерация Mermaid кода
  - Метод `generate(graph, format) -> str`

## Этап 6: Postprocessing (День 4)

### 6.1 Форматирование выходных данных
- [ ] `src/postprocessing/formatter.py`:
  - Класс `ResponseFormatter`
  - Сборка унифицированного JSON
  - Кодирование изображений в base64
  - Добавление метаданных (время обработки)

### 6.2 Template Engine
- [ ] `src/postprocessing/template_engine.py`:
  - Класс `TemplateEngine`
  - Загрузка Jinja2 шаблонов
  - Метод `render_description(graph) -> str`
  - Генерация человекочитаемого описания алгоритма

### 6.3 Jinja2 шаблоны
- [ ] `templates/algorithm_description.j2`:
  - Шаблон для текстового описания
  - Форматирование шагов алгоритма
  - Описание условий и циклов

## Этап 7: Утилиты (День 4)

### 7.1 Работа с графами
- [ ] `src/utils/graph_utils.py`:
  - Функции валидации графа
  - Поиск циклов
  - Топологическая сортировка
  - Конвертация форматов графов

### 7.2 Работа с изображениями
- [ ] `src/utils/image_utils.py`:
  - Функции для base64 кодирования/декодирования
  - Изменение размера изображений
  - Конвертация форматов

## Этап 8: Docker и развертывание (День 5)

### 8.1 Dockerfile
- [ ] `docker/Dockerfile`:
  - Base image: python:3.10-slim
  - Установка системных зависимостей (opencv, graphviz)
  - Копирование кода и установка Poetry
  - Установка Python зависимостей
  - Скачивание моделей
  - CMD для запуска FastAPI

### 8.2 Docker Compose
- [ ] `docker/docker-compose.yml`:
  - Сервис diagram-service
  - Volume для моделей
  - Переменные окружения
  - Порты (8000:8000)

### 8.3 GPU поддержка
- [ ] `docker/Dockerfile.gpu`:
  - Base image: nvidia/cuda:11.8.0-runtime-ubuntu22.04
  - Установка Python 3.10
  - CUDA-совместимые версии библиотек

## Этап 9: Скрипты и тесты (День 5)

### 9.1 Вспомогательные скрипты
- [ ] `scripts/download_models.py`:
  - Скачивание YOLOv8n весов
  - Скачивание PaddleOCR моделей
  - Проверка целостности файлов

- [ ] `scripts/test_service.py`:
  - Примеры запросов к API
  - Тестирование обеих задач
  - Измерение времени обработки

### 9.2 Базовые тесты
- [ ] `tests/test_api/test_analyze.py`:
  - Тест успешного анализа
  - Тест с невалидным изображением
  - Тест формата ответа

- [ ] `tests/test_api/test_generate.py`:
  - Тест успешной генерации
  - Тест с невалидным текстом
  - Тест форматов вывода

## Этап 10: Документация (День 5)

### 10.1 README.md
- [ ] Описание проекта
- [ ] Требования к системе
- [ ] Инструкции по установке
- [ ] Примеры использования API
- [ ] Запуск через Docker
- [ ] Конфигурация (CPU/GPU)

### 10.2 API документация
- [ ] `docs/API.md`:
  - Описание эндпоинтов
  - Примеры запросов/ответов
  - Коды ошибок
  - Rate limits (если есть)

### 10.3 Деплоймент
- [ ] `docs/DEPLOYMENT.md`:
  - Требования к серверу
  - Установка Docker
  - Настройка GPU
  - Мониторинг и логи

## Этап 11: Примеры данных

### 11.1 Тестовые изображения
- [ ] `data/samples/input_images/`:
  - 5-10 примеров диаграмм разных типов
  - BPMN диаграммы
  - Блок-схемы
  - UML диаграммы

### 11.2 Примеры выходных данных
- [ ] `data/samples/output_examples/`:
  - JSON ответы для каждого примера
  - Сгенерированные изображения
  - Сгенерированный код диаграмм

## Чек-лист перед завершением

- [ ] Все зависимости указаны в pyproject.toml
- [ ] Docker образ собирается без ошибок
- [ ] API возвращает корректные ответы
- [ ] Логирование работает
- [ ] README содержит полные инструкции
- [ ] Примеры запросов работают
- [ ] Код следует структуре PROJECT_STRUCTURE.md
- [ ] Нет дублирующихся файлов
- [ ] Git репозиторий инициализирован
- [ ] Код загружен на GitHub

## Метрики успеха

### Прямая задача (image → text):
- Детекция элементов: Precision > 0.85, Recall > 0.80
- OCR точность: > 90% для печатного текста
- Время обработки: < 10 сек на CPU, < 3 сек на GPU

### Обратная задача (text → diagram):
- Парсинг: успешное извлечение > 90% шагов
- Визуализация: корректное расположение узлов
- Время генерации: < 5 сек

### API:
- Uptime: > 99%
- Response time: < 15 сек (95 percentile)
- Memory usage: < 4 GB на CPU, < 8 GB на GPU
