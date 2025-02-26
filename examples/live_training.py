import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.visualization.dashboard import TradingDashboard
from src.genetic.evolution import EvolutionEngine
from src.evaluation.evaluator import StrategyEvaluator
from src.config.config import GeneticConfig
import pandas as pd

def run_live_training():
    # Cargar datos
    data = pd.read_csv('/workspaces/codespaces-blank/data/historical_data.csv')
    
    # Preparar datos
    train_size = int(len(data) * 0.8)
    train_data = data[:train_size]
    test_data = data[train_size:]
    
    # Configurar dashboard
    dashboard = TradingDashboard()
    dashboard.create_layout()
    
    # Configurar entrenamiento
    config = GeneticConfig()
    evaluator = StrategyEvaluator(train_data, test_data)
    evolution = EvolutionEngine(config, evaluator)
    
    # Iniciar dashboard
    dash_generator = dashboard.show()
    next(dash_generator)
    
    try:
        # Entrenar con actualización en tiempo real
        for gen in range(config.generations):
            # Ejecutar una generación
            best_agent, fitness_history = evolution.evolve_one_generation()
            
            # Actualizar dashboard
            dashboard.update_metrics(
                generation=gen,
                best_fitness=best_agent.fitness,
                avg_fitness=sum(a.fitness for a in evolution.population)/len(evolution.population),
                best_agent_metrics=best_agent.train_metrics
            )
            
            dashboard.update_charts(
                fitness_history=evolution.best_fitness_history,
                trade_history=best_agent.trade_history if hasattr(best_agent, 'trade_history') else []
            )
            
            # Actualizar estado
            if gen % 5 == 0:
                dashboard.update_status(
                    f"Entrenando generación {gen}/{config.generations}...",
                    style="green"
                )
            
            time.sleep(0.1)  # Para visualización
            
    except KeyboardInterrupt:
        dashboard.update_status("Entrenamiento interrumpido por el usuario", style="yellow")
        time.sleep(2)

if __name__ == "__main__":
    run_live_training()
