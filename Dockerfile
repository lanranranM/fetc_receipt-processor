FROM python:3.8
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

ENV APP_MODE = run

CMD if [ "$APP_MODE" = "test" ] ; then python -m unittest discover; else python receipt_processor.py; fi