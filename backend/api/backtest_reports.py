"""回测报告API - 文件存储"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import json
import os
from loguru import logger

router = APIRouter()

# 回测报告存储目录
BACKTEST_REPORTS_DIR = Path("data/backtest_reports")
BACKTEST_REPORTS_DIR.mkdir(parents=True, exist_ok=True)


class BacktestReportSave(BaseModel):
    """保存回测报告请求"""
    data: Dict[str, Any]
    strategy_name: Optional[str] = None


class BacktestReportResponse(BaseModel):
    """回测报告响应"""
    filename: str
    strategy_name: str
    stock_code: str
    start_date: str
    end_date: str
    create_time: str
    file_path: str


def _generate_report_filename(stock_code: str, strategy_name: str) -> str:
    """生成报告文件名"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # 清理策略名称中的特殊字符
    clean_strategy = strategy_name.replace(" ", "_").replace("/", "_")
    return f"{stock_code}_{clean_strategy}_{timestamp}.json"


@router.post("/save")
async def save_backtest_report(request: BacktestReportSave):
    """保存回测报告到文件"""
    try:
        logger.info(f"保存回测报告: {request.strategy_name}")
        
        # 从数据中提取关键信息
        data = request.data
        stock_code = data.get('stock_code', 'unknown')
        start_date = data.get('start_date', '')
        end_date = data.get('end_date', '')
        strategy_name = request.strategy_name or '未命名策略'
        
        # 生成文件名
        filename = _generate_report_filename(stock_code, strategy_name)
        file_path = BACKTEST_REPORTS_DIR / filename
        
        # 添加元数据
        report_data = {
            'metadata': {
                'create_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'strategy_name': strategy_name,
                'stock_code': stock_code,
                'start_date': start_date,
                'end_date': end_date,
                'filename': filename
            },
            'data': data
        }
        
        # 保存到文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"回测报告已保存: {filename}")
        
        return {
            "code": 200,
            "message": "回测报告保存成功",
            "data": {
                "filename": filename,
                "file_path": str(file_path)
            }
        }
        
    except Exception as e:
        logger.error(f"保存回测报告失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"保存回测报告失败: {str(e)}"
        )


@router.get("/list", response_model=List[BacktestReportResponse])
async def list_backtest_reports():
    """获取所有回测报告列表"""
    try:
        logger.info("获取回测报告列表")
        
        reports = []
        
        # 遍历报告目录
        for file_path in BACKTEST_REPORTS_DIR.glob("*.json"):
            try:
                # 读取文件元数据
                with open(file_path, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                
                metadata = report_data.get('metadata', {})
                
                reports.append({
                    'filename': file_path.name,
                    'strategy_name': metadata.get('strategy_name', '未知策略'),
                    'stock_code': metadata.get('stock_code', '未知'),
                    'start_date': metadata.get('start_date', ''),
                    'end_date': metadata.get('end_date', ''),
                    'create_time': metadata.get('create_time', ''),
                    'file_path': str(file_path)
                })
                
            except Exception as e:
                logger.warning(f"读取报告文件失败 {file_path}: {e}")
                continue
        
        # 按创建时间倒序排列
        reports.sort(key=lambda x: x['create_time'], reverse=True)
        
        return reports
        
    except Exception as e:
        logger.error(f"获取回测报告列表失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取回测报告列表失败: {str(e)}"
        )


@router.get("/load/{filename}")
async def load_backtest_report(filename: str):
    """加载指定的回测报告"""
    try:
        logger.info(f"加载回测报告: {filename}")
        
        # 验证文件名安全性
        if not filename.endswith('.json') or '/' in filename or '\\' in filename:
            raise HTTPException(status_code=400, detail="无效的文件名")
        
        file_path = BACKTEST_REPORTS_DIR / filename
        
        # 检查文件是否存在
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="回测报告不存在")
        
        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        
        # 返回数据和元数据
        return {
            "code": 200,
            "message": "加载成功",
            "data": report_data['data'],
            "metadata": report_data['metadata']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"加载回测报告失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"加载回测报告失败: {str(e)}"
        )


@router.delete("/{filename}")
async def delete_backtest_report(filename: str):
    """删除回测报告"""
    try:
        logger.info(f"删除回测报告: {filename}")
        
        # 验证文件名安全性
        if not filename.endswith('.json') or '/' in filename or '\\' in filename:
            raise HTTPException(status_code=400, detail="无效的文件名")
        
        file_path = BACKTEST_REPORTS_DIR / filename
        
        # 检查文件是否存在
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="回测报告不存在")
        
        # 删除文件
        os.remove(file_path)
        
        logger.info(f"回测报告已删除: {filename}")
        
        return {
            "code": 200,
            "message": "回测报告删除成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除回测报告失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"删除回测报告失败: {str(e)}"
        )