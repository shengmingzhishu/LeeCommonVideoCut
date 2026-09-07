---
name: eval-case-design
version: "1.0.0"
lastUpdated: "2026-09-03"
description: "适用于 ai-eval-server 项目的评测用例设计场景：指导如何编写高质量的评测用例（输入构造、预期输出定义、评分规则设定），确保用例可复现、可自动化、结果可信。"
user-invocable: true
---

# 评测用例设计

## 技能目标

当需要在 ai-eval-server 中**编写或优化评测用例**时，使用本技能。

本技能提供各评测方向的用例编写最佳实践，确保用例质量高、覆盖全面、结果可复现。

## 适用场景

- 为新评测方向设计首批用例
- 补充现有方向的边界用例和异常用例
- 优化现有用例的评分规则
- 设计回归测试集（防止模型升级导致质量下降）

## 用例质量标准

一个合格的评测用例必须满足：

| 维度 | 标准 | 不合格示例 |
|------|------|-----------|
| **可复现** | 相同输入 + 相同配置 → 相同结果 | 依赖随机种子但未固定；引用外部动态数据 |
| **可自动化** | 无需人工判断即可得出分数 | 预期输出是"看起来合理"；需要人工审核 |
| **覆盖充分** | 正常 + 边界 + 异常 + 性能场景 | 只有 happy path |
| **独立性** | 用例之间无执行顺序依赖 | 用例 B 依赖用例 A 创建的数据 |

## 各方向用例模板

### 1. 文本问答（text_qa）

```json
{
  "case_id": "text_qa_001",
  "direction": "text_qa",
  "method": "ai_model",
  "name": "基础事实问答-中国首都",
  "input": {
    "question": "中国的首都是哪个城市？",
    "context": "",
    "expected_answer": "北京"
  },
  "expected_output": {
    "contains_keywords": ["北京"],
    "forbidden_keywords": ["上海", "广州", "不确定"],
    "min_score": 90,
    "max_latency_ms": 5000
  },
  "metadata": {
    "category": "factual",
    "difficulty": "easy",
    "tags": ["地理", "常识"],
    "priority": "P0"
  }
}
```

**设计要点**：
- `expected_answer` 用于精确匹配或相似度计算
- `contains_keywords` / `forbidden_keywords` 用于关键词评分
- `min_score` 设定及格线，低于此分自动标记为异常

### 2. SQL 正确性（sql_correctness）

```json
{
  "case_id": "sql_001",
  "direction": "sql_correctness",
  "method": "ai_model",
  "name": "单表查询-用户列表分页",
  "input": {
    "schema": "CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100), age INT, created_at DATETIME);",
    "natural_language_query": "查询年龄大于25岁的前10个用户，按创建时间倒序排列",
    "database_type": "mysql",
    "reference_sql": "SELECT * FROM users WHERE age > 25 ORDER BY created_at DESC LIMIT 10;"
  },
  "expected_output": {
    "semantic_equivalent": true,
    "check_execution": true,
    "test_data": [
      {"id": 1, "name": "张三", "age": 30, "created_at": "2024-01-01"},
      {"id": 2, "name": "李四", "age": 20, "created_at": "2024-06-01"}
    ],
    "expected_result_count": 1,
    "forbidden_patterns": ["SELECT *", "--", "; DROP"]
  },
  "metadata": {
    "category": "single_table",
    "difficulty": "medium",
    "tags": ["分页", "过滤", "排序"],
    "priority": "P0"
  }
}
```

**设计要点**：
- 提供 DDL schema 让 AI 理解表结构
- `reference_sql` 作为金标准答案
- `test_data` 用于实际执行对比结果
- `forbidden_patterns` 过滤危险 SQL

### 3. RAG 评分（rag_scoring）

```json
{
  "case_id": "rag_001",
  "direction": "rag_scoring",
  "method": "rag_scoring",
  "name": "检索准确性-技术文档问答",
  "input": {
    "question": "FastAPI 如何实现依赖注入？",
    "retrieved_contexts": [
      {"content": "FastAPI 使用 Depends() 函数声明依赖...", "score": 0.95, "source": "doc_page_1"},
      {"content": "Python 的依赖注入模式有多种实现...", "score": 0.72, "source": "doc_page_5"},
      {"content": "Django 的中间件机制与 FastAPI 不同...", "score": 0.45, "source": "doc_page_9"}
    ],
    "generated_answer": "FastAPI 通过 Depends() 函数声明依赖..."
  },
  "expected_output": {
    "retrieval_metrics": {
      "min_recall": 0.8,
      "min_precision": 0.7,
      "top1_relevant": true
    },
    "generation_metrics": {
      "faithfulness_min": 0.85,
      "answer_relevance_min": 0.8,
      "context_utilization_min": 0.7
    }
  },
  "metadata": {
    "category": "technical_qa",
    "difficulty": "hard",
    "tags": ["RAG", "检索", "生成"],
    "priority": "P0"
  }
}
```

**设计要点**：
- `retrieved_contexts` 包含检索结果及其相关性得分
- 分别评估检索质量和生成质量
- `faithfulness` 检查生成内容是否忠实于检索上下文

### 4. 代码评审（code_review）— 扩展方向示例

```json
{
  "case_id": "cr_001",
  "direction": "code_review",
  "method": "ai_model",
  "name": "安全漏洞检测-SQL注入",
  "input": {
    "code": "def get_user(user_id):\n    query = f\"SELECT * FROM users WHERE id = {user_id}\"\n    return db.execute(query)",
    "language": "python",
    "review_focus": ["security", "correctness"]
  },
  "expected_output": {
    "must_detect_issues": [
      {"type": "security", "severity": "high", "keyword": "SQL注入"}
    ],
    "min_score": 80,
    "expected_categories": ["security"]
  },
  "metadata": {
    "category": "security",
    "difficulty": "medium",
    "tags": ["SQL注入", "安全"],
    "priority": "P0"
  }
}
```

## 用例设计原则

### 1. 渐进式难度

每个方向都应包含不同难度的用例：

| 难度 | 占比 | 特征 |
|------|------|------|
| easy | 40% | 明确答案，单一知识点，低歧义 |
| medium | 35% | 需要多步推理，可能有多解 |
| hard | 20% | 边界情况，陷阱题，需要领域知识 |
| extreme | 5% | 压力测试，极端输入，性能边界 |

### 2. 反向用例（Negative Cases）

每种方向必须包含反向用例，验证系统能识别错误：

```json
{
  "name": "反向-幻觉检测",
  "input": {
    "question": "请介绍 2025 年发布的 Python 4.0 新特性",
    "context": ""
  },
  "expected_output": {
    "should_refuse": true,
    "refusal_keywords": ["不存在", "未发布", "没有", "截至"],
    "max_score": 30  # 如果模型编造答案，应得低分
  }
}
```

### 3. 回归保护集

为防止模型升级导致质量下降，维护一组**冻结的回归用例**：

```bash
# 回归用例目录结构
tests/regression/
├── text_qa_baseline.jsonl    # 文本问答基线（100条）
├── sql_baseline.jsonl         # SQL 基线（50条）
└── rag_baseline.jsonl         # RAG 基线（30条）
```

每次模型更新后运行回归集，对比分数变化：

| 指标 | 基线版本 | 新版本 | 变化 | 判定 |
|------|---------|--------|------|------|
| text_qa 平均分 | 87.3 | 85.1 | -2.2 | ⚠️ 需关注 |
| sql 准确率 | 92.0% | 93.5% | +1.5% | ✅ 提升 |
| rag 忠实度 | 0.89 | 0.86 | -0.03 | ⚠️ 需关注 |

## 用例批量导入格式

支持 Excel 导入时的列定义：

| 列名 | 必填 | 说明 | 示例 |
|------|------|------|------|
| case_id | 是 | 全局唯一标识 | text_qa_001 |
| direction | 是 | 评测方向 | text_qa |
| name | 是 | 用例名称 | 中国首都问答 |
| input | 是 | JSON 格式输入 | 见上方模板 |
| expected_output | 是 | JSON 格式预期 | 见上方模板 |
| priority | 否 | 优先级 P0/P1/P2 | P0 |
| tags | 否 | 标签，逗号分隔 | 地理,常识 |
| is_active | 否 | 是否启用 | true |

## 检查清单

- [ ] 每个 case_id 全局唯一
- [ ] input 字段包含该方向必需的全部参数
- [ ] expected_output 包含明确的判定条件（非主观描述）
- [ ] 难度分布合理（easy ≥ 35%，hard+extreme ≤ 25%）
- [ ] 包含反向用例（验证拒绝/纠错能力）
- [ ] 敏感信息已脱敏（无真实密钥、IP、个人信息）
- [ ] 用例可在隔离环境中独立执行
- [ ] 预期输出不依赖特定模型版本（除非是回归对比）

## 常见错误

| 错误 | 原因 | 修复 |
|------|------|------|
| 用例执行结果不稳定 | 输入含随机因素或时间敏感数据 | 固定随机种子，使用静态测试数据 |
| 评分忽高忽低 | 预期输出太模糊（如"回答合理"） | 改为可量化的关键词/分数阈值 |
| 新模型全绿但实际变差 | 缺少回归保护集 | 建立基线用例集，定期跑回归 |
| 导入失败 | Excel 中 JSON 列格式错误 | 确保 JSON 是有效格式，避免单元格内换行问题 |

## 非目标

- 不涉及用例的执行引擎实现
- 不涉及前端用例编辑器的 UI 设计
- 不自动生成用例（用例应由领域专家设计）
