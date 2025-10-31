FROM python:3.12-slim

# Crear y establecer el directorio de trabajo
WORKDIR /usr/src/app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar los archivos de dependencias primero (para aprovechar la cache de Docker)
COPY requirements.txt ./

# Instalar dependencias de Python
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

# Copiar y preparar db_init
COPY db_init.sh ./db_init.sh
RUN chmod +x ./db_init.sh

ENTRYPOINT ["./db_init.sh"]
CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" ]