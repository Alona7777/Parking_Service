# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libleptonica-dev \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && apt-get clean

# Устанавливаем Python-зависимости
# Устанавливаем Python-зависимости
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копируем код приложения в контейнер
COPY . /app
WORKDIR /app

# Проверка наличия файла best.pt
RUN ls /app

# Указываем команду для запуска приложения
CMD ["python", "manage.py", "runserver"]