import uuid
from AbstractSymbol import AbstractOrderedPair
from ConcreteSymbol import ConcreteOrderedPair

from sqlalchemy import (
    Column,
    String,
    JSON,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class Mapping(Base):
    __tablename__ = "mapping"
    id = Column("id", String, primary_key=True)
    abstract = Column("abstract", JSON)
    concrete = Column("concrete", JSON)


class OracleTable:
    session = None

    def __init__(self, dbURL) -> None:
        engine = create_engine(dbURL, echo=False)
        self.session = sessionmaker(bind=engine)()
        Base.metadata.create_all(engine)

    def add(self, abstract: AbstractOrderedPair, concrete: ConcreteOrderedPair):
        mapping = Mapping()
        mapping.id = str(uuid.uuid4())

        mapping.abstract = abstract.toJSON()
        mapping.concrete = concrete.toJSON()
        self.session.add(mapping)
        self.session.commit()
