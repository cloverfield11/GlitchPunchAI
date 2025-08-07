FROM python:3.9-slim

WORKDIR /code

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libgomp1 \
    libatomic1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get purge -y build-essential cmake \
    && apt-get autoremove -y \
    && apt-get clean

COPY app.py .

EXPOSE 7860

CMD ["python", "app.py"]