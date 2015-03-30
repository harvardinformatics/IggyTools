import os.path as path
import logging
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from iggytools.iggypipeline.sqlalchemy_models import getBase, PipelineRecord, ModuleRecord, MaxID
from sqlalchemy.orm.exc import NoResultFound


class iggypipeDB(object):


    def __init__(self, pref):

        Base = getBase()

        if pref.DB_TYPE == 'mysql':
            engine = create_engine('mysql://%s:%s@%s:'%(pref.MYSQL_USER, pref.MYSQL_PASS, pref.MYSQL_HOST) \
                                       + path.join('3306',pref.MYSQL_DB), echo = pref.LOGGING_LEVEL == logging.DEBUG)

        elif pref.DB_TYPE == 'sqlite':
            engine = create_engine('sqlite:///' + path.join(pref.LOG_DIR,'iggyref.db'), echo = pref.LOGGING_LEVEL == logging.DEBUG)

        else:
            raise Exception('Unrecognized DB_TYPE: %s' % pref.DB_TYPE)

        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine, autoflush=True, autocommit=False)

        self.session = Session()


    def write_new_pipe_and_modules(self, pipe):

        self.write_new_pipe(pipe)

        # set modules ID's for modules in pipeline
        for mod in pipe.modules:
            self.write_new_module(mod)


    def get_maxObj(self):
        # get max ID object
        try:
            return self.session.query(MaxID).with_for_update().one()  #block table
        except NoResultFound:
            m = MaxID()  #default maxes are zero                                                                                                                
            self.session.add(m)
            return m

    def write_new_pipe(self, pipe):

        maxObj = self.get_maxObj()
        maxObj.pipeID += 1
        self.session.commit()

        pipe.pipeID = maxObj.pipeID

        self.write_pipe_record(pipe, status = 'NEW')  #set pipeline status to new


    def write_new_module(self, mod, status = 'NEW'):
        if not mod.pipe.pipeID:
            self.write_new_pipe(mod.pipe)            

        maxObj = self.get_maxObj()
        maxObj.modID += 1
        self.session.commit()

        mod.modID = maxObj.modID

        self.write_module_record(mod, status = status)  #set mod status to new


    def write_pipe_record(self, pipe, status = None):

        pRecord = PipelineRecord(pipe, status)

        self.session.add(pRecord)
        self.session.commit()


    def write_module_record(self, mod, status = None):

        mRecord = ModuleRecord(mod, status)

        self.session.add(mRecord)
        self.session.commit()


    def close(self):
        self.session.close()
