# За базу используем официальный image питона
FROM python:3.10.6

# Отключаем буферизацию логов
ENV PYTHONUNBUFFERED 1

# Обновляем пакетный менеджер
RUN pip install --upgrade pip

# Копируем все файлы приложения в рабочую директорию в контейнере
WORKDIR /usr/src/app
ADD . /usr/src/app
RUN python3 -m pip install --upgrade --no-cache-dir setuptools==58.0
RUN pip install -r requirements.txt
