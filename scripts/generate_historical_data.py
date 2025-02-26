import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_historical_data(start_date: str, days: int, minutes_per_day: int = 1440):
    """
    Genera datos históricos simulados de trading
    start_date: fecha inicial en formato 'YYYYMMDD'
    days: número de días a generar
    minutes_per_day: minutos por día (default 1440 = 24h)
    """
    
    # Crear lista para almacenar los datos
    data = []
    base_price = 15900  # Precio base inicial
    volatility = 0.0003  # Volatilidad del precio
    
    start = datetime.strptime(start_date, '%Y%m%d')
    
    for day in range(days):
        current_date = start + timedelta(days=day)
        current_price = base_price
        
        for minute in range(minutes_per_day):
            current_time = (datetime.min + timedelta(minutes=minute)).strftime('%H:%M:%S')
            
            # Generar precios con movimientos realistas
            price_change = np.random.normal(0, volatility)
            open_price = current_price
            close_price = open_price * (1 + price_change)
            high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, volatility/2)))
            low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, volatility/2)))
            volume = int(np.random.exponential(100))  # Volumen aleatorio
            
            data.append({
                'Date': current_date.strftime('%Y%m%d'),
                'Time': current_time,
                'Open': round(open_price, 2),
                'High': round(high_price, 2),
                'Low': round(low_price, 2),
                'Close': round(close_price, 2),
                'Volume': volume
            })
            
            current_price = close_price
    
    # Convertir a DataFrame
    df = pd.DataFrame(data)
    return df

def main():
    # Generar datos para 30 días
    df = generate_historical_data('20231201', days=30)
    
    # Guardar en CSV
    output_file = '/workspaces/codespaces-blank/data/historical_data.csv'
    
    # Crear directorio si no existe
    import os
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    df.to_csv(output_file, index=False)
    print(f"Datos históricos generados en: {output_file}")
    print("\nPrimeras 5 filas:")
    print(df.head())
    print(f"\nTotal de registros: {len(df)}")

if __name__ == "__main__":
    main()
