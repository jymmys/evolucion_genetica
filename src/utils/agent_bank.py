from pathlib import Path
import json
from typing import List, Dict
from rich.console import Console
from rich.table import Table
from src.genetic.agent import TradingAgent

console = Console()

class AgentBank:
    def __init__(self, base_path: str = "agents"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        self.metadata_file = self.base_path / "metadata.json"
        self.load_metadata()
    
    def load_metadata(self):
        if self.metadata_file.exists():
            with open(self.metadata_file) as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {"agents": {}}
    
    def save_agent(self, agent: TradingAgent, generation: int, metrics: Dict):
        # Crear directorio para la generación
        gen_dir = self.base_path / f"generation_{generation}"
        gen_dir.mkdir(exist_ok=True)
        
        # Guardar agente
        agent_id = f"AG-{generation:04d}-{len(self.metadata['agents']):04d}"
        agent_path = gen_dir / f"{agent_id}.pkl"
        agent.save(str(agent_path))
        
        # Actualizar metadata
        self.metadata["agents"][agent_id] = {
            "generation": generation,
            "path": str(agent_path),
            "metrics": metrics,
            "indicators": agent.indicators
        }
        
        # Guardar metadata
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
        
        return agent_id
    
    def get_best_agents(self, n: int = 10, metric: str = "sharpe_ratio") -> List[Dict]:
        agents = list(self.metadata["agents"].items())
        return sorted(
            agents,
            key=lambda x: x[1]["metrics"][metric],
            reverse=True
        )[:n]
    
    def display_agent_stats(self, agent_id: str):
        if agent_id not in self.metadata["agents"]:
            console.print(f"[red]Agente {agent_id} no encontrado[/red]")
            return
            
        agent_data = self.metadata["agents"][agent_id]
        table = Table(title=f"Estadísticas del Agente {agent_id}")
        table.add_column("Métrica", style="cyan")
        table.add_column("Valor", justify="right", style="green")
        
        for metric, value in agent_data["metrics"].items():
            table.add_row(metric, f"{value:.4f}")
            
        console.print(table)
