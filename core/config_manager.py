# -*- coding: utf-8 -*-
import configparser
from pathlib import Path
import os
import logging

logger = logging.getLogger("ConfigManager")

class ConfigManager:
    def __init__(self, config_path="config/config.ini"):
        self.config_path = Path(config_path)
        self.config = configparser.ConfigParser()
        self._ensure_config_exists()
    
    def _ensure_config_exists(self):
        """确保配置文件存在且有效"""
        try:
            self.config_path.parent.mkdir(exist_ok=True)
            if not self.config_path.exists():
                self._create_default_config()
            else:
                # 验证现有配置文件
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if not content.strip():
                        self._create_default_config()
        except Exception as e:
            logger.error(f"配置文件初始化失败: {str(e)}")
            raise

    def _create_default_config(self):
        """创建默认配置文件"""
        self.config['DEFAULT'] = {
            'theme': 'light',
            'font_size': '10',
            'api_timeout': '30',
            'max_threads': '5',
            'auto_save': 'true',
            'save_interval': '5'
        }
        self.save_config()

    def save_config(self):
        """保存当前配置"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            self.config.write(f)

    def get(self, section, option, fallback=None):
        """获取配置值"""
        try:
            return self.config.get(section, option, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback

    def get_app_settings(self):
        """获取所有应用设置"""
        return {
            'theme': self.get('DEFAULT', 'theme', 'light'),
            'font_size': self.getint('DEFAULT', 'font_size', 10),
            'api_timeout': self.getint('DEFAULT', 'api_timeout', 30),
            'max_threads': self.getint('DEFAULT', 'max_threads', 5),
            'auto_save': self.getboolean('DEFAULT', 'auto_save', True),
            'save_interval': self.getint('DEFAULT', 'save_interval', 5)
        }