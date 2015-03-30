import os.path as path
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_models import getBase, FileRecord, CollectionRecord, CommonName

class iggyrefDB(object):

    def __init__(self, config):
        Base = getBase()
        if config.DB_TYPE == 'mysql':
            engine = create_engine('mysql://%s:%s@%s:'%(config.MYSQL_USER, config.MYSQL_PASS, config.MYSQL_HOST) \
                                       + path.join('3306',config.MYSQL_DB), echo = config.LOG_LEVEL == logging.DEBUG)
        elif config.DB_TYPE == 'sqlite':
            engine = create_engine('sqlite:///' + path.join(config.LOG_DIR,'iggyref.db'), echo = config.LOG_LEVEL == logging.DEBUG)
        else:
            raise Exception('Unrecognized DB_TYPE: %s' % config.DB_TYPE)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine, autoflush=True, autocommit=False)
        self.session = Session()

    def addSpeciesCommonName(self, speciesID, commonName):
        def upperFirst(myStr):
            return myStr[0].upper() + myStr[1:].lower()

        speciesID = upperFirst(speciesID)
        commonName = upperFirst(commonName)

        cn = self.session.query(CommonName).filter_by(speciesID=speciesID).first()
        if not cn:
            cn = CommonName(speciesID, commonName)
            self.session.add(cn)
            self.session.commit()
        elif cn.commonName != commonName:
            raise Exception('Name mismatch: Previous (Species, common name): (%s, %s); Current (species, common name): (%s, %s).' \
                                % (cn.speciesID, cn.commonName, speciesID, commonName))

    def writeCollectionRecord(self, C, status, addendum = None):
        coll = CollectionRecord(C.primaryID, C.secondaryID, C.type, C.repo.source, status, addendum)
        self.session.add(coll)
        self.session.commit()

    def writeFileRecord(self, File, C, status, checksum = None, addendum = None):
        fRecord = FileRecord(File.name, C.primaryID, C.secondaryID, C.type, C.repo.source, status)
        if File.remoteTimeString:
            fRecord.remoteTimeString = File.remoteTimeString
        if File.remoteChecksum:
            fRecord.checksum = checksum
        elif File.localChecksum:
            fRecord.checksum = File.localChecksum
        if addendum:
            fRecord.addendum = addendum
        self.session.add(fRecord)
        self.session.commit()

    def getFileAttribute(self, File, C, status, attribute): 
        fRecord = self.session.query(FileRecord).filter_by(fileName = File.name, primaryID = C.primaryID, secondaryID = C.secondaryID, cType = C.type, \
                                                     source = C.repo.source, status = status).order_by('-timestamp').first()
        if fRecord:
            attr = getattr(fRecord, attribute)
            if attr:
                return attr
        return ''

    def close(self):
        self.session.close()
