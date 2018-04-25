FROM gcr.io/cloud-builders/gcloud

# install python
RUN apt-get update && apt-get install python python-pip -y

# update gcloud
RUN gcloud --quiet components update

COPY requirements-ci.txt .
RUN pip install -r requirements-ci.txt

#ENTRYPOINT ["/bin/sh", "-c"]
