# What is Behavior-Driven Development (BDD)?

**Behavior-Driven Development (BDD)** is a software development approach that encourages collaboration between developers, QA, and non-technical or business participants in a software project.

Instead of writing tests that are highly technical and only readable by developers, BDD focuses on the **behavior** of the application from the user's perspective. 

## The Core Idea

The core idea is simple: **Write tests in plain English before writing the code.** 

By doing this:
1. **Business people** can read the tests and confirm "Yes, that is exactly how we want the app to behave."
2. **Developers** know exactly what they need to code to make the test pass.
3. **QA testers** have a clear, automatable checklist of behaviors to verify.

## How it works

BDD is typically broken down into three phases:

1. **Discovery:** The team (Product managers, developers, testers) discuss what a feature should do in plain language.
2. **Formulation:** Those discussions are written down into structured English rules. We use a syntax called **Gherkin** for this (more on that in the next file).
3. **Automation:** Developers write brief technical scripts (using a tool like `pytest-bdd`) that connect the plain English sentences to actual Python code that tests the software.

## Why is it useful?

- **Living Documentation:** The tests become a source of truth for how the application is supposed to behave. Because they are written in English, anyone can read them to understand the system.
- **Fewer Misunderstandings:** Because the requirements are strict and testable, developers don't accidentally build the wrong thing.
- **Easy to read:** When a test fails, it doesn't say `Error UserAuthException Line 45`. It says `"Given the user is on the login page... When they enter an incorrect password... Then they should see an error message" - FAILED`. This makes it immediately obvious what is broken.

[Next up: Learn how we write these English tests in Gherkin Syntax](02_Gherkin_Syntax.md)
