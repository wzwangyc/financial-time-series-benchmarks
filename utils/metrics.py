# -*- coding: utf-8 -*-
"""
Metrics Collection

Business Intent:
    Track system performance and business metrics.
    Enable real-time monitoring and alerting.
    All metrics must be measurable and actionable.

Design Boundaries:
    - Counter: Monotonically increasing values
    - Gauge: Current values that can go up/down
    - Histogram: Distribution of values
    - All metrics must have labels for filtering

Applicable Scenarios:
    - Trade execution tracking
    - Model performance tracking
    - System performance monitoring
    - Business metric tracking
"""

from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json


@dataclass
class MetricPoint:
    """
    Single metric data point.
    
    Business Intent:
        Store metric value with timestamp and labels.
        All metrics must be timestamped and labeled.
    """
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    value: float = 0.0
    labels: Dict[str, str] = field(default_factory=dict)


class Counter:
    """
    Counter metric (monotonically increasing).
    
    Business Intent:
        Track cumulative counts (trades, errors, etc.).
        Value can only increase.
    
    Usage:
        >>> trade_counter = Counter('trades_total', 'Total number of trades')
        >>> trade_counter.inc()
        >>> trade_counter.inc(5)
        >>> value = trade_counter.get()
    """
    
    def __init__(self, name: str, description: str, labels: Optional[List[str]] = None):
        self.name = name
        self.description = description
        self.labels = labels or []
        self._value = 0
        self._history: List[MetricPoint] = []
    
    def inc(self, amount: float = 1.0, **labels) -> None:
        """Increment counter"""
        if amount < 0:
            raise ValueError("Counter can only increase")
        
        self._value += amount
        self._history.append(MetricPoint(value=self._value, labels=labels))
    
    def get(self) -> float:
        """Get current value"""
        return self._value
    
    def reset(self) -> None:
        """Reset counter"""
        self._value = 0


class Gauge:
    """
    Gauge metric (can go up and down).
    
    Business Intent:
        Track current values (PnL, latency, etc.).
        Value can increase or decrease.
    
    Usage:
        >>> pnl_gauge = Gauge('pnl', 'Current PnL')
        >>> pnl_gauge.set(1000.0)
        >>> pnl_gauge.set(-500.0)  # Can go negative
        >>> value = pnl_gauge.get()
    """
    
    def __init__(self, name: str, description: str, labels: Optional[List[str]] = None):
        self.name = name
        self.description = description
        self.labels = labels or []
        self._value = 0.0
        self._history: List[MetricPoint] = []
    
    def set(self, value: float, **labels) -> None:
        """Set gauge value"""
        self._value = value
        self._history.append(MetricPoint(value=self._value, labels=labels))
    
    def inc(self, amount: float = 1.0) -> None:
        """Increment gauge"""
        self._value += amount
        self._history.append(MetricPoint(value=self._value))
    
    def dec(self, amount: float = 1.0) -> None:
        """Decrement gauge"""
        self._value -= amount
        self._history.append(MetricPoint(value=self._value))
    
    def get(self) -> float:
        """Get current value"""
        return self._value


class Histogram:
    """
    Histogram metric (distribution of values).
    
    Business Intent:
        Track value distributions (latency, returns, etc.).
        Calculate percentiles and statistics.
    
    Usage:
        >>> latency_hist = Histogram('latency', 'Request latency')
        >>> latency_hist.observe(0.05)
        >>> latency_hist.observe(0.10)
        >>> percentiles = latency_hist.get_percentiles()
    """
    
    def __init__(self, name: str, description: str, labels: Optional[List[str]] = None):
        self.name = name
        self.description = description
        self.labels = labels or []
        self._values: List[float] = []
        self._count = 0
        self._sum = 0.0
    
    def observe(self, value: float, **labels) -> None:
        """Observe a value"""
        self._values.append(value)
        self._count += 1
        self._sum += value
    
    def get_count(self) -> int:
        """Get observation count"""
        return self._count
    
    def get_sum(self) -> float:
        """Get sum of observations"""
        return self._sum
    
    def get_average(self) -> float:
        """Get average value"""
        if self._count == 0:
            return 0.0
        return self._sum / self._count
    
    def get_percentiles(self, percentiles: List[float] = None) -> Dict[float, float]:
        """
        Get percentile values.
        
        Args:
            percentiles: List of percentiles to calculate (default: [50, 90, 95, 99])
        
        Returns:
            Dictionary of percentile -> value
        """
        if percentiles is None:
            percentiles = [50, 90, 95, 99]
        
        if not self._values:
            return {p: 0.0 for p in percentiles}
        
        sorted_values = sorted(self._values)
        result = {}
        
        for p in percentiles:
            k = (len(sorted_values) - 1) * (p / 100)
            f = int(k)
            c = f + 1 if f + 1 < len(sorted_values) else f
            
            if f == c:
                result[p] = sorted_values[f]
            else:
                result[p] = (sorted_values[f] * (c - k)) + (sorted_values[c] * (k - f))
        
        return result
    
    def reset(self) -> None:
        """Reset histogram"""
        self._values = []
        self._count = 0
        self._sum = 0.0


class MetricsRegistry:
    """
    Central registry for all metrics.
    
    Business Intent:
        Centralized metric management.
        Export metrics for monitoring systems.
    
    Usage:
        >>> registry = MetricsRegistry()
        >>> counter = registry.counter('trades', 'Total trades')
        >>> counter.inc()
        >>> metrics = registry.export()
    """
    
    def __init__(self):
        self._counters: Dict[str, Counter] = {}
        self._gauges: Dict[str, Gauge] = {}
        self._histograms: Dict[str, Histogram] = {}
    
    def counter(self, name: str, description: str, labels: Optional[List[str]] = None) -> Counter:
        """Get or create counter"""
        if name not in self._counters:
            self._counters[name] = Counter(name, description, labels)
        return self._counters[name]
    
    def gauge(self, name: str, description: str, labels: Optional[List[str]] = None) -> Gauge:
        """Get or create gauge"""
        if name not in self._gauges:
            self._gauges[name] = Gauge(name, description, labels)
        return self._gauges[name]
    
    def histogram(self, name: str, description: str, labels: Optional[List[str]] = None) -> Histogram:
        """Get or create histogram"""
        if name not in self._histograms:
            self._histograms[name] = Histogram(name, description, labels)
        return self._histograms[name]
    
    def export(self) -> Dict[str, any]:
        """
        Export all metrics.
        
        Returns:
            Dictionary of all metrics
            
        Usage:
            >>> metrics = registry.export()
            >>> print(json.dumps(metrics, indent=2))
        """
        return {
            'counters': {name: counter.get() for name, counter in self._counters.items()},
            'gauges': {name: gauge.get() for name, gauge in self._gauges.items()},
            'histograms': {
                name: {
                    'count': hist.get_count(),
                    'sum': hist.get_sum(),
                    'avg': hist.get_average(),
                    'percentiles': hist.get_percentiles(),
                }
                for name, hist in self._histograms.items()
            },
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }


# Global registry instance
_registry = None


def get_registry() -> MetricsRegistry:
    """
    Get global metrics registry.
    
    Business Intent:
        Single registry instance for consistent metrics.
        Lazy initialization.
    
    Returns:
        Global metrics registry
    """
    global _registry
    if _registry is None:
        _registry = MetricsRegistry()
    return _registry


# Convenience functions

def track_trade(strategy: str, symbol: str, pnl: float) -> None:
    """
    Track trade execution.
    
    Business Intent:
        Full observability for all trades.
        Enable real-time monitoring and alerting.
    
    Args:
        strategy: Strategy name
        symbol: Trading symbol
        pnl: Trade PnL
    
    Usage:
        >>> track_trade('momentum', 'AAPL', 1000.0)
    """
    registry = get_registry()
    
    # Track trade count
    trades_counter = registry.counter('trade_executions_total', 'Total number of trades', ['strategy', 'symbol'])
    trades_counter.inc(strategy=strategy, symbol=symbol)
    
    # Track PnL
    pnl_gauge = registry.gauge('trade_pnl', 'Trade PnL', ['strategy', 'symbol'])
    pnl_gauge.set(pnl, strategy=strategy, symbol=symbol)


def track_model_prediction(model: str, accuracy: float) -> None:
    """
    Track model prediction accuracy.
    
    Business Intent:
        Monitor model performance over time.
        Alert on performance degradation.
    
    Args:
        model: Model name
        accuracy: Prediction accuracy
    
    Usage:
        >>> track_model_prediction('arima', 0.85)
    """
    registry = get_registry()
    
    # Track accuracy
    accuracy_hist = registry.histogram('model_accuracy', 'Model prediction accuracy', ['model'])
    accuracy_hist.observe(accuracy, model=model)


def track_system_latency(operation: str, latency_ms: float) -> None:
    """
    Track system latency.
    
    Business Intent:
        Monitor system performance.
        Alert on high latency.
    
    Args:
        operation: Operation name
        latency_ms: Latency in milliseconds
    
    Usage:
        >>> track_system_latency('backtest', 150.0)
    """
    registry = get_registry()
    
    # Track latency
    latency_hist = registry.histogram('system_latency_ms', 'System latency in ms', ['operation'])
    latency_hist.observe(latency_ms, operation=operation)
