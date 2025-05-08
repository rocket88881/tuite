import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from PyQt5.QtWidgets import QMessageBox
import logging

logger = logging.getLogger("GroupManager")

class GroupManager:
    def __init__(self, config_path: str = "config/groups.json"):
        self.config_path = Path(config_path)
        self.groups: Dict[str, List[dict]] = {}
        self._ensure_config_exists()
        self.load_groups()
    
    def _ensure_config_exists(self):
        """确保配置文件存在"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            if not self.config_path.exists():
                with open(self.config_path, 'w') as f:
                    json.dump({}, f)
        except Exception as e:
            logger.error(f"初始化分组文件失败: {str(e)}")
            raise
    
    def load_groups(self):
        """加载分组数据"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.groups = json.load(f)
                    # 确保数据格式正确
                    if not isinstance(self.groups, dict):
                        self.groups = {}
                        self.save_groups()
        except json.JSONDecodeError:
            logger.warning("分组文件损坏，重置为空")
            self.groups = {}
            self.save_groups()
        except Exception as e:
            logger.error(f"加载分组失败: {str(e)}")
            raise
    
    def save_groups(self):
        """保存分组数据"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.groups, f, indent=4)
        except Exception as e:
            logger.error(f"保存分组失败: {str(e)}")
            raise
    
    def create_group(self, group_name: str) -> (bool, str):
        """创建新分组"""
        try:
            if not group_name.strip():
                return False, "分组名不能为空"
                
            if group_name in self.groups:
                return False, "分组已存在"
                
            self.groups[group_name] = []
            self.save_groups()
            logger.info(f"创建分组: {group_name}")
            return True, f"分组 '{group_name}' 创建成功"
        except Exception as e:
            logger.error(f"创建分组失败: {str(e)}")
            return False, f"创建分组失败: {str(e)}"
    
    def delete_group(self, group_name: str) -> (bool, str):
        """删除分组"""
        try:
            if group_name not in self.groups:
                return False, "分组不存在"
                
            del self.groups[group_name]
            self.save_groups()
            logger.info(f"删除分组: {group_name}")
            return True, f"分组 '{group_name}' 已删除"
        except Exception as e:
            logger.error(f"删除分组失败: {str(e)}")
            return False, f"删除分组失败: {str(e)}"
    
    def add_account_to_group(self, group_name: str, account_info: dict) -> (bool, str):
        """添加账号到分组"""
        try:
            if group_name not in self.groups:
                return False, "分组不存在"
                
            # 检查账号是否已在组中
            for acc in self.groups[group_name]:
                if acc.get('username') == account_info.get('username'):
                    return False, "账号已在组中"
                    
            self.groups[group_name].append(account_info)
            self.save_groups()
            logger.info(f"添加账号到分组 {group_name}: {account_info.get('username')}")
            return True, f"账号已添加到 '{group_name}'"
        except Exception as e:
            logger.error(f"添加账号到分组失败: {str(e)}")
            return False, f"添加账号到分组失败: {str(e)}"
    
    def move_account(self, from_group: str, to_group: str, username: str) -> (bool, str):
        """移动账号到其他分组"""
        try:
            if from_group not in self.groups:
                return False, "源分组不存在"
                
            if to_group not in self.groups:
                return False, "目标分组不存在"
                
            # 查找账号
            account = None
            for acc in self.groups[from_group]:
                if acc.get('username') == username:
                    account = acc
                    break
                    
            if not account:
                return False, "账号不在源分组中"
                
            # 从原分组移除
            self.groups[from_group] = [acc for acc in self.groups[from_group] 
                                     if acc.get('username') != username]
            
            # 添加到新分组
            self.groups[to_group].append(account)
            self.save_groups()
            logger.info(f"移动账号 {username} 从 {from_group} 到 {to_group}")
            return True, f"账号已从 '{from_group}' 移动到 '{to_group}'"
        except Exception as e:
            logger.error(f"移动账号失败: {str(e)}")
            return False, f"移动账号失败: {str(e)}"
    
    def get_group_names(self) -> List[str]:
        """获取所有分组名"""
        return list(self.groups.keys())
    
    def get_accounts_in_group(self, group_name: str) -> List[dict]:
        """获取分组中的账号"""
        return self.groups.get(group_name, [])
    
    def find_account_groups(self, username: str) -> List[str]:
        """查找账号所在的所有分组"""
        return [group for group, accounts in self.groups.items() 
               if any(acc.get('username') == username for acc in accounts)]