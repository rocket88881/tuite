import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QListWidget, QLabel, 
                            QInputDialog, QMessageBox, QListWidgetItem,
                            QGroupBox, QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal
from core.group_manager import GroupManager
from core.config_manager import ConfigManager
import logging
from typing import List, Dict, Optional

logger = logging.getLogger("GroupPanel")

class GroupPanel(QWidget):
    """分组管理面板，处理Twitter账号的分组管理"""
    
    groups_updated = pyqtSignal()  # 分组更新信号
    
    def __init__(self, config: ConfigManager):
        super().__init__()
        self.logger = logging.getLogger("GroupPanel")
        self.config = config
        self.group_manager = GroupManager()
        self.current_group = None
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        self.logger.debug("初始化分组面板UI")
        
        # 主布局
        main_layout = QHBoxLayout()
        
        # 左侧 - 分组管理
        left_layout = QVBoxLayout()
        
        self.group_list = QListWidget()
        self.group_list.itemClicked.connect(self.show_accounts_in_group)
        self.refresh_group_list()
        
        # 分组操作按钮
        group_btn_layout = QHBoxLayout()
        self.create_group_btn = QPushButton("创建分组")
        self.delete_group_btn = QPushButton("删除分组")
        
        group_btn_layout.addWidget(self.create_group_btn)
        group_btn_layout.addWidget(self.delete_group_btn)
        
        left_layout.addWidget(QLabel("分组列表:"))
        left_layout.addWidget(self.group_list)
        left_layout.addLayout(group_btn_layout)
        
        # 右侧 - 账号管理
        right_layout = QVBoxLayout()
        
        self.account_list = QListWidget()
        
        # 账号操作按钮
        account_btn_layout = QHBoxLayout()
        self.move_account_btn = QPushButton("移动选中账号到...")
        self.remove_account_btn = QPushButton("从分组移除")
        
        account_btn_layout.addWidget(self.move_account_btn)
        account_btn_layout.addWidget(self.remove_account_btn)
        
        right_layout.addWidget(QLabel("分组中的账号:"))
        right_layout.addWidget(self.account_list)
        right_layout.addLayout(account_btn_layout)
        
        # 添加到主布局
        main_layout.addLayout(left_layout, 30)
        main_layout.addLayout(right_layout, 70)
        
        self.setLayout(main_layout)
        
        # 连接信号槽
        self.create_group_btn.clicked.connect(self.create_group)
        self.delete_group_btn.clicked.connect(self.delete_group)
        self.move_account_btn.clicked.connect(self.move_account)
        self.remove_account_btn.clicked.connect(self.remove_account)
        
        self.logger.info("分组面板初始化完成")
    
    def refresh_group_list(self):
        """刷新分组列表"""
        self.group_list.clear()
        groups = self.group_manager.get_group_names()
        for group in groups:
            self.group_list.addItem(group)
        
        if groups:
            self.group_list.setCurrentRow(0)
            self.current_group = groups[0]
            self.show_accounts_in_group(self.group_list.currentItem())
    
    def show_accounts_in_group(self, item):
        """显示选中分组中的账号"""
        group_name = item.text()
        self.current_group = group_name
        self.account_list.clear()
        
        accounts = self.group_manager.get_accounts_in_group(group_name)
        for acc in accounts:
            self.account_list.addItem(f"{acc['name']} (@{acc['username']})")
    
    def create_group(self):
        """创建新分组"""
        group_name, ok = QInputDialog.getText(
            self, "创建分组", "请输入分组名称:",
            flags=Qt.WindowCloseButtonHint
        )
        
        if ok and group_name:
            success, message = self.group_manager.create_group(group_name)
            QMessageBox.information(self, "提示", message)
            if success:
                self.refresh_group_list()
                self.groups_updated.emit()
                logger.info(f"创建新分组: {group_name}")
    
    def delete_group(self):
        """删除选中分组"""
        current_item = self.group_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择一个分组")
            return
            
        group_name = current_item.text()
        reply = QMessageBox.question(
            self, "确认", 
            f"确定要删除分组 '{group_name}' 吗? 这将移除分组中的所有账号。", 
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self.group_manager.delete_group(group_name)
            QMessageBox.information(self, "提示", message)
            if success:
                self.refresh_group_list()
                self.groups_updated.emit()
                logger.info(f"删除分组: {group_name}")
    
    def move_account(self):
        """移动账号到其他分组"""
        if not self.current_group:
            QMessageBox.warning(self, "警告", "请先选择一个分组")
            return
            
        account_item = self.account_list.currentItem()
        if not account_item:
            QMessageBox.warning(self, "警告", "请先选择一个账号")
            return
            
        # 从显示文本中提取用户名
        account_text = account_item.text()
        username = account_text.split('@')[-1].rstrip(')')
        
        # 获取目标分组
        target_group, ok = QInputDialog.getItem(
            self, "选择目标分组", 
            "请选择目标分组:", 
            [g for g in self.group_manager.get_group_names() 
             if g != self.current_group], 
            0, False, flags=Qt.WindowCloseButtonHint
        )
        
        if ok and target_group:
            success, message = self.group_manager.move_account(
                self.current_group, target_group, username)
            QMessageBox.information(self, "提示", message)
            if success:
                self.show_accounts_in_group(self.group_list.currentItem())
                self.groups_updated.emit()
                logger.info(f"移动账号 {username} 到 {target_group}")
    
    def remove_account(self):
        """从分组中移除账号"""
        if not self.current_group:
            QMessageBox.warning(self, "警告", "请先选择一个分组")
            return
            
        account_item = self.account_list.currentItem()
        if not account_item:
            QMessageBox.warning(self, "警告", "请先选择一个账号")
            return
            
        # 从显示文本中提取用户名
        account_text = account_item.text()
        username = account_text.split('@')[-1].rstrip(')')
        
        reply = QMessageBox.question(
            self, "确认", 
            f"确定要从分组 '{self.current_group}' 移除账号 @{username} 吗?", 
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 通过移动账号到临时分组然后删除临时分组来实现移除
            temp_group = "__temp__"
            self.group_manager.create_group(temp_group)
            
            success, message = self.group_manager.move_account(
                self.current_group, temp_group, username)
            
            if success:
                self.group_manager.delete_group(temp_group)
                self.show_accounts_in_group(self.group_list.currentItem())
                self.groups_updated.emit()
                logger.info(f"从分组 {self.current_group} 移除账号 {username}")
                QMessageBox.information(self, "成功", f"已从分组移除 @{username}")
            else:
                QMessageBox.warning(self, "失败", message)