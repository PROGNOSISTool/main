from typing import List
import jsons
import re
from TCP import FlagSet


class AbstractSymbol:
    isNull: bool = True
    flags: FlagSet = FlagSet()
    seqNumber: int = None
    ackNumber: int = None
    payloadLength: int = None

    def __init__(
        self,
        string: str = None,
        flags: str = None,
        seqNumber: int = None,
        ackNumber: int = None,
        payloadLength: int = None,
    ):
        if flags is not None:
            self.isNull = False
        self.flags = FlagSet(flags)
        self.seqNumber = seqNumber
        self.ackNumber = ackNumber
        self.payloadLength = payloadLength

        if string is not None:
            pattern = re.compile("([A-Z+]+)\(([0-9?]+),([0-9?]+),([0-9?]+)\)")
            capture = pattern.match(string)
            self.isNull = False
            self.flags = FlagSet(
                "".join(map(lambda x: x[0], capture.group(1).split("+")))
            )
            self.seqNumber = int(capture.group(2)) if capture.group(2) != "?" else None
            self.ackNumber = int(capture.group(3)) if capture.group(3) != "?" else None
            self.payloadLength = (
                int(capture.group(4)) if capture.group(4) != "?" else None
            )

    def __str__(self) -> str:
        if self.isNull:
            return "NIL"
        else:
            flagsString = str(self.flags)
            seqString = "?" if self.seqNumber is None else str(self.seqNumber)
            ackString = "?" if self.ackNumber is None else str(self.ackNumber)
            payloadLenString = (
                "?" if self.payloadLength is None else str(self.payloadLength)
            )
            return (
                flagsString
                + "("
                + seqString
                + ","
                + ackString
                + ","
                + payloadLenString
                + ")"
            )

    def toJSON(self) -> str:
        if self.isNull:
            return "{}"
        else:
            return jsons.dumps(self)


class AbstractOrderedPair:
    abstractInputs: List[AbstractSymbol] = []
    abstractOutputs: List[AbstractSymbol] = []

    def __init__(self, inputs: List[AbstractSymbol], outputs: List[AbstractSymbol]):
        self.abstractInputs = inputs
        self.abstractOutputs = outputs

    def __str__(self) -> str:
        abstractInputStrings = map(str, self.abstractInputs)
        concreteInputStrings = map(str, self.abstractOutputs)

        aiString = "[{}]".format(", ".join(abstractInputStrings))
        aoString = "[{}]".format(", ".join(concreteInputStrings))
        return "({},{})".format(aiString, aoString)

    def toJSON(self):
        return jsons.dumps(self)
