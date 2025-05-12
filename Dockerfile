FROM python:3.9-slim
#RUN mkdir /opt
WORKDIR /opt/
EXPOSE 8080
# 将 requirements.txt 复制到 /opt/ 目录
COPY ["requirements.txt", "/opt/"]
RUN pip3 install https://github.com/encode/requests-async/archive/refs/heads/master.tar.gz
RUN pip3 install flask -r requirements.txt
# 将其余文件复制到 /opt/ 目录
COPY [".", "/opt/"]
#CMD   uvicorn server:app --port 8081 --host 0.0.0.0
ENV ms.db.url mysql://root:W1PkWn2hfOAy@172.27.240.4:3306/cda_db?useSSL=false&useUnicode=true&characterEncoding=UTF-8
ENV send.message.list ["dev", "test", "prod"]
ENV send.message.token {"dev": {"token": "7853704896:AAHQyOHkUVUGTrlgn9dV8iPKdQXzq_4S23E", "chat_ids": ["-4539437068","-1002536630151"]},"test": {"token": "7853704896:AAHQyOHkUVUGTrlgn9dV8iPKdQXzq_4S23E", "chat_ids": ["-1002111465087","-1002536630151"]},"prod": {"token": "6566268578:AAGc4sGBLHlIpCBBtUBCJDVu4fzP5IdhUeg", "chat_ids": ["-1001280903433", "-1002622004671"], "tg_name":"@CDAReporterBot"}}
CMD python3 -u server.py

