"""
Database setup and models for Base Identity Protocol.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, String, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

Base = declarative_base()


class Identity(Base):
    """Database model for wallet identities."""
    __tablename__ = "identities"
    
    address = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    tier = Column(String, nullable=False)
    verdict = Column(String, nullable=False)
    stats = Column(JSON, nullable=False)
    scores = Column(JSON, nullable=False)
    minted = Column(Boolean, default=False, nullable=False)
    mint_tx_hash = Column(String, nullable=True)
    minted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Identity(address={self.address}, name={self.name}, tier={self.tier})>"


def init_db(db_path: str = "wallet_identities.db"):
    """Initialize database connection and create tables."""
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    return engine


def save_identity(data: dict, db_path: str = "wallet_identities.db"):
    """
    Upsert identity data (merges if address exists).
    
    Args:
        data: Dictionary with keys: address, name, tier, verdict, stats, scores, minted (optional), mint_tx_hash (optional)
        db_path: Path to SQLite database
    """
    engine = init_db(db_path)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # Check if address exists
        existing = session.query(Identity).filter(Identity.address == data['address']).first()
        
        if existing:
            # Update existing record (preserve mint status)
            existing.name = data['name']
            existing.tier = data['tier']
            existing.verdict = data['verdict']
            existing.stats = data['stats']
            existing.scores = data['scores']
            # Only update mint fields if provided
            if 'minted' in data:
                existing.minted = data['minted']
            if 'mint_tx_hash' in data:
                existing.mint_tx_hash = data['mint_tx_hash']
            if 'minted_at' in data:
                existing.minted_at = data['minted_at']
            existing.created_at = datetime.utcnow()
        else:
            # Insert new record
            identity = Identity(
                address=data['address'],
                name=data['name'],
                tier=data['tier'],
                verdict=data['verdict'],
                stats=data['stats'],
                scores=data['scores'],
                minted=data.get('minted', False),
                mint_tx_hash=data.get('mint_tx_hash'),
                minted_at=data.get('minted_at'),
                created_at=datetime.utcnow()
            )
            session.add(identity)
        
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def mark_as_minted(address: str, tx_hash: str, db_path: str = "wallet_identities.db"):
    """
    Mark an identity as minted.
    
    Args:
        address: Wallet address
        tx_hash: Transaction hash of the mint payment
        db_path: Path to SQLite database
    """
    engine = init_db(db_path)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        identity = session.query(Identity).filter(Identity.address == address).first()
        if identity:
            identity.minted = True
            identity.mint_tx_hash = tx_hash
            identity.minted_at = datetime.utcnow()
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_identity(address: str, db_path: str = "wallet_identities.db") -> Optional[Identity]:
    """
    Retrieve an identity by address.
    
    Args:
        address: Wallet address
        db_path: Path to SQLite database
        
    Returns:
        Identity object or None if not found
    """
    engine = init_db(db_path)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        return session.query(Identity).filter(Identity.address == address).first()
    finally:
        session.close()
