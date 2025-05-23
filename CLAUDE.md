# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Virtual queuing system with SMS notifications built with FastAPI (Python backend) and React (frontend).

## Development Setup

This project uses UV for Python package management and Ruff for linting/formatting.

### Commands

- `uv sync` - Install all dependencies
- `uv sync --dev` - Install including dev dependencies
- `ruff check .` - Lint the codebase
- `ruff format .` - Format the codebase
- `python run.py` - Run the development server
- `uvicorn app.main:app --reload` - Alternative way to run the server
- `pytest` - Run tests

### Environment Variables

Copy `.env.example` to `.env` and fill in the required values.

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Alembic, Twilio
- **Package Management**: UV
- **Linting/Formatting**: Ruff
- **Database**: SQLite (development), PostgreSQL (production)