#!/bin/bash

# Instalar dependencias del sistema para TA-Lib
echo "Instalando dependencias del sistema..."
sudo apt-get update
sudo apt-get install -y build-essential wget pkg-config

# Instalar TA-Lib desde el código fuente
echo "Instalando TA-Lib..."
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
cd ..
rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Verificar la instalación de TA-Lib
sudo ldconfig
pkg-config --libs ta-lib

# Crear y activar entorno virtual
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python -m venv venv
fi

source venv/bin/activate

# Actualizar pip e instalar dependencias en orden específico
echo "Actualizando pip e instalando dependencias..."
pip install --upgrade pip wheel setuptools
pip install numpy  # Instalar numpy primero
pip install Cython  # Necesario para algunos paquetes
export TA_LIBRARY_PATH="/usr/lib"
export TA_INCLUDE_PATH="/usr/include"
pip install ta-lib  # Instalar TA-Lib con las variables de entorno configuradas

# Instalar el resto de dependencias
pip install -r requirements.txt

# Crear directorios necesarios
mkdir -p results agents/generation_1

# Limpiar caché de Python
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Configurar PYTHONPATH
export PYTHONPATH="/workspaces/codespaces-blank"

# Ejecutar el sistema
python src/main.py --mode train --output results/ --config config.json
