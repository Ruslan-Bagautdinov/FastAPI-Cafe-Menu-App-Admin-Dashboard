FROM python:3.11
COPY . /app
WORKDIR /app
VOLUME /app/img
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8015", "--workers", "4"]
