FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Download Swagger UI for offline use
COPY download_swagger_ui.py ./
RUN python3 download_swagger_ui.py && rm download_swagger_ui.py

# Copy application source
COPY src ./src
COPY alembic ./alembic
COPY alembic.ini ./
COPY tools ./tools

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
