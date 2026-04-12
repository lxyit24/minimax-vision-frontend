#!/usr/bin/env python3
"""
慧眼 - 定时监控检查脚本
用于 cron 或 systemd timer 定期执行
"""

import sys
import os
import json
import time
import urllib.request
import urllib.error

# 添加 backend 目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from monitoring import (
    metrics_collector,
    process_alerts,
    update_daily_stats,
    check_api_health,
    get_prometheus_metrics,
    ALERT_EMAIL,
    ALERT_THRESHOLD_ERROR_RATE,
    ALERT_THRESHOLD_RESPONSE_TIME
)


def check_api_endpoints():
    """检查 API 端点是否正常响应"""
    base_url = os.environ.get('API_BASE_URL', 'http://localhost:5001')
    
    endpoints = [
        '/api/health',
        '/api/metrics/json',
        '/api/alerts'
    ]
    
    results = {}
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as response:
                results[endpoint] = {
                    'status': 'ok',
                    'code': response.status
                }
        except urllib.error.HTTPError as e:
            results[endpoint] = {
                'status': 'error',
                'code': e.code,
                'error': str(e)
            }
        except Exception as e:
            results[endpoint] = {
                'status': 'error',
                'error': str(e)
            }
    
    return results


def run_health_check():
    """执行完整健康检查"""
    print("=" * 60)
    print(f"慧眼监控检查 - {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 检查 API 端点
    print("\n[1] API 端点检查:")
    endpoint_results = check_api_endpoints()
    all_ok = True
    for endpoint, result in endpoint_results.items():
        status = result.get('status', 'unknown')
        code = result.get('code', '-')
        print(f"  {endpoint}: {status.upper()} {code}")
        if status != 'ok':
            all_ok = False
    
    # 2. 获取本地指标
    print("\n[2] 系统指标:")
    metrics = metrics_collector.get_metrics()
    print(f"  请求总数: {metrics['requests']['total']}")
    print(f"  5分钟错误率: {metrics['requests']['error_rate_5min_percent']}%")
    print(f"  平均响应时间: {metrics['performance']['avg_response_time_ms']:.0f}ms")
    print(f"  CPU: {metrics['system']['cpu_percent']}%")
    print(f"  内存: {metrics['system']['memory_percent']}%")
    print(f"  磁盘: {metrics['system']['disk_percent']}%")
    
    # 3. 检查告警
    print("\n[3] 告警检查:")
    alerts = metrics_collector.check_alerts()
    if alerts:
        for alert in alerts:
            print(f"  [{alert['level'].upper()}] {alert['message']}")
            all_ok = False
    else:
        print("  无活跃告警 ✓")
    
    # 4. 详细健康状态
    print("\n[4] 详细健康状态:")
    health = check_api_health()
    print(f"  总体状态: {health.get('status', 'unknown').upper()}")
    print(f"  MySQL: {health.get('mysql', 'unknown')}")
    print(f"  系统: {health}")
    
    # 5. 处理告警（发送通知）
    if alerts:
        print("\n[5] 发送告警通知:")
        process_alerts()
    
    # 6. 更新每日统计
    print("\n[6] 更新每日统计:")
    update_daily_stats()
    print("  完成 ✓")
    
    print("\n" + "=" * 60)
    
    if all_ok:
        print("状态: 所有检查通过 ✓")
        return 0
    else:
        print("状态: 存在问题，请检查上述输出")
        return 1


if __name__ == '__main__':
    sys.exit(run_health_check())
