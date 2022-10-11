FROM python:3.10-slim-buster

WORKDIR /python-docker

COPY requirenments.txt .
RUN pip3 install -r requirenments.txt

COPY python/*.py ./

ENV BOT_TOKEN ''
ENV SHEETS_ACC_JSON ''
ENV SHEETS_NAME ''
ENV SHEET_GROUPS ''
ENV SHEET_INFO ''
ENV SHEET_REPORT 10
ENV SHEET_HELP ''
ENV SHEET_UPDATE_TIMEOUT 10

CMD [ "python3", "-u", "main.py"]