FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl && rm -rf /var/lib/apt/lists/*

# ensure pip is up-to-date
RUN python -m pip install --upgrade pip setuptools

# copy and install requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy app code
COPY . .

# non-root user (optional)
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

CMD ["python", "main.py"]