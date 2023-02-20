FROM python:3.8-slim-buster

# Install packages
COPY apt_packages.txt /tmp
RUN apk add --no-cache $(cat /tmp/apt_packages.txt) \
    && rm /tmp/apt_packages.txt

# Install Python modules
COPY requirements.txt /tmp
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir wheel && \
    python3 -m pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

# Run app as non-root user
RUN adduser --disabled-password --gecos '' puppeteer && \
    chown -R puppeteer /usr/local/lib/python3.8/site-packages

# Switch to non-root user
USER puppeteer

# Copy app
COPY --chown=puppeteer:puppeteer . /app
WORKDIR /app

# Run app
CMD ["python3", "app.py"]