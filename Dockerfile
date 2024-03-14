FROM python:3-alpine

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./
COPY static/favicon.ico ./static/

CMD [ "python", "./app.py" ]

EXPOSE 80
