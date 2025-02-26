from typing import List, Tuple, Dict
import numpy as np
import random
from rich.console import Console
from rich.progress import track
from ..evaluation.evaluator import StrategyEvaluator
from .agent import TradingAgent

console = Console()

class EvolutionEngine:
    def __init__(self, config, evaluator: StrategyEvaluator):
        self.config = config
        self.evaluator = evaluator
        self.generation = 0
        self.best_fitness_history = []
        self.population = []
        self.initialize_population()

    def initialize_population(self):
        """Inicializa la población con agentes aleatorios"""
        self.population = [TradingAgent() for _ in range(self.config.population_size)]
        
    def evolve(self) -> Tuple[TradingAgent, List[float]]:
        """Ejecuta el proceso evolutivo completo"""
        self.initialize_population()
        best_agent = None
        stagnation_counter = 0
        
        for gen in track(range(self.config.generations), description="Evolucionando..."):
            self.generation = gen
            
            # Evaluar población
            fitness_values = self.evaluator.evaluate_population(self.population)
            
            # Actualizar mejor agente
            current_best = max(self.population, key=lambda x: x.fitness)
            if best_agent is None or current_best.fitness > best_agent.fitness:
                best_agent = current_best.clone()
                stagnation_counter = 0
            else:
                stagnation_counter += 1
            
            # Verificar estancamiento
            if stagnation_counter >= self.config.restart_threshold:
                console.print("[yellow]Evolución estancada. Reiniciando población...[/yellow]")
                self._restart_population(best_agent)
                stagnation_counter = 0
            
            # Crear nueva generación
            self.population = self._create_next_generation()
            
            # Registrar progreso
            self.best_fitness_history.append(current_best.fitness)
            
            # Aplicar fresh blood periódicamente
            if gen % self.config.fresh_blood_frequency == 0:
                self._inject_fresh_blood()
        
        return best_agent, self.best_fitness_history
    
    def evolve_one_generation(self) -> Tuple[TradingAgent, Dict]:
        """Evoluciona la población por una generación"""
        try:
            # Evaluar población actual
            fitness_values = self.evaluator.evaluate_population(self.population)
            
            # Actualizar fitness de cada agente
            for agent, fitness in zip(self.population, fitness_values):
                agent.fitness = fitness
            
            # Ordenar población por fitness
            self.population.sort(key=lambda x: x.fitness, reverse=True)
            
            # Obtener el mejor agente de esta generación
            best_agent = self.population[0].clone()
            
            # Calcular estadísticas de la población
            population_metrics = {
                'avg_fitness': np.mean(fitness_values),
                'max_fitness': np.max(fitness_values),
                'min_fitness': np.min(fitness_values),
                'std_fitness': np.std(fitness_values),
                'generation': self.generation
            }
            
            # Crear nueva generación
            next_generation = []
            
            # Elitismo: mantener los mejores individuos
            elite_count = max(1, int(self.config.population_size * 0.1))
            next_generation.extend(self.population[:elite_count])
            
            # Generar resto de la población
            while len(next_generation) < self.config.population_size:
                # Selección por torneo
                parent1 = self._tournament_select()
                parent2 = self._tournament_select()
                
                # Crossover
                if random.random() < self.config.crossover_prob:
                    child1, child2 = parent1.crossover(parent2, self.config.crossover_prob)
                    
                    # Mutación
                    child1.mutate(self.config.mutation_prob)
                    child2.mutate(self.config.mutation_prob)
                    
                    next_generation.extend([child1, child2])
            
            # Actualizar población
            self.population = next_generation[:self.config.population_size]
            self.generation += 1
            
            # Registrar mejor fitness
            self.best_fitness_history.append(best_agent.fitness)
            
            return best_agent, population_metrics
            
        except Exception as e:
            console.print(f"[red]Error en evolve_one_generation: {str(e)}[/red]")
            raise
    
    def _create_next_generation(self) -> List[TradingAgent]:
        """Crea la siguiente generación usando diversos operadores genéticos"""
        next_gen = []
        
        # Elitismo
        elite_count = max(1, int(len(self.population) * 0.1))
        elite = sorted(self.population, key=lambda x: x.fitness, reverse=True)[:elite_count]
        next_gen.extend(elite)
        
        # Generar resto de la población
        while len(next_gen) < self.config.population_size:
            if random.random() < 0.8:  # 80% crossover
                parent1 = self._tournament_select()
                parent2 = self._tournament_select()
                child1, child2 = parent1.crossover(parent2, self.config.crossover_prob)
                child1.mutate(self.config.mutation_prob)
                child2.mutate(self.config.mutation_prob)
                next_gen.extend([child1, child2])
            else:  # 20% clonación con mutación
                parent = self._tournament_select()
                child = parent.clone()
                child.mutate(self.config.mutation_prob * 2)  # Mutación más agresiva
                next_gen.append(child)
        
        return next_gen[:self.config.population_size]
    
    def _tournament_select(self, k: int = 3) -> TradingAgent:
        """Selección por torneo"""
        tournament = random.sample(self.population, k)
        return max(tournament, key=lambda agent: agent.fitness)
    
    def _inject_fresh_blood(self):
        """Inyecta nuevos individuos aleatorios en la población"""
        num_fresh = int(len(self.population) * self.config.fresh_blood_rate)
        sorted_pop = sorted(self.population, key=lambda x: x.fitness)
        
        # Reemplazar los peores individuos con nuevos
        for i in range(num_fresh):
            sorted_pop[i] = TradingAgent()
        
        self.population = sorted_pop
    
    def _restart_population(self, best_agent: TradingAgent):
        """Reinicia la población manteniendo el mejor agente"""
        self.population = [TradingAgent() for _ in range(self.config.population_size - 1)]
        self.population.append(best_agent.clone())
        random.shuffle(self.population)
