# 真实数据改造（继续执行）

更新时间：2026-03-07

## 本轮完成

### 1) 策略页不再回退 mock 数据

文件：`frontend/src/pages/Strategies.tsx`

- 移除本地 `mockStrategies` 兜底数据。
- 策略列表仅使用后端真实接口返回数据。
- 列表为空时展示空态（`Empty`）。
- 加载失败时仅提示错误，不再伪造展示数据。

### 2) 策略优化接入真实后端接口

文件：
- `frontend/src/services/strategy.ts`
- `frontend/src/pages/Strategies.tsx`

改造内容：
- `strategyService.optimizeStrategy` 改为提交真实请求体（含日期区间、参数空间、目标函数）。
- 策略页“优化参数”按钮调用后端 `/strategies/{id}/optimize`。
- 优化成功后自动把 `best_params` 回填到当前表单。

### 3) 后端优化接口改为真实执行

文件：`backend/api/strategies.py`

改造内容：
- `POST /api/v1/strategies/{id}/optimize` 改为真实优化流程：
  1. 从数据库读取策略。
  2. 解析 `param_ranges`（支持数组或 `min/max/step`）。
  3. 生成参数组合并逐组执行真实回测。
  4. 按 `objective` 评分，返回最优参数和评估结果。
  5. 将最优参数合并写回策略配置。
- 增加组合数上限（300）避免接口阻塞过久。
- 修复异常处理：保留 `400/404`，避免被误转为 `500`。

---

## 你现在可直接验证

1. 打开策略页（前端）查看是否仅显示真实策略数据。
2. 新建策略后刷新列表，确认数据库中可见。
3. 在策略页发起回测，再点“优化参数”，确认：
   - 优化接口返回 `best_params`
   - 表单参数被自动回填

---

## 仍待完成

1. 优化流程当前为串行执行，可继续改并行/异步任务。
2. 优化结果历史入库与查询（独立优化记录表）尚未实现。
3. 前端项目仍有历史 TypeScript 报错，需单独清理以恢复全量 build 通过。
