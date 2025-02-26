#!/bin/bash

# Crear estructura de directorios
mkdir -p src/genetic src/config src/indicators results agents/generation_1

# Crear archivos __init__.py necesarios
touch src/__init__.py
touch src/genetic/__init__.py
touch src/config/__init__.py
touch src/indicators/__init__.py

# Instalar dependencias
pip install -r requirements.txt

# Limpiar caché de Python
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Establecer PYTHONPATH
export PYTHONPATH="/workspaces/codespaces-blank"

# Dar permisos de ejecución
chmod +x run.sh
