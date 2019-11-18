FROM ubuntu:18.04

RUN apt-get -y update
RUN apt-get -y install wget
RUN wget https://www.xilinx.com/bin/public/openDownload?filename=xrt_201920.2.3.1301_18.04-xrt.deb -O xrt_201920.2.3.1301_18.04-xrt.deb

RUN apt-get -y install /xrt_201920.2.3.1301_18.04-xrt.deb 

ENV APP_HOME /app
WORKDIR $APP_HOME

# Install production dependencies.
# RUN pip install gunicorn
RUN apt-get -y install python3-pip
RUN pip3 install grpcio tensorflow keras

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.

#CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app

#EXPOSE 50051
COPY go.sh /go.sh
CMD /go.sh
