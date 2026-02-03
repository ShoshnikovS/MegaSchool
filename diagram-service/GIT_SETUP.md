# Git Setup и загрузка на GitHub

## Инициализация Git репозитория

### 1. Инициализация локального репозитория

```bash
cd diagram-service
git init
```

### 2. Добавление файлов

```bash
# Добавить все файлы
git add .

# Проверить статус
git status
```

### 3. Первый коммит

```bash
git commit -m "Initial commit: Project structure and base implementation

- Created project structure following PROJECT_STRUCTURE.md
- Implemented FastAPI application with /analyze and /generate endpoints
- Added Docker support (CPU and GPU)
- Configured Poetry for dependency management
- Added logging with loguru
- Created configuration management with pydantic-settings
- Added API documentation and deployment guide
- Implemented test scripts
- Added comprehensive README"
```

## Создание репозитория на GitHub

### Через веб-интерфейс GitHub

1. Перейдите на https://github.com
2. Нажмите "New repository" (зеленая кнопка)
3. Заполните форму:
   - **Repository name**: `diagram-service`
   - **Description**: `ML-сервис для двухстороннего преобразования диаграмм: изображение ↔ текстовое описание`
   - **Visibility**: Private (рекомендуется) или Public
   - **НЕ** инициализируйте с README, .gitignore или license (у нас уже есть эти файлы)
4. Нажмите "Create repository"

### Через GitHub CLI (альтернатива)

```bash
# Установка GitHub CLI (если не установлен)
# Windows: winget install GitHub.cli
# macOS: brew install gh
# Linux: см. https://github.com/cli/cli#installation

# Авторизация
gh auth login

# Создание репозитория
gh repo create diagram-service --private --source=. --remote=origin
```

## Подключение к GitHub

### Вариант 1: HTTPS

```bash
# Добавить remote
git remote add origin https://github.com/ВАШЕ_ИМЯ_ПОЛЬЗОВАТЕЛЯ/diagram-service.git

# Проверить remote
git remote -v

# Отправить код
git branch -M main
git push -u origin main
```

### Вариант 2: SSH (рекомендуется)

#### Настройка SSH ключа (если еще не настроен)

```bash
# Генерация SSH ключа
ssh-keygen -t ed25519 -C "your.email@example.com"

# Запуск ssh-agent
eval "$(ssh-agent -s)"

# Добавление ключа
ssh-add ~/.ssh/id_ed25519

# Копирование публичного ключа
cat ~/.ssh/id_ed25519.pub
```

Затем:
1. Перейдите на GitHub → Settings → SSH and GPG keys
2. Нажмите "New SSH key"
3. Вставьте скопированный публичный ключ
4. Нажмите "Add SSH key"

#### Подключение репозитория

```bash
# Добавить remote
git remote add origin git@github.com:ВАШЕ_ИМЯ_ПОЛЬЗОВАТЕЛЯ/diagram-service.git

# Проверить remote
git remote -v

# Отправить код
git branch -M main
git push -u origin main
```

## Последующие обновления

### Добавление изменений

```bash
# Проверить статус
git status

# Добавить измененные файлы
git add .

# Или добавить конкретные файлы
git add src/api/main.py src/core/config.py

# Коммит
git commit -m "Описание изменений"

# Отправка на GitHub
git push
```

### Создание веток для новых функций

```bash
# Создать новую ветку
git checkout -b feature/yolo-training

# Работа над функцией...
git add .
git commit -m "Add YOLO training script"

# Отправка ветки на GitHub
git push -u origin feature/yolo-training

# Создание Pull Request через веб-интерфейс GitHub
```

## Рекомендуемая структура коммитов

### Типы коммитов

- `feat:` - новая функциональность
- `fix:` - исправление бага
- `docs:` - изменения в документации
- `style:` - форматирование кода
- `refactor:` - рефакторинг кода
- `test:` - добавление тестов
- `chore:` - обновление зависимостей, конфигурации

### Примеры

```bash
git commit -m "feat: Add YOLOv8 detector implementation"
git commit -m "fix: Resolve memory leak in image preprocessing"
git commit -m "docs: Update API documentation with new endpoints"
git commit -m "refactor: Simplify graph construction logic"
git commit -m "test: Add unit tests for text parser"
git commit -m "chore: Update dependencies to latest versions"
```

## Полезные команды

```bash
# Просмотр истории коммитов
git log --oneline --graph --all

# Откат последнего коммита (сохраняя изменения)
git reset --soft HEAD~1

# Просмотр изменений
git diff

# Просмотр изменений конкретного файла
git diff src/api/main.py

# Создание тега для релиза
git tag -a v0.1.0 -m "Initial release"
git push origin v0.1.0

# Клонирование репозитория на другой машине
git clone https://github.com/ВАШЕ_ИМЯ_ПОЛЬЗОВАТЕЛЯ/diagram-service.git
```

## GitHub Actions (CI/CD)

Для автоматизации тестирования и деплоя можно создать `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install Poetry
      run: |
        curl -sSL https://install.python-poetry.org | python3 -
        echo "$HOME/.local/bin" >> $GITHUB_PATH
    
    - name: Install dependencies
      run: poetry install
    
    - name: Run tests
      run: poetry run pytest tests/ -v
    
    - name: Build Docker image
      run: docker build -f docker/Dockerfile -t diagram-service:test .
```

## Защита main ветки

Рекомендуется настроить защиту main ветки на GitHub:

1. Перейдите в Settings → Branches
2. Добавьте правило для `main`
3. Включите:
   - "Require pull request reviews before merging"
   - "Require status checks to pass before merging"
   - "Require branches to be up to date before merging"

## .gitignore проверка

Убедитесь, что следующие файлы/папки НЕ попадают в репозиторий:

```bash
# Проверить, что игнорируется
git status --ignored

# Если что-то попало случайно, удалить из индекса
git rm --cached путь/к/файлу
git commit -m "Remove accidentally committed file"
```

## Быстрая команда для первой загрузки

```bash
# Выполните все команды одной строкой (замените ВАШЕ_ИМЯ_ПОЛЬЗОВАТЕЛЯ)
cd diagram-service && \
git init && \
git add . && \
git commit -m "Initial commit: Complete project structure" && \
git branch -M main && \
git remote add origin https://github.com/ВАШЕ_ИМЯ_ПОЛЬЗОВАТЕЛЯ/diagram-service.git && \
git push -u origin main
```

## Готово!

После выполнения команд ваш проект будет доступен на GitHub по адресу:
```
https://github.com/ВАШЕ_ИМЯ_ПОЛЬЗОВАТЕЛЯ/diagram-service
```
