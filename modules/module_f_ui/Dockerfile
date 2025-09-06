FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY modules/module_f_ui/ ./modules/module_f_ui/
COPY shared/ ./shared/

EXPOSE 8000

CMD ["streamlit", "run", "modules/module_f_ui/main.py", "--server.port", "8000", "--server.address", "0.0.0.0"]