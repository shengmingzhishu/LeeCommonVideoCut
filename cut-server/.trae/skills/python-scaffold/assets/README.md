# {{ project_name }}

{{ description }}

## Features

- Structured Python project setup
- Configuration management with Pydantic
- Automated testing with Pytest
- Basic shell scripts for process management (start/stop)
- Makefile for common tasks

## Getting Started

### Prerequisites

- Python 3.9+
- Make (optional)

### Installation

1. Clone the repository
2. Setup environment and install dependencies:
   ```bash
   make install
   ```
   Or manually:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   ```

### Usage

To run the application:
```bash
make run
```
Or:
```bash
./start.sh
```

To stop the background process:
```bash
./stop.sh
```

## Development

### Running Tests
```bash
make test
```

### Formatting and Linting
```bash
make format
make lint
```

## Project Structure

- `{{ project_name }}/`: Main package directory
  - `main.py`: Entry point
  - `config.py`: Configuration management
- `tests/`: Test suite
- `scripts/`: Utility scripts
- `Makefile`: Task automation
