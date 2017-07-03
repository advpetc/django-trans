FROM daocloud.io/python


ENV PYTHONUNBUFFERED 1

WORKDIR /atman/
ADD . /atman/

RUN pip install -r requirements.txt
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
