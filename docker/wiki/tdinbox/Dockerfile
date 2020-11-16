FROM centos:8 as lib-builder

RUN dnf group install -y "Development Tools" && \
    yum install -y git clang gcc openssl zlib cmake openssl-devel && \
    yum install dnf-plugins-core && \
    yum config-manager --set-enabled PowerTools && \
    yum install -y gperf && \
    git clone https://github.com/tdlib/td.git && \
    cd td && mkdir build && cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release .. && cmake --build .

FROM ubuntu:focal
RUN apt-get update && apt-get install -y openssl python3 && mkdir /app
COPY --from=lib-builder td/build/libtdjson.so* /app/
COPY tdinbox.py /app

ENTRYPOINT [ "python3", "/app/tdinbox.py" ]
