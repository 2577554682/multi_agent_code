from typing import TypedDict


class State(TypedDict):
    requirement: str
    spec: str
    code: str
    review: str
    review_passed: bool
    test_code: str
    test_passed: bool
    iteration: int


def initial_state(requirement: str) -> State:
    return {
        "requirement": requirement,
        "spec": "",
        "code": "",
        "review": "",
        "review_passed": False,
        "test_code": "",
        "test_passed": False,
        "iteration": 0,
    }
