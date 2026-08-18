import sys
import asyncio
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, Product, PriceLog
from scraper import fetch_product_price
from notifier import send_price_drop_alert

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

async def scrape_all_products():
    db = SessionLocal()
    try:
        products = db.query(Product).all()
        for product in products:
            new_price = await fetch_product_price(product.url, product.target_price_selector)
            if new_price is not None:
                latest_log = (
                    db.query(PriceLog)
                    .filter(PriceLog.product_id == product.id)
                    .order_by(PriceLog.timestamp.desc())
                    .first()
                )

                if latest_log and new_price < latest_log.price:
                    send_price_drop_alert(product.title, latest_log.price, new_price, product.url)

                log = PriceLog(product_id=product.id, price=new_price)
                db.add(log)
        db.commit()
    finally:
        db.close()

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(scrape_all_products, 'interval', hours=1)
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(title="Price Tracker API", lifespan=lifespan)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ProductCreate(BaseModel):
    title: str
    url: str
    target_price_selector: str

@app.post("/products/", status_code=201)
def track_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(
        title=product.title,
        url=str(product.url),
        target_price_selector=product.target_price_selector
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products/")
def get_all_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

async def run_scraper_task(product_id: int):
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return

        price = await fetch_product_price(product.url, product.target_price_selector)
        if price is not None:
            latest_log = (
                db.query(PriceLog)
                .filter(PriceLog.product_id == product.id)
                .order_by(PriceLog.timestamp.desc())
                .first()
            )

            if latest_log and price < latest_log.price:
                send_price_drop_alert(product.title, latest_log.price, price, product.url)

            log = PriceLog(product_id=product.id, price=price)
            db.add(log)
            db.commit()
    finally:
        db.close()

@app.post("/products/{product_id}/scrape")
async def trigger_scrape(product_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    background_tasks.add_task(run_scraper_task, product_id)
    return {"message": f"Price scrape initiated for '{product.title}'"}

@app.get("/products/{product_id}/history")
def get_price_history(product_id: int, db: Session = Depends(get_db)):
    logs = db.query(PriceLog).filter(PriceLog.product_id == product_id).all()
    return [{"price": log.price, "timestamp": log.timestamp} for log in logs]