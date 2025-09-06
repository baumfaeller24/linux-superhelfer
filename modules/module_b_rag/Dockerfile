FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY modules/module_b_rag/ ./modules/module_b_rag/
COPY shared/ ./shared/

RUN mkdir -p /app/data

EXPOSE 8002

CMD ["python", "modules/module_b_rag/main.py"]