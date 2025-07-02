#!/usr/bin/env python3
"""
Performance Monitor for FaceAuth
Real-time performance tracking and optimization suggestions.
"""

import time
import psutil
import logging
import functools
import threading
from datetime import datetime
from typing import Dict, List, Any
import json

class PerformanceMonitor:
    """Monitor and track FaceAuth performance metrics."""
    
    def __init__(self, log_file="logs/performance.log"):
        self.metrics = {}
        self.start_time = time.time()
        self.setup_logging(log_file)
        self.performance_data = []
        
    def setup_logging(self, log_file):
        """Setup performance logging."""
        import os
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('performance')
        
    def measure_function(self, func_name=None):
        """Decorator to measure function performance."""
        def decorator(func):
            name = func_name or func.__name__
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss
                
                try:
                    result = func(*args, **kwargs)
                    success = True
                    error_msg = None
                except Exception as e:
                    result = None
                    success = False
                    error_msg = str(e)
                    raise
                finally:
                    execution_time = time.time() - start_time
                    end_memory = psutil.Process().memory_info().rss
                    memory_used = end_memory - start_memory
                    
                    self.record_metric(
                        function_name=name,
                        execution_time=execution_time,
                        memory_used=memory_used,
                        success=success,
                        error_msg=error_msg
                    )
                
                return result
            return wrapper
        return decorator
    
    def record_metric(self, function_name: str, execution_time: float, 
                     memory_used: int, success: bool, error_msg: str = None):
        """Record performance metric."""
        metric = {
            'timestamp': datetime.now().isoformat(),
            'function': function_name,
            'execution_time': execution_time,
            'memory_used_mb': memory_used / 1024 / 1024,
            'success': success,
            'error': error_msg
        }
        
        self.performance_data.append(metric)
        
        # Log performance
        if success:
            self.logger.info(
                f"{function_name}: {execution_time:.3f}s, "
                f"{metric['memory_used_mb']:.2f}MB"
            )
        else:
            self.logger.error(
                f"{function_name} FAILED: {execution_time:.3f}s, "
                f"Error: {error_msg}"
            )
        
        # Store in metrics dict for quick access
        if function_name not in self.metrics:
            self.metrics[function_name] = []
        self.metrics[function_name].append(metric)
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get current system performance info."""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'memory_used_gb': psutil.virtual_memory().used / 1024**3,
            'memory_available_gb': psutil.virtual_memory().available / 1024**3,
            'disk_usage_percent': psutil.disk_usage('/').percent,
            'uptime_hours': (time.time() - self.start_time) / 3600
        }
    
    def get_function_stats(self, function_name: str) -> Dict[str, Any]:
        """Get statistics for a specific function."""
        if function_name not in self.metrics:
            return None
        
        data = self.metrics[function_name]
        execution_times = [m['execution_time'] for m in data if m['success']]
        memory_usage = [m['memory_used_mb'] for m in data if m['success']]
        
        if not execution_times:
            return {'error': 'No successful executions recorded'}
        
        return {
            'total_calls': len(data),
            'successful_calls': len(execution_times),
            'success_rate': len(execution_times) / len(data) * 100,
            'avg_execution_time': sum(execution_times) / len(execution_times),
            'min_execution_time': min(execution_times),
            'max_execution_time': max(execution_times),
            'avg_memory_usage_mb': sum(memory_usage) / len(memory_usage) if memory_usage else 0,
            'total_memory_used_mb': sum(memory_usage)
        }
    
    def generate_performance_report(self) -> str:
        """Generate comprehensive performance report."""
        report = []
        report.append("=" * 60)
        report.append("FaceAuth Performance Report")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append()
        
        # System info
        sys_info = self.get_system_info()
        report.append("System Performance:")
        report.append(f"  CPU Usage: {sys_info['cpu_percent']:.1f}%")
        report.append(f"  Memory Usage: {sys_info['memory_percent']:.1f}%")
        report.append(f"  Memory Used: {sys_info['memory_used_gb']:.2f} GB")
        report.append(f"  Uptime: {sys_info['uptime_hours']:.2f} hours")
        report.append()
        
        # Function statistics
        report.append("Function Performance:")
        for func_name in self.metrics.keys():
            stats = self.get_function_stats(func_name)
            if stats and 'error' not in stats:
                report.append(f"  {func_name}:")
                report.append(f"    Total Calls: {stats['total_calls']}")
                report.append(f"    Success Rate: {stats['success_rate']:.1f}%")
                report.append(f"    Avg Time: {stats['avg_execution_time']:.3f}s")
                report.append(f"    Min/Max Time: {stats['min_execution_time']:.3f}s / {stats['max_execution_time']:.3f}s")
                report.append(f"    Avg Memory: {stats['avg_memory_usage_mb']:.2f}MB")
                report.append()
        
        # Performance recommendations
        report.append("Optimization Recommendations:")
        recommendations = self.get_optimization_recommendations()
        for rec in recommendations:
            report.append(f"  • {rec}")
        
        return "\n".join(report)
    
    def get_optimization_recommendations(self) -> List[str]:
        """Generate optimization recommendations based on metrics."""
        recommendations = []
        
        # Check system resources
        sys_info = self.get_system_info()
        if sys_info['cpu_percent'] > 80:
            recommendations.append("High CPU usage detected - consider async processing")
        if sys_info['memory_percent'] > 85:
            recommendations.append("High memory usage - implement memory cleanup")
        
        # Check function performance
        for func_name, stats in [(name, self.get_function_stats(name)) for name in self.metrics.keys()]:
            if stats and 'error' not in stats:
                if stats['avg_execution_time'] > 2.0:
                    recommendations.append(f"{func_name}: Slow execution (>{stats['avg_execution_time']:.1f}s) - optimize algorithm")
                if stats['success_rate'] < 95:
                    recommendations.append(f"{func_name}: Low success rate ({stats['success_rate']:.1f}%) - improve error handling")
                if stats['avg_memory_usage_mb'] > 50:
                    recommendations.append(f"{func_name}: High memory usage ({stats['avg_memory_usage_mb']:.1f}MB) - implement memory optimization")
        
        if not recommendations:
            recommendations.append("All systems performing optimally!")
        
        return recommendations
    
    def save_metrics_to_file(self, filename="performance_metrics.json"):
        """Save all metrics to JSON file."""
        with open(filename, 'w') as f:
            json.dump({
                'system_info': self.get_system_info(),
                'metrics': self.performance_data,
                'generated_at': datetime.now().isoformat()
            }, f, indent=2)
        
        self.logger.info(f"Performance metrics saved to {filename}")
    
    def start_monitoring_thread(self, interval=30):
        """Start background monitoring thread."""
        def monitor():
            while True:
                time.sleep(interval)
                sys_info = self.get_system_info()
                self.logger.info(f"System Monitor - CPU: {sys_info['cpu_percent']:.1f}%, Memory: {sys_info['memory_percent']:.1f}%")
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        self.logger.info("Background monitoring started")


# Global performance monitor instance
performance_monitor = PerformanceMonitor()

# Convenience decorators
def monitor_performance(func_name=None):
    """Decorator to monitor function performance."""
    return performance_monitor.measure_function(func_name)

def get_performance_report():
    """Get current performance report."""
    return performance_monitor.generate_performance_report()

def save_performance_metrics(filename="performance_metrics.json"):
    """Save performance metrics to file."""
    performance_monitor.save_metrics_to_file(filename)


if __name__ == "__main__":
    # Example usage
    @monitor_performance("test_function")
    def test_function():
        time.sleep(0.1)  # Simulate work
        return "test result"
    
    # Run test
    result = test_function()
    
    # Generate report
    print(get_performance_report())
    
    # Save metrics
    save_performance_metrics()
