# THE BASE SYSTEM
FROM python:3.12-slim

# THE WORKING DIRECTORY
WORKDIR /code

# COPY THE DEPENDENCIES
COPY requirements.txt .

# INSTALL THE DEPENDENCIES
RUN pip install --no-cache-dir -r requirements.txt

# COPY THE ARCHITECTURE
COPY . .

# OPEN THE NETWORK PORT
EXPOSE 8000

# THE BOOT COMMAND
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]