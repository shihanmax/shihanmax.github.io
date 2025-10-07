#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版博客自动部署Webhook服务
收到POST请求后直接执行git pull
"""

import logging
import os
import subprocess
import hashlib
import hmac
from flask import Flask, request, jsonify
# 加载.env文件中的环境变量
from dotenv import load_dotenv
load_dotenv()


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 博客根目录
BLOG_ROOT = "."

# webhook 密钥（从环境变量获取）
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', 'change-me-in-production')

def verify_signature(payload_body, secret_token, signature_header):
    """验证 GitHub webhook 签名"""
    if not signature_header:
        return False
    
    hash_object = hmac.new(secret_token.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    
    return hmac.compare_digest(expected_signature, signature_header)

def git_pull():
    """执行git pull拉取最新代码"""
    try:
        # 切换到博客主目录
        os.chdir(BLOG_ROOT)
        logger.info(f"切换到目录: {BLOG_ROOT}")
        
        # 执行git pull
        result = subprocess.run(['git', 'pull'], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            logger.info("Git pull执行成功")
            logger.info(f"输出: {result.stdout.strip()}")
            return True, result.stdout.strip()
        else:
            logger.error(f"Git pull失败: {result.stderr.strip()}")
            return False, result.stderr.strip()
            
    except subprocess.TimeoutExpired:
        logger.error("Git pull超时")
        return False, "Git pull timeout"
    except Exception as e:
        logger.error(f"Git pull时出错: {e}")
        return False, str(e)

@app.route("/hook", methods=['POST'])
def webhook():
    """处理webhook请求，直接执行git pull"""
    # 验证 webhook 签名
    signature = request.headers.get('X-Hub-Signature-256')
    if not verify_signature(request.get_data(), WEBHOOK_SECRET, signature):
        logger.warning("Webhook签名验证失败")
        return jsonify({
            "status": "error",
            "message": "Unauthorized"
        }), 401
    
    try:
        logger.info("收到webhook请求")
        
        # 执行git pull
        success, output = git_pull()
        
        if success:
            logger.info("Webhook处理成功")
            return jsonify({
                "status": "success",
                "message": "Git pull completed successfully",
                "output": output
            }), 200
        else:
            logger.error("Git pull失败")
            return jsonify({
                "status": "error",
                "message": "Git pull failed",
                "error": output
            }), 500
            
    except Exception as e:
        logger.error(f"Webhook处理时出错: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error",
            "error": str(e)
        }), 500

@app.route("/status", methods=['GET'])
def status():
    """检查服务状态"""
    return jsonify({
        "status": "running",
        "blog_root": BLOG_ROOT,
        "message": "Webhook service is running"
    }), 200

@app.route("/", methods=['GET'])
def index():
    """根路径访问"""
    return jsonify({
        "message": "Simple Blog Webhook Service",
        "endpoints": {
            "webhook": "/hook (POST)",
            "status": "/status (GET)"
        }
    }), 200


if __name__ == "__main__":
    logger.info("启动简化版博客Webhook服务...")
    logger.info(f"博客根目录: {BLOG_ROOT}")
    logger.info("监听端口: 8082")
    
    app.run(port=8082, debug=False)
