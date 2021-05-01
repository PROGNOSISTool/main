import json
import time
from AbstractSymbol import AbstractOrderedPair
from ConcreteSymbol import ConcreteOrderedPair

class OracleTable:
    internalMap: {str : ConcreteOrderedPair} = {}

    def add(self, abstract: AbstractOrderedPair, concrete: ConcreteOrderedPair):
        self.internalMap[str(abstract)] = concrete

    def save(self):
        with open('oracleTable-{}.json'.format(int(time.time())), 'w') as outFile:
            json.dump(self.internalMap, outFile, default=lambda o: o.__dict__)
