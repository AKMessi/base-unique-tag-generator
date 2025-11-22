import datetime
from sqlalchemy import create_engine, Column, String, Integer, JSON, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Identity(Base):
    __tablename__ = 'identities'
    address = Column(String, primary_key=True)
    name = Column(String)
    tier = Column(String)
    verdict = Column(String)
    stats = Column(JSON)
    scores = Column(JSON)
    mint_status = Column(Boolean, default=False)
    mint_tx = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Database:
    def __init__(self):
        self.engine = create_engine('sqlite:///identities.db')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def save_identity(self, data):
        session = self.Session()
        try:
            existing = session.query(Identity).filter_by(address=data['address']).first()
            if existing:
                existing.name = data['name']
                existing.tier = data['tier']
                existing.verdict = data['verdict']
                existing.stats = data['stats']
                existing.scores = data['scores']
            else:
                new_id = Identity(**data)
                session.add(new_id)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def mark_minted(self, address, tx_hash):
        session = self.Session()
        try:
            record = session.query(Identity).filter_by(address=address).first()
            if record:
                record.mint_status = True
                record.mint_tx = tx_hash
                session.commit()
                return True
            return False
        finally:
            session.close()

    def get_identity(self, address):
        session = self.Session()
        try:
            return session.query(Identity).filter_by(address=address).first()
        finally:
            session.close()