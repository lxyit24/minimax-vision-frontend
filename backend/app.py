"""
MiniMax Vision Backend - Flask API
调用 MiniMax MCP 工具进行图片理解
"""

import os
import json
import base64
import tempfile
from subprocess import Popen, PIPE
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# MiniMax API Key (从环境变量读取)
MINIMAX_API_KEY = os.environ.get('MINIMAX_API_KEY', '')
MINIMAX_API_HOST = os.environ.get('MINIMAX_API_HOST', 'https://api.minimaxi.com')


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


@app.route('/')
def index():
    return jsonify({
        "name": "MiniMax Vision API",
        "version": "1.0.0",
        "endpoints": {
            "POST /analyze": "上传图片并获取分析结果",
            "GET /health": "健康检查"
        }
    })


@app.route('/health')
def health():
    return jsonify({"status": "ok"})


@app.route('/analyze', methods=['POST'])
def analyze():
    """
    接收图片文件，调用 MiniMax MCP 进行分析
    """
    if 'image' not in request.files:
        return jsonify({"error": "未找到图片文件"}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({"error": "文件名为空"}), 400
    
    # 保存到临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as f:
        temp_path = f.name
        file.save(temp_path)
    
    try:
        # 获取提示词（可选）
        prompt = request.form.get('prompt', '请详细描述这张图片的全部内容，包括：主要对象、背景、颜色、任何可见的文字、整体布局等。')
        
        # 调用 MCP 工具
        result = call_mcp_understand_image(temp_path, prompt)
        
        return jsonify({
            "success": True,
            "result": result
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    
    finally:
        # 删除临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == '__main__':
    print("=" * 50)
    print("MiniMax Vision Backend")
    print("=" * 50)
    print(f"MiniMax API Host: {MINIMAX_API_HOST}")
    print(f"API Key: {MINIMAX_API_KEY[:10]}..." if MINIMAX_API_KEY else "API Key: NOT SET")
    print("=" * 50)
    
    if not MINIMAX_API_KEY:
        print("警告: MINIMAX_API_KEY 环境变量未设置!")
        print("请设置: export MINIMAX_API_KEY=your_key")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
