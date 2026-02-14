"""WebSocket实时行情推送"""
from typing import Set, Dict
import json
import asyncio
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from loguru import logger
import datetime

router = APIRouter()


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 活跃连接
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # 订阅关系 {stock_code: set(connection_ids)}
        self.subscriptions: Dict[str, Set[str]] = {}
        # 连接ID映射 {connection_id: (websocket, stock_codes)}
        self.connection_info: Dict[str, tuple] = {}
    
    async def connect(self, websocket: WebSocket, connection_id: str):
        """建立连接"""
        await websocket.accept()
        self.active_connections[connection_id] = {websocket}
        self.connection_info[connection_id] = (websocket, set())
        logger.info(f"WebSocket连接建立: {connection_id}")
    
    def disconnect(self, connection_id: str):
        """断开连接"""
        if connection_id in self.active_connections:
            # 取消所有订阅
            if connection_id in self.connection_info:
                _, stock_codes = self.connection_info[connection_id]
                for stock_code in stock_codes:
                    if stock_code in self.subscriptions:
                        self.subscriptions[stock_code].discard(connection_id)
            
            del self.active_connections[connection_id]
            if connection_id in self.connection_info:
                del self.connection_info[connection_id]
            logger.info(f"WebSocket连接断开: {connection_id}")
    
    async def subscribe(self, connection_id: str, stock_codes: list):
        """订阅股票行情"""
        if connection_id not in self.connection_info:
            return False
        
        _, subscribed_codes = self.connection_info[connection_id]
        
        # 添加新订阅
        for code in stock_codes:
            subscribed_codes.add(code)
            if code not in self.subscriptions:
                self.subscriptions[code] = set()
            self.subscriptions[code].add(connection_id)
        
        logger.info(f"连接 {connection_id} 订阅股票: {stock_codes}")
        return True
    
    async def unsubscribe(self, connection_id: str, stock_codes: list):
        """取消订阅"""
        if connection_id not in self.connection_info:
            return False
        
        _, subscribed_codes = self.connection_info[connection_id]
        
        for code in stock_codes:
            subscribed_codes.discard(code)
            if code in self.subscriptions:
                self.subscriptions[code].discard(connection_id)
        
        logger.info(f"连接 {connection_id} 取消订阅: {stock_codes}")
        return True
    
    async def broadcast_quote(self, stock_code: str, quote_data: dict):
        """广播行情数据"""
        if stock_code not in self.subscriptions:
            return
        
        message = {
            "type": "quote",
            "code": stock_code,
            "data": quote_data,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # 向所有订阅该股票的连接发送数据
        disconnected = []
        for connection_id in self.subscriptions[stock_code]:
            if connection_id in self.active_connections:
                for websocket in self.active_connections[connection_id]:
                    try:
                        await websocket.send_json(message)
                    except Exception as e:
                        logger.error(f"发送行情数据失败: {e}")
                        disconnected.append(connection_id)
        
        # 清理断开的连接
        for conn_id in disconnected:
            self.disconnect(conn_id)
    
    async def send_personal_message(self, message: dict, connection_id: str):
        """发送个人消息"""
        if connection_id not in self.active_connections:
            return False
        
        for websocket in self.active_connections[connection_id]:
            try:
                await websocket.send_json(message)
                return True
            except Exception as e:
                logger.error(f"发送消息失败: {e}")
                self.disconnect(connection_id)
                return False
        
        return False


# 全局连接管理器
manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket连接端点"""
    connection_id = f"conn_{id(websocket)}"
    
    await manager.connect(websocket, connection_id)
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_json()
            
            msg_type = data.get("type")
            
            if msg_type == "auth":
                # 认证（后续可以实现JWT验证）
                await manager.send_personal_message({
                    "type": "auth_result",
                    "success": True,
                    "message": "认证成功"
                }, connection_id)
            
            elif msg_type == "subscribe":
                # 订阅股票
                stock_codes = data.get("codes", [])
                await manager.subscribe(connection_id, stock_codes)
                await manager.send_personal_message({
                    "type": "subscribe_result",
                    "success": True,
                    "codes": stock_codes,
                    "message": f"订阅成功: {', '.join(stock_codes)}"
                }, connection_id)
            
            elif msg_type == "unsubscribe":
                # 取消订阅
                stock_codes = data.get("codes", [])
                await manager.unsubscribe(connection_id, stock_codes)
                await manager.send_personal_message({
                    "type": "unsubscribe_result",
                    "success": True,
                    "codes": stock_codes,
                    "message": f"取消订阅: {', '.join(stock_codes)}"
                }, connection_id)
            
            elif msg_type == "ping":
                # 心跳
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.datetime.now().isoformat()
                }, connection_id)
            
            else:
                await manager.send_personal_message({
                    "type": "error",
                    "message": f"未知消息类型: {msg_type}"
                }, connection_id)
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket客户端断开连接: {connection_id}")
        manager.disconnect(connection_id)
    
    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
        manager.disconnect(connection_id)


# 模拟行情推送任务（实际应该从数据源获取）
async def mock_market_data_generator():
    """模拟实时行情推送"""
    import random
    
    test_stocks = {
        "600771.SH": {"name": "广誉远", "price": 20.50},
        "000001.SZ": {"name": "平安银行", "price": 10.20},
        "000002.SZ": {"name": "万科A", "price": 8.50},
    }
    
    while True:
        for code, info in test_stocks.items():
            # 模拟价格波动
            change = random.uniform(-0.1, 0.1)
            new_price = info["price"] + change
            info["price"] = round(new_price, 2)
            
            # 构造行情数据
            quote_data = {
                "code": code,
                "name": info["name"],
                "price": info["price"],
                "change": round(change, 2),
                "change_percent": round((change / info["price"]) * 100, 2),
                "volume": random.randint(1000000, 5000000),
                "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
            }
            
            # 广播行情
            await manager.broadcast_quote(code, quote_data)
        
        # 每3秒推送一次
        await asyncio.sleep(3)


# 启动行情推送任务
async def start_market_data_task():
    """启动市场数据推送任务"""
    logger.info("启动实时行情推送任务")
    await mock_market_data_generator()


# 导出路由器（兼容main.py的导入）
websocket_router = router