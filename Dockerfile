# Используем базовый образ Python
FROM python:3.11

# Указываем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY ./requirements.txt /app/requirements.txt

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копируем все файлы проекта в контейнер
COPY . /app

# Создаем volume для данных SQLite базы данных
VOLUME /app/core/data

# Создаем пользователя для выполнения приложения
RUN useradd -m appuser
USER appuser

# Указываем порт для работы приложения
EXPOSE 8000  # Укажите, если приложение работает на определённом порту (например, FastAPI)

# Устанавливаем команду для запуска приложения
CMD ["python", "main.py"]
