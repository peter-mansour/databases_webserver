FROM python:3
WORKDIR /home/peter/Documents/Github/databases_webserver
COPY . .
RUN pip3 install -r requirements.txt
CMD ["server.py"]
ENTRYPOINT ["python3"]
