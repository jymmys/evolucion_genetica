import multiprocessing
from typing import List, Callable
from ..genetic.agent import TradingAgent

def parallel_evaluate(agents: List[TradingAgent], 
                     eval_func: Callable,
                     n_jobs: int = None) -> List[float]:
    if n_jobs is None:
        n_jobs = max(1, multiprocessing.cpu_count() - 2)
    
    with multiprocessing.Pool(n_jobs) as pool:
        return pool.map(eval_func, agents)

def evaluate_agent(agent: TradingAgent) -> float:
    # Implementar evaluación de agente individual
    return agent.fitness
