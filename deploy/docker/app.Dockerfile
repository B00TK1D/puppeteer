FROM python:3.8-slim-buster

# Install dependencies
RUN apt-get update && apt-get install -y gzip tshark

# Install mergecap
RUN apt-get install -y wireshark-common && \
    apt-get install -y tshark && \
    apt-get install -y wireshark && \
    apt-get install -y libcap2-bin


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
#USER puppeteer

# Own app directory
#RUN chown -R puppeteer /app
WORKDIR /app

# Run app
CMD ["python3", "app.py"]