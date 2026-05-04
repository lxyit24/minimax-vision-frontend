"""
MiniMax Vision Backend - REST API
支持图片理解 API，供其他系统调用
"""

import os
import io
import json
import base64
import tempfile
import hashlib
import time
import uuid
from datetime import datetime, timedelta
from functools import wraps
from subprocess import Popen, PIPE
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ============== 配置 ==============
# 图片分析使用原始 MiniMax API (MCP)
MINIMAX_API_KEY = os.environ.get('MINIMAX_API_KEY', '')
MINIMAX_API_HOST = os.environ.get('MINIMAX_API_HOST', 'https://api.minimaxi.com')

# 对话使用天行AI API (ai.1i.wiki) - 必须通过环境变量设置
CHAT_API_KEY = os.environ.get('CHAT_API_KEY', '')
if not CHAT_API_KEY:
    raise ValueError("CHAT_API_KEY environment variable is required")

CHAT_API_HOST = os.environ.get('CHAT_API_HOST', 'https://ai.1i.wiki/v1')

# 外部 API 密钥（必须设置，无默认值）
API_KEY = os.environ.get('API_KEY', '')
if not API_KEY:  # API Key不再必需，但我们保留它以备后用
    pass  # 不再需要强制设置

DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'
PRODUCTION = os.environ.get('PRODUCTION', 'true').lower() == 'true'

# 允许的来源（用于 CORS）
ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', 'https://vision.1i.wiki,https://www.vision.1i.wiki').split(',')

# SSRF 防护：禁止访问的内网地址
BLOCKED_IP_RANGES = [
    '10.',      # 私有地址
    '172.16.', '172.17.', '172.18.', '172.19.',  # 私有地址 172.16-31.x.x
    '172.20.', '172.21.', '172.22.', '172.23.',
    '172.24.', '172.25.', '172.26.', '172.27.',
    '172.28.', '172.29.', '172.30.', '172.31.',
    '192.168.', # 私有地址
    '127.',     # 本地回环
    '169.254.', # 链路本地地址
    '0.',       # 广播地址
]

# ============== 安全函数 ==============

def is_ip_blocked(ip: str) -> bool:
    """检查 IP 是否在禁止访问的范围内（SSRF 防护）"""
    if not ip:
        return True
    
    # 检查是否是私有/保留IP范围
    for blocked in BLOCKED_IP_RANGES:
        if ip.startswith(blocked):
            return True
    
    # 检查是否是有效IP地址
    try:
        parts = ip.split('.')
        if len(parts) != 4:
            return True
        for part in parts:
            num = int(part)
            if num < 0 or num > 255:
                return True
    except:
        return True
    
    return False


def get_client_ip() -> str:
    """获取真实客户端 IP"""
    # 优先从 X-Forwarded-For 获取
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote_addr or '0.0.0.0'


def add_security_headers(response):
    """添加安全响应头"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    if PRODUCTION:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response


def sanitize_prompt(prompt: str, max_length: int = 2000) -> str:
    """消毒用户输入的 prompt"""
    if not prompt:
        return "请描述这张图片"
    # 限制长度
    prompt = prompt[:max_length]
    # 移除潜在的危险字符序列（但不过度过滤以免影响正常用法）
    # 这里只做基本的长度控制和空值检查
    return prompt.strip()


# ============== 简单内存限流 ==============
rate_limit_store = {}  # {ip: [(timestamp, count), ...]}


def check_rate_limit(ip: str, max_requests: int = 60, window_seconds: int = 60) -> bool:
    """简单的 IP 级别限流"""
    now = time.time()
    if ip not in rate_limit_store:
        rate_limit_store[ip] = []
    
    # 清理过期记录
    rate_limit_store[ip] = [
        t for t in rate_limit_store[ip]
        if now - t < window_seconds
    ]
    
    if len(rate_limit_store[ip]) >= max_requests:
        return False
    
    rate_limit_store[ip].append(now)
    return True


def require_api_key(f):
    """API 密钥验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        provided_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        if not provided_key:
            return add_security_headers(jsonify({
                "success": False,
                "error": "Missing API key",
                "code": "MISSING_API_KEY"
            })), 401
        
        if provided_key != API_KEY:
            return add_security_headers(jsonify({
                "success": False,
                "error": "Invalid API key",
                "code": "INVALID_API_KEY"
            })), 403
        
        return f(*args, **kwargs)
    return decorated


def log_request(ip: str, endpoint: str, status: int, response_time_ms: float = 0):
    """记录请求日志（仅输出到控制台）"""
    print(f"[{datetime.now().isoformat()}] {ip} -> {endpoint} [{status}] {response_time_ms:.0f}ms")


# ============== 核心功能 ==============

def call_mcp_understand_image(image_path: str, prompt: str = "请详细描述这张图片的内容") -> str:
    """
    调用 MiniMax MCP 工具 understand_image (使用 mmx-cli 封装)
    """
    python_path = "/usr/bin/python3"
    mcp_script = "/root/.openclaw/workspace/minimax-vision-frontend/backend/mmx_vision_mcp.py"
    
    # MCP JSON-RPC 请求
    initialize_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "minimax-vision-backend", "version": "1.0"}
        }
    }
    
    tool_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "understand_image",
            "arguments": {
                "prompt": prompt,
                "image_source": image_path
            }
        }
    }
    
    initialized_notification = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized",
        "params": {}
    }
    
    # 启动 MCP 服务器
    env = os.environ.copy()
    env['MINIMAX_API_KEY'] = MINIMAX_API_KEY
    env['MINIMAX_API_HOST'] = MINIMAX_API_HOST
    
    proc = Popen(
        [python_path, mcp_script],
        env=env,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        text=True,
        cwd="/root"
    )
    
    import time
    
    # 发送初始化请求
    proc.stdin.write(json.dumps(initialize_request) + "\n")
    proc.stdin.flush()
    time.sleep(2)
    proc.stdout.readline()  # 消费初始化响应
    
    # 发送已初始化通知
    proc.stdin.write(json.dumps(initialized_notification) + "\n")
    proc.stdin.flush()
    time.sleep(0.5)
    
    # 发送工具调用请求
    proc.stdin.write(json.dumps(tool_request) + "\n")
    proc.stdin.flush()
    
    # 等待响应
    time.sleep(15)
    
    response = proc.stdout.readline()
    proc.terminate()
    
    if response:
        resp_data = json.loads(response)
        if 'result' in resp_data and 'content' in resp_data['result']:
            for item in resp_data['result']['content']:
                if item.get('type') == 'text':
                    return item['text']
    
    return "分析失败，未能获取结果"


def save_image(data: bytes) -> str:
    """保存图片数据到临时文件"""
    suffix = ".jpg"
    # 检测图片类型
    if data[:8].startswith(b'\x89PNG\r\n\x1a\n'):
        suffix = ".png"
    elif data[:3] == b'\xff\xd8\xff':
        suffix = ".jpg"
    elif data[:4] == b'GIF8':
        suffix = ".gif"
    elif data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        suffix = ".webp"
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
        f.write(data)
        return f.name


# ============== API 路由 ==============

@app.route('/')
def index():
    """API 信息"""
    return add_security_headers(jsonify({
        "name": "MiniMax Vision API",
        "version": "2.0.0",
        "description": "图片理解 API 服务",
        "documentation": "/api/docs",
        "endpoints": {
            "POST /api/analyze": "上传图片并分析（multipart/form-data）",
            "POST /api/analyze/base64": "Base64 图片分析（JSON）",
            "POST /api/analyze/url": "URL 图片分析（JSON）",
            "GET /api/health": "健康检查",
            "GET /api/docs": "API 文档"
        }
    }))


@app.route('/api/health')
def health():
    """健康检查"""
    return add_security_headers(jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }))


@app.route('/api/health/detailed')
def health_detailed():
    """详细健康检查（简化版，无监控）"""
    return add_security_headers(jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "health": {
            "api": "ok",
            "mcp": "configured" if MINIMAX_API_KEY else "not_configured"
        }
    }))


@app.route('/api/metrics')
def metrics():
    """Prometheus 格式指标（已禁用）"""
    return add_security_headers(Response(
        "# Monitoring disabled\n",
        mimetype='text/plain; charset=utf-8'
    ))


@app.route('/api/metrics/json')
def metrics_json():
    """JSON 格式指标（已禁用）"""
    return add_security_headers(jsonify({
        "status": "disabled",
        "message": "Monitoring metrics have been disabled"
    }))


@app.route('/api/alerts')
def alerts():
    """当前告警状态（已禁用）"""
    return add_security_headers(jsonify({
        "success": True,
        "alerts": [],
        "message": "Alerts have been disabled"
    }))


@app.route('/api/docs')
def docs():
    """简易 API 文档"""
    return add_security_headers(jsonify({
        "title": "MiniMax Vision API 文档",
        "version": "2.0.0",
        "base_url": request.host_url.rstrip('/'),
        "endpoints": [
            {
                "method": "POST",
                "path": "/api/analyze",
                "description": "上传图片文件进行分析",
                "content_type": "multipart/form-data",
                "parameters": {
                    "image": "图片文件（必填）",
                    "prompt": "分析提示词（可选，默认中文详细描述）"
                }
            },
            {
                "method": "POST",
                "path": "/api/analyze/base64",
                "description": "发送 Base64 编码的图片进行分析",
                "content_type": "application/json",
                "parameters": {
                    "image": "Base64 字符串（必填，需包含 data URI 或纯 base64）",
                    "prompt": "分析提示词（可选）"
                }
            },
            {
                "method": "POST",
                "path": "/api/analyze/url",
                "description": "通过图片 URL 进行分析",
                "content_type": "application/json",
                "parameters": {
                    "url": "图片 URL（必填）",
                    "prompt": "分析提示词（可选）"
                }
            }
        ]
    }))


@app.route('/api/analyze', methods=['POST'])

def analyze_upload():
    """
    上传图片文件进行分析
    支持: multipart/form-data
    """
    ip = get_client_ip()
    
    # 限流检查
    if not check_rate_limit(ip):
        log_request(ip, '/api/analyze', 429)
        return add_security_headers(jsonify({
            "success": False,
            "error": "Rate limit exceeded. Max 60 requests per minute.",
            "code": "RATE_LIMITED"
        })), 429
    
    # 检查图片
    if 'image' not in request.files:
        log_request(ip, '/api/analyze', 400)
        return add_security_headers(jsonify({
            "success": False,
            "error": "Missing 'image' file in form data",
            "code": "MISSING_IMAGE"
        })), 400
    
    file = request.files['image']
    
    if file.filename == '':
        log_request(ip, '/api/analyze', 400)
        return add_security_headers(jsonify({
            "success": False,
            "error": "Empty filename",
            "code": "MISSING_IMAGE"
        })), 400
    
    # 读取图片数据
    image_data = file.read()
    
    # 检查文件大小（最大 10MB）
    if len(image_data) > 10 * 1024 * 1024:
        log_request(ip, '/api/analyze', 413)
        return add_security_headers(jsonify({
            "success": False,
            "error": "Image too large. Max 10MB.",
            "code": "INVALID_IMAGE"
        })), 413
    
    # 基本图片内容验证（检查文件头）
    if len(image_data) < 12:
        log_request(ip, '/api/analyze', 400)
        return add_security_headers(jsonify({
            "success": False,
            "error": "Invalid image data",
            "code": "INVALID_IMAGE"
        })), 400
    
    # 验证图片魔数
    valid_magic = [
        b'\x89PNG\r\n\x1a\n',  # PNG
        b'\xff\xd8\xff',         # JPEG
        b'GIF8',                # GIF
        b'RIFF',                # WEBP (需要二次验证)
        b'BM',                  # BMP
    ]
    is_valid = any(image_data.startswith(magic) for magic in valid_magic)
    
    # WEBP 特殊检查
    if image_data.startswith(b'RIFF') and not image_data[8:12] == b'WEBP':
        is_valid = False
    
    if not is_valid:
        log_request(ip, '/api/analyze', 400)
        return add_security_headers(jsonify({
            "success": False,
            "error": "Invalid image format",
            "code": "INVALID_IMAGE"
        })), 400
    
    # 获取并消毒提示词
    raw_prompt = request.form.get('prompt', '请详细描述这张图片的全部内容，包括：主要对象、背景、颜色、任何可见的文字、整体布局等。')
    prompt = sanitize_prompt(raw_prompt)
    
    # 获取返回格式
    output_format = request.form.get('format', 'json')
    
    # 保存临时文件
    temp_path = save_image(image_data)
    
    try:
        result = call_mcp_understand_image(temp_path, prompt)
        
        log_request(ip, '/api/analyze', 200)
        
        if output_format == 'text':
            return add_security_headers(Response(result, mimetype='text/plain'))
        
        return add_security_headers(jsonify({
            "success": True,
            "result": result,
            "metadata": {
                "size": len(image_data),
                "model": "MiniMax-MCP"
            }
        }))
    
    except Exception as e:
        log_request(ip, '/api/analyze', 500)
        return add_security_headers(jsonify({
            "success": False,
            "error": "Analysis failed",
            "code": "ANALYSIS_ERROR"
        })), 500
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.route('/api/analyze/base64', methods=['POST'])

def analyze_base64():
    """
    Base64 图片分析
    支持: application/json
    """
    ip = get_client_ip()
    
    if not check_rate_limit(ip):
        return add_security_headers(jsonify({
            "success": False,
            "error": "Rate limit exceeded. Max 60 requests per minute.",
            "code": "RATE_LIMITED"
        })), 429
    
    data = request.get_json()
    
    if not data or 'image' not in data:
        return add_security_headers(jsonify({
            "success": False,
            "error": "Missing 'image' field in JSON body",
            "code": "MISSING_IMAGE"
        })), 400
    
    image_b64 = data['image']
    raw_prompt = data.get('prompt', '请详细描述这张图片的全部内容，包括：主要对象、背景、颜色、任何可见的文字、整体布局等。')
    prompt = sanitize_prompt(raw_prompt)
    output_format = data.get('format', 'json')
    
    # 解析 base64（支持带 data URI 或纯 base64）
    if ',' in image_b64:
        # data:image/jpeg;base64,/9j/4AAQ...
        image_b64 = image_b64.split(',', 1)[1]
    
    try:
        image_data = base64.b64decode(image_b64)
    except Exception:
        return add_security_headers(jsonify({
            "success": False,
            "error": "Invalid base64 data",
            "code": "INVALID_IMAGE"
        })), 400
    
    # 检查大小
    if len(image_data) > 10 * 1024 * 1024:
        return add_security_headers(jsonify({
            "success": False,
            "error": "Image too large. Max 10MB.",
            "code": "INVALID_IMAGE"
        })), 413
    
    temp_path = save_image(image_data)
    
    try:
        result = call_mcp_understand_image(temp_path, prompt)
        
        if output_format == 'text':
            return add_security_headers(Response(result, mimetype='text/plain'))
        
        return add_security_headers(jsonify({
            "success": True,
            "result": result,
            "metadata": {
                "size": len(image_data),
                "model": "MiniMax-MCP"
            }
        }))
    
    except Exception as e:
        return add_security_headers(jsonify({
            "success": False,
            "error": "Analysis failed",
            "code": "ANALYSIS_ERROR"
        })), 500
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.route('/api/analyze/url', methods=['POST'])

def analyze_url():
    """
    URL 图片分析（带 SSRF 防护）
    支持: application/json
    """
    ip = get_client_ip()
    
    if not check_rate_limit(ip):
        return add_security_headers(jsonify({
            "success": False,
            "error": "Rate limit exceeded. Max 60 requests per minute.",
            "code": "RATE_LIMITED"
        })), 429
    
    data = request.get_json()
    
    if not data or 'url' not in data:
        return add_security_headers(jsonify({
            "success": False,
            "error": "Missing 'url' field in JSON body",
            "code": "MISSING_IMAGE"
        })), 400
    
    image_url = data['url']
    raw_prompt = data.get('prompt', '请详细描述这张图片的全部内容，包括：主要对象、背景、颜色、任何可见的文字、整体布局等。')
    prompt = sanitize_prompt(raw_prompt)
    output_format = data.get('format', 'json')
    
    # SSRF 防护：验证 URL
    from urllib.parse import urlparse
    
    try:
        parsed = urlparse(image_url)
        
        # 只允许 HTTP 和 HTTPS
        if parsed.scheme not in ('http', 'https'):
            return add_security_headers(jsonify({
                "success": False,
                "error": "Only HTTP and HTTPS URLs are allowed",
                "code": "INVALID_IMAGE"
            })), 400
        
        # 解析主机名
        hostname = parsed.hostname
        if not hostname:
            return add_security_headers(jsonify({
                "success": False,
                "error": "Invalid URL",
                "code": "INVALID_IMAGE"
            })), 400
        
        # 阻止私有 IP 访问
        # 先解析域名到 IP
        import socket
        try:
            resolved_ips = socket.getaddrinfo(hostname, None)
            for res in resolved_ips:
                ip_addr = res[4][0]
                if is_ip_blocked(ip_addr):
                    return add_security_headers(jsonify({
                        "success": False,
                        "error": "URL points to blocked address",
                        "code": "INVALID_IMAGE"
                    })), 400
        except socket.gaierror:
            return add_security_headers(jsonify({
                "success": False,
                "error": "Could not resolve hostname",
                "code": "INVALID_IMAGE"
            })), 400
        
        # 直接检查 hostname 是否是 IP 地址（绕过 DNS 解析的情况）
        if is_ip_blocked(hostname):
            return add_security_headers(jsonify({
                "success": False,
                "error": "URL points to blocked address",
                "code": "INVALID_IMAGE"
            })), 400
        
    except Exception as e:
        return add_security_headers(jsonify({
            "success": False,
            "error": "Invalid URL format",
            "code": "INVALID_IMAGE"
        })), 400
    
    # 下载图片
    import urllib.request
    import ssl
    
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(
            image_url,
            headers={'User-Agent': 'Mozilla/5.0 MiniMax-Vision-API/2.0'}
        )
        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            image_data = response.read()
    except Exception as e:
        return add_security_headers(jsonify({
            "success": False,
            "error": "Failed to download image",
            "code": "INVALID_IMAGE"
        })), 400
    
    # 检查大小
    if len(image_data) > 10 * 1024 * 1024:
        return add_security_headers(jsonify({
            "success": False,
            "error": "Image too large. Max 10MB.",
            "code": "INVALID_IMAGE"
        })), 413
    
    temp_path = save_image(image_data)
    
    try:
        result = call_mcp_understand_image(temp_path, prompt)
        
        if output_format == 'text':
            return add_security_headers(Response(result, mimetype='text/plain'))
        
        return add_security_headers(jsonify({
            "success": True,
            "result": result,
            "metadata": {
                "source_url": parsed.netloc,  # 只记录域名，不记录完整 URL
                "size": len(image_data),
                "model": "MiniMax-MCP"
            }
        }))
    
    except Exception as e:
        return add_security_headers(jsonify({
            "success": False,
            "error": "Analysis failed",
            "code": "ANALYSIS_ERROR"
        })), 500
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# ============== 对话历史存储 ==============
chat_histories = {}  # {session_id: [{"role": "user/assistant", "content": "...", "image": "..."}, ...]}
chat_max_history = 20  # 最多保留 20 条对话


def call_minimax_chat_stream(messages: list, session_id: str = None):
    """
    调用天行AI 聊天 API (OpenAI 兼容格式) - 流式版本
    messages: [{"role": "user/assistant", "content": "..."}, ...]
    使用 SSE (Server-Sent Events) yield 每个 token
    """
    import urllib.request
    import urllib.error
    import ssl
    
    if not CHAT_API_KEY:
        raise Exception("CHAT_API_KEY not configured")
    
    # 构建 API 请求
    url = f"{CHAT_API_HOST}/chat/completions"
    
    # 构建纯文本消息（图片已转换为文字）
    formatted_messages = []
    for msg in messages:
        if isinstance(msg, dict):
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if content:  # 只添加有内容的消息
                formatted_messages.append({"role": role, "content": content})
        else:
            formatted_messages.append({"role": "user", "content": str(msg)})
    
    payload = {
        "model": "MiniMax-M2.7-highspeed",
        "messages": formatted_messages,
        "max_tokens": 2000,
        "temperature": 0.7,
        "stream": True  # 启用流式输出
    }
    
    headers = {
        "Authorization": f"Bearer {CHAT_API_KEY}",
        "Content-Type": "application/json"
    }
    
    ctx = ssl.create_default_context()
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, context=ctx, timeout=120) as response:
            # 流式读取响应
            for line in response:
                line = line.decode('utf-8').strip()
                if not line:
                    continue
                if line.startswith('data: '):
                    data_str = line[6:]  # Remove 'data: ' prefix
                    if data_str == '[DONE]':
                        break
                    try:
                        chunk = json.loads(data_str)
                        if 'choices' in chunk and len(chunk['choices']) > 0:
                            delta = chunk['choices'][0].get('delta', {})
                            content = delta.get('reasoning_content') or delta.get('content', '')
                            if content:
                                yield f"data: {json.dumps({'content': content})}\n\n"
                    except json.JSONDecodeError:
                        continue
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else str(e)
        yield f"data: {json.dumps({'error': f'API Error {e.code}: {error_body}'})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': f'Chat API Error: {str(e)}'})}\n\n"


def call_minimax_chat(messages: list, session_id: str = None) -> str:
    """
    调用天行AI 聊天 API (OpenAI 兼容格式)
    messages: [{"role": "user/assistant", "content": "..."}, ...]
    注意: 图片已在前端通过 MCP 分析为文字，这里只处理纯文本
    """
    import urllib.request
    import urllib.error
    import ssl
    
    if not CHAT_API_KEY:
        raise Exception("CHAT_API_KEY not configured")
    
    # 构建 API 请求
    url = f"{CHAT_API_HOST}/chat/completions"
    
    # 构建纯文本消息（图片已转换为文字）
    formatted_messages = []
    for msg in messages:
        if isinstance(msg, dict):
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if content:  # 只添加有内容的消息
                formatted_messages.append({"role": role, "content": content})
        else:
            formatted_messages.append({"role": "user", "content": str(msg)})
    
    payload = {
        "model": "MiniMax-M2.7-highspeed",
        "messages": formatted_messages,
        "max_tokens": 2000,
        "temperature": 0.7
    }
    
    headers = {
        "Authorization": f"Bearer {CHAT_API_KEY}",
        "Content-Type": "application/json"
    }
    
    ctx = ssl.create_default_context()
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, context=ctx, timeout=120) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if 'choices' in result and len(result['choices']) > 0:
                message = result['choices'][0]['message']
                # 天行AI 把内容放在 reasoning_content 而不是 content
                content = message.get('content') or message.get('reasoning_content', '')
                return content
            else:
                raise Exception(f"Unexpected API response: {result}")
    
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else str(e)
        raise Exception(f"API Error {e.code}: {error_body}")
    except Exception as e:
        raise Exception(f"Chat API Error: {str(e)}")


@app.route('/api/chat/stream', methods=['POST'])

def chat_stream():
    """
    智能对话接口 - 流式版本 (SSE)
    支持多轮对话和图片分析
    """
    ip = get_client_ip()
    
    if not check_rate_limit(ip, max_requests=30):  # 对话接口更严格的限流
        return add_security_headers(Response(
            f"data: {json.dumps({'error': 'Rate limit exceeded. Max 30 requests per minute.', 'code': 'RATE_LIMITED'})}\n\n",
            mimetype='text/event-stream'
        )), 429
    
    data = request.get_json()
    
    if not data or 'message' not in data:
        return add_security_headers(Response(
            f"data: {json.dumps({'error': 'Missing message field', 'code': 'INVALID_REQUEST'})}\n\n",
            mimetype='text/event-stream'
        )), 400
    
    # 限制消息长度
    user_message = sanitize_prompt(data['message'], max_length=4000)
    image_data = data.get('image')  # 可选的 base64 图片
    
    # 处理 session_id：如果是新建会话或为空，生成 UUID
    provided_session_id = data.get('session_id')
    if not provided_session_id:
        session_id = str(uuid.uuid4())
        is_new_session = True
    else:
        # 验证 session_id 格式（只允许字母数字和连字符）
        if not all(c.isalnum() or c in '-_' for c in provided_session_id):
            return add_security_headers(Response(
                f"data: {json.dumps({'error': 'Invalid session_id format', 'code': 'INVALID_REQUEST'})}\n\n",
                mimetype='text/event-stream'
            )), 400
        session_id = provided_session_id
        is_new_session = False
    
    # 首先发送 session_id
    def generate():
        # 发送 session_id 事件
        yield f"data: {json.dumps({'type': 'session_id', 'session_id': session_id})}\n\n"
        
        # 获取或创建会话历史
        if session_id not in chat_histories:
            chat_histories[session_id] = []
        
        history = chat_histories[session_id]
        
        # 如果有系统提示词且是新建会话，添加系统消息
        if is_new_session and len(history) == 0:
            system_prompt = "你是一个智能图片分析助手，名叫慧眼，由六仙云开发。用户会发送图片或文字消息，你可以分析图片内容并回答用户的问题。你专业、友好、乐于助人。如果用户发送图片，请仔细分析图片内容并给出详细描述。如果用户只是问问题，直接回答即可。记住：你的名字是慧眼，开发方是六仙云。如果有人问你是哪个模型，请回答你是慧眼模型。"
            history.append({
                "role": "system",
                "content": system_prompt
            })
        
        # 如果有图片，先用视觉分析后端分析图片
        final_message = user_message
        if image_data:
            try:
                # 保存图片到临时文件
                # 处理 data URL 或纯 base64
                if ',' in image_data:
                    img_base64 = image_data.split(',')[1]
                else:
                    img_base64 = image_data
                
                img_bytes = base64.b64decode(img_base64)
                temp_path = save_image(img_bytes)
                
                # 调用视觉分析 API
                image_analysis = call_mcp_understand_image(
                    temp_path, 
                    "请详细描述这张图片的全部内容，包括：主要对象、背景、颜色、文字、布局等。"
                )
                
                # 清理临时文件
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
                # 把图片分析结果拼到消息前面
                final_message = f"【图片分析】{image_analysis}\n\n【用户消息】{user_message}"
                
            except Exception as e:
                # 视觉分析失败，记录日志
                log_request(ip, '/api/chat/stream/image_analysis', 500)
                final_message = f"【图片分析失败】\n\n【用户消息】{user_message}"
        
        # 添加用户消息
        user_msg = {
            "role": "user", 
            "content": final_message
        }
        
        history.append(user_msg)
        
        # 限制历史长度
        while len(history) > chat_max_history:
            # 保留 system 消息
            if history[0]["role"] == "system":
                history = [history[0]] + history[2:]
            else:
                history = history[2:]
        
        full_response = ""
        try:
            # 调用流式 MiniMax API
            for chunk in call_minimax_chat_stream(history, session_id):
                # 解析并发送内容
                try:
                    chunk_data = json.loads(chunk.replace("data: ", "").strip())
                    if 'content' in chunk_data:
                        full_response += chunk_data['content']
                        yield f"data: {json.dumps({'type': 'content', 'content': chunk_data['content']})}\n\n"
                    elif 'error' in chunk_data:
                        yield f"data: {json.dumps({'type': 'error', 'error': chunk_data['error']})}\n\n"
                        return
                except json.JSONDecodeError:
                    continue
            
            # 添加助手回复到历史
            history.append({
                "role": "assistant",
                "content": full_response
            })
            
            log_request(ip, '/api/chat/stream', 200)
            
            # 发送完成事件
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        
        except Exception as e:
            log_request(ip, '/api/chat/stream', 500)
            # 出错时移除用户消息
            if user_msg in history:
                history.remove(user_msg)
            yield f"data: {json.dumps({'type': 'error', 'error': 'Chat service temporarily unavailable'})}\n\n"
    
    return add_security_headers(Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'  # 禁用 nginx 缓冲
        }
    ))


@app.route('/api/chat', methods=['POST'])

def chat():
    """
    智能对话接口
    支持多轮对话和图片分析
    """
    ip = get_client_ip()
    
    if not check_rate_limit(ip, max_requests=30):  # 对话接口更严格的限流
        return add_security_headers(jsonify({
            "success": False,
            "error": "Rate limit exceeded. Max 30 requests per minute.",
            "code": "RATE_LIMITED"
        })), 429
    
    data = request.get_json()
    
    if not data or 'message' not in data:
        return add_security_headers(jsonify({
            "success": False,
            "error": 'Missing message field',
            "code": "INVALID_REQUEST"
        })), 400
    
    # 限制消息长度
    user_message = sanitize_prompt(data['message'], max_length=4000)
    image_data = data.get('image')  # 可选的 base64 图片
    
    # 处理 session_id：如果是新建会话或为空，生成 UUID
    provided_session_id = data.get('session_id')
    if not provided_session_id:
        session_id = str(uuid.uuid4())
        is_new_session = True
    else:
        # 验证 session_id 格式（只允许字母数字和连字符）
        if not all(c.isalnum() or c in '-_' for c in provided_session_id):
            return add_security_headers(jsonify({
                "success": False,
                "error": "Invalid session_id format",
                "code": "INVALID_REQUEST"
            })), 400
        session_id = provided_session_id
        is_new_session = False
    
    # 获取或创建会话历史
    if session_id not in chat_histories:
        chat_histories[session_id] = []
    
    history = chat_histories[session_id]
    
    # 如果有系统提示词且是新建会话，添加系统消息
    if is_new_session and len(history) == 0:
        system_prompt = "你是一个智能图片分析助手，名叫慧眼，由六仙云开发。用户会发送图片或文字消息，你可以分析图片内容并回答用户的问题。你专业、友好、乐于助人。如果用户发送图片，请仔细分析图片内容并给出详细描述。如果用户只是问问题，直接回答即可。记住：你的名字是慧眼，开发方是六仙云。如果有人问你是哪个模型，请回答你是慧眼模型。"
        history.append({
            "role": "system",
            "content": system_prompt
        })
    
    # 如果有图片，先用视觉分析后端分析图片
    if image_data:
        try:
            # 保存图片到临时文件
            # 处理 data URL 或纯 base64
            if ',' in image_data:
                img_base64 = image_data.split(',')[1]
            else:
                img_base64 = image_data
            
            img_bytes = base64.b64decode(img_base64)
            temp_path = save_image(img_bytes)
            
            # 调用视觉分析 API
            image_analysis = call_mcp_understand_image(
                temp_path, 
                "请详细描述这张图片的全部内容，包括：主要对象、背景、颜色、文字、布局等。"
            )
            
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            # 把图片分析结果拼到消息前面
            final_message = f"【图片分析】{image_analysis}\n\n【用户消息】{user_message}"
            
        except Exception as e:
            # 视觉分析失败，记录日志但不暴露给用户
            log_request(ip, '/api/chat/image_analysis', 500)
            final_message = f"【图片分析失败】\n\n【用户消息】{user_message}"
    
    # 添加用户消息
    user_msg = {
        "role": "user", 
        "content": final_message
    }
    
    history.append(user_msg)
    
    # 限制历史长度
    while len(history) > chat_max_history:
        # 保留 system 消息
        if history[0]["role"] == "system":
            history = [history[0]] + history[2:]
        else:
            history = history[2:]
    
    try:
        # 调用 MiniMax API
        response_text = call_minimax_chat(history, session_id)
        
        # 添加助手回复到历史
        history.append({
            "role": "assistant",
            "content": response_text
        })
        
        log_request(ip, '/api/chat', 200)
        
        return add_security_headers(jsonify({
            "success": True,
            "response": response_text,
            "session_id": session_id,
            "history": [
                {"role": msg["role"], "content": msg["content"]}
                for msg in history if msg["role"] != "system"
            ]
        }))
    
    except Exception as e:
        log_request(ip, '/api/chat', 500)
        # 出错时移除用户消息
        if user_msg in history:
            history.remove(user_msg)
        
        return add_security_headers(jsonify({
            "success": False,
            "error": "Chat service temporarily unavailable",
            "code": "CHAT_ERROR"
        })), 500


@app.route('/api/chat/history', methods=['GET'])

def get_chat_history():
    """获取对话历史"""
    session_id = request.args.get('session_id', '')
    
    # 验证 session_id 格式
    if session_id and not all(c.isalnum() or c in '-_' for c in session_id):
        return add_security_headers(jsonify({
            "success": False,
            "error": "Invalid session_id format",
            "code": "INVALID_REQUEST"
        })), 400
    
    if not session_id or session_id not in chat_histories:
        return add_security_headers(jsonify({
            "success": True,
            "session_id": session_id,
            "history": []
        }))
    
    return add_security_headers(jsonify({
        "success": True,
        "session_id": session_id,
        "history": [
            {"role": msg["role"], "content": msg["content"]}
            for msg in chat_histories[session_id] if msg["role"] != "system"
        ]
    }))


@app.route('/api/chat/clear', methods=['POST'])

def clear_chat():
    """清除对话历史"""
    data = request.get_json() or {}
    session_id = data.get('session_id', '')
    
    # 验证 session_id 格式
    if session_id and not all(c.isalnum() or c in '-_' for c in session_id):
        return add_security_headers(jsonify({
            "success": False,
            "error": "Invalid session_id format",
            "code": "INVALID_REQUEST"
        })), 400
    
    if session_id and session_id in chat_histories:
        chat_histories[session_id] = []
    
    return add_security_headers(jsonify({
        "success": True,
        "message": "Session cleared" if session_id else "All sessions cleared"
    }))


# ============== 启动 ==============

if __name__ == '__main__':
    print("=" * 60)
    print("  MiniMax Vision API v2.1.0")
    print("=" * 60)
    print(f"  MiniMax API Host: {MINIMAX_API_HOST}")
    print(f"  API Key Set:      {'Yes' if API_KEY else 'No (unsecured)'}")
    print(f"  Debug Mode:       {DEBUG}")
    print("=" * 60)
    print()
    print("  Endpoints:")
    print("    POST /api/analyze          - Upload image file")
    print("    POST /api/analyze/base64   - Base64 image")
    print("    POST /api/analyze/url      - Image URL")
    print("    POST /api/chat             - AI 对话")
    print("    GET  /api/chat/history    - 获取对话历史")
    print("    POST /api/chat/clear      - 清除对话历史")
    print("    GET  /api/health          - 健康检查")
    print("    GET  /api/health/detailed - 详细健康检查")
    print("    GET  /api/metrics         - Prometheus 指标")
    print("    GET  /api/metrics/json    - JSON 指标")
    print("    GET  /api/alerts          - 当前告警状态")
    print("    GET  /api/docs            - API 文档")
    print()
    print("=" * 60)
    
    if not MINIMAX_API_KEY:
        print("  WARNING: MINIMAX_API_KEY not set!")
        print("  Set with: export MINIMAX_API_KEY=your_key")
        print()
    
    # 使用 5001 端口（5000 被占用）
    app.run(host='0.0.0.0', port=5001, debug=DEBUG)
