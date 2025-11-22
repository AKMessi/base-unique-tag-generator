import datetime
import os
from sqlalchemy import create_engine, Column, String, JSON, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# Load environment variables immediately
load_dotenv()

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
        # 1. Get URL from .env
        db_url = os.getenv("DATABASE_URL")
        
        # 2. Clean up common URL issues
        if db_url:
            # Fix Postgres protocol for SQLAlchemy
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql://", 1)
            
            # Check if user accidentally left the placeholder
            if "your_neon_connection_string" in db_url or "neondb_owner" in db_url and "..." in db_url:
                print("⚠️  WARNING: Invalid DATABASE_URL detected. Switching to Local SQLite.")
                db_url = None

        # 3. Fallback logic
        if not db_url:
            db_url = "sqlite:///identities.db"

        # 4. Attempt Connection with Failover
        try:
            self.engine = create_engine(db_url)
            Base.metadata.create_all(self.engine)
            print(f"✅ Connected to Database: {'SQLite' if 'sqlite' in db_url else 'Neon Cloud'}")
        except Exception as e:
            print(f"❌ Cloud DB Connection Failed: {e}")
            print("⚠️  Falling back to local SQLite database...")
            self.engine = create_engine("sqlite:///identities.db")
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
                # Only update mint status if explicitly provided
                if 'minted' in data:
                    existing.mint_status = data['minted']
                if 'mint_tx' in data:
                    existing.mint_tx = data['mint_tx']
                existing.created_at = datetime.datetime.utcnow()
            else:
                new_id = Identity(
                    address=data['address'],
                    name=data['name'],
                    tier=data['tier'],
                    verdict=data['verdict'],
                    stats=data['stats'],
                    scores=data['scores'],
                    mint_status=data.get('minted', False),
                    mint_tx=data.get('mint_tx'),
                    created_at=datetime.datetime.utcnow()
                )
                session.add(new_id)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Database Error: {e}")
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