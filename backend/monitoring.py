"""
慧眼 - 监控与告警模块
负责：指标收集、数据库日志、告警检查
"""

import os
import time
import json
import psutil
import socket
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import defaultdict, deque
from threading import Lock

# ============== 配置 ==============

MYSQL_HOST = os.environ.get('MYSQL_HOST', '127.0.0.1')
MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
MYSQL_USER = os.environ.get('MYSQL_USER', 'huiyan')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'BhEyrdGTeRA7n8cW')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'huiyan')

ALERT_EMAIL = os.environ.get('ALERT_EMAIL', 'lxyit24@qq.com')
ALERT_THRESHOLD_ERROR_RATE = float(os.environ.get('ALERT_THRESHOLD_ERROR_RATE', 5.0))  # 5% 错误率阈值
ALERT_THRESHOLD_RESPONSE_TIME = float(os.environ.get('ALERT_THRESHOLD_RESPONSE_TIME', 3000))  # 3000ms 响应时间阈值
ALERT_THRESHOLD_RATE_LIMIT = int(os.environ.get('ALERT_THRESHOLD_RATE_LIMIT', 100))  # 100次/分钟阈值

# ============== 内存指标存储 ==============

class MetricsCollector:
    """内存指标收集器（启动时初始化）"""
    
    def __init__(self):
        self.lock = Lock()
        
        # 请求计数 {endpoint: count}
        self.request_count = defaultdict(int)
        
        # 错误计数 {endpoint: error_count}
        self.error_count = defaultdict(int)
        
        # 响应时间队列 {endpoint: deque of (timestamp, response_time_ms)}
        self.response_times = defaultdict(lambda: deque(maxlen=1000))
        
        # 时间窗口内的请求 (用于滑动窗口统计)
        self.window_requests = deque(maxlen=600)  # 保留最近 600 条记录（约10分钟）
        
        # 上次告警时间
        self.last_alert_time = {}
        
        # 系统启动时间
        self.start_time = time.time()
        
        # 累计计数（用于持久化统计）
        self.total_requests = 0
        self.total_errors = 0
        
    def record_request(self, endpoint: str, status: int, response_time_ms: float, ip: str = None):
        """记录一次请求"""
        with self.lock:
            self.request_count[endpoint] += 1
            self.total_requests += 1
            
            if status >= 400:
                self.error_count[endpoint] += 1
                self.total_errors += 1
            
            self.response_times[endpoint].append((time.time(), response_time_ms))
            
            # 添加到滑动窗口
            self.window_requests.append({
                'timestamp': time.time(),
                'endpoint': endpoint,
                'status': status,
                'response_time_ms': response_time_ms,
                'ip': ip
            })
    
    def get_metrics(self) -> dict:
        """获取当前指标"""
        with self.lock:
            now = time.time()
            window_start = now - 300  # 5分钟窗口
            
            # 计算近5分钟内的请求
            recent_requests = [r for r in self.window_requests if r['timestamp'] >= window_start]
            
            # 计算近5分钟错误率
            if recent_requests:
                recent_errors = sum(1 for r in recent_requests if r['status'] >= 400)
                error_rate_5min = (recent_errors / len(recent_requests)) * 100
            else:
                error_rate_5min = 0
            
            # 计算平均响应时间
            all_response_times = []
            for endpoint_times in self.response_times.values():
                for ts, rt in endpoint_times:
                    if now - ts < 300:  # 5分钟内的
                        all_response_times.append(rt)
            
            avg_response_time = sum(all_response_times) / len(all_response_times) if all_response_times else 0
            
            # 系统指标
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # 网络连接数
            connections = len(psutil.net_connections())
            
            return {
                'timestamp': datetime.now().isoformat(),
                'uptime_seconds': int(now - self.start_time),
                
                # 请求统计
                'requests': {
                    'total': self.total_requests,
                    'by_endpoint': dict(self.request_count),
                    'last_5min': len(recent_requests),
                    'error_rate_5min_percent': round(error_rate_5min, 2)
                },
                
                # 错误统计
                'errors': {
                    'total': self.total_errors,
                    'by_endpoint': dict(self.error_count)
                },
                
                # 性能指标
                'performance': {
                    'avg_response_time_ms': round(avg_response_time, 2),
                    'max_response_time_ms': max([r[1] for r in all_response_times], default=0)
                },
                
                # 系统指标
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_used_mb': round(memory.used / 1024 / 1024, 2),
                    'memory_total_mb': round(memory.total / 1024 / 1024, 2),
                    'disk_percent': disk.percent,
                    'disk_used_gb': round(disk.used / 1024 / 1024 / 1024, 2),
                    'disk_total_gb': round(disk.total / 1024 / 1024 / 1024, 2),
                    'network_connections': connections,
                    'load_average': os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0
                }
            }
    
    def check_alerts(self) -> list:
        """检查是否需要告警"""
        alerts = []
        metrics = self.get_metrics()
        
        # 检查错误率
        if metrics['requests']['error_rate_5min_percent'] > ALERT_THRESHOLD_ERROR_RATE:
            alerts.append({
                'level': 'error',
                'type': 'HIGH_ERROR_RATE',
                'message': f"错误率过高: {metrics['requests']['error_rate_5min_percent']}% (阈值: {ALERT_THRESHOLD_ERROR_RATE}%)",
                'value': metrics['requests']['error_rate_5min_percent'],
                'threshold': ALERT_THRESHOLD_ERROR_RATE
            })
        
        # 检查平均响应时间
        if metrics['performance']['avg_response_time_ms'] > ALERT_THRESHOLD_RESPONSE_TIME:
            alerts.append({
                'level': 'warning',
                'type': 'SLOW_RESPONSE',
                'message': f"响应时间过长: {metrics['performance']['avg_response_time_ms']}ms (阈值: {ALERT_THRESHOLD_RESPONSE_TIME}ms)",
                'value': metrics['performance']['avg_response_time_ms'],
                'threshold': ALERT_THRESHOLD_RESPONSE_TIME
            })
        
        # 检查 CPU 使用率
        if metrics['system']['cpu_percent'] > 80:
            alerts.append({
                'level': 'warning',
                'type': 'HIGH_CPU',
                'message': f"CPU 使用率过高: {metrics['system']['cpu_percent']}%",
                'value': metrics['system']['cpu_percent'],
                'threshold': 80
            })
        
        # 检查内存使用率
        if metrics['system']['memory_percent'] > 85:
            alerts.append({
                'level': 'warning',
                'type': 'HIGH_MEMORY',
                'message': f"内存使用率过高: {metrics['system']['memory_percent']}%",
                'value': metrics['system']['memory_percent'],
                'threshold': 85
            })
        
        # 检查磁盘使用率
        if metrics['system']['disk_percent'] > 90:
            alerts.append({
                'level': 'error',
                'type': 'HIGH_DISK',
                'message': f"磁盘使用率过高: {metrics['system']['disk_percent']}%",
                'value': metrics['system']['disk_percent'],
                'threshold': 90
            })
        
        return alerts

# 全局指标收集器实例
metrics_collector = MetricsCollector()


# ============== MySQL 日志 ==============

def get_mysql_connection():
    """获取 MySQL 连接"""
    try:
        import pymysql
        return pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    except ImportError:
        print("[monitoring] pymysql not installed, MySQL logging disabled")
        return None
    except Exception as e:
        print(f"[monitoring] MySQL connection failed: {e}")
        return None


def init_mysql_tables():
    """初始化 MySQL 表"""
    conn = get_mysql_connection()
    if not conn:
        return
    
    try:
        with conn.cursor() as cursor:
            # API 请求日志表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_request_logs (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME NOT NULL,
                    endpoint VARCHAR(100) NOT NULL,
                    method VARCHAR(10) NOT NULL,
                    status INT NOT NULL,
                    response_time_ms FLOAT NOT NULL,
                    client_ip VARCHAR(45),
                    user_agent VARCHAR(500),
                    error_code VARCHAR(50),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_timestamp (timestamp),
                    INDEX idx_endpoint (endpoint),
                    INDEX idx_status (status)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            # 每日统计表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_daily_stats (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    date DATE NOT NULL UNIQUE,
                    total_requests INT DEFAULT 0,
                    total_errors INT DEFAULT 0,
                    total_response_time_ms FLOAT DEFAULT 0,
                    avg_response_time_ms FLOAT DEFAULT 0,
                    max_response_time_ms FLOAT DEFAULT 0,
                    min_response_time_ms FLOAT DEFAULT 0,
                    unique_ips INT DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_date (date)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            # 告警记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alert_history (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME NOT NULL,
                    alert_type VARCHAR(50) NOT NULL,
                    level VARCHAR(20) NOT NULL,
                    message TEXT NOT NULL,
                    value FLOAT,
                    threshold FLOAT,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolved_at DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_timestamp (timestamp),
                    INDEX idx_type (alert_type),
                    INDEX idx_resolved (resolved)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            conn.commit()
            print("[monitoring] MySQL tables initialized")
    
    except Exception as e:
        print(f"[monitoring] MySQL table init failed: {e}")
    finally:
        conn.close()


def log_request_to_mysql(endpoint: str, method: str, status: int, response_time_ms: float, 
                         client_ip: str = None, user_agent: str = None, error_code: str = None):
    """记录请求到 MySQL（异步，不阻塞主请求）"""
    import threading
    
    def _write():
        conn = get_mysql_connection()
        if not conn:
            return
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO api_request_logs 
                    (timestamp, endpoint, method, status, response_time_ms, client_ip, user_agent, error_code)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (datetime.now(), endpoint, method, status, response_time_ms, client_ip, user_agent, error_code))
                conn.commit()
        except Exception as e:
            print(f"[monitoring] Failed to log request: {e}")
        finally:
            conn.close()
    
    thread = threading.Thread(target=_write, daemon=True)
    thread.start()


def update_daily_stats(date: datetime = None):
    """更新每日统计"""
    if date is None:
        date = datetime.now()
    
    conn = get_mysql_connection()
    if not conn:
        return
    
    try:
        with conn.cursor() as cursor:
            # 计算今日统计
            today_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_requests,
                    SUM(CASE WHEN status >= 400 THEN 1 ELSE 0 END) as total_errors,
                    AVG(response_time_ms) as avg_response_time,
                    MAX(response_time_ms) as max_response_time,
                    MIN(response_time_ms) as min_response_time,
                    COUNT(DISTINCT client_ip) as unique_ips
                FROM api_request_logs 
                WHERE timestamp >= %s AND timestamp < %s
            """, (today_start, today_end))
            
            result = cursor.fetchone()
            
            if result and result['total_requests'] > 0:
                cursor.execute("""
                    INSERT INTO api_daily_stats 
                    (date, total_requests, total_errors, avg_response_time_ms, max_response_time_ms, min_response_time_ms, unique_ips)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        total_requests = VALUES(total_requests),
                        total_errors = VALUES(total_errors),
                        avg_response_time_ms = VALUES(avg_response_time_ms),
                        max_response_time_ms = VALUES(max_response_time_ms),
                        min_response_time_ms = VALUES(min_response_time_ms),
                        unique_ips = VALUES(unique_ips)
                """, (date.date(), result['total_requests'], result['total_errors'],
                      result['avg_response_time'], result['max_response_time'],
                      result['min_response_time'], result['unique_ips']))
                
                conn.commit()
    
    except Exception as e:
        print(f"[monitoring] Failed to update daily stats: {e}")
    finally:
        conn.close()


def record_alert(alert: dict):
    """记录告警到 MySQL"""
    conn = get_mysql_connection()
    if not conn:
        return
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO alert_history 
                (timestamp, alert_type, level, message, value, threshold)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (datetime.now(), alert.get('type'), alert.get('level'), 
                  alert.get('message'), alert.get('value'), alert.get('threshold')))
            conn.commit()
    except Exception as e:
        print(f"[monitoring] Failed to record alert: {e}")
    finally:
        conn.close()


# ============== 告警通知 ==============

def send_alert_email(alert: dict):
    """发送告警邮件"""
    try:
        # QQ 邮箱 SMTP 设置
        smtp_server = 'smtp.qq.com'
        smtp_port = 587
        smtp_user = 'alerts@1i.wiki'  # 需要配置为你的发送邮箱
        smtp_password = os.environ.get('SMTP_PASSWORD', '')  # QQ 邮箱授权码
        
        if not smtp_password:
            print(f"[monitoring] SMTP_PASSWORD not set, skipping email alert")
            return
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"【慧眼监控告警】{alert['type']} - {alert['level'].upper()}"
        msg['From'] = smtp_user
        msg['To'] = ALERT_EMAIL
        
        # 邮件正文
        body = f"""
        <html>
        <body>
            <h2>慧眼监控告警</h2>
            <table style="border-collapse: collapse; width: 100%;">
                <tr style="border: 1px solid #ddd;">
                    <td style="padding: 8px; font-weight: bold;">告警类型</td>
                    <td style="padding: 8px;">{alert['type']}</td>
                </tr>
                <tr style="border: 1px solid #ddd;">
                    <td style="padding: 8px; font-weight: bold;">严重级别</td>
                    <td style="padding: 8px;">{alert['level'].upper()}</td>
                </tr>
                <tr style="border: 1px solid #ddd;">
                    <td style="padding: 8px; font-weight: bold;">告警信息</td>
                    <td style="padding: 8px;">{alert['message']}</td>
                </tr>
                <tr style="border: 1px solid #ddd;">
                    <td style="padding: 8px; font-weight: bold;">当前值</td>
                    <td style="padding: 8px;">{alert['value']}</td>
                </tr>
                <tr style="border: 1px solid #ddd;">
                    <td style="padding: 8px; font-weight: bold;">阈值</td>
                    <td style="padding: 8px;">{alert['threshold']}</td>
                </tr>
                <tr style="border: 1px solid #ddd;">
                    <td style="padding: 8px; font-weight: bold;">服务器</td>
                    <td style="padding: 8px;">{socket.gethostname()}</td>
                </tr>
                <tr style="border: 1px solid #ddd;">
                    <td style="padding: 8px; font-weight: bold;">时间</td>
                    <td style="padding: 8px;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
                </tr>
            </table>
            <p style="margin-top: 20px;">
                <a href="https://vision.1i.wiki">访问慧眼控制台</a>
            </p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        print(f"[monitoring] Alert email sent to {ALERT_EMAIL}")
    
    except Exception as e:
        print(f"[monitoring] Failed to send alert email: {e}")


def send_alert_qq(alert: dict):
    """发送 QQ 消息通知（通过 QQ 机器人）"""
    # 可以通过 QQ 机器人 API 发送消息
    # 这里预留接口，实际使用时可配置
    qq_webhook = os.environ.get('QQ_WEBHOOK_URL', '')
    
    if not qq_webhook:
        print(f"[monitoring] QQ_WEBHOOK_URL not set, skipping QQ alert")
        return
    
    try:
        import urllib.request
        
        message = f"""
🚨 慧眼监控告警

类型: {alert['type']}
级别: {alert['level'].upper()}
信息: {alert['message']}
当前值: {alert['value']}
阈值: {alert['threshold']}
时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        data = json.dumps({"msg_type": "text", "content": message}).encode('utf-8')
        req = urllib.request.Request(
            qq_webhook,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"[monitoring] QQ alert sent: {response.read().decode('utf-8')}")
    
    except Exception as e:
        print(f"[monitoring] Failed to send QQ alert: {e}")


def process_alerts():
    """处理告警检查和发送"""
    alerts = metrics_collector.check_alerts()
    
    for alert in alerts:
        # 检查是否需要发送（避免重复告警，5分钟内同一类型只告警一次）
        alert_key = alert['type']
        last_time = metrics_collector.last_alert_time.get(alert_key, 0)
        
        if time.time() - last_time > 300:  # 5分钟冷却
            # 记录到 MySQL
            record_alert(alert)
            
            # 发送通知
            send_alert_email(alert)
            send_alert_qq(alert)
            
            # 更新上次告警时间
            metrics_collector.last_alert_time[alert_key] = time.time()
            
            print(f"[monitoring] ALERT: {alert['message']}")
        else:
            print(f"[monitoring] Alert {alert_key} in cooldown, skipping")


# ============== Prometheus 格式输出 ==============

def get_prometheus_metrics() -> str:
    """生成 Prometheus 格式的指标"""
    metrics = metrics_collector.get_metrics()
    
    output = []
    output.append(f"# HELP vision_requests_total Total number of API requests")
    output.append(f"# TYPE vision_requests_total counter")
    output.append(f"vision_requests_total {metrics['requests']['total']}")
    
    output.append(f"# HELP vision_errors_total Total number of API errors")
    output.append(f"# TYPE vision_errors_total counter")
    output.append(f"vision_errors_total {metrics['errors']['total']}")
    
    output.append(f"# HELP vision_error_rate_5m Error rate over last 5 minutes")
    output.append(f"# TYPE vision_error_rate_5m gauge")
    output.append(f"vision_error_rate_5m {metrics['requests']['error_rate_5min_percent']}")
    
    output.append(f"# HELP vision_avg_response_time_ms Average response time in ms")
    output.append(f"# TYPE vision_avg_response_time_ms gauge")
    output.append(f"vision_avg_response_time_ms {metrics['performance']['avg_response_time_ms']}")
    
    output.append(f"# HELP vision_cpu_percent CPU usage percent")
    output.append(f"# TYPE vision_cpu_percent gauge")
    output.append(f"vision_cpu_percent {metrics['system']['cpu_percent']}")
    
    output.append(f"# HELP vision_memory_percent Memory usage percent")
    output.append(f"# TYPE vision_memory_percent gauge")
    output.append(f"vision_memory_percent {metrics['system']['memory_percent']}")
    
    output.append(f"# HELP vision_uptime_seconds Service uptime in seconds")
    output.append(f"# TYPE vision_uptime_seconds counter")
    output.append(f"vision_uptime_seconds {metrics['uptime_seconds']}")
    
    return '\n'.join(output)


# ============== 健康检查 ==============

def check_api_health() -> dict:
    """检查 API 健康状态"""
    import urllib.request
    import urllib.error
    
    health_status = {
        'api': 'unknown',
        'mysql': 'unknown',
        'uptime_seconds': int(time.time() - metrics_collector.start_time)
    }
    
    # 检查 MySQL
    conn = get_mysql_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_status['mysql'] = 'ok'
        except:
            health_status['mysql'] = 'error'
        finally:
            conn.close()
    else:
        health_status['mysql'] = 'disabled'
    
    # 检查系统资源
    metrics = metrics_collector.get_metrics()
    health_status['system'] = {
        'cpu': 'ok' if metrics['system']['cpu_percent'] < 80 else 'warning',
        'memory': 'ok' if metrics['system']['memory_percent'] < 85 else 'warning',
        'disk': 'ok' if metrics['system']['disk_percent'] < 90 else 'error'
    }
    
    # 总体状态
    if all(v == 'ok' or v == 'disabled' for v in health_status.values()) and \
       all(v == 'ok' for v in health_status['system'].values()):
        health_status['status'] = 'healthy'
    elif health_status['system']['disk'] == 'error':
        health_status['status'] = 'critical'
    else:
        health_status['status'] = 'degraded'
    
    return health_status


# ============== 初始化 ==============

def init_monitoring():
    """初始化监控模块"""
    print("[monitoring] Initializing monitoring system...")
    
    # 确保 MySQL 数据库存在
    try:
        import pymysql
        conn = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            charset='utf8mb4'
        )
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE}")
        conn.close()
        print(f"[monitoring] Database '{MYSQL_DATABASE}' ready")
    except Exception as e:
        print(f"[monitoring] Failed to create database: {e}")
    
    # 初始化表
    init_mysql_tables()
    
    print("[monitoring] Monitoring system initialized")


if __name__ == '__main__':
    # 单独运行监控检查
    init_monitoring()
    
    print("\n=== 当前指标 ===")
    metrics = metrics_collector.get_metrics()
    print(json.dumps(metrics, indent=2, ensure_ascii=False))
    
    print("\n=== 告警检查 ===")
    alerts = metrics_collector.check_alerts()
    if alerts:
        for alert in alerts:
            print(f"  [{alert['level'].upper()}] {alert['message']}")
    else:
        print("  无告警")
    
    print("\n=== 健康检查 ===")
    health = check_api_health()
    print(json.dumps(health, indent=2, ensure_ascii=False))
