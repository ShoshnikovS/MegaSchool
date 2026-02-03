# Deployment Guide

## Требования к серверу

### Минимальные (CPU режим)
- **CPU**: 4 ядра (2.0 GHz+)
- **RAM**: 4 GB
- **Диск**: 10 GB свободного места
- **ОС**: Linux (Ubuntu 20.04+), macOS, Windows Server

### Рекомендуемые (GPU режим)
- **CPU**: 8 ядер (2.5 GHz+)
- **RAM**: 8 GB
- **GPU**: NVIDIA с CUDA поддержкой, ≥8 GB VRAM
- **Диск**: 20 GB свободного места
- **ОС**: Linux (Ubuntu 20.04+)

## Установка Docker

### Ubuntu/Debian

```bash
# Обновление пакетов
sudo apt-get update

# Установка зависимостей
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Добавление GPG ключа Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Добавление репозитория Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Установка Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Проверка установки
sudo docker --version
```

### Настройка GPU (NVIDIA)

```bash
# Установка NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Перезапуск Docker
sudo systemctl restart docker

# Проверка GPU
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

## Развертывание

### 1. Клонирование репозитория

```bash
git clone https://github.com/yourusername/diagram-service.git
cd diagram-service
```

### 2. Настройка переменных окружения

```bash
cp .env.example .env
nano .env
```

Основные параметры для настройки:
- `DEVICE=cpu` или `DEVICE=cuda`
- `LOG_LEVEL=INFO` или `LOG_LEVEL=DEBUG`
- `APP_PORT=8000`

### 3. Запуск сервиса

#### CPU режим

```bash
cd docker
docker-compose up -d --build
```

#### GPU режим

```bash
cd docker
docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up -d --build
```

### 4. Проверка работы

```bash
# Проверка статуса контейнера
docker ps

# Проверка логов
docker logs diagram-service

# Проверка health check
curl http://localhost:8000/health
```

## Мониторинг

### Просмотр логов

```bash
# Все логи
docker logs diagram-service

# Последние 100 строк
docker logs --tail 100 diagram-service

# Следить за логами в реальном времени
docker logs -f diagram-service
```

### Метрики контейнера

```bash
# Использование ресурсов
docker stats diagram-service

# Детальная информация
docker inspect diagram-service
```

### Логи приложения

Логи сохраняются в `logs/app.log` внутри контейнера и маппятся на хост:

```bash
tail -f logs/app.log
```

## Обновление

### Обновление кода

```bash
# Остановка сервиса
docker-compose down

# Получение обновлений
git pull origin main

# Пересборка и запуск
docker-compose up -d --build
```

### Обновление моделей

```bash
# Вход в контейнер
docker exec -it diagram-service bash

# Запуск скрипта загрузки моделей
poetry run python scripts/download_models.py

# Перезапуск сервиса
docker restart diagram-service
```

## Масштабирование

### Горизонтальное масштабирование

Для обработки большего количества запросов можно запустить несколько инстансов:

```yaml
# docker-compose.scale.yml
version: '3.8'

services:
  diagram-service:
    deploy:
      replicas: 3
```

```bash
docker-compose -f docker-compose.yml -f docker-compose.scale.yml up -d
```

### Использование Nginx как балансировщика

```nginx
upstream diagram_service {
    least_conn;
    server localhost:8001;
    server localhost:8002;
    server localhost:8003;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://diagram_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Резервное копирование

### Модели

```bash
# Создание резервной копии моделей
tar -czf models_backup_$(date +%Y%m%d).tar.gz models/

# Восстановление
tar -xzf models_backup_20260203.tar.gz
```

### Логи

```bash
# Архивирование логов
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/
```

## Troubleshooting

### Контейнер не запускается

```bash
# Проверка логов
docker logs diagram-service

# Проверка конфигурации
docker-compose config

# Пересборка без кэша
docker-compose build --no-cache
```

### Высокое использование памяти

```bash
# Ограничение памяти в docker-compose.yml
services:
  diagram-service:
    deploy:
      resources:
        limits:
          memory: 4G
```

### GPU не обнаруживается

```bash
# Проверка NVIDIA драйверов
nvidia-smi

# Проверка Docker GPU поддержки
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

# Проверка переменной окружения
docker exec diagram-service env | grep DEVICE
```

### Медленная обработка

1. Проверьте, используется ли GPU (если доступен)
2. Увеличьте количество workers в `.env`
3. Оптимизируйте размер входных изображений
4. Рассмотрите горизонтальное масштабирование

## Безопасность

### Рекомендации

1. **Не выставляйте сервис напрямую в интернет** - используйте reverse proxy (Nginx, Traefik)
2. **Используйте HTTPS** - настройте SSL сертификаты
3. **Ограничьте доступ** - используйте firewall правила
4. **Регулярно обновляйте** - следите за обновлениями зависимостей
5. **Мониторьте логи** - настройте систему мониторинга (ELK, Grafana)

### Пример Nginx с SSL

```nginx
server {
    listen 443 ssl http2;
    server_name diagram-service.example.com;
    
    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        client_max_body_size 10M;
    }
}
```

## Production Checklist

- [ ] Docker и Docker Compose установлены
- [ ] GPU драйверы настроены (если используется GPU)
- [ ] Переменные окружения настроены
- [ ] Модели загружены
- [ ] Сервис запущен и доступен
- [ ] Health check проходит успешно
- [ ] Логирование настроено
- [ ] Мониторинг настроен
- [ ] Резервное копирование настроено
- [ ] SSL сертификаты установлены
- [ ] Firewall правила настроены
- [ ] Документация доступна команде
