from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, TIMESTAMP, DateTime, func
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey
from datetime import datetime

Base = declarative_base()

class PipelineRecord(Base):

    __tablename__ = 'pipeline'

    id         = Column(Integer, primary_key=True)

    pipeName   = Column('pipe_name', String(100))
    pipeID     = Column('pipe_id', Integer())
    status     = Column(String(100))
    timestamp  = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    pipeDir    = Column('pipe_dir', String(200))
    addendum   = Column(String(200))

    def __init__(self, pipe, status = None, addendum = None):

        self.pipeName = pipe.name
        self.pipeID = pipe.pipeID
        self.status = status
        self.pipeDir = pipe.pipeDir
        if addendum:
            self.addendum = addendum

    def __repr__(self):
        return "<Pipeline(%s, %s)>" % (self.pipeName, self.pipeID)


class ModuleRecord(Base):

    __tablename__ = 'module'

    id        = Column(Integer, primary_key=True)

    modName   = Column('mod_name', String(50))
    modID     = Column('mod_id', Integer())

    pipeName  = Column('pipe_name', String(100))
    pipeID    = Column('pipe_id', Integer())

    status    = Column(String(100))

    processID = Column('process_id', Integer())
    jobID     = Column('job_id', Integer())

    timestamp = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    modArgs   = Column('mod_args', String(1000))
    slurmArgs = Column('slurm_args', String(1000))
    addendum  = Column(String(200))

    def __init__(self, mod, status = None, addendum = None):

        self.modName = mod.name
        self.modID = mod.modID

        self.pipeName = mod.pipe.name
        self.pipeID = mod.pipe.pipeID

        self.status = status

        if mod.processID:
            self.processID = mod.processID
            
        if mod.jobID:
            self.jobID = mod.jobID

        if mod.modConfig.argsJson:
            self.modArgs = mod.modConfig.argsJson

        if mod.slurmConfig.argsJson:
            self.slurmArgs = mod.slurmConfig.argsJson

        if addendum:
            self.addendum = addendum

    def __repr__(self):
        return "<Module(%s, %s; %s, %s)>" % (self.modName, self.modID, self.pipeName, self.pipeID)


class MaxID(Base):

    __tablename__ = 'max_id'

    id        = Column(Integer, primary_key=True)

    pipeID     = Column('pipe_id', Integer())   #at obj instantiation, modID and pipeID are set to None.
    modID      = Column('mod_id', Integer())


    def __init__(self):

        self.pipeID = 0  #set defaults
        self.modID = 0


            
def getBase():
    return Base




