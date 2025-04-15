# Agent API

A Langgraph Chatbot FastAPI Template that provides intelligent agent capabilities including chatbot and minute writer functionalities.

## Features

- **Chatbot Agent**: Intelligent conversational agent built with Langgraph
- **Minute Writer Agent**: Automated meeting minutes generation
- **FastAPI Integration**: Modern, fast web API framework
- **Streamlit UI**: Interactive web interface for testing and demonstration

## Prerequisites

- Python 3.11 or higher
- Poetry (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd agent_api
```

2. Create a virtual environment:
```bash
python -m venv .venv
```

3. Activate the virtual environment:
```bash
source .venv/bin/activate
```

4. Install Poetry (if not already installed):
```bash
pip install poetry
```

5. Install dependencies:
```bash
poetry install
```

## Development

### Setting up the Development Environment

1. Install development dependencies:
```bash
poetry install --with dev
```

2. Run tests:
```bash
pytest
```

### Code Quality

This project uses Ruff for code formatting and linting. Configuration can be found in `pyproject.toml`.

To format and lint your code:
```bash
poetry run python cmd.py format
poetry run python cmd.py check
```

### Project Structure

```
.
├── src/
│   ├── agent/          # Core agent implementation
│   ├── api/            # API endpoints and schemas
│   ├── core/           # Core functionality and config
│   └── main.py         # Application entry point
├── tests/              # Test files
├── pyproject.toml      # Project configuration and dependencies
└── README.md          # Project documentation
```