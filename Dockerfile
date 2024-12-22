FROM python:3.10-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    libcairo2-dev \
    libffi-dev \
    && apt-get clean

# Instalar las dependencias de Python
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Copiar la aplicación
COPY . /app

CMD ["streamlit", "run", "app.py"]
