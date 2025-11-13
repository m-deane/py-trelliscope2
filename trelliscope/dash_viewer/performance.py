"""
Performance optimization utilities for Dash viewer.

Provides caching, debouncing, and optimization strategies for large datasets.
"""

from functools import lru_cache
from typing import Any, Dict, List
import pandas as pd
import time


class PerformanceMonitor:
    """Monitor and log performance metrics."""

    def __init__(self):
        self.timings = {}

    def time_operation(self, operation_name: str):
        """Context manager for timing operations."""
        class TimerContext:
            def __init__(self, monitor, name):
                self.monitor = monitor
                self.name = name
                self.start_time = None

            def __enter__(self):
                self.start_time = time.time()
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                elapsed = time.time() - self.start_time
                if self.name not in self.monitor.timings:
                    self.monitor.timings[self.name] = []
                self.monitor.timings[self.name].append(elapsed)

        return TimerContext(self, operation_name)

    def get_average_time(self, operation_name: str) -> float:
        """Get average time for an operation."""
        if operation_name not in self.timings:
            return 0.0
        times = self.timings[operation_name]
        return sum(times) / len(times) if times else 0.0

    def reset(self):
        """Reset all timings."""
        self.timings = {}


# Global performance monitor
performance_monitor = PerformanceMonitor()


def optimize_dataframe_operations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimize DataFrame for faster operations.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame

    Returns
    -------
    pd.DataFrame
        Optimized DataFrame
    """
    # Convert object columns to categorical if beneficial
    for col in df.select_dtypes(include=['object']).columns:
        num_unique = df[col].nunique()
        num_total = len(df)

        # Convert to categorical if < 50% unique values
        if num_unique / num_total < 0.5:
            df[col] = df[col].astype('category')

    return df


def chunk_dataframe(df: pd.DataFrame, chunk_size: int = 1000) -> List[pd.DataFrame]:
    """
    Split DataFrame into chunks for processing.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    chunk_size : int
        Size of each chunk

    Returns
    -------
    list
        List of DataFrame chunks
    """
    chunks = []
    for i in range(0, len(df), chunk_size):
        chunks.append(df.iloc[i:i + chunk_size])
    return chunks


@lru_cache(maxsize=128)
def cached_filter_operation(
    data_hash: int,
    filter_key: str,
    filter_value: Any
) -> tuple:
    """
    Cache filter operations.

    Note: This is a placeholder - actual implementation would need
    to handle DataFrame hashing properly.
    """
    # Placeholder for cached filter
    return ()


def should_use_pagination(num_panels: int, threshold: int = 10000) -> bool:
    """
    Determine if pagination should be used based on dataset size.

    Parameters
    ----------
    num_panels : int
        Total number of panels
    threshold : int
        Threshold for enabling pagination

    Returns
    -------
    bool
        True if pagination should be used
    """
    return num_panels > threshold


def estimate_memory_usage(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Estimate memory usage of DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame

    Returns
    -------
    dict
        Memory usage statistics
    """
    memory_bytes = df.memory_usage(deep=True).sum()
    memory_mb = memory_bytes / (1024 * 1024)

    return {
        'total_bytes': memory_bytes,
        'total_mb': memory_mb,
        'per_row_bytes': memory_bytes / len(df) if len(df) > 0 else 0,
        'columns': len(df.columns),
        'rows': len(df)
    }


def suggest_optimizations(df: pd.DataFrame) -> List[str]:
    """
    Suggest optimizations based on DataFrame characteristics.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame

    Returns
    -------
    list
        List of optimization suggestions
    """
    suggestions = []

    # Check size
    if len(df) > 10000:
        suggestions.append("Consider enabling virtual scrolling for large datasets")

    # Check memory usage
    memory_info = estimate_memory_usage(df)
    if memory_info['total_mb'] > 100:
        suggestions.append(f"High memory usage ({memory_info['total_mb']:.1f}MB) - consider data reduction")

    # Check for categorical optimization opportunities
    for col in df.select_dtypes(include=['object']).columns:
        num_unique = df[col].nunique()
        if num_unique < len(df) * 0.5:
            suggestions.append(f"Convert '{col}' to categorical for better performance")

    return suggestions


class DataFrameCache:
    """Simple cache for DataFrame operations."""

    def __init__(self, max_size: int = 10):
        self.cache = {}
        self.max_size = max_size
        self.access_times = {}

    def get(self, key: str) -> Any:
        """Get cached value."""
        if key in self.cache:
            self.access_times[key] = time.time()
            return self.cache[key]
        return None

    def set(self, key: str, value: Any):
        """Set cached value."""
        # Evict oldest if at max size
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            del self.cache[oldest_key]
            del self.access_times[oldest_key]

        self.cache[key] = value
        self.access_times[key] = time.time()

    def clear(self):
        """Clear cache."""
        self.cache = {}
        self.access_times = {}

    def __contains__(self, key: str) -> bool:
        """Check if key is in cache."""
        return key in self.cache


# Global DataFrame cache
df_cache = DataFrameCache(max_size=20)
