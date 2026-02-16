"""
服务层基类

所有服务类应继承此基类，确保统一的接口和错误处理

@module backend.core.base_service
@description 提供所有服务的基础功能，包括CRUD操作、错误处理、日志记录等
@author System
@version 1.0.0
@since 2024-02-16

@features
- 统一的CRUD接口
- 标准化错误处理
- 统一日志记录
- 异常捕获和转换

@see {@link ARCHITECTURE_STANDARDS.md}
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Tuple, TypeVar, Generic
import logging
from datetime import datetime

# ==================== 类型定义 ====================

T = TypeVar('T')

# ==================== 自定义异常 ====================

class ServiceError(Exception):
    """服务基础异常"""
    def __init__(self, message: str, code: int = 500, details: Dict[str, Any] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(ServiceError):
    """资源未找到异常"""
    def __init__(self, resource_type: str, resource_id: str, details: Dict[str, Any] = None):
        super().__init__(
            message=f"{resource_type} not found: {resource_id}",
            code=404,
            details=details
        )


class ValidationError(ServiceError):
    """数据验证异常"""
    def __init__(self, message: str, field: str = None, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            code=400,
            details={**({"field": field} if field else {}), **(details or {})}
        )


class ConflictError(ServiceError):
    """资源冲突异常"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            code=409,
            details=details
        )


# ==================== 响应模型 ====================

class BaseResponse(Generic[T]):
    """统一响应模型"""
    
    def __init__(
        self,
        code: int = 200,
        message: str = "success",
        data: Optional[T] = None,
        details: Dict[str, Any] = None
    ):
        self.code = code
        self.message = message
        self.data = data
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "code": self.code,
            "message": self.message,
            "timestamp": self.timestamp
        }
        if self.data is not None:
            result["data"] = self.data
        if self.details:
            result["details"] = self.details
        return result
    
    @classmethod
    def success(cls, data: Any = None, message: str = "success") -> 'BaseResponse[T]':
        """成功响应"""
        return cls(code=200, message=message, data=data)
    
    @classmethod
    def error(
        cls,
        message: str,
        code: int = 500,
        details: Dict[str, Any] = None
    ) -> 'BaseResponse[T]':
        """错误响应"""
        return cls(code=code, message=message, details=details)


class PaginatedResponse(BaseResponse[List[T]]):
    """分页响应模型"""
    
    def __init__(
        self,
        code: int = 200,
        message: str = "success",
        data: Optional[List[T]] = None,
        total: int = 0,
        page: int = 1,
        page_size: int = 20,
        details: Dict[str, Any] = None
    ):
        super().__init__(code=code, message=message, data=data, details=details)
        self.total = total
        self.page = page
        self.page_size = page_size
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = super().to_dict()
        result.update({
            "total": self.total,
            "page": self.page,
            "page_size": self.page_size
        })
        return result
    
    @classmethod
    def success(
        cls,
        items: List[T],
        total: int,
        page: int = 1,
        page_size: int = 20,
        message: str = "success"
    ) -> 'PaginatedResponse[T]':
        """成功分页响应"""
        return cls(
            code=200,
            message=message,
            data=items,
            total=total,
            page=page,
            page_size=page_size
        )


# ==================== 服务基类 ====================

class BaseService(ABC, Generic[T]):
    """
    服务基类
    
    提供所有服务的通用功能：
    1. 标准化的CRUD接口
    2. 统一的错误处理
    3. 日志记录
    4. 数据验证
    """
    
    def __init__(self):
        """初始化服务"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialized = False
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        初始化服务
        
        Returns:
            bool: 初始化是否成功
        """
        pass
    
    @abstractmethod
    async def get(self, id: str) -> Optional[T]:
        """
        获取单个资源
        
        Args:
            id: 资源ID
            
        Returns:
            资源对象，如果不存在返回None
            
        Raises:
            NotFoundError: 资源不存在
            ServiceError: 其他服务错误
        """
        pass
    
    @abstractmethod
    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = 'desc'
    ) -> Tuple[List[T], int]:
        """
        获取资源列表
        
        Args:
            page: 页码，从1开始
            page_size: 每页大小
            filters: 过滤条件
            sort_by: 排序字段
            sort_order: 排序方向，'asc' 或 'desc'
            
        Returns:
            (items, total): 数据列表和总数
            
        Raises:
            ValidationError: 参数验证失败
            ServiceError: 其他服务错误
        """
        pass
    
    @abstractmethod
    async def create(self, data: Dict[str, Any]) -> T:
        """
        创建资源
        
        Args:
            data: 资源数据
            
        Returns:
            创建的资源对象
            
        Raises:
            ValidationError: 数据验证失败
            ConflictError: 资源冲突
            ServiceError: 其他服务错误
        """
        pass
    
    @abstractmethod
    async def update(self, id: str, data: Dict[str, Any]) -> T:
        """
        更新资源
        
        Args:
            id: 资源ID
            data: 更新数据
            
        Returns:
            更新后的资源对象
            
        Raises:
            NotFoundError: 资源不存在
            ValidationError: 数据验证失败
            ServiceError: 其他服务错误
        """
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        """
        删除资源
        
        Args:
            id: 资源ID
            
        Returns:
            bool: 是否删除成功
            
        Raises:
            NotFoundError: 资源不存在
            ServiceError: 其他服务错误
        """
        pass
    
    # ==================== 辅助方法 ====================
    
    async def get_or_404(self, id: str) -> T:
        """
        获取资源或抛出404异常
        
        Args:
            id: 资源ID
            
        Returns:
            资源对象
            
        Raises:
            NotFoundError: 资源不存在
        """
        item = await self.get(id)
        if item is None:
            raise NotFoundError(
                resource_type=self.__class__.__name__.replace('Service', ''),
                resource_id=id
            )
        return item
    
    async def create_or_error(self, data: Dict[str, Any]) -> BaseResponse[T]:
        """
        创建资源或返回错误响应
        
        Args:
            data: 资源数据
            
        Returns:
            响应对象
        """
        try:
            item = await self.create(data)
            return BaseResponse.success(data=item, message="创建成功")
        except ValidationError as e:
            self.logger.error(f"数据验证失败: {e.message}")
            return BaseResponse.error(message=e.message, code=e.code, details=e.details)
        except ConflictError as e:
            self.logger.error(f"资源冲突: {e.message}")
            return BaseResponse.error(message=e.message, code=e.code, details=e.details)
        except Exception as e:
            self.logger.error(f"创建资源失败: {str(e)}")
            return BaseResponse.error(message="创建失败", code=500)
    
    async def update_or_error(self, id: str, data: Dict[str, Any]) -> BaseResponse[T]:
        """
        更新资源或返回错误响应
        
        Args:
            id: 资源ID
            data: 更新数据
            
        Returns:
            响应对象
        """
        try:
            item = await self.update(id, data)
            return BaseResponse.success(data=item, message="更新成功")
        except NotFoundError as e:
            self.logger.warning(f"资源不存在: {e.message}")
            return BaseResponse.error(message=e.message, code=e.code, details=e.details)
        except ValidationError as e:
            self.logger.error(f"数据验证失败: {e.message}")
            return BaseResponse.error(message=e.message, code=e.code, details=e.details)
        except Exception as e:
            self.logger.error(f"更新资源失败: {str(e)}")
            return BaseResponse.error(message="更新失败", code=500)
    
    async def delete_or_error(self, id: str) -> BaseResponse[bool]:
        """
        删除资源或返回错误响应
        
        Args:
            id: 资源ID
            
        Returns:
            响应对象
        """
        try:
            await self.delete(id)
            return BaseResponse.success(data=True, message="删除成功")
        except NotFoundError as e:
            self.logger.warning(f"资源不存在: {e.message}")
            return BaseResponse.error(message=e.message, code=e.code, details=e.details)
        except Exception as e:
            self.logger.error(f"删除资源失败: {str(e)}")
            return BaseResponse.error(message="删除失败", code=500)
    
    async def list_or_error(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> BaseResponse[List[T]]:
        """
        获取资源列表或返回错误响应
        
        Args:
            page: 页码
            page_size: 每页大小
            filters: 过滤条件
            
        Returns:
            响应对象
        """
        try:
            items, total = await self.list(page, page_size, filters)
            return BaseResponse.success(data=items, message="查询成功")
        except ValidationError as e:
            self.logger.error(f"参数验证失败: {e.message}")
            return BaseResponse.error(message=e.message, code=e.code, details=e.details)
        except Exception as e:
            self.logger.error(f"查询列表失败: {str(e)}")
            return BaseResponse.error(message="查询失败", code=500)
    
    def validate_pagination(
        self,
        page: int,
        page_size: int,
        max_page_size: int = 100
    ) -> Tuple[int, int]:
        """
        验证分页参数
        
        Args:
            page: 页码
            page_size: 每页大小
            max_page_size: 最大每页大小
            
        Returns:
            (page, page_size): 验证后的参数
            
        Raises:
            ValidationError: 参数验证失败
        """
        if page < 1:
            raise ValidationError(
                message="页码必须大于0",
                field="page"
            )
        
        if page_size < 1 or page_size > max_page_size:
            raise ValidationError(
                message=f"每页大小必须在1-{max_page_size}之间",
                field="page_size"
            )
        
        return page, page_size


# ==================== 导出 ====================

__all__ = [
    'ServiceError',
    'NotFoundError',
    'ValidationError',
    'ConflictError',
    'BaseResponse',
    'PaginatedResponse',
    'BaseService'
]