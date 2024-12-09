FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    VENV_PATH="/app/.venv"

RUN python -m venv $VENV_PATH
ENV PATH="$VENV_PATH/bin:$PATH"

WORKDIR /app

COPY requirements.txt .
COPY .env .
COPY app.py .
COPY scripts/ ./scripts
COPY export/ ./export
COPY images/ ./images
COPY .streamlit/ ./.streamlit

RUN pip install --upgrade pip && pip install -r requirements.txt

CMD ["streamlit", "run", "app.py"]