# ML Models

Эта директория содержит предобученные модели для работы сервиса.

## Структура

```
models/
├── yolov8/
│   └── yolov8n.pt          # YOLOv8 nano модель для детекции элементов диаграмм
└── README.md               # Этот файл
```

## Загрузка моделей

### Автоматическая загрузка

Запустите скрипт для автоматической загрузки всех необходимых моделей:

```bash
python scripts/download_models.py
```

### Ручная загрузка

#### YOLOv8n

YOLOv8n модель будет автоматически загружена при первом запуске через библиотеку `ultralytics`.

Или скачайте вручную:
```bash
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt -O models/yolov8/yolov8n.pt
```

#### PaddleOCR

PaddleOCR модели загружаются автоматически при первом использовании библиотеки.
Поддерживаемые языки: русский (ru), английский (en).

## Дообучение YOLOv8

Для дообучения YOLOv8 на собственных данных диаграмм:

1. Подготовьте датасет в формате YOLO
2. Запустите скрипт обучения:
   ```bash
   python scripts/train_yolo.py --data path/to/dataset.yaml --epochs 50
   ```
3. Обученная модель будет сохранена в `models/yolov8/custom_yolov8n.pt`
4. Обновите путь в `.env`: `YOLO_MODEL_PATH=models/yolov8/custom_yolov8n.pt`

## Требования к памяти

| Модель | CPU RAM | GPU VRAM |
|--------|---------|----------|
| YOLOv8n | ~500 MB | ~1.5 GB |
| PaddleOCR | ~300 MB | ~500 MB |
| **Итого** | ~1 GB | ~2 GB |

Рекомендуется минимум 2 GB RAM для CPU режима и 4 GB VRAM для GPU режима.

## Лицензии

- **YOLOv8**: AGPL-3.0 (https://github.com/ultralytics/ultralytics)
- **PaddleOCR**: Apache-2.0 (https://github.com/PaddlePaddle/PaddleOCR)
