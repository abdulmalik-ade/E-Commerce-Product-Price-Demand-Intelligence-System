from fastapi import FastAPI, HTTPException
import sqlite3
import pandas as pd

app = FastAPI(
    title="Price Intelligence API",
    description="REST API for serving product price trends, forecasting baselines, and buying recommendations.",
    version="1.0.0"
)

DB_PATH = "ecommerce_price_intelligence.db"

@app.get("/")
def read_root():
    return {"status": "online", "message": "Welcome to the Price & Demand Intelligence API Service!"}

@app.get("/products/{product_id}/recommendation")
def get_product_recommendation(product_id: int):
    """
    Returns real-time analytics and buying recommendations for a specific product ID.
    """
    conn = sqlite3.connect(DB_PATH)

    # Retrieve history for this product
    query = """
        SELECT p.product_id, p.product_name, p.category,
               h.price, h.rating, h.review_count, h.collected_at
        FROM price_history h
        JOIN products p ON h.product_id = p.product_id
        WHERE p.product_id = ?
        ORDER BY h.collected_at ASC
    """
    df = pd.read_sql_query(query, conn, params=(product_id,))
    conn.close()

    if df.empty:
        raise HTTPException(status_code=404, detail=f"Product ID {product_id} not found in historical logs.")

    # Compute current metrics & historical averages
    latest_entry = df.iloc[-1]
    current_price = float(latest_entry["price"])
    historical_average = float(df["price"].mean())

    # Determine buying recommendation status
    pct_diff = ((current_price - historical_average) / historical_average) * 100 if historical_average > 0 else 0.0

    if pct_diff < -5.0:
        recommendation = "BUY NOW"
        explanation = f"Current price (${current_price:.2f}) is significantly lower than the historical average (${historical_average:.2f})."
    elif pct_diff > 5.0:
        recommendation = "WAIT"
        explanation = f"Current price (${current_price:.2f}) is inflated compared to the historical average (${historical_average:.2f})."
    else:
        recommendation = "PRICE IS NORMAL"
        explanation = f"Price (${current_price:.2f}) is stable and aligns with the historical average of ${historical_average:.2f}."

    return {
        "product_id": product_id,
        "product_name": latest_entry["product_name"],
        "category": latest_entry["category"],
        "price_metrics": {
            "current_price": current_price,
            "historical_average": historical_average,
            "percentage_difference": round(pct_diff, 2)
        },
        "demand_signals": {
            "rating": float(latest_entry["rating"]),
            "review_count": int(latest_entry["review_count"])
        },
        "decision_engine": {
            "recommendation": recommendation,
            "explanation": explanation
        }
    }
