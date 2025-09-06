FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY modules/module_d_execution/ ./modules/module_d_execution/
COPY shared/ ./shared/

EXPOSE 8004

CMD ["python", "modules/module_d_execution/main.py"]