FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY modules/module_c_agents/ ./modules/module_c_agents/
COPY shared/ ./shared/

EXPOSE 8003

CMD ["python", "modules/module_c_agents/main.py"]