
# 🚀 Creación y Optimización Genética de un Agente de Trading

## 📌 Introducción

La implementación de la funcionalidad **evolucion genetica** se basa en el uso de **Entrenamiento Genético para Aprendizaje por Refuerzo (RL-GA)** en un entorno de trading. El objetivo es generar, evaluar y optimizar estrategias de trading de manera automatizada mediante la evolución de estrategias a través de selección, mutación y recombinación de parámetros. 🧬💡

---

## 🔥 Proceso de Construcción y Optimización Genética

### ⚙️ Pasos del Proceso

1. **🎯 Generación de Estrategias Iniciales**
   - Se crea una población inicial de estrategias de trading basadas en reglas aleatorias o configuraciones predefinidas.
2. **📊 Evaluación de Estrategias  ***Multiple Seleccion
   - Cada estrategia es evaluada según:
     - 📌 **Profit Factor** ✅ ≥ 1
     - 📌 **Trade Mínimo** ✅ ≥ 100
     - 📌 **Máximo DD** ✅ ≥ 10%
     - 📌 **Shape Ratio** ✅ ≥ 0.98
3. **🏆 Selección Natural**
   - Se eligen las mejores estrategias utilizando:
     - 🎲 Selección por torneo.
     - 📈 Selección por ranking.
     - 📊 Selección proporcional al rendimiento.
4. **🧬 Operadores Genéticos**
   - 🔀 **Cruzamiento (Crossover):** Combinación de características de dos estrategias.
   - 🎲 **Mutación:** Modificación aleatoria de parámetros para introducir variabilidad.
   - 🔄 **Reemplazo:** Sustitución de estrategias menos efectivas por nuevas versiones optimizadas.
5. **📈 Implementa indicadores tecnicos para Ninja traders 8**
   - El proceso incluye minimo 4 indicadores maximo 8 indicadores en un ciclo Ramdon para mejores probalidades "ADL, ADX, ADXR, APZ, Aroon, AroonOscillator, ATR, BarTimer, BlockVolume, Bollinger, BOP, BuySellPressure, BuySellVolume, CamarillaPivots, CandleStickPattern, CCI, ChaikinMoneyFlow, ChaikinOscillator, ChaikinVolatility, ChoppinessIndex, CMO, ConstantLines, Correlation, COT, CurrentDayOHL, Darvas, DEMA, DisparityIndex, DM, DMIndex, DMIndecs, DonchianChannel, DoubleStochastics, EaseOfMovement, EMA, FibonacciPivots, FisherTransform, FOSC, HMA, KAMA, KeltnerChannel, KeyReversalDown, KeyReversalUp, LinReg, LinRegIntercept, LinRegSlope, MAEnvelopes, MAX, McClellanOscillator, MFI, MIN, Momentum, MoneyFlowOscillator, MovingAverageRibbon, NBarsDown, NBarsUp, OBV, ParabolicSAR, PFE, Pivots, PPO, PriceLine, PriceOscillator, PriorDayOHLC, PsychologicalLine, Range, RangeCounter, RegressionChannel, RelativeVigorIndex, RIND, ROC, RSI, RSquared, RSS, RVI, SMA, StdDev, StdError, Stochastics, StochasticsFast, StochRSI, SUM, Swings, T3, TEMA, TickCounter, TMA, TrendLines, TRIX, TSF, TSI, UltimateOscillator, VMA, VOL, VOLMA, VolumeCounter, VolumeOscillator, VolumeProfile, VolumeUpDown, VolumeZones, Vortex, VROC, VWMA, WilliamsR, WMA, ZigZag, ZLEMA"
6. **♻️ Repetición del Ciclo**
   - El proceso se repite durante varias generaciones hasta alcanzar una estrategia óptima según los parámetros establecidos.

---

## 🛠️ Configuración del Modo de Test

- 📌 **Generaciones:** 10
- 📌 **Tamaño de Población:** 5
- 📌 **Probabilidad de Crossover:** 90% (mezcla de hiperparámetros exitosos)
- 📌 **Probabilidad de Mutación:** 25% (para explorar nuevas soluciones)
- 📌 **Islas Evolutivas:** 3 (múltiples entornos de entrenamiento)
- 📌 **Frecuencia de Migración:** Cada 60 generaciones
- 📌 **Tasa de Migración:** 15% de la población
- 📌 **Coeficiente de Decimación:** 1 (generar más modelos y seleccionar los mejores)
- 📌 **Fresh Blood:** Reemplazo del 15% de los peores modelos cada 3 generaciones
- 📌 **Restart Evolution:** Si el *fitness* no mejora en 20 generaciones

---

## 🤖 Instrucciones para el Agente

### ⚡ **Frameworks **
- 🚀 Implementación en **Python*
- 🏆 DEAP para optimización genética

### 🖥️ **Ejecución completamente por consola:**
- 🎛️ Configuración y ajustes mediante un menú interactivo.
- 📂 Soporte para archivos de configuración **INI o JSON**.

### 🔄 **Automatización y Flujos de Trabajo:**
- 🚀 Ejecución de múltiples configuraciones con un solo comando.
- ⚙️ Soporte para **parámetros de línea de comandos** para personalización avanzada.

---

## 🎯 Creación de un Banco de Agentes

💾 **Generaremos unacarpeta para guardar  el numero de agentes entrenados previamente introducir una variable de cuanto queremos el banco de agentes.
📌 Posteriormente, aplicaremos criterios más estrictos para seleccionar los mejores modelos y optimizar nuestras estrategias de trading de manera eficiente y automática.