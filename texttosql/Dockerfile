FROM ubuntu:24.04

# https://github.com/moby/buildkit/blob/master/frontend/dockerfile/docs/reference.md#run---mounttypecache
RUN rm -f /etc/apt/apt.conf.d/docker-clean; echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt update && \
    DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata && \
    apt install -y --no-install-recommends nano ca-certificates python3 python3-pip python3-venv && \
    apt -y upgrade && \
    apt autoremove -y

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /

COPY requirements.txt /

# https://docs.docker.com/build/guide/mounts/#add-a-cache-mount
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked pip3 install -r requirements.txt

COPY load-huggingface-embedding.py /

RUN --mount=type=cache,target=/root/.cache/huggingface,sharing=locked python3 /load-huggingface-embedding.py

COPY *.py /

RUN chmod +x /*.py

CMD ["python3", "/startup.py"]
# for debugging
# CMD ["tail", "-f", "/dev/null"]