import socketserver
from scapy.all import *
from scapy.layers.inet import IP
from scapy.config import conf
conf.use_pcap= True
from Mapper import Mapper
from AbstractSymbol import AbstractSymbol
from ConcreteSymbol import ConcreteSymbol

import logging
logging.basicConfig(level=logging.DEBUG,format='%(name)s: %(message)s')
class Adapter:
    mapper: Mapper = Mapper()
    localAddr: str = socket.gethostbyname(socket.gethostname())
    impAddress: str = socket.gethostbyname('implementation')
    timeout = 0.5
    connection = IP(src=localAddr, dst=impAddress)
    logger = logging.getLogger('Adapter')

    def reset(self):
        self.mapper.reset()

    def handleQuery(self, query: str) -> str:
        answers = []
        for symbol in query.split(" "):
            self.logger.info("Processing Symbol: " + symbol)

            abstractSymbolIn = AbstractSymbol(string=symbol)
            self.logger.info("Abstract Symbol In: " + str(abstractSymbolIn))

            packetIn = self.mapper.abstractToConcrete(abstractSymbolIn)

            concreteSymbolIn = ConcreteSymbol(packet=packetIn)
            self.logger.info("Concrete Symbol In: " + concreteSymbolIn.toJSON())

            packetOut = sr1(self.connection/packetIn, timeout=self.timeout)

            concreteSymbolOut = ConcreteSymbol(packet=packetOut)
            self.logger.info("Concrete Symbol Out: " + concreteSymbolOut.toJSON())

            if packetOut is not None:
                abstractSymbolOut = self.mapper.concreteToAbstract(packetOut)
                # Match abstraction level.
                if abstractSymbolIn.seqNumber is None:
                    abstractSymbolOut.seqNumber = None
                if abstractSymbolIn.ackNumber is None:
                    abstractSymbolOut.ackNumber = None
                if abstractSymbolIn.payloadLength is None:
                    abstractSymbolOut.payloadLength = None
            else:
                abstractSymbolOut = "TIMEOUT"

            self.logger.info("Abstract Symbol Out: " + str(abstractSymbolOut))

            answers.append(str(abstractSymbolOut))
        return " ".join(answers)

class QueryRequestHandler(socketserver.StreamRequestHandler):
    def __init__(self, request, client_address, server):
        self.logger = logging.getLogger('Query Handler')
        socketserver.BaseRequestHandler.__init__(self, request, client_address, server)
        return

    def handle(self):
        while True:
            query = self.rfile.readline().strip().decode("utf-8").rstrip("\n")
            self.logger.info("Received query: " + query)
            if query == "STOP":
                break
            elif query == "RESET":
                self.server.adapter.reset()
                self.wfile.write(bytearray("RESET" + "\n", 'utf-8'))
            else:
                answer = self.server.adapter.handleQuery(query)
                self.logger.info("Sending answer: " + answer)
                self.wfile.write(bytearray(answer + "\n", 'utf-8'))
        return

class AdapterServer(socketserver.TCPServer):
    def __init__(self, server_address, handler_class=QueryRequestHandler):
        self.adapter = Adapter()
        self.logger = logging.getLogger('Server')
        self.logger.info("Initialising server...")
        socketserver.TCPServer.__init__(self, server_address, handler_class)
        return

if __name__ == '__main__':
    address = ('0.0.0.0', 3333)
    server = AdapterServer(address, QueryRequestHandler)
    ip, port = server.server_address
    server.serve_forever()
