FROM mcr.microsoft.com/playwright/python:v1.41.0-jammy

# We use the official Playwright image because installing Playwright
# and its browser binaries from scratch on alpine/slim is very error-prone.
# However, this image is optimized and doesn't contain OpenCV/CUDA bloat.

WORKDIR /app

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY app/ ./app/
COPY workers/ ./workers/

# The Playwright image already has a non-root user 'pwuser' (UID 1000)
RUN chown -R pwuser:pwuser /app
USER pwuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
