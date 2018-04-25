FROM gcr.io/cloud-builders/gcloud
COPY requirements-ci.txt .
RUN pip install -r requirements-ci.txt

#ENTRYPOINT ["/bin/sh", "-c"]
