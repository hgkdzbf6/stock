# 真实数据改造进展（Auth + Strategies）

更新时间：2026-03-07

## 本次目标

将以下模块从“临时/模拟返回”切换为“真实数据库读写”：
- 认证模块（Auth）
- 策略模块（Strategies）

---

## 已完成

### 1. Auth 已接入真实数据库

文件：`backend/api/auth.py`

- 注册：校验用户名/邮箱唯一性后写入 `users`
- 登录：从数据库查询用户并校验密码哈希
- `/me`：根据 JWT `sub` 查询真实用户
- 资料更新：支持更新 `full_name/phone/email`，并校验邮箱冲突
- 修改密码：校验旧密码后更新哈希
- OAuth `tokenUrl` 修正为 `/api/v1/auth/login`

仍未完成：
- 登出 token 黑名单（可选增强）
- 头像上传存储

### 2. Strategies 已接入真实数据库

文件：`backend/api/strategies.py`

- 获取策略列表：从 `strategies` 查询，附带最近一次 `backtest_results` 的收益率/夏普
- 创建策略：真实入库（校验策略类型）
- 策略详情：真实查询 + 最近一次回测摘要
- 更新策略：真实更新
- 删除策略：真实删除
- 运行回测：
  - 优先读取数据库策略参数
  - 执行回测后写入 `backtest_results`

仍未完成：
- `/strategies/{id}/optimize` 仍是占位逻辑

### 3. 前端策略页改为优先读取后端真实数据

文件：`frontend/src/pages/Strategies.tsx`

- 页面加载时调用 `strategyService.getStrategies()`
- 回测提交改为调用 `strategyService.runBacktest()`
- 当前保留本地示例数据作为接口失败时兜底展示

---

## 验证结果

### 后端语法检查
- 已通过：`python -m py_compile api/auth.py api/strategies.py`

### 数据库读写自检
- 在 SQLite 下完成策略表增查测试并清理测试数据

---

## 注意事项

1. 前端全量 `npm run build` 当前仍有历史遗留 TS 报错（多页面未使用变量、类型导入等），不属于本次改造引入。
2. 策略页已支持真实数据，但在接口失败时仍显示本地示例；若要严格“只显示真实数据”，可移除该兜底。

---

## 下一步建议（高优先级）

1. 完成 `/strategies/{id}/optimize` 的真实优化任务逻辑
2. 去掉策略页本地示例兜底，改为空态 + 错误提示
3. 统一清理前端 TS 严格模式报错，恢复 `npm run build` 全量通过
