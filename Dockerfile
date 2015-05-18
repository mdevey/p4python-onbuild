FROM python:2-slim
#FROM python:2

# To build with dependencies sorted use 'FROM python:2' instead (it's just 300mb bigger)
# cut down version of what's in buildpack-deps:jessie
#https://github.com/docker-library/buildpack-deps/blob/44070019e0c6c4f83461f2058d110cc418da09c4/jessie/Dockerfile
RUN apt-get update && apt-get install -y \
		build-essential \
		tar \
        gzip \
	&& rm -rf /var/lib/apt/lists/*


# similar to python:2-onbuild

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

#Note we copy this first before the generic . copy so the cache is used.
ONBUILD COPY requirements_deb.txt /usr/src/app/

ONBUILD RUN apt-get update && \
            apt-get install -y $(sed s/#.*//g requirements_deb.txt | xargs echo) && \
	        rm -rf /var/lib/apt/lists/*

ONBUILD COPY requirements.txt /usr/src/app/
ONBUILD RUN pip install -r requirements.txt

ONBUILD COPY . /usr/src/app

#Now start building p4python.

COPY zips /zips
COPY app.py /usr/src/app/app.py

#Build and install p4python, which requires p4api
RUN tar zxf /zips/p4api.tgz
RUN tar zxf /zips/p4python.tgz

RUN cd p4python-* && python setup.py build --apidir /usr/src/app/p4api-* 
RUN cd p4python-* && gunzip -c /zips/p4d.gz > p4d && chmod a+x p4d
RUN cd p4python-* && PATH="./:$PATH" python p4test.py
RUN cd p4python-* && python setup.py install --apidir /usr/src/app/p4api-*

#delete source directories (/zips/ remain)
RUN rm -rf p4*-*

#Users preferrably volume bind .p4config & .p4tickets to /root, 
#Alternatively set ENVIRONMENT variables (see docker-compose.yml)
ENV P4CONFIG=/root/.p4config

CMD [ "python", "./app.py" ]


