from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "sqlite:///./price_tracker.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    target_price_selector = Column(String, nullable=False)
    price_logs = relationship("PriceLog", back_populates="product", cascade="all, delete-orphan")

class PriceLog(Base):
    __tablename__ = "price_logs"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="price_logs")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_all_products():
    db = SessionLocal()
    try:
        return db.query(Product).all()
    finally:
        db.close()

def add_product(title, url, target_price_selector):
    db = SessionLocal()
    try:
        product = Product(title=title, url=url, target_price_selector=target_price_selector)
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    finally:
        db.close()