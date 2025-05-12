FROM python:3.9-slim

# setting working directory
WORKDIR /opt/

# setting port
EXPOSE 8080

# copy requirements.txt and install dependencies
COPY ["requirements.txt", "/opt/"]
RUN pip3 install https://github.com/encode/requests-async/archive/refs/heads/master.tar.gz
RUN pip3 install flask -r requirements.txt

# copy source code
COPY [".", "/opt/"]

# run app
CMD python3 -u server.py

