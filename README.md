# FUR AND FURBLE

A FastAPI-based application for FUR and FURBLE application.

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

- [Python 3.8+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and resolver

### Cloning the Repository

```bash
git clone https://github.com/Sr-Raise/FandFstudio.git
cd FandFstudio
```

### Installing Dependencies

This project uses `uv` for package management. If you don't have `uv` installed, you can install it following the [official installation guide](https://github.com/astral-sh/uv#installation).

Once you have `uv` installed, run:

```bash
# Create a virtual environment
uv venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On Unix or MacOS:
source .venv/bin/activate

# Install dependencies
uv uv pip install -r pyproject.toml
```

## Running the Application

To start the FastAPI server:

```bash
python main.py
```

The API should now be running at `http://localhost:8000`.

You can access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
