FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY modules/module_a_core/ ./modules/module_a_core/
COPY shared/ ./shared/

EXPOSE 8001

CMD ["python", "modules/module_a_core/main.py"]