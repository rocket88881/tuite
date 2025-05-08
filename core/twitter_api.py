import requests
from PyQt5.QtWidgets import QMessageBox
from requests.exceptions import RequestException
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("TwitterAPI")

class TwitterAPIError(Exception):
    """自定义Twitter API错误"""
    pass

class TwitterAPI:
    def __init__(self, bearer_token: str, parent_ui=None):
        """初始化Twitter API客户端
        
        Args:
            bearer_token: Twitter Bearer Token
            parent_ui: 父UI组件，用于显示错误消息
        """
        self.base_url = "https://api.twitter.com/2/"
        self.headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json"
        }
        self.parent_ui = parent_ui
        self.logger = logging.getLogger(f"TwitterAPI.{id(self)}")
    
    def _handle_request(self, method: str, endpoint: str, 
                       params: Optional[Dict] = None, 
                       data: Optional[Dict] = None) -> Dict:
        """统一处理API请求
        
        Args:
            method: HTTP方法 (GET, POST等)
            endpoint: API端点
            params: 查询参数
            data: 请求体数据
            
        Returns:
            API响应数据
            
        Raises:
            TwitterAPIError: 当API请求失败时
        """
        url = f"{self.base_url}{endpoint}"
        self.logger.debug(f"请求 {method} {url}")
        
        try:
            response = requests.request(
                method,
                url,
                headers=self.headers,
                params=params,
                json=data,
                timeout=30
            )
            
            self.logger.debug(f"响应状态码: {response.status_code}")
            
            if response.status_code != 200:
                error_msg = self._parse_error(response)
                self.logger.error(f"API请求失败: {error_msg}")
                raise TwitterAPIError(error_msg)
                
            return response.json()
            
        except RequestException as e:
            error_msg = f"网络请求失败: {str(e)}"
            self.logger.error(error_msg)
            self._show_error(error_msg)
            raise TwitterAPIError(error_msg)
    
    def _parse_error(self, response) -> str:
        """解析API错误信息
        
        Args:
            response: requests.Response对象
            
        Returns:
            错误消息字符串
        """
        try:
            error_data = response.json()
            errors = error_data.get('errors', [])
            if errors:
                return "; ".join([e.get('detail', str(e)) for e in errors])
            return error_data.get('detail', response.text)
        except json.JSONDecodeError:
            return response.text
    
    def _show_error(self, message: str):
        """显示错误消息到UI
        
        Args:
            message: 错误消息
        """
        if self.parent_ui:
            QMessageBox.critical(self.parent_ui, "API错误", message)
    
    def verify_credentials(self) -> Dict:
        """验证token有效性并获取用户信息
        
        Returns:
            用户信息字典
            
        Raises:
            TwitterAPIError: 当验证失败时
        """
        try:
            user_data = self._handle_request('GET', 'users/me')
            self.logger.info(f"验证成功: {user_data.get('data', {}).get('username')}")
            return user_data
        except TwitterAPIError as e:
            raise TwitterAPIError(f"验证凭证失败: {str(e)}")
    
    def get_user_tweets(self, user_id: str, max_results: int = 10) -> Dict:
        """获取用户推文
        
        Args:
            user_id: 用户ID
            max_results: 最大结果数
            
        Returns:
            推文数据
            
        Raises:
            TwitterAPIError: 当请求失败时
        """
        params = {
            "max_results": max_results,
            "tweet.fields": "created_at,public_metrics"
        }
        try:
            return self._handle_request(
                'GET', 
                f'users/{user_id}/tweets', 
                params=params
            )
        except TwitterAPIError as e:
            raise TwitterAPIError(f"获取推文失败: {str(e)}")
    
    def get_user_info(self, username: str) -> Dict:
        """获取用户信息
        
        Args:
            username: Twitter用户名
            
        Returns:
            用户信息
            
        Raises:
            TwitterAPIError: 当请求失败时
        """
        params = {
            "user.fields": "description,profile_image_url"
        }
        try:
            return self._handle_request(
                'GET',
                f'users/by/username/{username}',
                params=params
            )
        except TwitterAPIError as e:
            raise TwitterAPIError(f"获取用户信息失败: {str(e)}")