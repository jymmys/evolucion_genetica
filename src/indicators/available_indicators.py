import random

NINJATRADER_INDICATORS = [
    # Tendencia
    "ADX", "ADXR", "APZ", "DEMA", "EMA", "HMA", "KAMA", "MA", "TEMA", "TRIX", "TSMA", "WMA",
    # Momentum
    "RSI", "CCI", "CMO", "DPO", "MACD", "MFI", "MOM", "ROC", "RSI", "STOCH", "StochRSI", "UO", "WillR",
    # Volatilidad
    "ATR", "BBANDS", "DC", "KC", "STARC", "VWAP",
    # Volumen
    "ADL", "CHAIKIN", "OBV", "PVT", "VWMA",
    # Precio
    "HLC3", "MEDPRICE", "OHLC4", "PIVOTS", "TYPICAL"
]

def get_random_indicators(min_count: int = 4, max_count: int = 8) -> list:
    """
    Selecciona un número aleatorio de indicadores entre min_count y max_count.
    Asegura una mezcla balanceada de diferentes tipos de indicadores.
    """
    num_indicators = random.randint(min_count, max_count)
    
    # Asegurar al menos un indicador de cada categoría importante
    essential_indicators = [
        random.choice(["EMA", "SMA", "WMA"]),  # Tendencia
        random.choice(["RSI", "MACD", "MOM"]),  # Momentum
        random.choice(["BBANDS", "ATR"]),       # Volatilidad
        random.choice(["OBV", "VWMA"])         # Volumen
    ]
    
    # Completar con indicadores aleatorios
    remaining_count = num_indicators - len(essential_indicators)
    if remaining_count > 0:
        additional_indicators = random.sample(
            [i for i in NINJATRADER_INDICATORS if i not in essential_indicators],
            remaining_count
        )
        selected_indicators = essential_indicators + additional_indicators
    else:
        selected_indicators = essential_indicators[:num_indicators]
    
    random.shuffle(selected_indicators)
    return selected_indicators
