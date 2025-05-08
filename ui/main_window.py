from PyQt5.QtWidgets import QMainWindow, QTabWidget, QStatusBar
from PyQt5.QtCore import pyqtSignal
from ui.login_panel import LoginPanel
from ui.group_panel import GroupPanel
from ui.settings_panel import SettingsPanel
from core.config_manager import ConfigManager
import logging

logger = logging.getLogger("MainWindow")

class MainWindow(QMainWindow):
    """主窗口类，包含所有功能面板"""
    
    config_changed = pyqtSignal(dict)  # 配置变更信号
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("MainWindow")
        self.config = ConfigManager()
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        self.logger.debug("初始化主窗口UI")
        
        # 加载配置
        settings = self.config.get_app_settings()
        self.logger.debug(f"加载应用设置: {settings}")
        
        # 设置窗口属性
        self.setWindowTitle("Twitter账号管理工具 v1.0")
        self.setGeometry(100, 100, 1000, 700)
        
        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
        
        # 创建主选项卡
        self.tabs = QTabWidget()
        
        # 创建各个功能面板
        self.login_panel = LoginPanel(self.config)
        self.group_panel = GroupPanel(self.config)
        self.settings_panel = SettingsPanel(self.config)
        
        # 连接配置变更信号
        self.settings_panel.config_changed.connect(self.handle_config_change)
        
        # 添加选项卡
        self.tabs.addTab(self.login_panel, "账号登录")
        self.tabs.addTab(self.group_panel, "分组管理")
        self.tabs.addTab(self.settings_panel, "设置")
        
        # 设置中心部件
        self.setCentralWidget(self.tabs)
        
        self.logger.info("主窗口初始化完成")
    
    def handle_config_change(self, new_config: dict):
        """处理配置变更"""
        self.logger.debug(f"配置变更: {new_config}")
        self.config_changed.emit(new_config)
        
        # 更新状态栏消息
        self.status_bar.showMessage("配置已更新，部分设置可能需要重启应用生效", 5000)