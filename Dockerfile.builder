FROM gcr.io/cloud-builders/gcloud
RUN apt-get update && apt-get install python python-pip -y
COPY requirements-ci.txt .
RUN pip install -r requirements-ci.txt
ENTRYPOINT ["/bin/sh", "-c"]
