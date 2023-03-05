FROM debian:buster-slim

# Add backports
RUN echo "deb http://deb.debian.org/debian buster-backports main" >> /etc/apt/sources.list

# Install OpenVPN
#RUN apt-get update
#RUN apt-get install -y wget apt-transport-https gnupg
#RUN wget https://swupdate.openvpn.net/repos/openvpn-repo-pkg-key.pub
#RUN apt-key add openvpn-repo-pkg-key.pub
#RUN wget -O /etc/apt/sources.list.d/openvpn3.list https://swupdate.openvpn.net/community/openvpn3/repos/openvpn3-buster.list
#RUN apt-get update
#RUN apt-get install -y openvpn3

# Install OpenVPN
RUN apt-get update
#RUN apt-get install -y openvpn

# Install WireGuard
#RUN apt-get install -y wireguard

# Install pcap dependencies
RUN apt-get update && apt-get install -y gzip tshark

# Install mergecap
RUN apt-get install -y wireshark-common && \
    apt-get install -y tshark && \
    apt-get install -y wireshark && \
    apt-get install -y libcap2-bin



# Install Python modules
COPY requirements.txt /tmp
RUN apt-get install -y python3 python3-pip
RUN python3 -m pip install --no-cache-dir --upgrade pip
RUN python3 -m pip install --no-cache-dir wheel
RUN python3 -m pip install --no-cache-dir -r /tmp/requirements.txt
RUN rm /tmp/requirements.txt

WORKDIR /app

# Run app
CMD ["python3", "app.py"]