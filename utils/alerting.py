# -*- coding: utf-8 -*-
"""
Alerting System

Business Intent:
    Alert on critical risk events and system failures.
    Enable rapid response to production issues.
    All critical events must trigger alerts.

Design Boundaries:
    - Alert levels: INFO, WARNING, ERROR, CRITICAL
    - Alert channels: Console, File, Email (future)
    - Alert throttling to prevent alert fatigue
    - All alerts must be actionable

Applicable Scenarios:
    - Critical risk events (MaxDD exceeded)
    - System failures (API failures, data corruption)
    - Performance degradation (high latency)
    - Business metric thresholds (PnL limits)
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from enum import Enum
import logging
import json
from collections import deque
from datetime import timedelta


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'


class Alert:
    """
    Alert object.
    
    Business Intent:
        Structured alert with all context.
        All alerts must be actionable.
    """
    
    def __init__(
        self,
        message: str,
        level: AlertLevel = AlertLevel.INFO,
        context: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.level = level
        self.context = context or {}
        self.timestamp = datetime.now(timezone.utc)
        self.id = f"alert_{self.timestamp.timestamp()}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'level': self.level.value,
            'message': self.message,
            'context': self.context,
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), ensure_ascii=False)


class AlertManager:
    """
    Alert manager with throttling and routing.
    
    Business Intent:
        Manage all alerts centrally.
        Prevent alert fatigue with throttling.
        Route alerts to appropriate channels.
    
    Usage:
        >>> alert_mgr = AlertManager()
        >>> alert_mgr.send_alert('MaxDD exceeded', AlertLevel.CRITICAL, {'mdd': -0.25})
    """
    
    def __init__(self, throttle_seconds: int = 60):
        """
        Initialize alert manager.
        
        Args:
            throttle_seconds: Minimum seconds between alerts of same type
        """
        self.throttle_seconds = throttle_seconds
        self._last_alerts: Dict[str, datetime] = {}
        self._alert_history: deque = deque(maxlen=1000)
        self._logger = logging.getLogger('ftsb.alerts')
    
    def send_alert(
        self,
        message: str,
        level: AlertLevel = AlertLevel.INFO,
        context: Optional[Dict[str, Any]] = None,
        alert_type: Optional[str] = None
    ) -> Optional[Alert]:
        """
        Send alert with throttling.
        
        Business Intent:
            Alert on critical events.
            Full context for diagnosis.
            Throttle to prevent fatigue.
        
        Args:
            message: Alert message
            level: Alert severity
            context: Additional context
            alert_type: Alert type for throttling (default: message)
        
        Returns:
            Alert object if sent, None if throttled
        
        Usage:
            >>> alert_mgr.send_alert('MaxDD exceeded', AlertLevel.CRITICAL, {'mdd': -0.25})
        """
        alert = Alert(message, level, context)
        alert_type = alert_type or message
        
        # Check throttling
        now = datetime.now(timezone.utc)
        last_alert = self._last_alerts.get(alert_type)
        
        if last_alert and (now - last_alert) < timedelta(seconds=self.throttle_seconds):
            # Throttled
            self._logger.debug(f"Alert throttled: {message}")
            return None
        
        # Update last alert time
        self._last_alerts[alert_type] = now
        
        # Add to history
        self._alert_history.append(alert)
        
        # Log alert
        log_method = getattr(self._logger, level.value.lower(), self._logger.info)
        log_method(f"ALERT [{level.value}]: {message}", extra={
            'alert_id': alert.id,
            'alert_level': level.value,
            'alert_context': context,
        })
        
        return alert
    
    def get_recent_alerts(self, count: int = 100) -> List[Alert]:
        """
        Get recent alerts.
        
        Args:
            count: Number of alerts to return
        
        Returns:
            List of recent alerts
        """
        return list(self._alert_history)[-count:]
    
    def clear_throttle(self, alert_type: Optional[str] = None) -> None:
        """
        Clear throttle for alert type.
        
        Args:
            alert_type: Alert type to clear (default: all)
        """
        if alert_type:
            self._last_alerts.pop(alert_type, None)
        else:
            self._last_alerts.clear()


# Global alert manager instance
_alert_manager = None


def get_alert_manager() -> AlertManager:
    """
    Get global alert manager.
    
    Business Intent:
        Single alert manager for consistent alerting.
        Lazy initialization.
    
    Returns:
        Global alert manager
    """
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager


# Convenience functions

def send_alert(message: str, level: AlertLevel = AlertLevel.INFO, **context) -> Optional[Alert]:
    """
    Send alert with context.
    
    Business Intent:
        Alert on critical events.
        Full context for diagnosis.
    
    Args:
        message: Alert message
        level: Alert severity
        **context: Additional context
    
    Usage:
        >>> send_alert('MaxDD exceeded', AlertLevel.CRITICAL, mdd=-0.25, threshold=-0.20)
    """
    alert_mgr = get_alert_manager()
    return alert_mgr.send_alert(message, level, context)


def send_critical_alert(message: str, **context) -> Optional[Alert]:
    """
    Send critical alert.
    
    Business Intent:
        Alert on critical failures.
        Requires immediate attention.
    
    Args:
        message: Alert message
        **context: Additional context
    
    Usage:
        >>> send_critical_alert('System failure', system='backtest_engine')
    """
    return send_alert(message, AlertLevel.CRITICAL, **context)


def send_warning_alert(message: str, **context) -> Optional[Alert]:
    """
    Send warning alert.
    
    Business Intent:
        Alert on potential issues.
        May require attention.
    
    Args:
        message: Alert message
        **context: Additional context
    
    Usage:
        >>> send_warning_alert('High latency detected', latency_ms=500)
    """
    return send_alert(message, AlertLevel.WARNING, **context)


def send_info_alert(message: str, **context) -> Optional[Alert]:
    """
    Send info alert.
    
    Business Intent:
        Log informational events.
        No action required.
    
    Args:
        message: Alert message
        **context: Additional context
    
    Usage:
        >>> send_info_alert('Backtest completed', trades=100, pnl=1000.0)
    """
    return send_alert(message, AlertLevel.INFO, **context)
