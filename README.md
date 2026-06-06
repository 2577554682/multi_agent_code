# Multi-Agent Code Generation

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/langgraph-0.2+-green.svg)](https://github.com/langchain-ai/langgraph)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)

基于 **LangGraph** 构建的多智能体协作代码生成系统，模拟软件开发团队的角色分工与协作流程。

## 工作流

```
用户需求
  │
  ▼
┌──────────────┐
│  📋 产品经理  │  分析需求 → 输出技术规格
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  💻 程序员    │  根据规格 → 生成代码
└──────┬───────┘
       │
       ▼
┌──────────────┐     ❌ 不通过       ┌──────────────┐
│  🔍 代码审查  │ ─────────────────→ │  🔧 修复代码  │
└──────┬───────┘ ←───────────────── └──────────────┘
       │  ✅ 通过          (最多循环 3 次)
       ▼
┌──────────────┐
│  🧪 测试工程  │  编写 pytest 测试用例
└──────┬───────┘
       │
       ▼
    最终交付
```

5 个 Agent 各司其职，代码审查不通过时自动进入"审查 → 修复 → 再审查"循环，最多迭代 3 次。

## 项目结构

```
multi_agent_code/
├── agents.py          # 5 个 Agent 节点（产品经理/程序员/审查/测试/修复）
├── graph.py           # LangGraph 图构建 + 条件路由
├── state.py           # 共享状态定义 + 初始化
├── main.py            # 入口：驱动图流式执行 + 终端 UI
├── config.py          # 集中配置（模型名、温度、最大迭代次数）
├── my_llm.py           # LLM 客户端工厂
├── env_utils.py        # 环境变量加载
├── .env.example        # 环境变量模板
├── requirements.txt    # 依赖清单
└── .gitignore
```

### 模块职责

| 模块 | 职责 |
|---|---|
| `agents.py` | 所有 Agent 节点的实现，含流式输出、代码围栏清洗、审查判定等工具函数 |
| `graph.py` | 用 `StateGraph` 构建 DAG，注册节点、边、条件分支，返回 `compiled` 图 |
| `state.py` | `State` TypedDict 定义 8 个共享字段 + `initial_state()` 工厂函数 |
| `main.py` | 入口逻辑：构建图 → `app.stream()` 驱动执行 → 终端美化输出 |
| `config.py` | `MAX_ITERATIONS` / `MODEL_NAME` / `TEMPERATURE` 三处集中配置 |
| `my_llm.py` | 封装 `ChatOpenAI`，从 `env_utils` 读取凭证，从 `config` 读取参数 |
| `env_utils.py` | `python-dotenv` 加载 `.env`，暴露 `API_KEY` / `BASE_URL` |

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-username/multi-agent-code.git
cd multi-agent-code
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 填入你的 API 信息：

```env
API_KEY=your-api-key-here
BASE_URL=https://api.example.com/v1
```

本项目使用 NVIDIA NIM API（兼容 OpenAI 协议），你也可以换成任意兼容的 API 端点。

### 4. 运行

```bash
python main.py
```

默认示例是"判断质数"函数。你也可以在代码中自定义需求：

```python
from main import run

run("""
写一个 REST API 客户端，支持 GET/POST 请求，
自动重试 3 次，超时 10 秒。
""")
```

## 配置说明

所有可调参数集中在 `config.py`：

```python
# config.py
MAX_ITERATIONS = 3                     # 审查-修复最大循环次数
MODEL_NAME = "openai/gpt-oss-20b"      # 模型名称
TEMPERATURE = 0.4                      # 生成温度
```

## 技术栈

| 组件 | 用途 |
|---|---|
| [LangGraph](https://github.com/langchain-ai/langgraph) | 有向图编排，条件路由，流式执行 |
| [LangChain](https://github.com/langchain-ai/langchain) | Prompt 模板，输出解析，链式调用 |
| [langchain-openai](https://github.com/langchain-ai/langchain) | OpenAI 兼容的 Chat 模型封装 |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | 环境变量管理 |

## 设计要点

**代码围栏防嵌套** — 修复循环中每次重写前先 `_strip_code_fences()` 去掉外层标记再统一 `_wrap_code()`，避免迭代中产生 ```` ```python\n```python\n... ``` ```` 的嵌套围栏。

**双语审查判定** — `_review_passed()` 同时匹配中英文通过/不通过标识词（`通过`/`pass`/`approved` vs `不通过`/`fail`/`bug`），不依赖 LLM 输出的精确措辞。

**强制终止保护** — 审查-修复循环内置 `MAX_ITERATIONS` 上限，达到后强制标记通过并继续流程，杜绝死循环。

**流式两层输出** — 外层用 LangGraph 原生 `app.stream()` 按节点驱动；内层每个 Agent 用 `chain.stream()` 逐 token 刷屏，实时看到 LLM 生成过程。

## 自定义 Agent

新增 Agent 只需三步：

1. **`agents.py`** — 添加节点函数 `def my_agent(state: State) -> State`
2. **`graph.py`** — `add_node("my_agent", my_agent)` + 连线
3. **`state.py`** — 如需新字段，扩展 `State` TypedDict 和 `initial_state()`

## License

MIT
