FROM python:3.8

COPY src/requirements.txt /tmp/

RUN pip install Cython==0.29.24 
RUN pip install -r /tmp/requirements.txt

WORKDIR /src/

COPY src ./
COPY ./gunicorn_starter.sh ./

EXPOSE 5000
EXPOSE 8000

# OK
# ENTRYPOINT ["python"]
# CMD ["app.py"]

# OK avec "gunicorn --worker-class eventlet -w 1 app:app -b 0.0.0.0:8000" dans le starter
# ENTRYPOINT ["./gunicorn_starter.sh"]
# CMD ["gunicorn --worker-class eventlet -w 1 app:app -b 0.0.0.0:8000"]

# OK, pareil avec env $PORT=8000
# ENTRYPOINT ["./gunicorn_starter.sh"]
# CMD ["gunicorn --worker-class eventlet -w 1 app:app -b 0.0.0.0:$PORT"]

ENTRYPOINT ["./gunicorn_starter.sh"]
CMD ["gunicorn", "--worker-class", "eventlet" ,"-w", "1", "app:app", "-b" ,"0.0.0.0:${PORT:-5000}"]