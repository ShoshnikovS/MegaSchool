# API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

В текущей версии аутентификация не требуется. Сервис предназначен для внутреннего использования.

## Endpoints

### Health Check

Проверка состояния сервиса.

**Endpoint**: `GET /health`

**Response** (200 OK):
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "device": "cpu",
  "models_loaded": true
}
```

---

### Analyze Diagram (Прямая задача)

Анализ изображения диаграммы и преобразование в текстовое описание.

**Endpoint**: `POST /api/v1/analyze`

**Request**:
- Content-Type: `multipart/form-data`
- Body:
  - `image` (file): Изображение диаграммы (PNG, JPEG)

**Example (curl)**:
```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@diagram.png"
```

**Example (Python)**:
```python
import requests

url = "http://localhost:8000/api/v1/analyze"
files = {"image": open("diagram.png", "rb")}
response = requests.post(url, files=files)
result = response.json()
```

**Response** (200 OK):
```json
{
  "task_type": "image_to_text",
  "description": "Алгоритм начинается с начального узла. Затем выполняется обработка данных...",
  "graph_representation": {
    "nodes": [
      {
        "id": "node_1",
        "type": "start",
        "label": "Начало",
        "position": [100, 50]
      },
      {
        "id": "node_2",
        "type": "process",
        "label": "Обработка данных",
        "position": [100, 150]
      }
    ],
    "edges": [
      {
        "source": "node_1",
        "target": "node_2",
        "label": null
      }
    ]
  },
  "artifacts": {},
  "processing_time_sec": 3.45,
  "metadata": {
    "image_filename": "diagram.png",
    "image_size_bytes": 245678
  }
}
```

**Error Responses**:

- **400 Bad Request**: Невалидное изображение
```json
{
  "error": "ValidationError",
  "message": "Invalid file type. Only images are supported.",
  "details": {
    "content_type": "application/pdf"
  }
}
```

- **413 Payload Too Large**: Изображение слишком большое
```json
{
  "error": "ValidationError",
  "message": "Image too large. Maximum size is 10MB.",
  "details": {
    "size": 15728640
  }
}
```

---

### Generate Diagram (Обратная задача)

Генерация диаграммы из текстового описания.

**Endpoint**: `POST /api/v1/generate`

**Request**:
- Content-Type: `application/json`
- Body:
```json
{
  "description": "Начало. Проверить условие X. Если истина, выполнить действие A, иначе действие B. Конец.",
  "output_format": "both",
  "diagram_type": "flowchart",
  "layout": "vertical"
}
```

**Parameters**:
- `description` (string, required): Текстовое описание алгоритма (10-5000 символов)
- `output_format` (string, optional): Формат вывода
  - `"image"`: Только изображение
  - `"code"`: Только код (PlantUML/Mermaid)
  - `"both"`: И изображение, и код (default)
- `diagram_type` (string, optional): Тип диаграммы
  - `"flowchart"`: Блок-схема (default)
  - `"bpmn"`: BPMN диаграмма
  - `"uml"`: UML диаграмма
- `layout` (string, optional): Направление компоновки
  - `"vertical"`: Вертикальное
  - `"horizontal"`: Горизонтальное
  - `"auto"`: Автоматическое (default)

**Example (curl)**:
```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Начало. Проверить условие X. Если истина, выполнить действие A, иначе действие B. Конец.",
    "output_format": "both"
  }'
```

**Example (Python)**:
```python
import requests
import base64

url = "http://localhost:8000/api/v1/generate"
data = {
    "description": "Начало. Проверить условие X. Если истина, выполнить действие A, иначе действие B. Конец.",
    "output_format": "both"
}
response = requests.post(url, json=data)
result = response.json()

# Сохранение изображения
if "diagram_image_base64" in result["artifacts"]:
    image_data = base64.b64decode(result["artifacts"]["diagram_image_base64"])
    with open("generated_diagram.png", "wb") as f:
        f.write(image_data)

# Сохранение кода
if "diagram_code" in result["artifacts"]:
    with open("diagram.puml", "w") as f:
        f.write(result["artifacts"]["diagram_code"])
```

**Response** (200 OK):
```json
{
  "task_type": "text_to_diagram",
  "description": "Начало. Проверить условие X...",
  "graph_representation": {
    "nodes": [
      {
        "id": "start",
        "type": "start",
        "label": "Начало",
        "position": [100, 50]
      },
      {
        "id": "check",
        "type": "decision",
        "label": "Условие X",
        "position": [100, 150]
      }
    ],
    "edges": [
      {
        "source": "start",
        "target": "check",
        "label": null
      }
    ]
  },
  "artifacts": {
    "diagram_image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
    "diagram_code": "@startuml\nstart\nif (условие X?) then (да)\n  :действие A;\nelse (нет)\n  :действие B;\nendif\nstop\n@enduml"
  },
  "processing_time_sec": 2.15,
  "metadata": {
    "output_format": "both",
    "diagram_type": "flowchart",
    "layout": "vertical"
  }
}
```

**Error Responses**:

- **400 Bad Request**: Невалидное описание
```json
{
  "error": "ValidationError",
  "message": "Description too short",
  "details": {}
}
```

- **500 Internal Server Error**: Ошибка генерации
```json
{
  "error": "VisualizationError",
  "message": "Failed to generate diagram",
  "details": {
    "error": "..."
  }
}
```

---

## Data Models

### Node Types

- `start`: Начальный узел (овал)
- `end`: Конечный узел (овал)
- `process`: Процесс/действие (прямоугольник)
- `decision`: Условие/решение (ромб)
- `data`: Данные (параллелограмм)

### Graph Representation

```json
{
  "nodes": [
    {
      "id": "unique_id",
      "type": "start|end|process|decision|data",
      "label": "Node label",
      "position": [x, y]
    }
  ],
  "edges": [
    {
      "source": "source_node_id",
      "target": "target_node_id",
      "label": "optional edge label"
    }
  ]
}
```

## Rate Limits

В текущей версии ограничения на количество запросов отсутствуют.

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - невалидные входные данные |
| 413 | Payload Too Large - файл слишком большой |
| 422 | Unprocessable Entity - ошибка валидации Pydantic |
| 500 | Internal Server Error - внутренняя ошибка сервера |

## Performance

### Прямая задача (image → text)
- **CPU**: ~8-12 секунд
- **GPU**: ~2-4 секунды

### Обратная задача (text → diagram)
- **CPU/GPU**: ~2-5 секунд

## Limits

- Максимальный размер изображения: **10 MB**
- Поддерживаемые форматы: **PNG, JPEG, JPG**
- Максимальная длина описания: **5000 символов**
- Минимальная длина описания: **10 символов**

## Interactive Documentation

Swagger UI доступен по адресу: `http://localhost:8000/docs`

ReDoc доступен по адресу: `http://localhost:8000/redoc`
