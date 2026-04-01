# Financial Time Series Benchmarks

**Enterprise-grade financial time series forecasting library**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

---

## Features

- **Baseline Models**: Random Walk, ARIMA, ETS
- **Evaluation Metrics**: Sharpe, MaxDD, Win Rate, etc.
- **Backtest Framework**: Realistic transaction costs
- **Observability**: Logging, metrics, alerting
- **Reproducibility**: Seed management

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Quick Start

```python
from data.loader import load_stock_data
from models.baseline.naive import RandomWalk
from evaluation.backtest import Backtest

# Load data
df = load_stock_data('AAPL', start='2023-01-01', end='2023-12-31')

# Train model
model = RandomWalk()
model.fit(df['Close'])

# Predict
predictions = model.predict(steps=10)

# Backtest
backtest = Backtest()
results = backtest.run(df['Close'], predictions)

print(f"Sharpe: {results['metrics']['sharpe']:.2f}")
```

---

## Documentation

- **README_CN.md**: Chinese documentation
- **QUICK_START_GUIDE.md**: Quick start guide

---

## License

MIT License
