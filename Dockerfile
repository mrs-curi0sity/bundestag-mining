FROM python:3.11-slim-bullseye as builder

RUN apt-get update && apt-get install -y gnupg
RUN apt-key adv --refresh-keys --keyserver keyserver.ubuntu.com
RUN apt-get clean

# System-Abhängigkeiten installieren
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Poetry installieren
RUN curl -sSL https://install.python-poetry.org | python3 -

# Poetry zum PATH hinzufügen
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Nur pyproject.toml und poetry.lock kopieren (falls vorhanden)
COPY pyproject.toml poetry.lock* ./

# Abhängigkeiten installieren
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# Restliche Projektdateien kopieren
COPY . .

# Produktions-Image
FROM python:3.11-slim-bullseye

WORKDIR /app

# Kopieren Sie die installierten Abhängigkeiten und Projektdateien
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app /app

# Erstellen Sie einen nicht-root Benutzer
RUN useradd -m myuser

# Stellen Sie sicher, dass alle notwendigen Verzeichnisse existieren und die richtigen Berechtigungen haben
RUN mkdir -p /app/data/2024/output /app/plots \
    && chown -R myuser:myuser /app

# Wechseln Sie zum nicht-root Benutzer
USER myuser

# Exponieren Sie den Port
EXPOSE 8050

# Führen Sie die Anwendung aus
CMD ["python3", "./dashboard/abgeordneten-dashboard.py"]