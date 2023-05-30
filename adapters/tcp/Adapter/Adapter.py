from ast import List
import socket
import socketserver
import sys
from scapy.all import *
from scapy.layers.inet import IP, TCP
from Mapper import Mapper
from AbstractSymbol import AbstractSymbol, AbstractOrderedPair
from ConcreteSymbol import ConcreteSymbol, ConcreteOrderedPair
from Tracker import Tracker
from OracleTable import OracleTable

import logging

logging.basicConfig(level=logging.DEBUG, format="%(name)s: %(message)s")


class Adapter:
    mapper: Mapper = Mapper()
    oracleTable: OracleTable = OracleTable()
    localAddr: str = socket.gethostbyname(socket.gethostname())
    impAddress: str = socket.gethostbyname("implementation")
    timeout = 0.4
    connection = IP(src=localAddr, dst=impAddress, flags="DF", version=4)
    tracker: Tracker = Tracker("eth0", impAddress)
    logger = logging.getLogger("Adapter")

    def stop(self):
        self.tracker.stop()
        self.mapper.stop()
        self.oracleTable.save()

    def reset(self):
        self.logger.info("Sending RESET...")
        self.handleQuery("RST(?,?,?)")
        self.mapper.reset()
        self.logger.info("RESET finished.")

    def handleQuery(self, query: str) -> str:
        answers = []
        abstractSymbolsIn: List[AbstractSymbol] = []
        concreteSymbolsIn: List[AbstractSymbol] = []
        abstractSymbolsOut: List[ConcreteSymbol] = []
        concreteSymbolsOut: List[ConcreteSymbol] = []
        for symbol in query.split(" "):
            self.logger.info("Processing Symbol: " + symbol)

            abstractSymbolIn: AbstractSymbol = AbstractSymbol(string=symbol)
            self.logger.info("Abstract Symbol In: " + str(abstractSymbolIn))

            packetIn = self.mapper.abstractToConcrete(abstractSymbolIn)

            if packetIn is None:
                concreteSymbolIn: ConcreteSymbol = ConcreteSymbol()
                concreteSymbolOut: ConcreteSymbol = ConcreteSymbol()
                abstractSymbolOut: AbstractSymbol = AbstractSymbol()
            else:
                concreteSymbolIn: ConcreteSymbol = ConcreteSymbol(packet=packetIn)
                self.logger.info("Concrete Symbol In: " + concreteSymbolIn.toJSON())

                self.tracker.clearLastResponse()
                send([self.connection / packetIn], iface="eth0", verbose=True)
                concreteSymbolOut: ConcreteSymbol = self.tracker.sniffForResponse(
                    packetIn[TCP].dport, packetIn[TCP].sport, self.timeout
                )
                self.logger.info("Concrete Symbol Out: " + concreteSymbolOut.toJSON())

                if not concreteSymbolOut.isNull:
                    abstractSymbolOut: AbstractSymbol = self.mapper.concreteToAbstract(
                        concreteSymbolOut
                    )
                    # Match abstraction level.
                    if abstractSymbolIn.seqNumber is None:
                        abstractSymbolOut.seqNumber = None
                    if abstractSymbolIn.ackNumber is None:
                        abstractSymbolOut.ackNumber = None
                    if abstractSymbolIn.payloadLength is None:
                        abstractSymbolOut.payloadLength = None
                else:
                    concreteSymbolOut.isNull = True
                    abstractSymbolOut: AbstractSymbol = AbstractSymbol()
                    abstractSymbolOut.isNull = True

                self.logger.info("Abstract Symbol Out: " + str(abstractSymbolOut))

            answers.append(str(abstractSymbolOut))

            abstractSymbolsIn.append(abstractSymbolIn)
            concreteSymbolsIn.append(concreteSymbolIn)
            abstractSymbolsOut.append(abstractSymbolOut)
            concreteSymbolsOut.append(concreteSymbolOut)

        self.oracleTable.add(
            AbstractOrderedPair(abstractSymbolsIn, abstractSymbolsOut),
            ConcreteOrderedPair(concreteSymbolsIn, concreteSymbolsOut),
        )
        return " ".join(answers)


class QueryRequestHandler(socketserver.StreamRequestHandler):
    def __init__(self, request, client_address, server):
        self.logger = logging.getLogger("Query Handler")
        socketserver.BaseRequestHandler.__init__(self, request, client_address, server)
        return

    def handle(self):
        while True:
            query = self.rfile.readline().strip().decode("utf-8").rstrip("\n")
            if query != "":
                self.logger.info("Received query: " + query)
                if query == "STOP":
                    self.server.adapter.stop()
                    self.wfile.write(bytearray("STOP" + "\n", "utf-8"))
                    break
                elif query == "RESET":
                    self.server.adapter.reset()
                    self.wfile.write(bytearray("RESET" + "\n", "utf-8"))
                else:
                    answer = self.server.adapter.handleQuery(query)
                    self.logger.info("Sending answer: " + answer)
                    self.wfile.write(bytearray(answer + "\n", "utf-8"))
            else:
                self.wfile.write(bytearray("NIL\n", "utf-8"))
        sys.exit(0)


class AdapterServer(socketserver.TCPServer):
    def __init__(self, server_address, handler_class=QueryRequestHandler):
        self.adapter = Adapter()
        self.adapter.tracker.start()
        self.logger = logging.getLogger("Server")
        self.logger.info("Initialising server...")
        socketserver.TCPServer.__init__(self, server_address, handler_class)
        return


address = ("0.0.0.0", 3333)
server = AdapterServer(address, QueryRequestHandler)

if __name__ == "__main__":
    server.serve_forever()
