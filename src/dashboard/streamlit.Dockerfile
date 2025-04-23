FROM python:3.13-slim

WORKDIR /app

COPY ./requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENTRYPOINT ["streamlit", "run", "--server.port", "8000", "streamlit.py"]
