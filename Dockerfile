FROM python:3.13-slim-bookworm

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY . .

# Install dependencies
RUN uv sync

# Set environment variables (example, adjust as needed)
ENV PYTHONPATH=$PYTHONPATH:/app

# Command to run the application (example, adjust as needed)
CMD ["uv", "run", "./examples/math_forge/run.py"]