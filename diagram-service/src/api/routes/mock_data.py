from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
import time
import json
from pathlib import Path

from src.core.logger import app_logger

router = APIRouter()

# Загружаем примеры диаграмм
EXAMPLES_FILE = Path(__file__).parent.parent.parent.parent / "diagram_examples.json"
DIAGRAM_EXAMPLES = {}

try:
    if EXAMPLES_FILE.exists():
        with open(EXAMPLES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            DIAGRAM_EXAMPLES = {ex['filename']: ex for ex in data['diagrams']}
except Exception as e:
    app_logger.error(f"Failed to load diagram examples: {e}")


@router.post("/analyze-mock")
async def analyze_diagram_mock(image: UploadFile = File(...)):
    """Мок-endpoint для демонстрации анализа диаграмм с реальными примерами"""
    
    app_logger.info(f"Mock analyze request: {image.filename}")
    
    # Симулируем обработку
    time.sleep(0.5)
    
    # Пытаемся найти пример для этой диаграммы
    example = DIAGRAM_EXAMPLES.get(image.filename)
    
    if example:
        # Используем реальный пример из датасета
        mock_result = {
            "description": example['description'],
        
            "graph_representation": {
                "nodes": [
                    {"id": f"node_{i}", "type": "process", "label": step.split('. ', 1)[1] if '. ' in step else step, "position": [100, 100 + i*100]}
                    for i, step in enumerate(example['sequence'])
                ],
                "edges": [
                    {"source": f"node_{i}", "target": f"node_{i+1}", "label": ""}
                    for i in range(len(example['sequence']) - 1)
                ]
            },
            "metadata": {
                "processing_time": 0.5,
                "num_detected_elements": len(example['sequence']),
                "image_filename": image.filename,
                "flow_type": example['type'],
                "confidence": 0.95
            }
        }
    else:
        # Дефолтный пример если диаграмма не найдена
        mock_result = {
            "description": "Бизнес-процесс с последовательными действиями. Процесс включает начальный этап, несколько промежуточных действий и завершающий этап.",
            "graph_representation": {
                "nodes": [
                    {"id": "node_0", "type": "start", "label": "Начало процесса", "position": [100, 50]},
                    {"id": "node_1", "type": "process", "label": "Действие 1", "position": [100, 150]},
                    {"id": "node_2", "type": "process", "label": "Действие 2", "position": [100, 250]},
                    {"id": "node_3", "type": "decision", "label": "Проверка условия", "position": [100, 350]},
                    {"id": "node_4", "type": "process", "label": "Действие 3", "position": [250, 450]},
                    {"id": "node_5", "type": "end", "label": "Конец процесса", "position": [250, 550]}
                ],
                "edges": [
                    {"source": "node_0", "target": "node_1", "label": ""},
                    {"source": "node_1", "target": "node_2", "label": ""},
                    {"source": "node_2", "target": "node_3", "label": ""},
                    {"source": "node_3", "target": "node_4", "label": "Да"},
                    {"source": "node_4", "target": "node_5", "label": ""}
                ]
            },
            "metadata": {
                "processing_time": 0.5,
                "num_detected_elements": 6,
                "image_filename": image.filename,
                "flow_type": "BPMN - Блок-схема",
                "confidence": 0.85
            }
        }
    
    return JSONResponse(content=mock_result)


def generate_svg_diagram(steps):
    """Генерирует SVG диаграмму из списка шагов"""
    box_width = 300
    box_height = 80
    vertical_spacing = 50
    start_x = 50
    start_y = 50
    
    width = box_width + 100
    height = start_y + len(steps) * (box_height + vertical_spacing) + 50
    
    svg_parts = [
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
        '<defs>',
        '<style>',
        '.box { fill: #87CEEB; stroke: black; stroke-width: 2; }',
        '.start-end { fill: #90EE90; stroke: black; stroke-width: 2; }',
        '.decision { fill: #FFD700; stroke: black; stroke-width: 2; }',
        '.text { font-family: Arial, sans-serif; font-size: 14px; text-anchor: middle; }',
        '</style>',
        '</defs>'
    ]
    
    for i, step in enumerate(steps):
        y = start_y + i * (box_height + vertical_spacing)
        center_x = start_x + box_width // 2
        
        # Определяем тип и рисуем фигуру
        text = step.split(': ', 1)[1] if ': ' in step else step
        
        if "Начало" in step or "Start" in step:
            # Овал для начала
            svg_parts.append(
                f'<ellipse cx="{center_x}" cy="{y + box_height//2}" '
                f'rx="{box_width//2}" ry="{box_height//2}" class="start-end"/>'
            )
        elif "Конец" in step or "End" in step:
            # Овал для конца
            svg_parts.append(
                f'<ellipse cx="{center_x}" cy="{y + box_height//2}" '
                f'rx="{box_width//2}" ry="{box_height//2}" class="start-end" '
                f'style="fill: #FFB6C1;"/>'
            )
        elif "Условие" in step or "?" in step:
            # Ромб для условия
            points = f"{center_x},{y} {start_x + box_width},{y + box_height//2} {center_x},{y + box_height} {start_x},{y + box_height//2}"
            svg_parts.append(f'<polygon points="{points}" class="decision"/>')
        else:
            # Прямоугольник для действия
            svg_parts.append(
                f'<rect x="{start_x}" y="{y}" width="{box_width}" '
                f'height="{box_height}" class="box"/>'
            )
        
        # Текст (разбиваем на строки если длинный)
        words = text.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            if len(' '.join(current_line)) > 35:
                if len(current_line) > 1:
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    current_line = []
        if current_line:
            lines.append(' '.join(current_line))
        
        text_y = y + box_height // 2 - (len(lines) - 1) * 7
        for line in lines:
            svg_parts.append(
                f'<text x="{center_x}" y="{text_y}" class="text">{line}</text>'
            )
            text_y += 18
        
        # Стрелка к следующему элементу
        if i < len(steps) - 1:
            arrow_start_y = y + box_height
            arrow_end_y = y + box_height + vertical_spacing
            svg_parts.append(
                f'<line x1="{center_x}" y1="{arrow_start_y}" '
                f'x2="{center_x}" y2="{arrow_end_y}" '
                f'stroke="black" stroke-width="2"/>'
            )
            svg_parts.append(
                f'<polygon points="{center_x},{arrow_end_y} '
                f'{center_x-5},{arrow_end_y-10} {center_x+5},{arrow_end_y-10}" '
                f'fill="black"/>'
            )
    
    svg_parts.append('</svg>')
    return ''.join(svg_parts)


@router.post("/generate-mock")
async def generate_diagram_mock():
    """Мок-endpoint для демонстрации генерации диаграмм с визуальным изображением"""
    
    app_logger.info("Mock generate request")
    
    # Симулируем обработку
    time.sleep(0.5)
    
    # Берем первый пример из датасета
    if DIAGRAM_EXAMPLES:
        example = list(DIAGRAM_EXAMPLES.values())[0]
        plantuml_code = example.get('plantuml', '@startuml\nstart\n:Процесс;\nstop\n@enduml')
        description = example['description']
        steps = example['sequence']
        num_nodes = len(steps)
    else:
        plantuml_code = "@startuml\nstart\n:Процесс;\nstop\n@enduml"
        description = "Бизнес-процесс."
        steps = ["1. Начало", "2. Действие", "3. Конец"]
        num_nodes = 3
    
    # Генерируем SVG диаграмму
    svg_diagram = generate_svg_diagram(steps)
    
    # Конвертируем SVG в base64
    import base64
    svg_base64 = base64.b64encode(svg_diagram.encode('utf-8')).decode('utf-8')
    diagram_image = f"data:image/svg+xml;base64,{svg_base64}"
    
    mock_result = {
        "diagram_code": plantuml_code,
        "diagram_image": diagram_image,
        "description": description,
        "metadata": {
            "processing_time": 0.5,
            "num_nodes": num_nodes,
            "num_edges": num_nodes - 1,
            "diagram_type": "flowchart"
        }
    }
    
    return JSONResponse(content=mock_result)
