from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QTextEdit, QLabel, 
                            QListWidget, QMessageBox, QProgressBar,
                            QInputDialog, QFileDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtCore import QThreadPool
from core.worker import Worker, BatchWorker
from core.twitter_api import TwitterAPI
from core.config_manager import ConfigManager
import json
import os
from pathlib import Path
import logging
from typing import List, Dict, Optional

logger = logging.getLogger("LoginPanel")

class LoginPanel(QWidget):
    """账号登录面板，处理Twitter账号的批量登录和验证"""
    
    login_complete = pyqtSignal(list)  # 登录完成信号
    
    def __init__(self, config: ConfigManager):
        super().__init__()
        self.config = config
        self.tokens_file = "config/tokens.json"
        self.accounts: List[Dict] = []
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(
            self.config.getint('DEFAULT', 'max_threads', 5)
        )
        self.logger = logging.getLogger("LoginPanel")
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        self.logger.debug("初始化登录面板UI")
        
        # 主布局
        layout = QVBoxLayout()
        
        # Token输入区域
        self.token_input = QTextEdit()
        self.token_input.setPlaceholderText("请输入Twitter Token，每行一个...")
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        self.load_btn = QPushButton("从文件导入")
        self.login_btn = QPushButton("批量登录")
        self.clear_btn = QPushButton("清空")
        
        btn_layout.addWidget(self.load_btn)
        btn_layout.addWidget(self.login_btn)
        btn_layout.addWidget(self.clear_btn)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)
        
        # 状态标签
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        
        # 账号列表
        self.account_list = QListWidget()
        
        # 添加到主布局
        layout.addWidget(QLabel("Twitter Tokens:"))
        layout.addWidget(self.token_input)
        layout.addLayout(btn_layout)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        layout.addWidget(QLabel("已登录账号:"))
        layout.addWidget(self.account_list)
        
        self.setLayout(layout)
        
        # 连接信号槽
        self.load_btn.clicked.connect(self.load_tokens_from_file)
        self.login_btn.clicked.connect(self.batch_login)
        self.clear_btn.clicked.connect(self.clear_tokens)
        
        # 加载已有token
        self.load_existing_tokens()
        
        self.logger.info("登录面板初始化完成")
    
    def load_existing_tokens(self):
        """加载已保存的token"""
        try:
            if os.path.exists(self.tokens_file):
                with open(self.tokens_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        self.logger.warning("tokens.json 文件为空")
                        return
                    
                    try:
                        tokens = json.loads(content)
                        if isinstance(tokens, list):
                            self.token_input.setText("\n".join(tokens))
                        else:
                            self.logger.warning("tokens.json 格式不正确，应为列表")
                    except json.JSONDecodeError:
                        self.logger.warning("tokens.json 格式错误，重置为空文件")
                        with open(self.tokens_file, 'w') as f:
                            json.dump([], f)
        except Exception as e:
            self.logger.error(f"加载已有token失败: {str(e)}")
            QMessageBox.warning(self, "警告", f"加载token失败: {str(e)}")
    
    def load_tokens_from_file(self):
        """从文件导入token"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, 
                "选择Token文件", 
                "", 
                "文本文件 (*.txt);;JSON文件 (*.json);;所有文件 (*)"
            )
            
            if file_path:
                with open(file_path, 'r') as f:
                    content = f.read().strip()
                    if file_path.endswith('.json'):
                        try:
                            tokens = json.loads(content)
                            if isinstance(tokens, list):
                                content = "\n".join(tokens)
                        except json.JSONDecodeError:
                            pass
                    
                    self.token_input.setText(content)
        except Exception as e:
            self.logger.error(f"从文件导入token失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"从文件导入token失败: {str(e)}")
    
    def batch_login(self):
        """批量登录验证"""
        tokens_text = self.token_input.toPlainText().strip()
        if not tokens_text:
            QMessageBox.warning(self, "警告", "请输入至少一个Token")
            return
            
        tokens = tokens_text.split('\n')
        self.account_list.clear()
        self.accounts.clear()
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("正在验证Token...")
        
        # 创建并启动工作线程
        worker = BatchWorker(
            tokens,
            self._verify_single_token,
            parent_ui=self
        )
        worker.signals.result.connect(self._handle_login_result)
        worker.signals.error.connect(self._handle_login_error)
        worker.signals.progress.connect(self._update_progress)
        worker.signals.finished.connect(self._on_login_finished)
        
        self.thread_pool.start(worker)
    
    def _verify_single_token(self, token: str, progress_callback: callable, 
                           parent_ui=None) -> Optional[Dict]:
        """验证单个Token"""
        token = token.strip()
        if not token:
            return None
            
        try:
            api = TwitterAPI(token, parent_ui)
            user_info = api.verify_credentials()
            
            if 'data' in user_info:
                return {
                    'token': token,
                    'username': user_info['data'].get('username', '未知用户'),
                    'name': user_info['data'].get('name', '未知名称'),
                    'id': user_info['data'].get('id')
                }
        except Exception as e:
            self.logger.warning(f"验证Token失败: {str(e)}")
            return None
    
    def _handle_login_result(self, results: List[Dict]):
        """处理登录结果"""
        valid_results = [r for r in results if r is not None]
        
        # 保存有效的token
        valid_tokens = [r['token'] for r in valid_results]
        try:
            with open(self.tokens_file, 'w') as f:
                json.dump(valid_tokens, f)
        except Exception as e:
            self.logger.error(f"保存Token失败: {str(e)}")
            QMessageBox.warning(self, "警告", f"保存Token失败: {str(e)}")
        
        # 更新账号列表
        for result in valid_results:
            self.account_list.addItem(f"{result['name']} (@{result['username']})")
            self.accounts.append(result)
        
        # 发出登录完成信号
        self.login_complete.emit(valid_results)
        
        self.logger.info(f"批量登录完成，验证了{len(valid_results)}个账号")
    
    def _handle_login_error(self, error_msg: str):
        """处理登录错误"""
        self.logger.error(f"批量登录出错: {error_msg}")
        QMessageBox.critical(self, "错误", f"批量登录时出错:\n{error_msg}")
    
    def _update_progress(self, progress: int, message: str):
        """更新进度"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(message)
    
    def _on_login_finished(self):
        """登录完成后的清理工作"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("验证完成")
        
        if self.account_list.count() > 0:
            QMessageBox.information(
                self, 
                "完成", 
                f"已验证{self.account_list.count()}个账号"
            )
    
    def clear_tokens(self):
        """清空token"""
        reply = QMessageBox.question(
            self, 
            "确认", 
            "确定要清空所有Token和账号吗?", 
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.token_input.clear()
            self.account_list.clear()
            self.accounts.clear()
            
            try:
                if os.path.exists(self.tokens_file):
                    os.remove(self.tokens_file)
            except Exception as e:
                self.logger.error(f"删除Token文件失败: {str(e)}")
                QMessageBox.warning(self, "警告", f"删除Token文件失败: {str(e)}")
            
            self.logger.info("已清空所有Token和账号")