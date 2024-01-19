FROM python:3.13.0a3-alpine
COPY main.py .
COPY startup.sh .
RUN chmod +x startup.sh
RUN apk update && apk add curl py3-pip aws-cli bash && \
    curl -LO "https://storage.googleapis.com/kubernetes-release/release/v1.19.0/bin/linux/amd64/kubectl" && chmod +x ./kubectl && mv ./kubectl /usr/local/bin/kubectl && \
    pip3 install flask requests && apk del py3-pip curl
EXPOSE 5000
CMD /bin/bash startup.sh ${CLUSTER_NAME} ${ROLE_NAME}
