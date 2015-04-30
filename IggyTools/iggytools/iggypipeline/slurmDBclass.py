import os.path as path
import commands, logging
from sqlalchemy import create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound


class SlurmDB(object):

    def __init__(self, pref, verbose = None):

        if verbose is None:
            verbose = pref.LOGGING_LEVEL == logging.DEBUG

        user = 'portal'
        db = 'portal'
        host = 'db-internal'
        
        with open('/n/informatics/saved/portal.txt') as fh:
            pw = fh.read().rstrip()

        engine = create_engine('mysql://%s:%s@%s:'%(user, pw, host) + path.join('3306',db), echo = verbose)

        Base = declarative_base()
        Base.metadata.bind = engine

        class Squeue(Base):
            __tablename__   = 'jobs_squeueresults'
            __table_args__  = {'autoload':True}

        self.Squeue = Squeue

        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine, autoflush=True, autocommit=False)

        self.session = Session()


    def getJobStatus(self, jobID):

        try:

            #get status from portal squeue db
            rec = self.session.query(self.Squeue).filter(self.Squeue.jobid == jobID).one()
            return rec.state

        except NoResultFound:

            #get status from sacct command
            return commands.getoutput('sacct -j %s --format=State --parsable2 --noheader' % jobID).split()[0]

        
    def close(self):
        self.session.close()
