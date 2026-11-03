## 快速开始

## 注意事项

当前版本还需要手动创建venv，自定下载依赖包，然后执行如下命令输出requirements.txt

```python
pip freeze > requirements.txt
```

根目录下的tree.py会把当前项目的树型结构输出到tree.txt中

```python
python tree.py
```


### utils工具集简要说明

**asynchttp.py**: HTTP工具，需要安装asyncio、aiohttp

**dateutil.py**: 日期工具

**db.py**: 数据库工具，需要安装sqlalchemy

**env.py**: 环境配置

**llmclient.py**: 大模型访问工具，需要安装openai、asyncio、mcp

**logs.py**: 日志工具，默认存放路径：当前目录/logs/

**redismgr.py**: redis工具，需要安装redis、asyncio

**string.py**: 字符串工具

**tasks.py**: 任务并发管理器工具

**tools.py**: 大模型输出提取工具

**utils.py**: 单例模式工具