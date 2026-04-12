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
from datetime import datetime, timedelta
from functools import wraps
from subprocess import Popen, PIPE
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ============== 配置 ==============
MINIMAX_API_KEY = os.environ.get('MINIMAX_API_KEY', '')
MINIMAX_API_HOST = os.environ.get('MINIMAX_API_HOST', 'https://api.minimaxi.com')
API_KEY = os.environ.get('API_KEY', '')  # 外部 API 密钥
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'

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
        # 如果没设置 API_KEY，跳过验证
        if not API_KEY:
            return f(*args, **kwargs)
        
        provided_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        if not provided_key:
            return jsonify({
                "success": False,
                "error": "Missing API key",
                "code": "MISSING_API_KEY"
            }), 401
        
        if provided_key != API_KEY:
            return jsonify({
                "success": False,
                "error": "Invalid API key",
                "code": "INVALID_API_KEY"
            }), 403
        
        return f(*args, **kwargs)
    return decorated


def log_request(ip: str, endpoint: str, status: int):
    """记录请求日志"""
    if DEBUG:
        print(f"[{datetime.now().isoformat()}] {ip} -> {endpoint} [{status}]")


# ============== 核心功能 ==============

def call_mcp_understand_image(image_path: str, prompt: str = "请详细描述这张图片的内容") -> str:
    """
    调用 MiniMax MCP 工具 understand_image
    """
    uvx_path = "/root/.local/bin/uvx"
    
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
        [uvx_path, "minimax-coding-plan-mcp", "-y"],
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
    return jsonify({
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
        },
        "authentication": {
            "type": "X-API-Key header",
            "env_var": "API_KEY"
        }
    })


@app.route('/api/health')
def health():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "services": {
            "minimax_api": "connected" if MINIMAX_API_KEY else "not_configured"
        }
    })


@app.route('/api/docs')
def docs():
    """简易 API 文档"""
    return jsonify({
        "title": "MiniMax Vision API 文档",
        "version": "2.0.0",
        "base_url": request.host_url.rstrip('/'),
        "authentication": {
            "method": "X-API-Key",
            "description": "在请求头中传递 API 密钥",
            "example": "X-API-Key: your-api-key"
        },
        "endpoints": [
            {
                "method": "POST",
                "path": "/api/analyze",
                "description": "上传图片文件进行分析",
                "content_type": "multipart/form-data",
                "parameters": {
                    "image": "图片文件（必填）",
                    "prompt": "分析提示词（可选，默认中文详细描述）",
                    "api_key": "API密钥（可选，header优先）"
                },
                "example": {
                    "curl": '''curl -X POST https://your-domain.com/api/analyze \\
  -H "X-API-Key: your-key" \\
  -F "image=@photo.jpg" \\
  -F "prompt=请描述这张图片"'''
                }
            },
            {
                "method": "POST",
                "path": "/api/analyze/base64",
                "description": "发送 Base64 编码的图片进行分析",
                "content_type": "application/json",
                "parameters": {
                    "image": "Base64 字符串（必填，需包含 data URI 或纯 base64）",
                    "prompt": "分析提示词（可选）",
                    "format": "返回格式，text 或 json（默认 json）"
                },
                "example": {
                    "request": {
                        "image": "data:image/jpeg;base64,/9j/4AAQ...",
                        "prompt": "请详细描述",
                        "format": "json"
                    }
                }
            },
            {
                "method": "POST",
                "path": "/api/analyze/url",
                "description": "通过图片 URL 进行分析",
                "content_type": "application/json",
                "parameters": {
                    "url": "图片 URL（必填）",
                    "prompt": "分析提示词（可选）",
                    "format": "返回格式，text 或 json（默认 json）"
                }
            }
        ],
        "response_formats": {
            "json": {
                "success": True,
                "result": "分析结果文本",
                "metadata": {
                    "model": "minimax-image-01",
                    "prompt": "使用的提示词"
                }
            },
            "text": {
                "type": "text",
                "content": "分析结果纯文本"
            }
        },
        "error_codes": {
            "MISSING_API_KEY": "未提供 API 密钥",
            "INVALID_API_KEY": "API 密钥无效",
            "RATE_LIMITED": "请求过于频繁",
            "MISSING_IMAGE": "未提供图片",
            "INVALID_IMAGE": "图片格式无效",
            "ANALYSIS_ERROR": "分析失败"
        }
    })


@app.route('/api/analyze', methods=['POST'])
@require_api_key
def analyze_upload():
    """
    上传图片文件进行分析
    支持: multipart/form-data
    """
    ip = request.remote_addr
    
    # 限流检查
    if not check_rate_limit(ip):
        log_request(ip, '/api/analyze', 429)
        return jsonify({
            "success": False,
            "error": "Rate limit exceeded. Max 60 requests per minute.",
            "code": "RATE_LIMITED"
        }), 429
    
    # 检查图片
    if 'image' not in request.files:
        log_request(ip, '/api/analyze', 400)
        return jsonify({
            "success": False,
            "error": "Missing 'image' file in form data",
            "code": "MISSING_IMAGE"
        }), 400
    
    file = request.files['image']
    
    if file.filename == '':
        log_request(ip, '/api/analyze', 400)
        return jsonify({
            "success": False,
            "error": "Empty filename",
            "code": "MISSING_IMAGE"
        }), 400
    
    # 读取图片数据
    image_data = file.read()
    
    # 检查文件大小（最大 10MB）
    if len(image_data) > 10 * 1024 * 1024:
        log_request(ip, '/api/analyze', 413)
        return jsonify({
            "success": False,
            "error": "Image too large. Max 10MB.",
            "code": "INVALID_IMAGE"
        }), 413
    
    # 获取提示词
    prompt = request.form.get('prompt', '请详细描述这张图片的全部内容，包括：主要对象、背景、颜色、任何可见的文字、整体布局等。')
    
    # 获取返回格式
    output_format = request.form.get('format', 'json')
    
    # 保存临时文件
    temp_path = save_image(image_data)
    
    try:
        result = call_mcp_understand_image(temp_path, prompt)
        
        log_request(ip, '/api/analyze', 200)
        
        if output_format == 'text':
            return Response(result, mimetype='text/plain')
        
        return jsonify({
            "success": True,
            "result": result,
            "metadata": {
                "filename": file.filename,
                "size": len(image_data),
                "prompt": prompt,
                "model": "MiniMax-MCP"
            }
        })
    
    except Exception as e:
        log_request(ip, '/api/analyze', 500)
        return jsonify({
            "success": False,
            "error": str(e),
            "code": "ANALYSIS_ERROR"
        }), 500
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.route('/api/analyze/base64', methods=['POST'])
@require_api_key
def analyze_base64():
    """
    Base64 图片分析
    支持: application/json
    """
    ip = request.remote_addr
    
    if not check_rate_limit(ip):
        return jsonify({
            "success": False,
            "error": "Rate limit exceeded. Max 60 requests per minute.",
            "code": "RATE_LIMITED"
        }), 429
    
    data = request.get_json()
    
    if not data or 'image' not in data:
        return jsonify({
            "success": False,
            "error": "Missing 'image' field in JSON body",
            "code": "MISSING_IMAGE"
        }), 400
    
    image_b64 = data['image']
    prompt = data.get('prompt', '请详细描述这张图片的全部内容，包括：主要对象、背景、颜色、任何可见的文字、整体布局等。')
    output_format = data.get('format', 'json')
    
    # 解析 base64（支持带 data URI 或纯 base64）
    if ',' in image_b64:
        # data:image/jpeg;base64,/9j/4AAQ...
        image_b64 = image_b64.split(',', 1)[1]
    
    try:
        image_data = base64.b64decode(image_b64)
    except Exception:
        return jsonify({
            "success": False,
            "error": "Invalid base64 data",
            "code": "INVALID_IMAGE"
        }), 400
    
    # 检查大小
    if len(image_data) > 10 * 1024 * 1024:
        return jsonify({
            "success": False,
            "error": "Image too large. Max 10MB.",
            "code": "INVALID_IMAGE"
        }), 413
    
    temp_path = save_image(image_data)
    
    try:
        result = call_mcp_understand_image(temp_path, prompt)
        
        if output_format == 'text':
            return Response(result, mimetype='text/plain')
        
        return jsonify({
            "success": True,
            "result": result,
            "metadata": {
                "size": len(image_data),
                "prompt": prompt,
                "model": "MiniMax-MCP"
            }
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "code": "ANALYSIS_ERROR"
        }), 500
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.route('/api/analyze/url', methods=['POST'])
@require_api_key
def analyze_url():
    """
    URL 图片分析
    支持: application/json
    """
    ip = request.remote_addr
    
    if not check_rate_limit(ip):
        return jsonify({
            "success": False,
            "error": "Rate limit exceeded. Max 60 requests per minute.",
            "code": "RATE_LIMITED"
        }), 429
    
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({
            "success": False,
            "error": "Missing 'url' field in JSON body",
            "code": "MISSING_IMAGE"
        }), 400
    
    image_url = data['url']
    prompt = data.get('prompt', '请详细描述这张图片的全部内容，包括：主要对象、背景、颜色、任何可见的文字、整体布局等。')
    output_format = data.get('format', 'json')
    
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
        return jsonify({
            "success": False,
            "error": f"Failed to download image: {str(e)}",
            "code": "INVALID_IMAGE"
        }), 400
    
    # 检查大小
    if len(image_data) > 10 * 1024 * 1024:
        return jsonify({
            "success": False,
            "error": "Image too large. Max 10MB.",
            "code": "INVALID_IMAGE"
        }), 413
    
    temp_path = save_image(image_data)
    
    try:
        result = call_mcp_understand_image(temp_path, prompt)
        
        if output_format == 'text':
            return Response(result, mimetype='text/plain')
        
        return jsonify({
            "success": True,
            "result": result,
            "metadata": {
                "source_url": image_url,
                "size": len(image_data),
                "prompt": prompt,
                "model": "MiniMax-MCP"
            }
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "code": "ANALYSIS_ERROR"
        }), 500
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# ============== 启动 ==============

if __name__ == '__main__':
    print("=" * 60)
    print("  MiniMax Vision API v2.0.0")
    print("=" * 60)
    print(f"  MiniMax API Host: {MINIMAX_API_HOST}")
    print(f"  API Key Set:      {'Yes' if API_KEY else 'No (unsecured)'}")
    print(f"  Debug Mode:       {DEBUG}")
    print("=" * 60)
    print()
    print("  Endpoints:")
    print("    POST /api/analyze         - Upload image file")
    print("    POST /api/analyze/base64  - Base64 image")
    print("    POST /api/analyze/url     - Image URL")
    print("    GET  /api/health          - Health check")
    print("    GET  /api/docs            - API documentation")
    print()
    print("=" * 60)
    
    if not MINIMAX_API_KEY:
        print("  WARNING: MINIMAX_API_KEY not set!")
        print("  Set with: export MINIMAX_API_KEY=your_key")
        print()
    
    # 使用 5001 端口（5000 被占用）
    app.run(host='0.0.0.0', port=5001, debug=DEBUG)
