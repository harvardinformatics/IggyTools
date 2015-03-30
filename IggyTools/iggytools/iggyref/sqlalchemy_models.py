from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, TIMESTAMP, DateTime, func
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey
from datetime import datetime

Base = declarative_base()

class CommonName(Base):
    __tablename__ = 'common_name'

    speciesID = Column('species_id', String(100), primary_key=True)
    commonName = Column('common_name', String(100))

    def __init__(self, speciesID, commonName):
        self.speciesID = speciesID
        self.commonName = commonName

    def __repr__(self):
        return "<CommonName(%s, %s)>" % (self.speciesID, self.commonName)

class CollectionRecord(Base):
    __tablename__ = 'collection'

    # the tuple (primaryID, secondaryID, source) uniquely identifies a collection
    id = Column(Integer, primary_key=True)
    primaryID = Column('primary_id', String(100))
    secondaryID = Column('secondary_id', String(100), ForeignKey('common_name.species_id')) 
    source = Column(String(100))
    cType = Column('type', String(100))
    status = Column(String(100))
    timestamp = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    addendum = Column(String(100))

    def __init__(self, primaryID, secondaryID, cType, source, status, addendum = None):
        self.primaryID = primaryID
        self.secondaryID = secondaryID
        self.cType = cType
	self.source = source
	self.status = status
        self.addendum = addendum

    def __repr__(self):
        return "<Species(%s, %s, %s, %s, %s)>" % (self.primaryID, self.secondaryID, self.source, self.status, self.timestamp)

class FileRecord(Base):
    __tablename__ = 'reffile'

    id = Column(Integer, primary_key=True)
    fileName = Column('filename', String(100))
    primaryID = Column('primary_id', String(100), ForeignKey('collection.primary_id'))
    secondaryID = Column('secondary_id', String(100), ForeignKey('collection.secondary_id'))
    source = Column(String(100), ForeignKey('collection.source'))
    cType = Column('type', String(100), ForeignKey('collection.type'))
    status = Column(String(100))
    timestamp = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    remoteTimeString = Column('remote_timestring',String(100))
    checksum = Column('checksum',String(100))
    addendum = Column(String(100))

    def __init__(self, fileName, primaryID, secondaryID, cType, source, status):
        self.fileName = fileName
	self.primaryID = primaryID
	self.secondaryID = secondaryID
        self.cType = cType
	self.source = source
	self.status = status

    def __repr__(self):
        return "<RefFile(%s, %s, %s, %s, %s, %s)>" % (self.fileName, self.primaryID, self.secondaryID, self.source, self.status, self.timestamp)

def getBase():
    return Base


