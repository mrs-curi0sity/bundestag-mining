## Projektstruktur

```
bundestag-mining/
├── blog/                  # Blog-Artikel Drafts
├── dashboard/             # Dash-Webanwendung
│   └── abgeordneten-dashboard.py
├── data/                  # Daten (Input/Output)
│   └── 2025/
│       ├── input/         # XML-Quelldaten
│       └── output/        # Verarbeitete CSV-Dateien
├── docs/                  # Dokumentation
│   ├── general_stuff.md   # Setup & Usage Guide
│   ├── docker_guide.md    # Docker Commands
│   ├── gcc_deployment.md  # Google Cloud
│   └── aws_deployment.md  # AWS Deployment
├── notebooks/             # Jupyter Notebooks für EDA
├── plots/                 # Generierte Plots
├── presentation/          # Quarto-Präsentationen
├── src/                   # Python Module
│   ├── config.py          # Konfiguration und Pfade
│   ├── data_processing.py # Datenverarbeitung und Mapping
│   ├── mapping_values.py  # Visualisierungsfunktionen
│   └── visualization.py   # Plot-Generierung
├── BRAINDUMP.md          # Ungeordnete Projektnotizen
└── pyproject.toml        # Poetry-Konfiguration
```

## Installation & Setup

### Voraussetzungen
- Python 3.11+
- Poetry für Dependency Management
- Jupyter Lab für Notebooks
- Quarto für Präsentationen (optional)

### Installation

1. Repository klonen:
```bash
git clone <repository-url>
cd bundestag-mining
```

2. Dependencies installieren:
```bash
poetry install
```

3. Jupyter Kernel einrichten:
```bash
poetry run python -m ipykernel install --user --name=bundestag-mining --display-name="Bundestag Mining (Poetry)"
```

## Verwendung

### Datenverarbeitung
1. Jupyter Lab starten:
```bash
poetry run jupyter lab
```

2. EDA und Preprocessing Notebooks ausführen um:
   - XML-Quelldaten zu bereinigen
   - Kategorien zu mappieren (Religion, Berufe, etc.)
   - Bereinigten Datensatz zu exportieren

### Dashboard
Das interaktive Web-Dashboard starten:
```bash
cd dashboard
poetry run python abgeordneten-dashboard.py
```

Das Dashboard ist dann verfügbar unter: http://localhost:8050

### Features des Dashboards:
- **Filter**: Wahlperioden und Parteien auswählen
- **Visualisierungen**: 
  - Parteienverteilung über Zeit
  - Geschlechter- und Altersverteilung
  - Berufsgruppen und Religion
  - Familienstand und Kinderanzahl
  - Bleibedauer der Abgeordneten
- **Datentabelle**: Filterbare und sortierbare Übersicht aller Abgeordneten



## Datenquellen

- **Hauptquelle**: MDB_STAMMDATEN.XML (Bundestag)
- **Zeitraum**: 1. Wahlperiode (1949) bis 21. Wahlperiode (2025)
- **Umfang**: Alle Bundestagsabgeordneten mit demografischen Informationen

## Technische Details

### Datenverarbeitung
- **Bereinigung**: Normalisierung von Berufsbezeichnungen, Religionsangaben
- **Kategorisierung**: Gruppierung in größere Kategorien für bessere Visualisierung
- **Mapping**: Vereinheitlichung historischer Parteinamen

### Visualisierung
- **Framework**: Plotly/Dash für interaktive Webvisualisierung
- **Responsive Design**: Bootstrap-basiertes Layout
- **Farbkodierung**: Partei-spezifische Farben nach politischen Konventionen

### Architektur
- **Modulare Struktur**: Saubere Trennung von Datenverarbeitung und Visualisierung
- **Konfigurationsmanagement**: Zentrale config.py für Pfade und Parameter
- **Metadaten**: Automatisches Laden von Kategorien aus verarbeiteten Daten

## Entwicklung

### Code-Struktur
- `data_processing.py`: Alle Mapping-Dictionaries und Bereinigungsfunktionen
- `config.py`: Pfade, Konfiguration und geladene Kategorien-Listen  
- `mapping_values.py`: Visualisierungsspezifische Funktionen (Farben)
- `dashboard/`: Dash-Anwendung mit interaktiven Komponenten


### Präsentationen
Quarto-Präsentation erstellen und anzeigen:
```bash
quarto preview presentation/2025_09_25_THAugsburg_ProfRichard.ipynb --no-browser
```

## Kontakt

- **web** https://yourcupofdata.com
- **mail** aretzelena@gmail.com
- **linkedin** https://www.linkedin.com/in/lena-aretz-0a305285/

