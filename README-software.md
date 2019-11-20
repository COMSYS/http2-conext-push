# Replaying Websites with Mahimahi-h2o

## Introduction
In our paper we conducted experiments by recording and replaying websites using the [Mahimahi](http://mahimahi.mit.edu) by Netravali et al.
As Mahimahi does [not support HTTP/2 yet](https://github.com/ravinet/mahimahi/issues/101), we created a a [Mahimahi Fork](https://github.com/worenga/mahimahi-h2o), which uses the [h2o](https://h2o.examp1e.net/) webserver instead of the Apache Webserver.
Is included into this repository as a submodule. And can be downloaded using the following git command:
```
git submodule update --init --recursive
```
Moreover, we want to record the website resources that are delivered via HTTP/2. To this end we need a recording infrastructure capable of recording HTTP/2 content, which is currently also not possible with mahimahi.
To this end we use the recording function of [mitmproxy](https://mitmproxy.org/) and we wrote an [exporter](https://github.com/worenga/mitmproxy2mahimahi) that can convert the mitmproxy recordings into the Mahimahi Protobuf format.

The following instructions have been tested on Ubuntu 18.04 LTS (bionic) and OpenSSL 1.1.0g.


## Installing H2O Webserver
We provide a patched version for the h2o webserver that implements our custom scheduler as described [here](https://push.netray.io/interleaving.html#interleaving).

```
cd sofware/h2o/
sudo apt-get install bison
cmake -DWITH_BUNDLED_SSL=on -DWITH_MRUBY=on . 
make
sudo make install
```

## Installing Mahimahi

Navigate into our mahimahi fork
```
cd software/mahimahi-h2o

```
set the `MAHIMAHI_ROOT` variable to the mahimahi source directory
```
export MAHIMAHI_ROOT=/home/bewo/repos/http2-conext-push/software/mahimahi-h2o
```

Install the required dependencies
```
sudo apt-get install dh-autoreconf apache2 dnsmasq protobuf-compiler apache2-dev libprotobuf-dev xcb libxcb-present-dev libpango1.0-dev python-flup
```

Compile Mahimahi
```
./autogen.sh
autoreconf -f -i -Wall,no-obsolete
./configure
make
sudo make install
```

Mahimahi needs IP Forwarding to be active
```
sudo sysctl -w net.ipv4.ip_forward=1
```


Moreover, the system needs to trust the ROOT CA Mahimahi uses to sign website certificates on startup, this may be different based on your distribution.
```
sudo cp mahimahica/cacert.pem /usr/local/share/ca-certificates/mahimahica/cacert.crt
sudo update-ca-certificates
```


You should now be able to replay some of the recordings in this repository using mahimahi, Chromium and browsertime.

```
cd dataset/interleaving_push/recordings
mm-webreplay data/mm-capture/wikipedia data/push_strategies/same-ip-mergelist-strategies/wikipedia/nopush.json same-ip mm-delay 100 browsertime -n 1 --xvfb --video --chrome.args="--ssl-version-max=tls1.2" --chrome.collectNetLog  --chrome.args="--disable-web-security" --speedIndex https://en.wikipedia.org/wiki/Barack_Obama
```
Check out [run_interleaving_eval.py](../blob/master/dataset/interleaving_push/eval/run_interleaving_eval.py) for an automated instrumentation of browsertime.
