FROM ubuntu:20.04

RUN apt update --fix-missing && DEBIAN_FRONTEND=noninteractive \
    apt install tzdata -qy &&\
	apt install -qy build-essential \
    python3-pip python3-setuptools python3-dev \
    pkg-config \
    sudo vim curl cmake git wget

WORKDIR /opt/workspace
COPY conf/pip/requirements.txt /opt/workspace/requirements.txt
# COPY conf/systemd/web.service /etc/systemd/system/web.service

RUN pip3 install -U pip
RUN pip3 install -r requirements.txt

# Clean up
RUN rm -rf /opt/workspace

# add user
RUN useradd -m developer && \
    usermod -aG sudo developer && \
    echo '%sudo ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers && \
    cp /root/.bashrc /home/developer/ && \
    mkdir /home/developer/workspace && \
    chown -R --from=root developer:developer /home/developer

# Use C.UTF-8 locale to avoid issues with ASCII encoding
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

WORKDIR /home/developer/workspace
ENV HOME /home/developer
ENV USER developer
USER developer

ENV PATH /home/developer/.local/bin:$PATH
# Avoid first use of sudo warning. c.f. https://askubuntu.com/a/22614/781671
RUN touch $HOME/.sudo_as_admin_successful

ENTRYPOINT ["/home/developer/workspace/src/main.py"]
