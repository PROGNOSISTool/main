import shlex
import subprocess
import string
import random
from typing import Optional

from scapy.layers.inet import TCP
from scapy.packet import Packet, Raw

from AbstractSymbol import AbstractSymbol
from ConcreteSymbol import ConcreteSymbol

import logging
logging.basicConfig(level=logging.DEBUG,format='%(name)s: %(message)s')

class Mapper:
    process = None
    sourcePort: int = random.randint(1024, 65535)
    destinationPort: int = 44344
    logger = logging.getLogger('Mapper')

    def __init__(self):
        self.process = subprocess.Popen(shlex.split('java -cp "/code/Mapper/dist/TCPMapper.jar:/code/Mapper/lib/*" Mapper'),
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE)

    def abstractToConcrete(self, symbol: AbstractSymbol) -> Optional[Packet]:
        self.process.stdin.write(bytearray("ABSTRACT " + str(symbol) + "\n", 'utf-8'))
        self.process.stdin.flush()
        out = self.process.stdout.readline().decode("utf-8").rstrip("\n")
        self.logger.debug("GOT: " + out)

        abs = AbstractSymbol(string = out)

        if abs.seqNumber is None or abs.ackNumber is None:
            return None

        payload = None
        if abs.payloadLength is not None and abs.payloadLength != 0:
            payload = self.randomPayload(abs.payloadLength)

        packet = TCP(flags=abs.flags.asScapy(),
                     sport=self.sourcePort,
                     dport=self.destinationPort,
                     seq=abs.seqNumber,
                     ack=abs.ackNumber)

        if payload is not None:
            packet = packet / Raw(load=payload)

        return packet

    def concreteToAbstract(self, symbol: ConcreteSymbol) -> AbstractSymbol:
        self.process.stdin.write(bytearray("CONCRETE " + str(symbol) + "\n", 'utf-8'))
        self.process.stdin.flush()
        self.process.stdout.readline().decode("utf-8").rstrip("\n")
        abs = AbstractSymbol(flags=symbol.flags,
                             seqNumber=symbol.seqNumber,
                             ackNumber=symbol.ackNumber,
                             payloadLength=len(symbol.payload))
        return abs

    def randomPayload(self, size: int) -> str:
        payload = ""
        for char in range(size):
            payload += random.choice(string.ascii_letters)
        return payload

    def reset(self):
        self.sourcePort = random.randint(1024, 65535)
        self.process.stdin.write(bytearray("RESET" + "\n", 'utf-8'))
        self.process.stdin.flush()
        self.process.stdout.readline().decode("utf-8")
