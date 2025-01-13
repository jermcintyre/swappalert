FROM python:3.12-alpine

# Create app directory
WORKDIR /app

# Install dependencies first for caching
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy script
COPY swappalert.py .

# Run script
ENTRYPOINT ["python3", "swappalert.py"]