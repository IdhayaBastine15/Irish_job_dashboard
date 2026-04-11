# BDD and Gherkin Guide with Pytest

Welcome to the Behavior-Driven Development (BDD) and Gherkin guide for the Irish Jobs Dashboard project! 

This folder acts as a tutorial to help you understand how our tests will be written in plain, readable English components, and how those components translate into actual python code using `pytest` and `pytest-bdd`.

## Table of Contents

1. [What is BDD?](01_What_is_BDD.md) - Start here for the high-level concepts.
2. [Gherkin Syntax](02_Gherkin_Syntax.md) - Learn how we write human-readable test scenarios.
3. [Pytest-BDD Basic Example](03_Pytest_BDD_Basic_Example.md) - Understand how we link those English tests to Python code.

## The Example Test Directory

Inside the `example_test` folder, you will find a complete (but simple) BDD test for logging into an application.
- `login.feature`: The test written in simple English.
- `test_login.py`: The Python script that runs the English test.

Read through these files in order, and you'll be writing BDD tests in no time!
