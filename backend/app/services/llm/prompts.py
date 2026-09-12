CODE_GENERATION_PROMPT = """
You are an expert software engineer.

Generate clean, production-quality code for the following requirement.

Requirements:
{requirement}

Rules:
- If the requirement asks for a full application, project, or multi-file system:
  - Output ALL files needed to run the app, using this exact format per file:
    === FILE: path/to/filename.ext ===
    (file content here)
  - Include a minimal but complete and working file structure (e.g. main entry point, config, key modules).
  - Keep it basic and functional to save tokens — no boilerplate comments, no placeholder TODOs.
  - Include a short README.md with instructions to run the app.
- If the requirement is a single function, algorithm, or script:
  - Return ONLY the Python code for solution.py.
- Do NOT use markdown fencing (no ```).
- Do NOT explain your solution.
"""


CODE_AND_TESTS_PROMPT = """
You are an expert Python engineer. Generate BOTH the implementation AND its pytest tests in a single response.

Requirement:
{requirement}

Return your answer in exactly this format — no markdown, no explanations:

=== SOLUTION ===
(your Python implementation here)

=== TESTS ===
(your pytest tests here — import from solution)

Rules:
- Tests must use pytest and import from solution.
- Cover normal cases and edge cases.
- Keep tests concise but thorough.
- Do NOT use markdown fencing.
"""


TEST_GENERATION_PROMPT = """
You are an expert Python QA engineer. Generate pytest tests for this code.

Python Code:
{code}

Rules:
- Use pytest, import from solution.
- Cover normal and edge cases.
- Return ONLY Python code, no markdown, no explanations.
"""


DEBUGGER_PROMPT = """
You are an expert Python engineer. Fix this code so all tests pass.

Code:
{code}

Test output:
{test_output}

Rules:
- Return ONLY the corrected Python code.
- Preserve function/class names and signatures.
- No markdown, no explanations.
"""