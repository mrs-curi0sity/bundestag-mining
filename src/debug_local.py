#!/usr/bin/env python3
"""
Debug-Script für lokale Fehlersuche
"""

import os
import sys
import traceback

def check_environment():
    """Überprüfe Umgebung und Abhängigkeiten"""
    print("=== UMGEBUNG CHECK ===")
    print(f"Python Version: {sys.version}")
    print(f"Working Directory: {os.getcwd()}")
    print(f"PORT Environment: {os.environ.get('PORT', 'nicht gesetzt')}")
    
    # Prüfe ob wichtige Dateien existieren
    important_files = [
        'src/config.py',
        'src/visualization.py', 
        'src/mapping_values.py'
    ]
    
    for file in important_files:
        if os.path.exists(file):
            print(f"✓ {file} existiert")
        else:
            print(f"✗ {file} fehlt!")
    
    # Prüfe sys.path
    print(f"\nPython Path:")
    for path in sys.path:
        print(f"  - {path}")

def check_imports():
    """Prüfe alle wichtigen Imports"""
    print("\n=== IMPORT CHECK ===")
    
    imports_to_test = [
        ('pandas', 'pd'),
        ('dash', None),
        ('dash_bootstrap_components', 'dbc'),
        ('plotly.graph_objs', 'go'),
        ('plotly.express', 'px')
    ]
    
    for module, alias in imports_to_test:
        try:
            if alias:
                exec(f"import {module} as {alias}")
            else:
                exec(f"import {module}")
            print(f"✓ {module} erfolgreich importiert")
        except Exception as e:
            print(f"✗ Fehler beim Import von {module}: {e}")

def test_data_files():
    """Prüfe Datendateien"""
    print("\n=== DATEN CHECK ===")
    
    # Füge parent directory zum Path hinzu (wie im Original)
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent_dir)
    
    try:
        from src.config import DF_MDB_PATH, DF_MDB_WP_PATH
        
        if os.path.exists(DF_MDB_PATH):
            print(f"✓ {DF_MDB_PATH} existiert")
        else:
            print(f"✗ {DF_MDB_PATH} fehlt!")
            
        if os.path.exists(DF_MDB_WP_PATH):
            print(f"✓ {DF_MDB_WP_PATH} existiert")
        else:
            print(f"✗ {DF_MDB_WP_PATH} fehlt!")
            
    except Exception as e:
        print(f"✗ Fehler beim Laden der Config: {e}")

def test_dashboard_import():
    """Versuche das Dashboard-Modul zu importieren"""
    print("\n=== DASHBOARD IMPORT TEST ===")
    
    try:
        # Simuliere die Imports aus dem Dashboard
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, parent_dir)
        
        from src.config import LIST_OF_COLORS, PAGE_SIZE, COLUMNS_FOR_DISPLAY
        from src.visualization import select_vis_data, compute_traces
        from src.mapping_values import get_color_for_party, get_color_for_age_group, get_color_palette
        
        print("✓ Alle Dashboard-Imports erfolgreich")
        
    except Exception as e:
        print(f"✗ Fehler beim Dashboard-Import: {e}")
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    check_environment()
    check_imports()
    test_data_files()
    test_dashboard_import()
    
    print("\n=== EMPFEHLUNGEN ===")
    print("1. Stellen Sie sicher, dass alle Dateien in src/ existieren")
    print("2. Prüfen Sie, ob die CSV-Dateien am richtigen Ort liegen")
    print("3. Testen Sie das Dashboard mit: python3 dashboard/abgeordneten-dashboard.py")