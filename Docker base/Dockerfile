FROM python:3.8

RUN apt-get update 
RUN apt-get upgrade --yes

# Mandatory SW to run selenium
RUN apt-get install xvfb --yes
RUN apt-get install default-jdk --yes
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install
RUN export LATEST_CHROMEDRIVER_VERSION=`curl https://chromedriver.storage.googleapis.com/LATEST_RELEASE` && wget https://chromedriver.storage.googleapis.com/$LATEST_CHROMEDRIVER_VERSION/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip
RUN mv chromedriver /usr/bin/chromedriver
RUN chown root:root /usr/bin/chromedriver
RUN chmod +x /usr/bin/chromedriver

# Python pip
RUN apt-get install python-pip --yes
RUN pip install selenium pyvirtualdisplay
RUN pip install paho-mqtt requests

# Scripts
COPY basic_selenium_auth.py /opt/basic_selenium_auth.py

# Workdir
WORKDIR /opt
CMD ["python", "basic_selenium_auth.py"]

