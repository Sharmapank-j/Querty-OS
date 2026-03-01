#!/usr/bin/env python3
"""
Querty-OS Performance Monitoring and Optimization
Tracks system performance metrics and implements optimization strategies.
"""

import logging
import psutil
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

logger = logging.getLogger("querty-performance")


@dataclass
class PerformanceMetrics:
    """Performance metrics snapshot."""

    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_usage_percent: float
    network_bytes_sent: int
    network_bytes_recv: int


class PerformanceMonitor:
    """Monitor system performance and collect metrics."""

    def __init__(self, collection_interval: int = 60):
        """
        Initialize performance monitor.

        Args:
            collection_interval: Seconds between metric collections
        """
        self.collection_interval = collection_interval
        self.metrics_history: List[PerformanceMetrics] = []
        self.max_history = 1000  # Keep last 1000 samples
        self._baseline_metrics: Optional[PerformanceMetrics] = None
        logger.info("Performance monitor initialized")

    def collect_metrics(self) -> PerformanceMetrics:
        """
        Collect current performance metrics.

        Returns:
            PerformanceMetrics snapshot
        """
        # Get network counters
        net_io = psutil.net_io_counters()

        metrics = PerformanceMetrics(
            timestamp=time.time(),
            cpu_percent=psutil.cpu_percent(interval=0.1),
            memory_percent=psutil.virtual_memory().percent,
            memory_available_mb=psutil.virtual_memory().available / (1024 * 1024),
            disk_usage_percent=psutil.disk_usage("/").percent,
            network_bytes_sent=net_io.bytes_sent,
            network_bytes_recv=net_io.bytes_recv,
        )

        # Add to history
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > self.max_history:
            self.metrics_history.pop(0)

        # Set baseline on first collection
        if self._baseline_metrics is None:
            self._baseline_metrics = metrics
            logger.info("Baseline metrics established")

        return metrics

    def get_average_metrics(self, samples: int = 10) -> Optional[PerformanceMetrics]:
        """
        Get average of recent metrics.

        Args:
            samples: Number of recent samples to average

        Returns:
            Averaged metrics or None if insufficient data
        """
        if len(self.metrics_history) < samples:
            return None

        recent = self.metrics_history[-samples:]

        return PerformanceMetrics(
            timestamp=time.time(),
            cpu_percent=sum(m.cpu_percent for m in recent) / samples,
            memory_percent=sum(m.memory_percent for m in recent) / samples,
            memory_available_mb=sum(m.memory_available_mb for m in recent) / samples,
            disk_usage_percent=sum(m.disk_usage_percent for m in recent) / samples,
            network_bytes_sent=recent[-1].network_bytes_sent,
            network_bytes_recv=recent[-1].network_bytes_recv,
        )

    def get_performance_report(self) -> Dict:
        """
        Generate performance report.

        Returns:
            Dict with performance analysis
        """
        if not self.metrics_history:
            return {"status": "no_data", "message": "No metrics collected yet"}

        current = self.metrics_history[-1]

        report = {
            "status": "healthy",
            "current": {
                "cpu_percent": current.cpu_percent,
                "memory_percent": current.memory_percent,
                "memory_available_mb": current.memory_available_mb,
                "disk_usage_percent": current.disk_usage_percent,
            },
            "warnings": [],
        }

        # Check for performance issues
        if current.cpu_percent > 90:
            report["warnings"].append("High CPU usage detected")
            report["status"] = "warning"

        if current.memory_percent > 90:
            report["warnings"].append("High memory usage detected")
            report["status"] = "warning"

        if current.disk_usage_percent > 90:
            report["warnings"].append("Low disk space")
            report["status"] = "warning"

        return report


class CacheManager:
    """Manage caching strategies for performance optimization."""

    def __init__(self, max_cache_size_mb: int = 100):
        """
        Initialize cache manager.

        Args:
            max_cache_size_mb: Maximum cache size in MB
        """
        self.max_cache_size_mb = max_cache_size_mb
        self.cache: Dict[str, any] = {}
        self.cache_hits = 0
        self.cache_misses = 0
        logger.info(f"Cache manager initialized with {max_cache_size_mb}MB limit")

    def get(self, key: str) -> Optional[any]:
        """
        Get item from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        if key in self.cache:
            self.cache_hits += 1
            logger.debug(f"Cache HIT for key: {key}")
            return self.cache[key]
        else:
            self.cache_misses += 1
            logger.debug(f"Cache MISS for key: {key}")
            return None

    def set(self, key: str, value: any):
        """
        Set item in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        self.cache[key] = value
        logger.debug(f"Cache SET for key: {key}")

    def clear(self):
        """Clear all cache."""
        self.cache.clear()
        logger.info("Cache cleared")

    def get_stats(self) -> Dict:
        """
        Get cache statistics.

        Returns:
            Dict with cache stats
        """
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "size": len(self.cache),
            "hits": self.cache_hits,
            "misses": self.cache_misses,
            "hit_rate_percent": hit_rate,
        }


class PerformanceOptimizer:
    """Main performance optimization coordinator."""

    def __init__(self):
        """Initialize performance optimizer."""
        self.monitor = PerformanceMonitor()
        self.cache_manager = CacheManager()
        self.optimizations_applied = []
        logger.info("Performance optimizer initialized")

    def analyze_and_optimize(self) -> Dict:
        """
        Analyze performance and apply optimizations.

        Returns:
            Dict with optimization results
        """
        # Collect current metrics
        metrics = self.monitor.collect_metrics()

        optimizations = []

        # Check if cache needs clearing
        if metrics.memory_percent > 85:
            logger.info("High memory usage - clearing cache")
            self.cache_manager.clear()
            optimizations.append("cache_cleared")

        # Log performance report
        report = self.monitor.get_performance_report()
        if report["status"] == "warning":
            logger.warning(f"Performance warnings: {report['warnings']}")
            optimizations.append("warnings_logged")

        self.optimizations_applied.extend(optimizations)

        return {
            "metrics": {
                "cpu": metrics.cpu_percent,
                "memory": metrics.memory_percent,
                "disk": metrics.disk_usage_percent,
            },
            "optimizations": optimizations,
            "status": report["status"],
        }

    def get_statistics(self) -> Dict:
        """
        Get comprehensive performance statistics.

        Returns:
            Dict with all statistics
        """
        return {
            "performance": self.monitor.get_performance_report(),
            "cache": self.cache_manager.get_stats(),
            "optimizations_count": len(self.optimizations_applied),
        }


__all__ = [
    "PerformanceMonitor",
    "PerformanceMetrics",
    "CacheManager",
    "PerformanceOptimizer",
]
