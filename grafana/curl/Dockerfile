FROM resin/armv7hf-debian:jessie

RUN apt-get update && \
    apt-get -y --no-install-recommends install curl  

COPY ./entrypoint.sh /entrypoint.sh
COPY ./datasources.json /datasources.json
COPY ./chamber_dashboard.json /chamber_dashboard.json
COPY ./wait-for-it.sh /wait-for-it.sh

RUN chmod +x /entrypoint.sh  && \
    chmod +x /wait-for-it.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["curl"]

