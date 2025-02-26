from typing import List
import random
from trading_genetic.genetic.agent import TradingAgent  # Importación absoluta
from trading_genetic.config.config import GeneticConfig  # Importación absoluta
from trading_genetic.indicators.technical import AVAILABLE_INDICATORS  # Importación absoluta

class EvolutionaryIsland:
    def __init__(self, config: GeneticConfig, population: List[TradingAgent]):
        self.config = config
        self.population = population
        self.generation = 0
        self.best_fitness = float('-inf')
        self.generations_without_improvement = 0

    def evolve(self):
        # Selección
        parents = self.select_parents()
        # Crossover y mutación
        new_population = []
        for i in range(0, len(parents), 2):
            if i + 1 < len(parents):
                child1, child2 = parents[i].crossover(parents[i+1], self.config.crossover_prob)
                child1.mutate(self.config.mutation_prob)
                child2.mutate(self.config.mutation_prob)
                new_population.extend([child1, child2])
        # Fresh blood
        if self.generation % self.config.fresh_blood_frequency == 0:
            self.inject_fresh_blood(new_population)
        self.population = new_population
        self.generation += 1

    def select_parents(self) -> List[TradingAgent]:
        # Implementar selección por torneo
        tournament_size = 3
        selected = []
        for _ in range(len(self.population)):
            tournament = random.sample(self.population, tournament_size)
            winner = max(tournament, key=lambda x: x.fitness)
            selected.append(winner)
        return selected

    def inject_fresh_blood(self, population: List[TradingAgent]):
        num_fresh = int(len(population) * self.config.fresh_blood_rate)
        population[-num_fresh:] = [TradingAgent(AVAILABLE_INDICATORS) for _ in range(num_fresh)]