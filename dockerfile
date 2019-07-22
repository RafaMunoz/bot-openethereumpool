FROM python:alpine
MAINTAINER Rafa Muñoz rafa93m@gmail.com (@rafa93m)

RUN pip install pymongo \
  && pip install urllib3 \
  && pip install pytelegrambotapi

RUN mkdir /opt/openethereumpool
COPY openethereumpool /opt/openethereumpool
RUN chmod -R 644 /opt/openethereumpool

WORKDIR /opt/openethereumpool

ENTRYPOINT ["/bin/sh","/opt/openethereumpool/docker-entrypoint.sh"]

CMD ["python3","/opt/openethereumpool/bot-OpenEthereumPool.py"]