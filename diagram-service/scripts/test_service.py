import requests
import base64
import json
import sys
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


def create_test_image():
    img = Image.new('RGB', (400, 300), color='white')
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([150, 20, 250, 60], outline='black', width=2)
    draw.text((200, 40), "Start", fill='black', anchor="mm")
    
    draw.rectangle([150, 100, 250, 140], outline='black', width=2)
    draw.text((200, 120), "Process", fill='black', anchor="mm")
    
    draw.polygon([200, 180, 250, 210, 200, 240, 150, 210], outline='black', width=2)
    draw.text((200, 210), "Decision", fill='black', anchor="mm")
    
    draw.line([200, 60, 200, 100], fill='black', width=2)
    draw.line([200, 140, 200, 180], fill='black', width=2)
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer


def test_health_check(base_url):
    print("\n=== Testing Health Check ===")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_analyze_endpoint(base_url):
    print("\n=== Testing Analyze Endpoint ===")
    try:
        image_buffer = create_test_image()
        
        files = {'image': ('test_diagram.png', image_buffer, 'image/png')}
        response = requests.post(f"{base_url}/api/v1/analyze", files=files)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Task Type: {result['task_type']}")
            print(f"Processing Time: {result['processing_time_sec']}s")
            print(f"Description: {result['description'][:100]}...")
            print(f"Nodes: {len(result['graph_representation']['nodes'])}")
            print(f"Edges: {len(result['graph_representation']['edges'])}")
            return True
        else:
            print(f"Error Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_generate_endpoint(base_url):
    print("\n=== Testing Generate Endpoint ===")
    try:
        data = {
            "description": "Начало. Проверить условие X. Если истина, выполнить действие A, иначе действие B. Конец.",
            "output_format": "both",
            "diagram_type": "flowchart",
            "layout": "vertical"
        }
        
        response = requests.post(
            f"{base_url}/api/v1/generate",
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Task Type: {result['task_type']}")
            print(f"Processing Time: {result['processing_time_sec']}s")
            print(f"Nodes: {len(result['graph_representation']['nodes'])}")
            print(f"Edges: {len(result['graph_representation']['edges'])}")
            
            if result['artifacts'].get('diagram_image_base64'):
                print("✓ Diagram image generated")
            if result['artifacts'].get('diagram_code'):
                print("✓ Diagram code generated")
                print(f"Code preview:\n{result['artifacts']['diagram_code'][:200]}...")
            
            return True
        else:
            print(f"Error Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print(f"Testing Diagram Service at {base_url}")
    print("=" * 50)
    
    results = []
    
    results.append(("Health Check", test_health_check(base_url)))
    results.append(("Analyze Endpoint", test_analyze_endpoint(base_url)))
    results.append(("Generate Endpoint", test_generate_endpoint(base_url)))
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print("=" * 50)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
