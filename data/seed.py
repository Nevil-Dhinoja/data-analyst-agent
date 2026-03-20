from sqlalchemy import create_engine
import pandas as pd
import random
from faker import Faker
import os

fake = Faker('en_IN')
os.makedirs("data", exist_ok=True)
engine = create_engine("sqlite:///data/ecommerce.db")
random.seed(42)
Faker.seed(42)

customers = pd.DataFrame({
    "customer_id": range(1, 201),
    "name": [fake.name() for _ in range(200)],
    "city": [random.choice(["Surat","Mumbai","Ahmedabad",
              "Baroda","Rajkot","Pune","Delhi","Bangalore"])
              for _ in range(200)],
    "age": [random.randint(18, 60) for _ in range(200)],
    "gender": [random.choice(["M","F"]) for _ in range(200)],
    "joined_date": [str(fake.date_between(
        start_date="-3y", end_date="today"))
        for _ in range(200)]
})

categories = ["Electronics","Clothing","Books",
              "Home & Kitchen","Sports","Beauty"]
products = pd.DataFrame({
    "product_id": range(1, 51),
    "name": [fake.catch_phrase() for _ in range(50)],
    "category": [random.choice(categories) for _ in range(50)],
    "price": [round(random.uniform(99, 9999), 2) for _ in range(50)],
    "stock": [random.randint(0, 500) for _ in range(50)],
    "rating": [round(random.uniform(2.5, 5.0), 1) for _ in range(50)]
})

orders = pd.DataFrame({
    "order_id": range(1, 1001),
    "customer_id": [random.randint(1, 200) for _ in range(1000)],
    "product_id": [random.randint(1, 50) for _ in range(1000)],
    "quantity": [random.randint(1, 5) for _ in range(1000)],
    "order_date": [str(fake.date_between(
        start_date="-1y", end_date="today"))
        for _ in range(1000)],
    "status": [random.choice(["delivered","pending",
               "cancelled","returned"]) for _ in range(1000)],
    "payment_method": [random.choice(["UPI","Card",
                       "COD","Netbanking"]) for _ in range(1000)]
})

price_map = dict(zip(products.product_id, products.price))
orders["revenue"] = orders.apply(
    lambda r: round(r["quantity"] * price_map[r["product_id"]], 2),
    axis=1
)

customers.to_sql("customers", engine, if_exists="replace", index=False)
products.to_sql("products", engine, if_exists="replace", index=False)
orders.to_sql("orders", engine, if_exists="replace", index=False)

print("Seeded successfully!")
print(f"Customers: {len(customers)} | Products: {len(products)} | Orders: {len(orders)}")