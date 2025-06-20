# Trading Bot MT5

Un bot de trading modular para MetaTrader 5 con soporte para estrategias, indicadores y simulación.

## Estructura del Proyecto

```
trading_bot_mt5/
├── bot.py               # Interfaz principal
├── log.py              # Sistema de logging
├── config.py          # Gestión de configuración
├── config.json        # Configuración por defecto
├── estilos.py        # Estilos de la UI
├── conexion/         # Conexión a MT5
├── estrategias/      # Estrategias de trading
├── indicadores/      # Indicadores técnicos
├── backtesting/      # Sistema de backtesting
├── modelo_ia/       # Modelos de IA
├── utils/           # Funciones utilitarias
└── README.md        # Documentación
```

## Características

- Interfaz gráfica moderna
- Sistema de logging robusto
- Gestión de configuración
- Modo simulación
- Soporte para múltiples estrategias
- Sistema de indicadores
- Backtesting
- Integración de IA

## Requisitos

- Python 3.8+
- MetaTrader 5
- pandas
- numpy
- scikit-learn
- joblib

## Instalación

1. Clonar el repositorio:
```bash
git clone [URL_DEL_REPOSITORIO]
```

2. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Configuración

La configuración se maneja a través de `config.json`:

```json
{
    "par_defecto": "EURUSD",
    "timeframe": "M5",
    "estrategia": "Estrategia Base",
    "lote_minimo": 0.01,
    "stop_loss": 50,
    "take_profit": 100,
    "modo_simulacion": false
}
```

## Uso

1. Ejecutar el bot:
```bash
python bot.py
```

2. Conectarse a MT5:
   - Click en "Conectar"
   - Seleccionar par de divisas
   - Seleccionar estrategia
   - Iniciar el bot

## Logging

El sistema utiliza un sistema de logging robusto que:
- Registra todos los eventos importantes
- Muestra mensajes en consola y archivo
- Diferencia entre info, warning y error
- Mantiene un archivo de log por día

## Manejo de Errores

El bot incluye:
- Manejo de errores robusto
- Validación de estados
- Mensajes de error informativos
- Recuperación automática cuando es posible

## Contribución

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add some amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## Licencia

MIT
