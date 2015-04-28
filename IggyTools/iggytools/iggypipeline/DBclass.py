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

    def write_new_pipe(self, pipe, status = 'NEW'):

        maxObj = self.get_maxObj()
        maxObj.pipeID += 1
        self.session.commit()

        pipe.pipeID = maxObj.pipeID

        pipe.dbRecord = PipelineRecord(pipe, status = status) 
        self.session.add(pipe.dbRecord)
        self.session.commit()


    def write_new_module(self, mod, status = 'NEW'):

        if not mod.pipe.pipeID:
            self.write_new_pipe(mod.pipe)            

        maxObj = self.get_maxObj()
        maxObj.modID += 1
        self.session.commit()

        mod.modID = maxObj.modID

        mod.dbRecord = ModuleRecord(mod, status = status)
        self.session.add(mod.dbRecord)
        self.session.commit()


    def update_pipe_record(self, pipe, status):
        
        if not pipe.pipeID:
            raise Exception('pipe.pipeID must be set')
    
        PipelineRecord.update()\
            .where(PipelineRecord.c.pipeID == pipe.pipeID)\
            .values(status = status)
        
        self.session.commit()


    def update_module_record(self, mod, status):
        
        if not mod.modID:
            raise Exception('mod.modID must be set')
    
        ModuleRecord.update()\
            .where(ModuleRecord.c.modID == mod.modID)\
            .values(status = status)
        
        self.session.commit()


    def close(self):
        self.session.close()
