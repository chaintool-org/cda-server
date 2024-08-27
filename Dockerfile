FROM python:3.9-slim
#RUN mkdir /opt
WORKDIR /opt/
EXPOSE 8080
# 将 requirements.txt 复制到 /opt/ 目录
COPY ["requirements.txt", "/opt/"]
RUN pip3 install flask
# 将其余文件复制到 /opt/ 目录
COPY [".", "/opt/"]
#CMD   uvicorn server:app --port 8081 --host 0.0.0.0
ENV ms.db.url mysql://root:W1PkWn2hfOAy@172.27.240.4:3306/cda_db?useSSL=false&useUnicode=true&characterEncoding=UTF-8
ENV send.message.list ["dev", "test", "prod"]
ENV send.message.token {"dev": {"token": "6625991991:AAFcsMIP8w_crVQuWnk1Y5_YGM0SLBYh_XQ", "chat_id": "-4099496644"},"test": {"token": "6625991991:AAFcsMIP8w_crVQuWnk1Y5_YGM0SLBYh_XQ", "chat_id": "-4099496644"},"prod": {"token": "6625991991:AAFcsMIP8w_crVQuWnk1Y5_YGM0SLBYh_XQ", "chat_id": "-4099496644"}}
CMD python3 -u server.py

