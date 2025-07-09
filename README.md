

This repository contains a Django project.

## Installation

Install the required packages (Django, pandas, numpy, Pillow, pydicom, requests, etc.):

```bash
pip install -r requirements.txt
```

# JLLM

This repository contains the JLLM review project.

## License

This project is licensed under the [MIT License](LICENSE).

# LLM Review Project

This repository contains a small Django web application used to review and edit inference results produced by a large language model. It provides an interface to create inference requests, view JSON results and track edit history.

## Environment Setup

1. **Create a virtual environment (recommended)**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   Create a `.env` file in the project root. The application reads this file on startup. Example:
   ```
   SECRET_KEY=replace_me
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   VLLM_API_URL=http://localhost:8001/v1/completions
   ```

   - `SECRET_KEY` – Django secret key.
   - `DEBUG` – set to `True` during development.
   - `ALLOWED_HOSTS` – comma separated list of allowed hosts.
   - `VLLM_API_URL` – URL of the backend API used in `editor.utils`.

## Running the Server

Apply migrations and start the development server:

```bash
python manage.py migrate
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/` by default.
