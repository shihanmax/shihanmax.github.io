#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全日志记录器
记录安全相关事件
"""

import logging
import os
from datetime import datetime
import json

class SecurityLogger:
    """安全日志记录器"""
    
    def __init__(self, log_file=None):
        """
        初始化安全日志记录器
        
        Args:
            log_file: 日志文件路径，默认为logs/security.log
        """
        if log_file is None:
            # 默认日志文件路径
            log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, 'security.log')
        
        self.log_file = log_file
        
        # 配置日志记录器
        self.logger = logging.getLogger('security')
        self.logger.setLevel(logging.INFO)
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_login_attempt(self, username, ip_address, success):
        """记录登录尝试"""
        status = "SUCCESS" if success else "FAILED"
        message = f"Login attempt - User: {username}, IP: {ip_address}, Status: {status}"
        self.logger.info(message)
    
    def log_unauthorized_access(self, ip_address, path, user_agent=None):
        """记录未授权访问尝试"""
        message = f"Unauthorized access attempt - IP: {ip_address}, Path: {path}"
        if user_agent:
            message += f", User-Agent: {user_agent}"
        self.logger.warning(message)
    
    def log_suspicious_activity(self, activity_type, details, ip_address=None):
        """记录可疑活动"""
        message = f"Suspicious activity - Type: {activity_type}, Details: {details}"
        if ip_address:
            message += f", IP: {ip_address}"
        self.logger.warning(message)
    
    def log_admin_action(self, action, user, ip_address=None):
        """记录管理员操作"""
        message = f"Admin action - Action: {action}, User: {user}"
        if ip_address:
            message += f", IP: {ip_address}"
        self.logger.info(message)