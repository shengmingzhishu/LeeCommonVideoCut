---
name: debugging
version: 1.0.0
description: 结构化调试流程。日志分析、断点调试、性能 profiling、内存泄漏排查。遇到复杂问题时使用。
---

# 调试技能

## 定位

提供系统化的调试方法论和工具链，避免盲目修改，提高问题定位效率。

## 调试方法论

### 第一步：复现与定位

```
1. 确认复现条件（环境、数据、操作步骤）
2. 最小化复现场景（剥离无关代码/配置）
3. 确定问题范围（前端/后端/接口/数据库/网络）
```

**范围判断矩阵**：

| 现象 | 前端问题 | 后端问题 | 网络问题 |
|------|---------|---------|---------|
| Console 有 JS 错误 | 是 | — | — |
| Network 返回 4xx/5xx | — | 是 | — |
| Network 超时/无响应 | — | 可能 | 是 |
| 页面渲染异常 | 是 | 可能 | — |
| 数据不正确 | 可能 | 是 | — |
| 特定环境才出现 | 可能 | 可能 | 是 |

### 第二步：信息收集

#### 后端调试

```python
# 1. 日志分析（通过 trace_id 串联）
grep "tx:a1b2c3d4" logs/app.log

# 2. 断点调试（VSCode/PyCharm）
import pdb; pdb.set_trace()
# 或
breakpoint()

# 3. 请求检查
# FastAPI 自动文档: http://localhost:8000/docs
# 或 curl 手动测试
curl -X POST http://localhost:8000/api/eval/suites \
  -H "Authorization: Bearer xxx" \
  -H "Content-Type: application/json" \
  -d '{"title": "test"}'
```

#### 前端调试

```typescript
// 1. DevTools Console 检查错误
// 2. Network 面板检查请求/响应
// 3. React DevTools 检查组件树和 props
// 4. Redux/Zustand DevTools 检查状态变化
// 5. Source 断点调试

// 临时调试日志（提交前清除）
console.log('debug:', { state, props });
```

### 第三步：根因分析

```
现象 → 直接原因 → 根本原因 → 修复方案
```

**根因分析方法**：
- **5 Whys**：连续追问 5 次"为什么"
- **二分法**：注释掉一半代码，确认问题是否消失
- **对比法**：与正常工作的版本对比差异
- **日志注入法**：在关键路径插入日志，确认执行路径

### 第四步：修复与验证

- 选择与之前失败方案不同的思路
- 修复后立即运行对应验证（单元测试/程序运行/浏览器验证）
- 添加回归测试，防止同类问题复发
- 记录调试过程到 `plan/03-问题记录.md`

## 性能 Profiling

### 后端性能分析

```python
# cProfile 性能分析
import cProfile
cProfile.run('your_function()', 'profile_output.prof')

# 分析结果
python -m pstats profile_output.prof
# 或使用 snakeviz 可视化
pip install snakeviz
snakeviz profile_output.prof
```

### 前端性能分析

- Chrome DevTools Performance 面板录制
- React Profiler 检查组件渲染时间
- Lighthouse CI 自动化性能检测

## 内存泄漏排查

### 后端

```python
# 使用 memory_profiler
from memory_profiler import profile

@profile
def memory_intensive_function():
    # ...
    pass
```

### 前端

- Chrome DevTools Memory 面板 → 堆快照对比
- 检查未清理的 setInterval/setTimeout
- 检查未移除的事件监听器
- 检查闭包引用的大对象

## 使用时机

- 反复修复不通过时（触发卡点恢复机制后）
- 性能问题排查
- 内存泄漏排查
- 复杂业务逻辑错误
- 跨端问题定位
