# 🛒 E-Commerce Product Price & Demand Intelligence System

A production-grade, portfolio-ready Machine Learning and Data Engineering project that ingests real-world product metrics, persists historical transactions, calculates sliding-window statistical features, and provides explainable buying recommendations through a multi-service architecture.

---

## 📐 Architecture Diagram

```text
      [ Real Online API ] (DummyJSON REST Endpoints)
              │
              ▼ (HTTP GET Ingestion Pipeline)
      [ SQLite Database ] (Static Catalog + Historical Ledger)
              │
              ▼ (Pandas Feature Engineering & ML Baseline Model)
     ┌────────┴────────┐
     ▼                 ▼
[ FastAPI Service ]   [ Streamlit Dashboard ]
 (Port: 8000)          (Port: 8501)
```

---

## 🛠️ Key Architectural Highlights
* **Dual-Table SQLite Design:** Splits entities into static `products` and chronological `price_history` to save disk space and eliminate redundancies.
* **Idempotent Ingestion Pipeline:** Outfitted with structural `Composite Unique Constraints` (`product_id` + `collected_at`) ensuring multiple accidental runs never double-write data.
* **Feature Engineering Pipeline:** Computes lag steps (`price_lag_1`), chronological price deltas (`price_diff_1`), and rolling moving statistics.
* **Time-Series Baseline Validator:** Implements forward validation with no lookahead bias, tracking model prediction quality using RMSE and MAE.
* **Explainable Decision Engine:** Provides explicit justification for `BUY NOW`, `WAIT`, and `PRICE IS NORMAL` purchasing alerts.

---

## 🚀 How to Spin Up the System

### Method 1: Local Docker Compose (Recommended)
1. Install [Docker](https://www.docker.com/)
2. In the project folder, run:
   ```bash
   docker-compose up --build
   ```
3. Access the **Streamlit Dashboard** at `http://localhost:8501`
4. Access the **FastAPI Service** at `http://localhost:8000/docs`

### Method 2: Manual Local Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Initialize database and fetch baseline data by executing Python extraction files.
3. Spin up the background microservices:
   ```bash
   uvicorn api:app --reload
   streamlit run app.py
   ```
