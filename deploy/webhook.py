#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
博客自动部署Webhook服务
支持GitHub webhook自动拉取代码并重启Flask应用
"""

import logging
import os
import time
import subprocess
import signal
import psutil
from flask import Flask, request, jsonify
import hashlib
import hmac

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/blog_webhook.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 生产环境配置
BLOG_ROOT = "/Users/shihanmax/Documents/code/blog"
FLASK_APP_PATH = os.path.join(BLOG_ROOT, "app.py")
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', '')  # GitHub webhook密钥
PID_FILE = '/tmp/blog_app.pid'  # Flask应用PID文件

def verify_signature(payload_body, secret_token, signature_header):
    """验证GitHub webhook签名"""
    if not secret_token:
        return True  # 如果没有配置密钥，跳过验证
    
    if not signature_header:
        return False
    
    hash_object = hmac.new(
        secret_token.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    
    return hmac.compare_digest(expected_signature, signature_header)

def kill_flask_app():
    """停止运行中的Flask应用"""
    try:
        # 查找运行中的Flask应用进程
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and any('app.py' in cmd for cmd in cmdline):
                    logger.info(f"找到Flask进程 PID: {proc.info['pid']}")
                    proc.terminate()
                    proc.wait(timeout=10)
                    logger.info(f"已停止Flask进程 PID: {proc.info['pid']}")
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                continue
        
        # 如果没找到进程，尝试通过端口杀死
        result = subprocess.run(['lsof', '-ti:8080'], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    logger.info(f"通过端口8080停止进程 PID: {pid}")
                    time.sleep(2)
                except ProcessLookupError:
                    pass
            return True
    except Exception as e:
        logger.error(f"停止Flask应用时出错: {e}")
    
    return False

def start_flask_app():
    """启动Flask应用"""
    try:
        # 切换到项目根目录
        os.chdir(BLOG_ROOT)
        
        # 激活虚拟环境并启动Flask应用
        cmd = f"cd {BLOG_ROOT} && source venv/bin/activate && nohup python app.py > /tmp/flask_app.log 2>&1 &"
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Flask应用启动成功")
            time.sleep(3)  # 等待应用启动
            return True
        else:
            logger.error(f"Flask应用启动失败: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"启动Flask应用时出错: {e}")
        return False

def git_pull():
    """执行git pull拉取最新代码"""
    try:
        os.chdir(BLOG_ROOT)
        result = subprocess.run(['git', 'pull'], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            logger.info("Git pull执行成功")
            logger.info(f"Git pull输出: {result.stdout}")
            return True, result.stdout
        else:
            logger.error(f"Git pull失败: {result.stderr}")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        logger.error("Git pull超时")
        return False, "Git pull timeout"
    except Exception as e:
        logger.error(f"Git pull时出错: {e}")
        return False, str(e)

@app.route("/hook", methods=['POST'])
def webhook():
    """处理GitHub webhook请求"""
    try:
        # 获取请求数据
        payload = request.get_data()
        signature = request.headers.get('X-Hub-Signature-256')
        event_type = request.headers.get('X-GitHub-Event', 'unknown')
        
        logger.info(f"收到webhook请求，事件类型: {event_type}")
        
        # 验证签名（如果配置了密钥）
        if WEBHOOK_SECRET and not verify_signature(payload, WEBHOOK_SECRET, signature):
            logger.warning("Webhook签名验证失败")
            return jsonify({"error": "Invalid signature"}), 401
        
        # 只处理push事件
        if event_type != 'push':
            logger.info(f"忽略事件类型: {event_type}")
            return jsonify({"message": f"Ignored event: {event_type}"}), 200
        
        # 执行部署流程
        logger.info("开始自动部署流程...")
        
        # 1. 拉取最新代码
        pull_success, pull_output = git_pull()
        if not pull_success:
            return jsonify({
                "error": "Git pull failed",
                "details": pull_output
            }), 500
        
        # 2. 停止当前Flask应用
        logger.info("停止当前Flask应用...")
        kill_flask_app()
        
        # 3. 等待一下确保进程完全停止
        time.sleep(2)
        
        # 4. 启动新的Flask应用
        logger.info("启动新的Flask应用...")
        if start_flask_app():
            deploy_time = time.ctime()
            logger.info(f"自动部署完成于: {deploy_time}")
            
            return jsonify({
                "status": "success",
                "message": "Blog updated successfully",
                "timestamp": deploy_time,
                "git_output": pull_output
            }), 200
        else:
            return jsonify({
                "error": "Failed to start Flask app",
                "git_output": pull_output
            }), 500
            
    except Exception as e:
        logger.error(f"Webhook处理时出错: {e}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500

@app.route("/status", methods=['GET'])
def status():
    """检查服务状态"""
    try:
        # 检查Flask应用是否在运行
        flask_running = False
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and any('app.py' in cmd for cmd in cmdline):
                    flask_running = True
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return jsonify({
            "webhook_service": "running",
            "flask_app": "running" if flask_running else "stopped",
            "timestamp": time.ctime()
        }), 200
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@app.route("/deploy", methods=['POST'])
def manual_deploy():
    """手动触发部署（用于测试）"""
    try:
        logger.info("手动触发部署...")
        
        # 执行与webhook相同的部署流程
        pull_success, pull_output = git_pull()
        if not pull_success:
            return jsonify({
                "error": "Git pull failed",
                "details": pull_output
            }), 500
        
        kill_flask_app()
        time.sleep(2)
        
        if start_flask_app():
            deploy_time = time.ctime()
            logger.info(f"手动部署完成于: {deploy_time}")
            
            return jsonify({
                "status": "success",
                "message": "Manual deployment completed",
                "timestamp": deploy_time,
                "git_output": pull_output
            }), 200
        else:
            return jsonify({
                "error": "Failed to start Flask app"
            }), 500
            
    except Exception as e:
        logger.error(f"手动部署时出错: {e}")
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == "__main__":
    logger.info("启动博客自动部署Webhook服务...")
    logger.info(f"博客根目录: {BLOG_ROOT}")
    logger.info(f"Flask应用路径: {FLASK_APP_PATH}")
    logger.info("监听端口: 8082")
    
    app.run(host="0.0.0.0", port=8082, debug=False)