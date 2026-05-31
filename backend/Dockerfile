FROM python:3.12-slim

WORKDIR /app

# Install system deps for psycopg2, curl, AND Playwright's Chromium in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl \
    # Chromium runtime dependencies (from playwright's own dep list)
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
    libxrandr2 libgbm1 libasound2 libpango-1.0-0 libpangocairo-1.0-0 \
    libcairo2 libx11-6 libx11-xcb1 libxcb1 libxext6 \
    fonts-liberation libappindicator3-1 xdg-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright Chromium browser (deps already installed above)
RUN playwright install chromium

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
