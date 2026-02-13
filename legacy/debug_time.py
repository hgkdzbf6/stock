from datetime import datetime, timedelta

# 测试30分钟间隔的时间点生成
date = datetime(2025, 1, 1)  # 测试日期
interval_minutes = 30

print("=== 30分钟间隔时间点测试 ===")

# 上午时段：9:30-11:30
print("上午时段 (9:30-11:30):")
morning_times = []
current_time = date.replace(hour=9, minute=30, second=0, microsecond=0)
end_morning = date.replace(hour=11, minute=30, second=0, microsecond=0)

while current_time <= end_morning:
    morning_times.append(current_time)
    print(f"  {current_time.strftime('%H:%M:%S')}")
    current_time += timedelta(minutes=interval_minutes)

print(f"上午时段总计: {len(morning_times)}个时间点")

# 下午时段：13:00-15:00
print("\n下午时段 (13:00-15:00):")
afternoon_times = []
current_time = date.replace(hour=13, minute=0, second=0, microsecond=0)
end_afternoon = date.replace(hour=15, minute=0, second=0, microsecond=0)

while current_time <= end_afternoon:
    afternoon_times.append(current_time)
    print(f"  {current_time.strftime('%H:%M:%S')}")
    current_time += timedelta(minutes=interval_minutes)

print(f"下午时段总计: {len(afternoon_times)}个时间点")

# 合并
day_times = morning_times + afternoon_times
print(f"\n全天总计: {len(day_times)}个时间点")

# 检查预期
print(f"\n预期分析:")
print(f"上午：9:30, 10:00, 10:30, 11:00, 11:30 = 5个点")
print(f"下午：13:00, 13:30, 14:00, 14:30, 15:00 = 5个点")
print(f"总计应该是: 10个点")
print(f"实际生成: {len(day_times)}个点")

# 但是akshare实际只有8个点，让我们看看akshare的时间点
print(f"\n=== akshare实际时间点对比 ===")
akshare_times = ["10:00:00", "10:30:00", "11:00:00", "11:30:00", "13:30:00", "14:00:00", "14:30:00", "15:00:00"]
print(f"akshare实际时间点: {akshare_times}")
print(f"akshare总计: {len(akshare_times)}个点")
print(f"缺少的时间点: 9:30:00, 13:00:00") 