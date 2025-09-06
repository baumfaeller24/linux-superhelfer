FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY modules/module_e_hybrid/ ./modules/module_e_hybrid/
COPY shared/ ./shared/

EXPOSE 8005

CMD ["python", "modules/module_e_hybrid/main.py"]