# From: https://gitlab.science.ru.nl/pfiteraubrostean/tcp-learner/-/blob/master/Adapter/tracker.py

from pcapy import open_live
from impacket.ImpactDecoder import EthDecoder, Dot11WPA2Decoder
from impacket.ImpactPacket import IP, TCP
import time
import threading
from ConcreteSymbol import ConcreteSymbol

# Tool that monitors communication of a server port and interface, built on the "pcapy" framework.
# It always stores the last response received from the server. The sender tool, in  case scapy did not receive
# a response, can query the tracker, to see if it did detect a packet. This is useful, since scapy does miss
# some responses.


class Tracker(threading.Thread):
    serverPort = 0
    senderPort = 0
    pcap = None
    interface = "eth0"
    decoder = None
    max_bytes = 1024
    promiscuous = False
    readTimeout = 1  # in milliseconds
    isStopped = False
    lastResponse = ConcreteSymbol()
    lastResponses = dict()

    def __init__(self, interface, serverIp, interfaceType=0, readTimeout=1):
        super(Tracker, self).__init__()
        str(interface)
        self.interface = interface
        # Wireless not yet supported
        self.decoder = self.getDecoder(interfaceType)
        self._stop = threading.Event()
        self._received = threading.Event()
        self.daemon = True
        self.readTimeout = readTimeout
        self.serverIp = serverIp
        self.lastResponse = ConcreteSymbol()
        self.lastResponses = dict()
        self.responseHistory = set()

    def getDecoder(self, interfaceType):
        if interfaceType == 0:
            return EthDecoder()
        else:
            return Dot11WPA2Decoder()
            # if interfaceType == InterfaceType.Wireless:
            #     print "In Tracker.py: Wireless not yet supported, sorry"
            #     exit(0)

    def stop(self):
        self._stop.set()

    def isStopped(self):
        return self._stop.isSet()

    # This is method is called periodically by pcapy
    def callback(self, hdr, data):
        if self.isStopped() == True:
            print("Tracker is stopped.")
            exit(-1)  # results in a strange warning
        else:
            if data is None:
                return
            packet = self.decoder.decode(data)
            l2 = packet.child()
            if isinstance(l2, IP):
                l3 = l2.child()
                #       Due to the filter used, all packets should use TCP
                src_ip = l2.get_ip_src()
                dst_ip = l2.get_ip_dst()
                tcp_src_port = l3.get_th_sport()
                tcp_dst_port = l3.get_th_dport()
                tcp_syn = l3.get_th_seq()
                tcp_ack = l3.get_th_ack()
                response = self.impacketResponseParse(l3)
                if self.isRetransmit(tcp_src_port, tcp_dst_port, response):
                    print("ignoring retransmission: ", response.__str__())
                else:
                    # print "received: ",(tcp_src_port, tcp_dst_port),":",(response.seq, response.ack, response.flags)
                    self.responseHistory.add(
                        (
                            (tcp_src_port, tcp_dst_port),
                            response.seqNumber,
                            response.ackNumber,
                            response.flags,
                        )
                    )
                    self.lastResponses[(tcp_src_port, tcp_dst_port)] = response
                    self.lastResponse = response
                    self._received.set()

    def isRetransmit(self, tcp_src_port, tcp_dst_port, response):
        isRet = (
            (tcp_src_port, tcp_dst_port),
            response.seqNumber,
            response.ackNumber,
            response.flags,
        ) in self.responseHistory and response.flags.replace("U", "") in [
            "SA",
            "AS",
            "AF",
            "FA",
            "S",
            "P",
            "PA",
        ]
        if not isRet:
            if "P" in response.flags and "A" in response.flags and response.payload > 0:
                for (src_port, dst_port), seq, ack, flags in self.responseHistory:
                    if (
                        (src_port, dst_port) == (tcp_src_port, tcp_dst_port)
                        and (seq == response.seq)
                        and "P" in flags
                        and "A" in flags
                    ):
                        isRet = True
        return isRet

    def processResponse(self, response):
        if not response.isNull:
            self.lastResponse = response
            if (
                response.flags == "SA" or response.flags == "AS"
            ) and response in self.lastResponses:
                print("ignoring SA retransmission " + response.__str__())
            else:
                print("non SA-ret packet:" + response.__str__())

    # MAKE SURE the order of checking/appending characters is the same here as it is in the sender
    def impacketResponseParse(self, tcpPacket):
        response = ConcreteSymbol()
        if isinstance(tcpPacket, TCP):
            tcp_syn = tcpPacket.get_th_seq()
            tcp_ack = tcpPacket.get_th_ack()

            flags = "F" if tcpPacket.get_FIN() == 1 else ""
            flags += "S" if tcpPacket.get_SYN() == 1 else ""
            flags += "R" if tcpPacket.get_RST() == 1 else ""
            flags += "P" if tcpPacket.get_PSH() == 1 else ""
            flags += "A" if tcpPacket.get_ACK() == 1 else ""
            flags += "U" if tcpPacket.get_URG() == 1 else ""
            payload = tcpPacket.get_data_as_string()

            response = ConcreteSymbol(
                None,
                flags
                + "("
                + str(tcp_syn)
                + ","
                + str(tcp_ack)
                + ","
                + str(len(payload))
                + ")",
            )
        return response

    # clears all last responses for all ports (keep that in mind if you have responses on several ports)
    # this is done because when learning, we only care about one port
    def clearLastResponse(self):
        self.lastResponse = ConcreteSymbol()
        self.lastResponses.clear()

    def reset(self):
        self.clearLastResponse()
        self.responseHistory.clear()
        self._received.clear()

    def sniffForResponse(self, serverPort, senderPort, waitTime):
        div = waitTime / 10
        response = ConcreteSymbol()
        # print "sniffing for response ", waitTime
        for i in range(0, 9):
            # print "waiting... ", div
            time.sleep(div)
            response = self.getLastResponse(serverPort, senderPort)
            if not response.isNull:
                break
                # self._received.wait(timeout=waitTime)
        # response = self.getLastResponse(serverPort, senderPort)
        # self._received.clear()
        return response

    # fetches the last response from an active port. If no response was sent, then it returns Timeout
    def getLastResponse(self, serverPort, senderPort):
        return (
            self.lastResponses.get((serverPort, senderPort))
            if self.lastResponses.get((serverPort, senderPort)) is not None
            else ConcreteSymbol()
        )

    def run(self):
        self.trackPackets()

    def trackPackets(self):
        self.pcap = open_live(
            self.interface, self.max_bytes, self.promiscuous, self.readTimeout
        )
        self.pcap.setfilter("tcp and ip src " + str(self.serverIp))
        while True:
            (header, packet) = self.pcap.next()
            self.callback(header, packet)
