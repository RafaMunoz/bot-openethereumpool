FROM python:alpine
MAINTAINER Rafa Muñoz rafa93m@gmail.com (@rafa93m)

RUN set -eux \
  && pip install pymongo \
  && pip install urllib3 \
  && pip install pytelegrambotapi

RUN mkdir /opt/openethereumpool
COPY openethereumpool /opt/openethereumpool
RUN chmod -R 644 /opt/openethereumpool

RUN echo "*    *    *    *    *    python3 /opt/openethereumpool/checkWorkers.py" >> /etc/crontabs/root
RUN echo "*    *    *    *    *    python3 /opt/openethereumpool/checkNewBlock.py" >> /etc/crontabs/root
RUN echo "*    *    *    *    *    python3 /opt/openethereumpool/checkPayments.py" >> /etc/crontabs/root

WORKDIR /opt/openethereumpool

ENTRYPOINT ["/bin/sh", "/opt/openethereumpool/docker-entrypoint.sh"]

CMD ["python3","/opt/openethereumpool/bot-OpenEthereumPool.py"]