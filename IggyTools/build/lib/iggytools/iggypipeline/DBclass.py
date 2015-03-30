from sqlalchemy.orm import sessionmaker
from sqlalchemy_models import getBaseAndEngine, FileRecord, CollectionRecord, CommonName

class iggyrefDB(object):

    def __init__(self):
        Base, engine = getBaseAndEngine()
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
        coll = CollectionRecord(C.primaryID, C.secondaryID, C.type, C.source, status, addendum)
        self.session.add(coll)
        self.session.commit()

    def writeFileRecord(self, File, C, status, checksum = None, addendum = None):
        fRecord = FileRecord(File.name, C.primaryID, C.secondaryID, C.type, C.source, status)
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
                                                     source = C.source, status = status).order_by('-timestamp').first()
        if fRecord:
            attr = getattr(fRecord, attribute)
            if attr:
                return attr
        return ''

    def close(self):
        self.session.close()
