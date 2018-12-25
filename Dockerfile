FROM ubuntu
VOLUME /home/wwwroot/api
RUN apt update -y && \
    apt install -y python3 python3-pip build-essential && \
    pip3 install uwsgi django djangorestframework
COPY . /home/wwwroot/api
WORKDIR /home/wwwroot/api
EXPOSE 8000
CMD ["uwsgi","--http",":8000","--module","backend.wsgi"]