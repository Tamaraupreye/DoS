# Secure Smart Traffic: DOS Attack Detection
This is a Python repository with all the files for the detection Denial of Service attacks on a Raspberry Pi in a
network.

## Getting Started
- Have a Raspberry Pi connected to your network
- Have Kali Linux running in a virtual machine with bridged networking and connected to your device

## What each file does
#### DOSHelper.py
This is a Python script that contains methods for connecting to via SSH, running commands on, and moving files to and 
from both the Raspberry Pi and Linux Kali. It also has commands for easily starting and stopping DOS attacks, launching 
countermeasures and starting or stopping Python programs on the Pi. Needs DOSHelperConfig.ini to work. It creates files 
called pi_logs and kali_logs on the respective devices to give an idea of what errors might have occurred when running 
the server or Metasploit attacks.

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

## Presentations and Other Links
[Metasploit Papers Studied](https://docs.google.com/document/d/1Sd_XhUCxBlOBOSzk6Z6ccgIeXhrHkL4AJ0olEWfULUo/edit?usp=sharing)

[Senior Design - Problem Statement](https://docs.google.com/document/d/1n68xlGU07YywAXPMpGL9K9J7cIQCQpe-tUON4wUxJKA/edit?usp=sharing)

[Senior Design - Design Requirements](https://docs.google.com/document/d/11PZTF6T4nRYcmjH9g7pVdV5uYIuQJupTRRH3lbEDiRk/edit?usp=sharing)

[Senior Design - Solution Presentation](https://docs.google.com/presentation/d/1ApbwHlydDVmaIVRZS7plRsq4RrU3ooM9OdxMwKhfc3w/edit?usp=sharing)

[Piece 1 Presentation - Data Collection](https://docs.google.com/presentation/d/1mKphcvQVs0ok8ns6mK9W09MdRgneyQtL6CPaE-UVw5Y/edit?usp=sharing)

[Piece 2 Presentation - Attack Detection](https://docs.google.com/presentation/d/13ygdzMmrBmUFGAKHZAc10L8srjsGTzwtOwnmus6O680/edit?usp=sharing)

[Piece 3 Presentation - Countermeasure](https://docs.google.com/presentation/d/1jP_rdIB-iN-vlTIcU2YNslPypVZTzVUfndWoRcrWQ0M/edit?usp=sharing)

[Senior Design - Final Presentation](https://docs.google.com/presentation/d/1t_H_K-v-8I31KZfuFfJh7FZYYhdAOQn04tfZ_T3IKuY/edit?usp=sharing)

[Senior Design - Presentation Video](http://www.mwftr.com/4014FY2021/Secure_5.mp4)

[Senior Design - Final Report](https://docs.google.com/document/d/1Y_cFyYR6SnNvX_YbckHAZmpKns3R7UMmvtzyH3gNX2E/edit?usp=sharing)

[DOS Impact Measurement](https://www.icloud.com/keynote/0axCr2n-09wst-mgWIHXdlCIQ#Presentation_-_DoS)

[DOS - SYN/ACK Ratio and Countermeasures](https://www.icloud.com/keynote/0RPbEsIs8xZSe_dJ5RAjfZOvg#Syn/Ack_Ratio_and_Countermeasures)

[DOS New Attacks Part 1](https://www.icloud.com/keynote/0S_VHjrfjrDveqEu6uKwDbXaQ#DoS-New_Attacks)

[DOS New Attacks Part 2](https://www.icloud.com/keynote/0T_JdIeMiv_uO2leGQ8IxucSQ#DoS-New_Attacks_2)

[DOS Countermeasures Part 2](https://docs.google.com/presentation/d/1Z6aMIc22ubzjIT2B27D0LLkT7iZgTZ5Z6YFbaieXxiE/edit?usp=sharing)

[DOS Countermeasures Part 3](https://docs.google.com/presentation/d/1fXBzW1EU2hTPIAIfGCYmLh48Pu6eSPXCIVgQHw6FOu0/edit?usp=sharing)

[ML for DOS Detection](https://docs.google.com/presentation/d/1nWV9f80kWP1sVxlE3IzAffERHyvJGTk2GZ-x_XfT3wY/edit?usp=sharing)
