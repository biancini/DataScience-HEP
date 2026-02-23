FROM ubuntu:22.04
USER root
WORKDIR /root

SHELL [ "/bin/bash", "-c" ]

# Existing lsb_release causes issues with modern installations of Python3
# https://github.com/pypa/pip/issues/4924#issuecomment-435825490
# Set (temporarily) DEBIAN_FRONTEND to avoid interacting with tzdata
RUN apt-get -y update && \
    DEBIAN_FRONTEND=noninteractive apt-get -y install \
        software-properties-common \
        clang lldb lld curl xdg-utils \
        python3.10 python3-debian python3-pip python3-venv \
        graphviz ttf-mscorefonts-installer

RUN fc-cache -f -v
RUN rm ~/.cache/matplotlib -rf

# Intstall dependencies and LLVM version 10 (needed by python dependencies)
COPY *.deb ./
RUN curl -sSL https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add -
RUN add-apt-repository 'deb http://apt.llvm.org/bionic/   llvm-toolchain-bionic-10  main'
RUN yes | dpkg -i libffi6_3.2.1-8_amd64.deb
RUN apt-get -y update && apt-get -y install llvm llvm-10
RUN pip3 install --upgrade pip

# Install poetry
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_VERSION=1.1.11

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python3 -
ENV PATH "/root/.local/bin:$PATH"
ENV LLVM_CONFIG "/usr/bin/llvm-config-10"
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

COPY pyproject.toml *.whl ./
RUN rm -f poetry.lock
RUN poetry install --no-interaction --no-ansi --no-root

WORKDIR /app
ENTRYPOINT [ "jupyter", "notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root" ]

