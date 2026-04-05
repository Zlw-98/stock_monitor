# -*- coding: utf-8 -*-
"""
邮件推送模块
负责发送每日技术分析日报
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime
from typing import Dict, List, Any
from .config_manager import config_manager
from .report_generator import report_generator


class EmailPusher:
    """邮件推送器"""
    
    def __init__(self):
        """初始化邮件推送器"""
        self.email_config = config_manager.get_email_config()
    
    def send_daily_report(self, report_data: Dict[str, Any]) -> bool:
        """
        发送每日技术分析日报
        
        Args:
            report_data: 报告数据
        
        Returns:
            是否发送成功
        """
        try:
            # 构建邮件内容
            subject = f"【股票监控日报】{datetime.now().strftime('%Y-%m-%d')} 持仓分析"
            body = self._build_report_body(report_data)
            
            # 发送邮件
            return self._send_email(subject, body)
            
        except Exception as e:
            print(f"❌ 发送邮件失败: {e}")
            return False
    
    def _build_report_body(self, report_data: Dict[str, Any]) -> str:
        """
        构建报告内容
        
        Args:
            report_data: 报告数据
        
        Returns:
            报告内容
        """
        # 使用报告生成器生成定投决策报告
        return report_generator.generate_daily_report(report_data)
    
    def _send_email(self, subject: str, body: str) -> bool:
        """
        发送邮件
        
        Args:
            subject: 邮件主题
            body: 邮件内容
        
        Returns:
            是否发送成功
        """
        try:
            # 获取邮箱配置
            smtp_server = self.email_config.get('smtp_server', 'smtp.qq.com')
            smtp_port = self.email_config.get('smtp_port', 465)
            sender_email = self.email_config.get('sender_email', '')
            sender_password = self.email_config.get('sender_password', '')
            receiver_email = self.email_config.get('receiver_email', '374186226@qq.com')
            
            if not sender_email or not sender_password:
                print("❌ 邮箱配置不完整")
                return False
            
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = Header(subject, 'utf-8')
            
            # 添加纯文本内容
            text_part = MIMEText(body, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # 发送邮件
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(sender_email, sender_password)
                server.send_message(msg)
            
            print("✅ 邮件发送成功")
            return True
            
        except Exception as e:
            print(f"❌ 发送邮件失败: {e}")
            return False


# 全局邮件推送实例
email_pusher = EmailPusher()
