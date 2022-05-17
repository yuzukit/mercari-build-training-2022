# FROM alpine
# RUN apk update && apk add --no-cache python3 py3-pip
# #RUN pip install fastapi uvicorn
# COPY ./python/requirements.txt requirements.txt
# RUN pip install -r requirements.txt
# EXPOSE 9000
# CMD ["python3", "-V"]
# RUN mkdir /python /db
# COPY /python app/python
# COPY /db app/db
# COPY /images app/images
# #CMD curl -D - -s  -o /dev/null http://example.com
# #CMD ["uvicorn", "python.main:app", "--host", "127.0.0.1", "--port", "9000"]
# CMD ["uvicorn", "main:app", "--reload", "--port", "9000"]


   
FROM python:3.10-slim-buster

WORKDIR /app

COPY ./python/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt && pip install fastapi uvicorn

COPY ./python /app/python
COPY ./db /app/db
COPY ./images /app/images

EXPOSE 9000

CMD ["uvicorn", "python.main:app", "--host", "0.0.0.0", "--port", "9000"]