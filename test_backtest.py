"""测试回测API"""
import requests
import json

# 测试回测API
url = "http://localhost:8000/api/v1/strategies/1/backtest"

payload = {
    "stock_code": "600771",
    "start_date": "2025-08-14",
    "end_date": "2026-02-14",
    "frequency": "daily",
    "initial_capital": 100000,
    "strategy_type": "MA",
    "custom_params": {
        "short_window": 5,
        "long_window": 20
    }
}

print("发送回测请求...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

response = requests.post(url, json=payload)

print(f"\n状态码: {response.status_code}")
print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# 检查关键数据
data = response.json().get('data', {})
print(f"\n=== 回测结果摘要 ===")
print(f"股票代码: {data.get('stock_code')}")
print(f"数据点数: {data.get('data_points')}")
print(f"初始资金: {data.get('initial_capital')}")
print(f"最终资金: {data.get('final_capital')}")
print(f"总收益率: {data.get('metrics', {}).get('total_return'):.2%}")
print(f"交易次数: {data.get('metrics', {}).get('trade_count')}")
print(f"胜率: {data.get('metrics', {}).get('win_rate'):.2%}")
print(f"夏普比率: {data.get('metrics', {}).get('sharpe_ratio'):.2f}")

# 检查交易明细
trades = data.get('trades', [])
print(f"\n=== 交易明细 (共{len(trades)}笔) ===")
for i, trade in enumerate(trades[:5]):  # 只显示前5笔
    print(f"{i+1}. {trade['date']} - {trade['type']} @ {trade['price']:.2f} x {trade['amount']:.0f}")

# 检查净值曲线
equity_curve = data.get('equity_curve', [])
print(f"\n=== 净值曲线 (共{len(equity_curve)}个点) ===")
for i, point in enumerate(equity_curve[:5]):  # 只显示前5个点
    print(f"{i+1}. {point['date']} - 总资产: {point['total_value']:.2f}, 收益: {point['cumulative_return']:.2%}")

if len(equity_curve) > 5:
    print(f"... (还有 {len(equity_curve)-5} 个数据点)")