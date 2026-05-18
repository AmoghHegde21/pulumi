---
description: This workflow enforces an automated development lifecycle where every code change is validated through linting, testing, failure analysis, automatic fixes, and regression verification. The AI must iteratively test and resolve issues until all impacted scenarios, edge cases, and validations pass successfully while maintaining production-quality standards and preventing regressions.
---
# AI Development Workflow

## Objective
Ensure every code change is validated with tests, fixes issues automatically where possible, and verifies all critical scenarios before completion.

---

# Workflow: Develop → Test → Fix → Retest

## ALWAYS

- Understand the existing implementation before modifying code
- Run linting before running tests
- Generate or update unit tests for every code change
- Validate edge cases and failure scenarios
- Re-run all impacted tests after fixes
- Ensure backward compatibility unless explicitly changing behavior
- Preserve existing public interfaces unless instructed otherwise
- Add meaningful logging for failures
- Verify imports, typing, and formatting
- Ensure code is production-ready before finalizing

---

# TESTING REQUIREMENTS

## ALWAYS validate

- Happy path
- Invalid inputs
- Null/None handling
- Empty values
- Boundary conditions
- Exception scenarios
- Retry/failure behavior
- Integration impact
- Existing functionality regression

---

# FIX STRATEGY

When tests fail:

1. Identify root cause
2. Fix the implementation
3. Re-run failing tests
4. Re-run complete impacted suite
5. Ensure fix does not introduce regressions
6. Verify formatting and linting again

---
