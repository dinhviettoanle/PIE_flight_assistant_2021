FROM python:3.8

COPY src/requirements.txt /tmp/

RUN pip install Cython==0.29.24 
RUN pip install -r /tmp/requirements.txt

WORKDIR /src/

COPY src ./

EXPOSE 5000
# ENV FLASK_APP=app.py
# CMD ["flask", "run", "--host", "0.0.0.0"]

ENTRYPOINT ["python"]
CMD ["app.py"]