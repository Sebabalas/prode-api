# Usar una imagen base ligera de Python
FROM python:3.9-slim

# Instalar dependencias necesarias
RUN apt-get update && apt-get install -y \
    firefox-esr \
    wget \
    tar \
    && rm -rf /var/lib/apt/lists/*

# Descargar e instalar geckodriver
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz \
    && tar -xvzf geckodriver-v0.30.0-linux64.tar.gz \
    && mv geckodriver /usr/local/bin/

# Copiar el archivo requirements.txt y luego instalar dependencias de Python
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copiar el código de la aplicación
COPY . /app

# Establecer el directorio de trabajo
WORKDIR /app

# Ejecutar la aplicación
CMD ["python", "Prode.py"]