"""A capture file, built from nothing, so filters can be graded for real.

The tcpdump module used to be content-only for a reason that was true when it
was written: D1 forbids putting an interface into promiscuous mode, so there
was no traffic to filter and therefore nothing to check. That reasoning
quietly assumed the only way to get a capture file is to capture one.

You can also just write the bytes. A pcap is a 24-byte header followed by
length-prefixed packets, and a packet is only a handful of structs. Nothing
here touches a network card, sends anything, or needs a privilege: it is a
file format, written the way any other file format is written. That turns
"read this canned output" into "your filter selected these packets and the
answer selects those", which is the difference between being told and being
checked.

**The inventory is fixed and documented**, because content is authored against
it. Every drill's expected packet set is derived by *running the reference
filter*, never by counting by hand, so this table is here to help an author
choose a question rather than to be trusted arithmetic. Adding packets is safe;
removing or renumbering them invalidates authored content, so `test.py` pins
the inventory.

    #   proto  from            to               notes
    1   TCP    10.0.0.5:50000  93.184.216.34:443  SYN
    2   TCP    93.184.216.34:443  10.0.0.5:50000  SYN-ACK
    3   TCP    10.0.0.5:50000  93.184.216.34:443  ACK
    4   TCP    10.0.0.5:50000  93.184.216.34:443  PSH-ACK, TLS-ish payload
    5   TCP    93.184.216.34:443  10.0.0.5:50000  FIN-ACK
    6   UDP    10.0.0.5:53210  10.0.0.1:53        DNS query
    7   UDP    10.0.0.1:53     10.0.0.5:53210     DNS response
    8   TCP    10.0.0.5:50002  10.0.0.9:22        SYN, ssh attempt
    9   TCP    10.0.0.9:22     10.0.0.5:50002     RST-ACK, refused
    10  TCP    10.0.0.7:50004  93.184.216.34:80   PSH-ACK, GET / HTTP/1.1
    11  TCP    93.184.216.34:80  10.0.0.7:50004   PSH-ACK, 200 OK
    12  ICMP   10.0.0.5        10.0.0.1           echo request
    13  ICMP   10.0.0.1        10.0.0.5           echo reply
    14  TCP    192.168.50.4:50006  10.0.0.5:445   SYN, another subnet
    15  TCP    10.0.0.5:50008  93.184.216.34:8080 SYN, high port

Fourteen would have done, but the shape matters more than the count: there are
two hosts on the local subnet and one off it, one conversation on a well-known
port and one on a high port, a protocol that is neither TCP nor UDP, and a
refused connection. Every one of those exists so some filter distinguishes it
from its neighbour. A capture where every packet looks alike cannot grade
anything.
"""

from __future__ import annotations

import struct

#: pcap, microsecond resolution, big-endian magic. The classic format rather
#: than pcapng: it is trivial to write, and every version of tcpdump and
#: tshark in circulation reads it without comment.
MAGIC = 0xa1b2c3d4
VERSION = (2, 4)
LINKTYPE_ETHERNET = 1
SNAPLEN = 262144

#: A fixed epoch so the file is byte-identical on every run and on every
#: machine. Reproducibility is not decoration here: authored content is
#: validated against filters run over this file, so a fixture that varied
#: would make `validate.py` flaky. 2023-11-14T22:13:20Z, chosen for being
#: round and unremarkable.
BASE_TIME = 1700000000

ETH_SRC = b'\x02\x00\x00\x00\x00\x01'
ETH_DST = b'\x02\x00\x00\x00\x00\x02'
ETHERTYPE_IPV4 = 0x0800

PROTO_ICMP, PROTO_TCP, PROTO_UDP = 1, 6, 17

# TCP flag bits, named because `0x12` in a packet table is unreadable.
FIN, SYN, RST, PSH, ACK = 0x01, 0x02, 0x04, 0x08, 0x10


def _checksum(data: bytes) -> int:
    """The internet checksum of RFC 1071.

    Computed properly rather than left zero. A student who reaches for
    `tcpdump -v` should not be told the fixture is corrupt: the first thing
    that teaches them is to distrust the exercise.
    """
    if len(data) % 2:
        data += b'\x00'
    total = sum(struct.unpack(f'!{len(data) // 2}H', data))
    while total >> 16:
        total = (total & 0xffff) + (total >> 16)
    return ~total & 0xffff


def _ip(addr: str) -> bytes:
    return bytes(int(part) for part in addr.split('.'))


def ipv4(src: str, dst: str, proto: int, payload: bytes, ident: int) -> bytes:
    """One IPv4 packet, checksummed."""
    header = struct.pack('!BBHHHBBH4s4s',
                         (4 << 4) | 5, 0, 20 + len(payload), ident, 0,
                         64, proto, 0, _ip(src), _ip(dst))
    header = header[:10] + struct.pack('!H', _checksum(header)) + header[12:]
    return header + payload


def _l4_checksum(src: str, dst: str, proto: int, segment: bytes) -> int:
    """TCP and UDP checksum over the pseudo-header, per RFC 793 and 768."""
    pseudo = _ip(src) + _ip(dst) + struct.pack('!BBH', 0, proto, len(segment))
    return _checksum(pseudo + segment)


def tcp(src: str, dst: str, sport: int, dport: int, flags: int,
        seq: int = 1000, ack: int = 0, payload: bytes = b'') -> bytes:
    segment = struct.pack('!HHIIBBHHH', sport, dport, seq, ack,
                          (5 << 4), flags, 8192, 0, 0) + payload
    ck = _l4_checksum(src, dst, PROTO_TCP, segment)
    return segment[:16] + struct.pack('!H', ck) + segment[18:]


def udp(src: str, dst: str, sport: int, dport: int, payload: bytes = b'') -> bytes:
    segment = struct.pack('!HHHH', sport, dport, 8 + len(payload), 0) + payload
    ck = _l4_checksum(src, dst, PROTO_UDP, segment)
    return segment[:6] + struct.pack('!H', ck) + segment[8:]


def icmp(kind: int, payload: bytes = b'') -> bytes:
    body = struct.pack('!BBHHH', kind, 0, 0, 1, 1) + payload
    return body[:2] + struct.pack('!H', _checksum(body)) + body[4:]


def ethernet(payload: bytes) -> bytes:
    return ETH_DST + ETH_SRC + struct.pack('!H', ETHERTYPE_IPV4) + payload


#: A DNS query for example.com, and its answer. Written out rather than
#: generated so tshark dissects it as real DNS and `dns.qry.name` drills work.
_DNS_QUERY = (b'\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00'
              b'\x07example\x03com\x00\x00\x01\x00\x01')
_DNS_REPLY = (b'\x12\x34\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00'
              b'\x07example\x03com\x00\x00\x01\x00\x01'
              b'\xc0\x0c\x00\x01\x00\x01\x00\x00\x0e\x10\x00\x04'
              b'\x5d\xb8\xd8\x22')

_HTTP_GET = (b'GET / HTTP/1.1\r\nHost: example.com\r\n'
             b'User-Agent: curl/8.4.0\r\nAccept: */*\r\n\r\n')
_HTTP_200 = (b'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n'
             b'Content-Length: 13\r\n\r\nhello, world\n')
#: A TLS record header, enough that a dissector calls it TLS rather than
#: leaving it as bytes. Handshake, TLS 1.2, ClientHello.
_TLS_HELLO = b'\x16\x03\x01\x00\x2c\x01\x00\x00\x28\x03\x03' + b'\x00' * 40


def packets() -> list[bytes]:
    """The fixture's packets, as Ethernet frames, in order.

    Kept as one flat list built in table order so it reads like the inventory
    in the module docstring, which is the thing an author will have open.
    """
    web, home, dns, ssh, other, far = ('93.184.216.34', '10.0.0.5', '10.0.0.1',
                                       '10.0.0.9', '10.0.0.7', '192.168.50.4')
    out = [
        # 1-5: an HTTPS conversation, opened, used and closed.
        ipv4(home, web, PROTO_TCP, tcp(home, web, 50000, 443, SYN), 1),
        ipv4(web, home, PROTO_TCP, tcp(web, home, 443, 50000, SYN | ACK,
                                       seq=5000, ack=1001), 2),
        ipv4(home, web, PROTO_TCP, tcp(home, web, 50000, 443, ACK,
                                       seq=1001, ack=5001), 3),
        ipv4(home, web, PROTO_TCP, tcp(home, web, 50000, 443, PSH | ACK,
                                       seq=1001, ack=5001,
                                       payload=_TLS_HELLO), 4),
        ipv4(web, home, PROTO_TCP, tcp(web, home, 443, 50000, FIN | ACK,
                                       seq=5001, ack=1052), 5),
        # 6-7: DNS, the reason `udp` is not a trick question.
        ipv4(home, dns, PROTO_UDP, udp(home, dns, 53210, 53, _DNS_QUERY), 6),
        ipv4(dns, home, PROTO_UDP, udp(dns, home, 53, 53210, _DNS_REPLY), 7),
        # 8-9: a refused connection, so RST is available to filter on.
        ipv4(home, ssh, PROTO_TCP, tcp(home, ssh, 50002, 22, SYN), 8),
        ipv4(ssh, home, PROTO_TCP, tcp(ssh, home, 22, 50002, RST | ACK,
                                       seq=0, ack=1001), 9),
        # 10-11: cleartext HTTP from a *different* local host, so `host` and
        # `port` filters select genuinely different sets.
        ipv4(other, web, PROTO_TCP, tcp(other, web, 50004, 80, PSH | ACK,
                                        payload=_HTTP_GET), 10),
        ipv4(web, other, PROTO_TCP, tcp(web, other, 80, 50004, PSH | ACK,
                                        seq=9000, ack=1077,
                                        payload=_HTTP_200), 11),
        # 12-13: neither TCP nor UDP, which is a filter people get wrong.
        ipv4(home, dns, PROTO_ICMP, icmp(8, b'hone' * 4), 12),
        ipv4(dns, home, PROTO_ICMP, icmp(0, b'hone' * 4), 13),
        # 14: off-subnet, so `net 10.0.0.0/24` is not the same as `not host`.
        ipv4(far, home, PROTO_TCP, tcp(far, home, 50006, 445, SYN), 14),
        # 15: a high port, so `portrange` and `port > 1024` have a target.
        ipv4(home, web, PROTO_TCP, tcp(home, web, 50008, 8080, SYN), 15),
    ]
    return [ethernet(p) for p in out]


#: One human sentence per packet, parallel to `packets()`. Feedback quotes
#: these, because "it also selects packet 6" is an accusation and "it also
#: selects the DNS query" is a lesson. Kept beside the packets so the two
#: cannot drift; `test.py` asserts they stay the same length.
LABELS: tuple[str, ...] = (
    'the HTTPS SYN',
    'the HTTPS SYN-ACK',
    'the HTTPS ACK',
    'the TLS client hello',
    'the HTTPS FIN',
    'the DNS query',
    'the DNS response',
    'the SSH SYN',
    'the SSH RST',
    'the HTTP GET',
    'the HTTP 200',
    'the ICMP echo request',
    'the ICMP echo reply',
    'the SMB SYN from 192.168.50.4',
    'the SYN to port 8080',
)


def label(number: int) -> str:
    """Describe packet `number`, counting from 1 as every tool displays it."""
    if 1 <= number <= len(LABELS):
        return f'{LABELS[number - 1]} (packet {number})'
    return f'packet {number}'


def number_for(timestamp: float) -> int | None:
    """Which packet a printed absolute timestamp belongs to.

    tcpdump identifies a packet by its clock and tshark by its index, and the
    two have to be comparable for one set difference to grade both. This is
    the inverse of the spacing `build()` applies, and it is exact rather than
    approximate because the timestamps are authored, not measured.
    """
    offset = round((timestamp - BASE_TIME) * 100)
    if 0 <= offset < len(LABELS):
        return offset + 1
    return None


def build() -> bytes:
    """The whole capture file as bytes. Deterministic."""
    out = [struct.pack('!IHHiIII', MAGIC, VERSION[0], VERSION[1], 0, 0,
                       SNAPLEN, LINKTYPE_ETHERNET)]
    for i, frame in enumerate(packets()):
        # One packet per 10ms, so timestamps are distinct and ordered. Distinct
        # matters: the oracle identifies a matched packet by its timestamp.
        out.append(struct.pack('!IIII', BASE_TIME + i // 100,
                               (i % 100) * 10000, len(frame), len(frame)))
        out.append(frame)
    return b''.join(out)


def write(path) -> None:
    with open(path, 'wb') as f:
        f.write(build())
