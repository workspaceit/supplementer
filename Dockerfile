# Use an official Python runtime as a parent image
FROM python:3.7
ENV PYTHONUNBUFFERED 1

RUN apt-get update

COPY . /app
RUN pip install --upgrade pip
WORKDIR /app
RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 8000

RUN chmod +x entrypoint.sh
# CMD ["./start.sh"]
ENTRYPOINT [ "./entrypoint.sh" ]