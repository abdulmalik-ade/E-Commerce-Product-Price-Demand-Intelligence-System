# Use a lightweight python image
FROM python:3.10-slim

# Prevent Python from writing pyc files to disk and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Install python packages
RUN pip install --no-cache-dir fastapi uvicorn streamlit pandas requests plotly scikit-learn matplotlib seaborn

# Copy project files
COPY . /app

# Expose default ports for both Streamlit and FastAPI
EXPOSE 8501
EXPOSE 8000

# Default container startup script
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
