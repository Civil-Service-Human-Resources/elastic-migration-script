# Elastic Migration Script

## (Optional step) Open a Docker container

This will open a Docker container using a Python 3.11 image. You'll need to have Docker installed:

```sh
docker run -it --rm -v $PWD:/root -w /root python:3.11.0-slim-buster bash
```

You can run the rest of the commands within that container.

If you choose not to use Docker, you'll need to have Python3 installed.

## 1. Initial setup

This will install the necessary packages (`dotenv` and `requests`) and also prompt you for the necessary environment variables.

```sh
. initial-setup.sh
```

## 2. Run script

This script will get the data from the existing ElasticSearch repo and attempt to copy them to the new one:

```sh
python main.py
```