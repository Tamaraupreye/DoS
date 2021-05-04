# Secure Smart Traffic: DOS Attack Detection
This is a Python repository with all the files for the detection Denial of Service attacks on a Raspberry Pi in a
network.

## Getting Started

## What each file does
#### DOSHelper.py
This is a Python script that contains methods for connecting to via SSH, running commands on, and moving files to and 
from both the Raspberry Pi and Linux Kali. It also has commands for easily starting and stopping DOS attacks, launching 
countermeasures and starting or stopping Python programs on the Pi. Needs DOSHelperConfig.ini to work.

#### DOSHelperConfigExample.ini
This is an example of a configuration file that holds the IP address, username and passwords for both the Raspberry 
Pi. Use this example to make a DOSHelperConfig.ini file with your own information.

#### dnsamp.rb
This is a Ruby Script that uses the Metasploit framework to launch a DNS amplification
attack against a victim. Can be added to Metasploit framework on Kali Linux by moving this
file to /usr/share/metasploit-framework/modules/auxiliary/dos/

#### icmpflooder.rb
This is a Ruby Script that uses the Metasploit framework to launch an ICMP flood
attack against a victim. Can be added to Metasploit framework on Kali Linux by moving this
file to /usr/share/metasploit-framework/modules/auxiliary/dos/

#### TCPServer.py
This is a Python Script intended to run on the Raspberry Pi. It uses the socket module to create an echo server
that listens for connections and replies with the same message. This is the sever that is attacked during the project.

#### TCPClient.py
This is a Python Script intended to run on the host's computer. It has methods that use the socket module 
to send messages to the echo server running on the Raspberry Pi. This is the client that is denied service by the 
DOS attack.

#### FancyTCPServer.py
This is a modification of the TCPServer.py that uses the Python selector module for robustness.

#### FancyTCPClient.py
This is a modification of the TCPClient.py that uses the Python selector module for robustness.

#### data_gather_ML.py
This is a Python script intended to be run on the host's computer for gathering training data for detecting DOS attacks.
It launches the gather_Pi.py script on the raspberry Pi and then for the duration of the data gathering, randomly 
launches DOS attacks against the Pi server using Kali Linux. At the end, a detect_data.csv file is generated. 

#### gather_Pi.py
This is a Python script intended to be run on the Raspberry Pi. It uses a tshark command to capture network packets in 
15-second bursts and then generates an array of features that can be used for detecting various DOS attacks. The 
features calculated are the ratio of SYN to ACK packets, the number of ICMP packets and the ratio of outgoing to 
incoming DNS packets. This [paper](http://palms.princeton.edu/system/files/Machine_Learning_Based_DDoS_Attack_Detection_From_Source_Side_in_Cloud_camera_ready.pdf) has more information.

#### ML_DOS_Detect_Train.ipynb
This is a Jupyter notebook that uses the detect_data.csv file to train Machine Learning models for detecting DOS 
attacks. The supervised models tried for classification are Random Forest and k-Nearest Neighbours.

#### train.py
Exporting the model trained with Jupyter notebook was problematic because most computers run a 64-bit version of Python 
compared to 32-bit Python on the Raspberry Pi. This Python script is intended to be run on the Raspberry Pi and uses 
the same code as the Jupyter notebook to train a model then uses Python's joblib model to export the model for 
persistence. The model is saved as "model.model"

#### detect.py
This is a Python script that runs on the Raspberry Pi to detect attacks using threshold values for the features 
calculated after the 15-second packet captures. We determined the threshold values by looking at the network data when 
under DOS attack and when running normally.

#### detect_ML.py
This is a Python script that runs on the Raspberry Pi to detect attacks using the exported machine learning model from
before.

#### dos_effectiveness.py
This is a Python script that runs on the host's computer and tries to visualize the effectiveness of the DOS attack
by looking at the number of network packets sent in the attack, the time the server (running on the Raspberry Pi) takes 
to respond to a client, and the memory used by the server. It should also look at CPU % utilization but not implemented 
yet.

#### countermeasure_effectiveness.py
This is a Python script that runs on the host's computer and tries to measure the effectiveness of our DOS 
countermeasures by looking at the time for the server to fail before and after countermeasures. The countermeasures 
involve tweaking Linux network parameters on the Pi in /proc/sys/net/ipv4/ like tcp_max_syn_backlog, tcp_synack_retries 
and tcp_syncookies.

## Presentation Links
