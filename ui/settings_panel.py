from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QComboBox, QSpinBox, 
                            QPushButton, QGroupBox, QMessageBox,
                            QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal
from core.config_manager import ConfigManager
import logging

logger = logging.getLogger("SettingsPanel")

class SettingsPanel(QWidget):
    """设置面板，管理应用程序配置"""
    
    config_changed = pyqtSignal(dict)  # 配置变更信号
    
    def __init__(self, config: ConfigManager):
        super().__init__()
        self.logger = logging.getLogger("SettingsPanel")
        self.config = config
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """初始化用户界面"""
        self.logger.debug("初始化设置面板UI")
        
        layout = QVBoxLayout()
        
        # 主题设置
        theme_group = QGroupBox("界面设置")
        theme_layout = QVBoxLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark", "system"])
        theme_layout.addWidget(QLabel("主题:"))
        theme_layout.addWidget(self.theme_combo)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 20)
        theme_layout.addWidget(QLabel("字体大小:"))
        theme_layout.addWidget(self.font_size_spin)
        
        theme_group.setLayout(theme_layout)
        
        # 性能设置
        perf_group = QGroupBox("性能设置")
        perf_layout = QVBoxLayout()
        
        self.max_threads_spin = QSpinBox()
        self.max_threads_spin.setRange(1, 20)
        perf_layout.addWidget(QLabel("最大线程数:"))
        perf_layout.addWidget(self.max_threads_spin)
        
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 120)
        perf_layout.addWidget(QLabel("API超时(秒):"))
        perf_layout.addWidget(self.timeout_spin)
        
        perf_group.setLayout(perf_layout)
        
        # 数据设置
        data_group = QGroupBox("数据设置")
        data_layout = QVBoxLayout()
        
        self.auto_save_check = QCheckBox("自动保存更改")
        self.save_interval_spin = QSpinBox()
        self.save_interval_spin.setRange(1, 60)
        self.save_interval_spin.setSuffix(" 分钟")
        
        data_layout.addWidget(self.auto_save_check)
        data_layout.addWidget(QLabel("自动保存间隔:"))
        data_layout.addWidget(self.save_interval_spin)
        
        data_group.setLayout(data_layout)
        
        # 保存按钮
        save_btn = QPushButton("保存设置")
        save_btn.clicked.connect(self.save_settings)
        
        layout.addWidget(theme_group)
        layout.addWidget(perf_group)
        layout.addWidget(data_group)
        layout.addStretch()
        layout.addWidget(save_btn)
        
        self.setLayout(layout)
        
        self.logger.info("设置面板初始化完成")
    
    def load_settings(self):
        """加载当前设置"""
        settings = self.config.get_app_settings()
        self.theme_combo.setCurrentText(settings['theme'])
        self.font_size_spin.setValue(settings['font_size'])
        self.max_threads_spin.setValue(settings['max_threads'])
        self.timeout_spin.setValue(settings['api_timeout'])
        self.auto_save_check.setChecked(settings['auto_save'])
        self.save_interval_spin.setValue(settings['save_interval'])
    
    def save_settings(self):
        """保存设置"""
        new_settings = {
            'theme': self.theme_combo.currentText(),
            'font_size': self.font_size_spin.value(),
            'max_threads': self.max_threads_spin.value(),
            'api_timeout': self.timeout_spin.value(),
            'auto_save': self.auto_save_check.isChecked(),
            'save_interval': self.save_interval_spin.value()
        }
        
        # 保存到配置文件
        for key, value in new_settings.items():
            self.config.set('DEFAULT', key, value)
        
        # 发出配置变更信号
        self.config_changed.emit(new_settings)
        
        QMessageBox.information(
            self, 
            "成功", 
            "设置已保存，部分设置需要重启应用生效"
        )
        
        logger.info("保存新设置", extra={'new_settings': new_settings})