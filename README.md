# Python Project

A Python project template with best practices.

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)

## Setup

### 1. Create and Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## Project Structure

```
.
├── src/              # Source code
├── tests/            # Unit tests
├── requirements.txt  # Project dependencies
└── README.md         # This file
```

## Running the Project

```bash
python src/main.py
```

## Running Tests

```bash
pytest tests/
```

## Code Quality

Format code with Black:
```bash
black src/ tests/
```

Lint with Flake8:
```bash
flake8 src/ tests/
```

Type checking with mypy:
```bash
mypy src/
```

## License

MIT
