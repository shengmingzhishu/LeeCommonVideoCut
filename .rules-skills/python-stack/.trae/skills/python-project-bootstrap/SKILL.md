---
name: python-project-bootstrap
description: "在工作目录下创建或补充通用 Python 项目结构。适用于初始化新项目脚手架、添加常见目录如 dao 和 service、将可选的 db 或 openai 结构仅作为参考扩展，以及不覆盖现有文件等场景。"
argument-hint: "项目用途或包名"
user-invocable: true
---

# Python Project Bootstrap

> **定位**：最小化项目初始化工具。只创建目录结构 + 基础配置文件，**不生成**模板代码。
>
> **与 python-scaffold 的区别**：
> - `python-project-bootstrap` = 轻量初始化（目录 + pyproject.toml + .gitignore + README），适合快速起步
> - `python-scaffold` = 完整脚手架（含模板代码、测试脚本、CI 配置、检查脚本），适合团队规范化项目
>
> **选择建议**：需要"能跑的最小项目"用 bootstrap；需要"开箱即用的完整项目"用 scaffold。

## assets处理

- `assets/static/`目录的各个子目录下的文件直接复制到项目中对应位置，保持原有目录结构不变。例：不得把env.py复制到config目录，需要复制到utils目录下
- `assets/*.template`目录下的文件作为模板文件，复制到项目中对应位置，并将其中的占位符替换为用户输入的参数。

## 占位符说明：

- 替换`<PACKAGE_NAME>`时，替换为UPPER_CASE（大写下划线）的包名，替换`<package_name>`时，替换为snake_case（小写下划线）的包名。

## python模块说明

- 每个包下都包含一个`__init__.py`文件，标志该目录为Python包。

## 项目目录结构

```text
.
├── bin/
│   ├── kill.sh
│   ├── main.ss
│   ├── run.sh
│   └── start.sh
├── logs/
│   └── run.log
├── resources/
│   ├── .env.prod
│   └── .env.test
├── src/
│   └── <package_name>/
│       ├── main.py
│       ├── config/
│       ├── controllers/
│       │   └── controller.py
│       ├── models/
│       ├── services/
│       └── utils/
│           ├── asynchttp.py
│           ├── dateutil.py
│           ├── db.py
│           ├── env.py
│           ├── llmclient.py
│           ├── logs.py
│           ├── redismgr.py
│           ├── string.py
│           ├── tasks.py
│           ├── tools.py
│           └── utils.py
├── tests/
│   └── test_smoke.py
├── tree.py
├── .gitignore
├── README.md
├── requirements.txt
├── GET_STARTED.md
└── pyproject.toml
```
