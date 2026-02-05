"""
Скрипт для генерации визуальных изображений диаграмм из PlantUML кода
"""
import base64
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json


def create_simple_flowchart(steps, output_path, width=800, height=None):
    """Создает простую блок-схему из списка шагов"""
    
    # Параметры
    box_width = 300
    box_height = 80
    vertical_spacing = 50
    start_x = (width - box_width) // 2
    start_y = 50
    
    # Вычисляем высоту
    if height is None:
        height = start_y + len(steps) * (box_height + vertical_spacing) + 50
    
    # Создаем изображение
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Пытаемся загрузить шрифт
    try:
        font = ImageFont.truetype("arial.ttf", 14)
        font_bold = ImageFont.truetype("arialbd.ttf", 16)
    except:
        font = ImageFont.load_default()
        font_bold = font
    
    # Рисуем каждый шаг
    for i, step in enumerate(steps):
        y = start_y + i * (box_height + vertical_spacing)
        
        # Определяем тип элемента и цвет
        if "Начало" in step or "Start" in step:
            # Овал для начала
            color = "#90EE90"  # Светло-зеленый
            draw.ellipse([start_x, y, start_x + box_width, y + box_height], 
                        fill=color, outline="black", width=2)
        elif "Конец" in step or "End" in step or "Завершение" in step:
            # Овал для конца
            color = "#FFB6C1"  # Светло-розовый
            draw.ellipse([start_x, y, start_x + box_width, y + box_height], 
                        fill=color, outline="black", width=2)
        elif "Условие" in step or "Проверка" in step or "?" in step:
            # Ромб для условия
            color = "#FFD700"  # Золотой
            points = [
                (start_x + box_width // 2, y),  # Верх
                (start_x + box_width, y + box_height // 2),  # Право
                (start_x + box_width // 2, y + box_height),  # Низ
                (start_x, y + box_height // 2)  # Лево
            ]
            draw.polygon(points, fill=color, outline="black")
        else:
            # Прямоугольник для действия
            color = "#87CEEB"  # Голубой
            draw.rectangle([start_x, y, start_x + box_width, y + box_height], 
                          fill=color, outline="black", width=2)
        
        # Рисуем текст
        text = step.split(': ', 1)[1] if ': ' in step else step
        # Разбиваем длинный текст на строки
        words = text.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] > box_width - 20:
                if len(current_line) > 1:
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(test_line)
                    current_line = []
        if current_line:
            lines.append(' '.join(current_line))
        
        # Центрируем текст
        text_height = len(lines) * 20
        text_y = y + (box_height - text_height) // 2
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = start_x + (box_width - text_width) // 2
            draw.text((text_x, text_y), line, fill="black", font=font)
            text_y += 20
        
        # Рисуем стрелку к следующему элементу
        if i < len(steps) - 1:
            arrow_start_y = y + box_height
            arrow_end_y = y + box_height + vertical_spacing
            arrow_x = start_x + box_width // 2
            
            # Линия
            draw.line([(arrow_x, arrow_start_y), (arrow_x, arrow_end_y)], 
                     fill="black", width=2)
            # Наконечник стрелки
            draw.polygon([
                (arrow_x, arrow_end_y),
                (arrow_x - 5, arrow_end_y - 10),
                (arrow_x + 5, arrow_end_y - 10)
            ], fill="black")
    
    # Сохраняем
    img.save(output_path)
    print(f"Создана диаграмма: {output_path}")
    
    return output_path


def image_to_base64(image_path):
    """Конвертирует изображение в base64"""
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


def main():
    # Загружаем примеры
    examples_file = Path(__file__).parent / "diagram_examples.json"
    with open(examples_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Создаем папку для изображений
    output_dir = Path(__file__).parent / "generated_diagrams"
    output_dir.mkdir(exist_ok=True)
    
    # Генерируем изображения для каждого примера
    for example in data['diagrams']:
        filename = example['filename'].replace('.png', '_generated.png')
        output_path = output_dir / filename
        
        steps = example['sequence']
        create_simple_flowchart(steps, output_path)
        
        # Конвертируем в base64 и сохраняем
        base64_str = image_to_base64(output_path)
        base64_file = output_path.with_suffix('.txt')
        with open(base64_file, 'w') as f:
            f.write(base64_str)
        
        print(f"  Base64 сохранен: {base64_file}")
    
    print(f"\nВсе диаграммы созданы в папке: {output_dir}")


if __name__ == "__main__":
    main()
