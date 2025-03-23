FROM python:3.12
WORKDIR /
COPY project/main.py requirements.txt ./
RUN pip install -r requirements.txt
RUN pip install gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]
