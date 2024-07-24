FROM python:3.9
# 添加时区环境变量，亚洲，上海
ENV TimeZone=Asia/Shanghai
# 使用软连接，并且将时区配置覆盖/etc/timezone
RUN ln -snf /usr/share/zoneinfo/$TimeZone /etc/localtime && echo $TimeZone > /etc/timezone
WORKDIR /app
COPY ./* /app/
RUN pip3 install -r requirements.txt
RUN echo 'Asia/Shanghai' >/etc/timezone
VOLUME /autokuro
CMD ["/bin/bash","python3 main.py"]
