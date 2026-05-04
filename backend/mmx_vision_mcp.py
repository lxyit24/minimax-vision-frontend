#!/usr/bin/env python3
"""
MiniMax Vision MCP Server
 Wraps mmx-cli vision command as an MCP server
"""

import json
import subprocess
import sys
import os

def handle_initialize(params):
    """Handle initialize request"""
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {"tools": {}},
        "serverInfo": {"name": "minimax-vision-mcp", "version": "1.0.0"}
    }

def handle_tools_call(params):
    """Handle tools/call request"""
    name = params.get("name")
    arguments = params.get("arguments", {})
    
    if name == "understand_image":
        image_source = arguments.get("image_source")
        prompt = arguments.get("prompt", "请详细描述这张图片的内容")
        
        if not image_source:
            return {"content": [{"type": "text", "text": "错误: 缺少 image_source 参数"}]}
        
        # Call mmx vision command
        try:
            result = subprocess.run(
                ["mmx", "vision", image_source, "--prompt", prompt],
                capture_output=True,
                text=True,
                timeout=60,
                env={**os.environ, "MINIMAX_API_KEY": os.environ.get("MINIMAX_API_KEY", "")}
            )
            
            if result.returncode == 0:
                output = json.loads(result.stdout)
                # Extract content from mmx output
                if "content" in output:
                    return {"content": [{"type": "text", "text": output["content"]}]}
                elif "error" in output:
                    return {"content": [{"type": "text", "text": f"错误: {output['error']}"}]}
                else:
                    return {"content": [{"type": "text", "text": result.stdout}]}
            else:
                return {"content": [{"type": "text", "text": f"命令执行失败: {result.stderr}"}]}
        except subprocess.TimeoutExpired:
            return {"content": [{"type": "text", "text": "错误: mmx vision 命令超时"}]}
        except json.JSONDecodeError:
            return {"content": [{"type": "text", "text": f"解析输出失败: {result.stdout}"}]}
        except Exception as e:
            return {"content": [{"type": "text", "text": f"错误: {str(e)}"}]}
    else:
        return {"content": [{"type": "text", "text": f"未知工具: {name}"}]}

def handle_request(request):
    """Handle incoming JSON-RPC request"""
    method = request.get("method")
    req_id = request.get("id")
    params = request.get("params", {})
    
    if method == "initialize":
        result = handle_initialize(params)
        return {"jsonrpc": "2.0", "id": req_id, "result": result}
    elif method == "notifications/initialized":
        # Empty response for notifications
        return None
    elif method == "tools/call":
        result = handle_tools_call(params)
        return {"jsonrpc": "2.0", "id": req_id, "result": result}
    else:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}

def main():
    """Main loop - read JSON-RPC requests from stdin and write responses to stdout"""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            line = line.strip()
            if not line:
                continue
            
            request = json.loads(line)
            response = handle_request(request)
            
            if response is not None:
                print(json.dumps(response), flush=True)
        except json.JSONDecodeError as e:
            error_response = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": f"Parse error: {str(e)}"}}
            print(json.dumps(error_response), flush=True)
        except Exception as e:
            error_response = {"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": f"Internal error: {str(e)}"}}
            print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    main()
