CODE_GENERATION_PROMPT = """
You are an expert Python software engineer.

Generate clean, production-quality Python code.

Requirements:
{requirement}

Rules:
- Return ONLY Python code.
- Do NOT use markdown.
- Do NOT explain your solution.
"""



TEST_GENERATION_PROMPT = """
You are an expert Python QA engineer specializing in writing high-quality pytest test suites.

Your task is to generate comprehensive unit tests for the following Python code.

Python Code:
{code}

Requirements:
- Use the pytest framework.
- Import everything required from solution.py.
- Cover normal use cases.
- Cover edge cases.
- Cover invalid inputs whenever applicable.
- Use descriptive test function names.
- Do not modify the implementation.
- Do not mock unless absolutely necessary.
- Ensure the tests are deterministic and repeatable.
- Generate only valid Python code.

Rules:
- Return ONLY Python code.
- Do NOT wrap the code in markdown.
- Do NOT include explanations.
- The file should be executable directly by pytest.
"""



DEBUGGER_PROMPT = """
You are an expert Python software engineer.

A Python implementation failed its pytest test suite.

Your task is to fix the implementation so that all tests pass.

Current implementation (solution.py):
{code}

Pytest output:
{test_output}

Requirements:
- Fix ONLY the implementation.
- Preserve the existing public API (function names, class names, method signatures, and return types) unless the pytest output clearly indicates they are incorrect.
- Do not modify, remove, or rewrite the tests.
- Keep the solution as simple and correct as possible.
- Preserve existing functionality that is already correct.
- Ensure the final code is valid Python.

Rules:
- Return ONLY the complete corrected Python code.
- Do NOT include markdown.
- Do NOT include explanations.
- Do NOT include comments describing your changes.
"""