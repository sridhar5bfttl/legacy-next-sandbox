FROM python:3.11-slim-bookworm

# Install build tools, gfortran, g++, and the Eigen matrix library headers
RUN apt-get update && apt-get install -y --no-install-recommends \
    gfortran \
    g++ \
    libeigen3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Flask web server framework
RUN pip install --no-cache-dir flask

# Copy backend engines and static web resources
COPY src/app.py /app/app.py
COPY src/translator.py /app/translator.py
COPY src/evaluator.py /app/evaluator.py
COPY src/static /app/static

EXPOSE 8080

# Run Flask server
CMD ["python", "app.py"]
