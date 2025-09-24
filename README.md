# Bundestag Mining

Analysis and visualization of data about the German parliament (Bundestag).

Ein interaktives Dashboard zur Analyse demografischer Daten der deutschen Bundestagsabgeordneten von 1949 bis heute.


## Übersicht

Dieses Projekt analysiert die Zusammensetzung des Deutschen Bundestags über alle Wahlperioden hinweg und visualisiert Trends in:
- Parteizugehörigkeit
- Geschlechterverteilung  
- Altersstruktur
- Berufsgruppen
- Religionszugehörigkeit
- Familienstand
- Bleibedauer im Parlament



## Quick Start

Das interaktive Web-Dashboard starten:
```bash
poetry install
cd dashboard
poetry run python abgeordneten-dashboard.py
```
Dashboard verfügbar unter: http://localhost:8050


## Documentation

All project documentation can be found in the [`docs/`](docs/) directory, including:
- **[Setup and Installation Guide](docs/general_stuff.md)** - Comprehensive setup instructions and usage
- **[Docker Deployment Guide](docs/docker_guide.md)** - Container deployment and cloud deployment
- **[GCC Deployment](docs/gcc_deployment.md)** - Google Cloud deployment specifics
- **[AWS Deployment](docs/aws_deployment.md)** - AWS deployment instructions