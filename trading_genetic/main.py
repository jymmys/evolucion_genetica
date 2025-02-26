import argparse
import json
import multiprocessing
from pathlib import Path
import sys

# Configurar PYTHONPATH
root_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, root_dir)

from trading_genetic.genetic.agent import TradingAgent
from trading_genetic.config.config import GeneticConfig, FitnessCriteria
from trading_genetic.indicators.technical import AVAILABLE_INDICATORS

def show_menu():
    print("1. Entrenar agentes")
    print("2. Salir")
    return input("Seleccione una opción: ")

def train_agents(config: GeneticConfig, output_path: str):
    print(f"Entrenando agentes con la configuración: {config}")
    print(f"Guardando resultados en: {output_path}")
    # Implementar la lógica de entrenamiento de agentes

def main():
    parser = argparse.ArgumentParser(description="Sistema de Trading Genético")
    parser.add_argument('--config', type=str, required=True, help="Archivo de configuración JSON")
    parser.add_argument('--output', type=str, required=True, help="Directorio de salida para los resultados")
    parser.add_argument('--mode', type=str, required=True, choices=['train', 'test'], help="Modo de operación: train o test")
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config_data = json.load(f)

    config = GeneticConfig(**config_data['genetic_algorithm'])
    fitness_criteria = FitnessCriteria(**config_data['fitness_criteria'])

    if args.mode == 'train':
        train_agents(config, args.output)
    else:
        print("Modo de operación no soportado")

if __name__ == '__main__':
    main()