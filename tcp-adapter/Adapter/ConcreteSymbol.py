import json
import re

from scapy.layers.inet import TCP
from scapy.packet import Packet, Raw

from TCP import FlagSet

class ConcreteSymbol():
    isNull: bool = True
    sourcePort: int = 20
    destinationPort: int = 80
    seqNumber: int = 0
    ackNumber: int = 0
    dataOffset: int = None
    reserved: int = 0
    flags: str = ""
    window: int = 8192
    checksum: str = None
    urgentPointer: int = 0
    payload: str = ""

    def __init__(self, packet: Packet = None, string: str = None):
        if packet is not None:
            self.isNull = False
            self.sourcePort = packet[TCP].sport
            self.destinationPort = packet[TCP].dport
            self.seqNumber = packet[TCP].seq
            self.ackNumber = packet[TCP].ack
            self.dataOffset = packet[TCP].dataofs
            self.reserved = packet[TCP].reserved
            self.flags = str(packet[TCP].flags)
            self.window = packet[TCP].window
            self.checksum = packet[TCP].chksum
            self.urgentPointer = packet[TCP].urgptr
            if Raw in packet:
                self.payload = packet[Raw].load.decode("utf-8")
        if string is not None:
            self.isNull = False
            pattern = re.compile("([A-Z+]+)\(([0-9]+),([0-9]+),([0-9]+)\)")
            capture = pattern.match(string)
            if "+" in self.flags:
                self.flags = "".join(map(lambda x: x[0], capture.group(1).split("+")))
            self.seqNumber = int(capture.group(2))
            self.ackNumber = int(capture.group(3))

    def __str__(self) -> str:
        if self.isNull:
            return "NIL"
        else:
            flagsString = str(FlagSet(self.flags))
            seqString = str(self.seqNumber)
            ackString = str(self.ackNumber)
            payloadLenString = str(len(self.payload))
            return flagsString + "(" + seqString + "," + ackString + "," + payloadLenString + ")"


    def toJSON(self) -> str:
        if self.isNull:
            return "{}"
        else:
            return json.dumps(self, default=lambda o: o.__dict__)


class ConcreteOrderedPair:
    concreteInputs : [ConcreteSymbol] = []
    concreteOutputs : [ConcreteSymbol] = []

    def __init__(self, inputs: [ConcreteSymbol], outputs: [ConcreteSymbol]):
        self.concreteInputs = inputs
        self.concreteOutputs = outputs

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)