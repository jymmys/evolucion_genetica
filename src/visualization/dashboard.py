import numpy as np
import pandas as pd
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich.console import Console
from rich.console import Group
from datetime import datetime
import matplotlib.pyplot as plt
from io import StringIO
import pickle
import threading
import queue
import time

class TradingDashboard:
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        self.metrics_history = []
        self.best_agents_history = []
        self.paused = False
        self.command_queue = queue.Queue()
        self.is_running = True
        
    def create_layout(self):
        """Crea el layout del dashboard"""
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="main", size=15),
            Layout(name="footer", size=5)
        )
        
        self.layout["main"].split_row(
            Layout(name="metrics", ratio=2),
            Layout(name="charts", ratio=3)
        )
        
        self.layout["footer"].split_row(
            Layout(name="controls", ratio=2),
            Layout(name="status", ratio=3)
        )
    
    def update_metrics(self, generation: int, best_fitness: float, avg_fitness: float, 
                      best_agent_metrics: dict):
        """Actualiza las métricas en tiempo real"""
        metrics_panel = Table.grid()
        metrics_panel.add_column(style="cyan", justify="right")
        metrics_panel.add_column(style="green")
        
        # Métricas de Evolución
        metrics_panel.add_row("Generación:", f"{generation}")
        metrics_panel.add_row("Mejor Fitness:", f"{best_fitness:.4f}")
        metrics_panel.add_row("Fitness Promedio:", f"{avg_fitness:.4f}")
        
        # Métricas de Trading
        metrics_panel.add_row("Profit Factor:", f"{best_agent_metrics.get('profit_factor', 0):.2f}")
        metrics_panel.add_row("Sharpe Ratio:", f"{best_agent_metrics.get('sharpe_ratio', 0):.2f}")
        metrics_panel.add_row("Drawdown Máximo:", f"{best_agent_metrics.get('max_drawdown', 0):.2%}")
        metrics_panel.add_row("Win Rate:", f"{best_agent_metrics.get('win_rate', 0):.2%}")
        metrics_panel.add_row("Trades Totales:", f"{best_agent_metrics.get('total_trades', 0)}")
        metrics_panel.add_row("Expectancy:", f"{best_agent_metrics.get('expectancy', 0):.4f}")
        
        self.layout["metrics"].update(
            Panel(metrics_panel, title="Métricas de Trading", border_style="blue")
        )
    
    def update_charts(self, fitness_history: list, trade_history: list):
        """Actualiza los gráficos de evolución"""
        chart = self._create_ascii_chart(fitness_history[-30:] if len(fitness_history) > 30 else fitness_history)
        self.layout["charts"].update(
            Panel(chart, title="Evolución del Fitness", border_style="green")
        )
    
    def _create_ascii_chart(self, data: list, width: int = 50, height: int = 10) -> str:
        """Crea un gráfico ASCII simple"""
        if not data:
            return "No hay datos suficientes"
            
        # Normalizar datos
        min_val = min(data)
        max_val = max(data)
        range_val = max_val - min_val if max_val != min_val else 1
        normalized = [(x - min_val) / range_val for x in data]
        
        # Crear gráfico
        chars = '▁▂▃▄▅▆▇█'
        chart = []
        for val in normalized:
            idx = int(val * (len(chars) - 1))
            chart.append(chars[idx])
            
        return ''.join(chart)
    
    def update_status(self, message: str, style: str = "white"):
        """Actualiza el mensaje de estado"""
        self.layout["status"].update(
            Panel(message, title="Estado", border_style=style)
        )
    
    def update_controls(self):
        """Actualiza panel de controles"""
        controls_table = Table.grid()
        controls_table.add_column(style="cyan")
        
        status = "PAUSADO" if self.paused else "EJECUTANDO"
        controls_table.add_row("Estado:", f"[{'yellow' if self.paused else 'green'}]{status}")
        controls_table.add_row("Comandos:")
        controls_table.add_row("p - Pausar/Reanudar")
        controls_table.add_row("s - Guardar estado")
        controls_table.add_row("q - Cerrar Dashboard")
        
        self.layout["controls"].update(
            Panel(controls_table, title="Controles", border_style="blue")
        )
    
    def save_state(self, filename: str = "dashboard_state.pkl"):
        """Guarda el estado actual del dashboard"""
        state = {
            'metrics_history': self.metrics_history,
            'best_agents_history': self.best_agents_history
        }
        with open(filename, 'wb') as f:
            pickle.dump(state, f)
        return f"Estado guardado en {filename}"
    
    def load_state(self, filename: str = "dashboard_state.pkl"):
        """Carga un estado guardado"""
        with open(filename, 'rb') as f:
            state = pickle.load(f)
        self.metrics_history = state['metrics_history']
        self.best_agents_history = state['best_agents_history']
    
    def handle_input(self):
        """Maneja la entrada de comandos"""
        while self.is_running:
            try:
                cmd = input().lower()
                self.command_queue.put(cmd)
            except EOFError:
                break
    
    def process_commands(self):
        """Procesa los comandos en la cola"""
        while not self.command_queue.empty():
            cmd = self.command_queue.get()
            if cmd == 'p':
                self.paused = not self.paused
            elif cmd == 's':
                msg = self.save_state()
                self.update_status(msg, "yellow")
            elif cmd == 'q':
                self.is_running = False
    
    def show(self):
        """Muestra el dashboard"""
        input_thread = threading.Thread(target=self.handle_input, daemon=True)
        input_thread.start()
        
        with Live(self.layout, refresh_per_second=4, screen=True) as live:
            while self.is_running:
                self.process_commands()
                self.update_controls()
                live.update(self.layout)
                
                if not self.paused:
                    yield
                else:
                    time.sleep(0.1)
            
            self.update_status("Dashboard cerrado. El programa continúa ejecutándose...", "yellow")
            live.update(self.layout)
            time.sleep(2)
