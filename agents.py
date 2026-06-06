import sys

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from my_llm import llm
from state import State
from config import MAX_ITERATIONS


def _stream_chain(template: str, **kwargs) -> str:
    """Run chain with token-by-token streaming to stdout."""
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()

    full_text = ""
    for chunk in chain.stream(kwargs):
        sys.stdout.write(chunk)
        sys.stdout.flush()
        full_text += chunk
    return full_text


def _strip_code_fences(code: str) -> str:
    code = code.strip()
    if code.startswith("```"):
        newline_idx = code.find("\n")
        if newline_idx != -1:
            code = code[newline_idx + 1:]
        if code.endswith("```"):
            code = code[:-3]
    return code.strip()


def _wrap_code(code: str) -> str:
    return f"```python\n{_strip_code_fences(code)}\n```"


def _review_passed(review: str) -> bool:
    review_lower = review.lower()
    fail_markers = ["不通过", "not pass", "fail", "issues found", "bug"]
    pass_markers = ["通过", "pass", "approved", "looks good", "lgtm"]
    has_fail = any(m in review_lower for m in fail_markers)
    has_pass = any(m in review_lower for m in pass_markers)
    return has_pass and not has_fail


# ═══════════════════════════════════════════════════════════════
#  Agent Nodes
# ═══════════════════════════════════════════════════════════════

def product_manager(state: State) -> State:
    print(f"{'─' * 55}\n  📋  产品经理\n{'─' * 55}")
    template = """\
你是一个资深产品经理。根据以下需求，输出详细的技术规格说明。

需求：{requirement}

技术规格要求：
1. 功能描述
2. 输入输出说明
3. 边界条件
4. 示例用法

技术规格："""
    state["spec"] = _stream_chain(template, requirement=state["requirement"])
    print()
    return state


def programmer(state: State) -> State:
    print(f"{'─' * 55}\n  💻  程序员\n{'─' * 55}")
    template = """\
你是一个经验丰富的Python程序员。根据技术规格写出完整代码。

技术规格：
{spec}

要求：
- 代码要完整、可运行
- 包含必要的注释
- 处理边界情况
- 只输出代码，不要解释

代码：
```python"""
    code = _stream_chain(template, spec=state["spec"])
    print()
    state["code"] = _wrap_code(code)
    return state


def code_reviewer(state: State) -> State:
    print(f"{'─' * 55}\n  🔍  代码审查员\n{'─' * 55}")
    template = """\
你是一个严格的代码审查专家。审查以下代码。

代码：
{code}

检查项：
1. 逻辑是否正确
2. 是否有 bug
3. 是否处理了边界情况
4. 代码风格是否规范

输出格式：
- 如果你认为代码正确无误，回复"通过"并简要说明理由
- 如果你发现问题，回复"不通过"并说明具体问题和修改建议

审查结果："""
    review = _stream_chain(template, code=state["code"])
    print()
    state["review"] = review
    state["review_passed"] = _review_passed(review)

    if state["review_passed"]:
        print(f"  ✅  审查通过\n")
    else:
        print(f"  ❌  审查不通过 → 返回修复\n")
    return state


def tester(state: State) -> State:
    print(f"{'─' * 55}\n  🧪  测试工程师\n{'─' * 55}")
    template = """\
你是一个测试工程师。为以下代码编写测试用例。

代码：
{code}

要求：
1. 写出 pytest 格式的测试代码
2. 包含正常情况和边界情况
3. 测试函数名以 test_ 开头

测试代码：
```python"""
    state["test_code"] = _stream_chain(template, code=state["code"])
    print()
    state["test_passed"] = True
    print(f"  ✅  测试用例已生成\n")
    return state


def fix_code(state: State) -> State:
    if state["iteration"] >= MAX_ITERATIONS:
        print(f"\n  ⚠️   已达最大迭代次数 ({MAX_ITERATIONS})，强制通过\n")
        state["review_passed"] = True
        return state

    print(f"{'─' * 55}\n  🔧  程序员 · 第 {state['iteration'] + 1} 次修复\n{'─' * 55}")
    template = """\
你是程序员。根据审查意见修改代码。

原代码：
{code}

审查意见：
{review}

请输出修改后的完整代码：
```python"""
    fixed = _stream_chain(
        template,
        code=state["code"],
        review=state["review"],
    )
    print()
    state["code"] = _wrap_code(fixed)
    state["iteration"] += 1
    return state
