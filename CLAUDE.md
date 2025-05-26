# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Virtual queuing system with SMS notifications built with FastAPI (Python backend) and React (frontend).

## Development Principles

### Test-Driven Development (TDD)
When implementing new features or fixing bugs:
1. **Write tests first** - Create failing tests that define the desired behavior
2. **Make tests pass** - Write the minimal code needed to pass the tests
3. **Refactor** - Clean up the code while keeping tests green
4. **Repeat** - Continue the cycle for each new feature

This ensures high code quality, better design, and comprehensive test coverage.

## Development Setup

This project uses UV for Python package management and Ruff for linting/formatting.

### Commands

- `uv sync --extra dev` - Install including dev dependencies
- `ruff check .` - Lint the codebase
- `ruff format .` - Format the codebase
- `uv run python run.py` - Run the development server
- `cd client && npm run dev` - Run the frontend
- `uv run pytest -v` - Run tests
- `uv run python create_dummy_data.py` - Create test data for development
- `pre-commit install` - Install pre-commit hooks
- `pre-commit run --all-files` - Run pre-commit on all files

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Alembic, Twilio
- **Package Management**: UV
- **Linting/Formatting**: Ruff
- **Database**: SQLite (development), PostgreSQL (production)