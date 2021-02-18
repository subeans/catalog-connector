FROM amazonlinux:latest as base

ENV LANG C.UTF-8
ARG NAME 
ARG PASSWORD

ENV AWS_ACCESS_KEY_ID=AKIAQECLFED6JTMTPPIS
ENV AWS_SECRET_ACCESS_KEY=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
ENV FACEBOOK_TOKEN=EAAFoU0uCqsYBAAA4y7ZCIZBob76XUCValyJjfy2eGih0tcLCKTkCJqxnuTUeRuvsm8dsCL7WQtuVSzycke94TsOVmWDGIpxjXcp9ohAZAURjOroU5OurZCgjwKmq1usnh5wAkNjlLeo7d1StR8CwGMFZBqNB9WL36pYEX2QZABSUrG5HQMQ3ih



RUN yum -y update & yum -y upgrade
RUN yum install -y git python3 python3-pip python3-devel gcc make 
RUN python3 -m pip --no-cache-dir install -U pip setuptools

RUN git clone https://${NAME}:${PASSWORD}@github.com/metric-studio/catalog-connector-batch.git
RUN python3 -m pip install --no-cache-dir -r catalog-connector-batch/reward-batch/requirements.txt 
RUN python3 -m pip install --no-cache-dir -r catalog-connector-batch/upload-batch/requirements.txt 

RUN unset NAME
RUN unset PASSWORD
