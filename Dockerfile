FROM resin/rpi-raspbian:jessie
LABEL version="1.0" \
      description=""

RUN apt-get update && \
    apt-get upgrade -y

# Get the 'Ubuntu & Debian (ARM)' package from https://influxdata.com/downloads/#influxdb
#ADD https://dl.influxdata.com/influxdb/releases/influxdb_0.13.0_armhf.deb .
ADD https://dl.influxdata.com/influxdb/releases/influxdb_1.1.1_armhf.deb .
RUN dpkg -i influxdb_1.1.1_armhf.deb && \
    rm -f influxdb_1.1.1_armhf.deb

COPY influxdb.conf /etc/influxdb/

VOLUME ["/var/lib/influxdb", "/var/lib/backups"]

EXPOSE 8086

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

COPY influx_backups/ /tmp/backups

RUN influxd restore -metadir /var/lib/influxdb/meta /tmp/backups/metabackup
RUN influxd restore -database meatsack -datadir /var/lib/influxdb/data /tmp/backups/databackup

CMD ["influxd"]
