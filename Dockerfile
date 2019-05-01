FROM python:2.7.14-slim
ARG app_version

LABEL maintainer="IAX"
LABEL version="${app_version}"
ENV APP_VERSION ${app_version}

ADD . /project

RUN pip install -r /project/requirements.txt
RUN chmod a+x /project/run.sh

EXPOSE 8000
CMD ["/project/run.sh"]
