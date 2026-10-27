import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

DB_PATH = "ecommerce_price_intelligence.db"

st.set_page_config(page_title="E-Commerce Price Intelligence", layout="wide")

# Dynamic Database Loading
def load_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        query = """
            SELECT p.product_id, p.product_name, p.category,
                   h.price, h.rating, h.review_count, h.availability, h.collected_at
            FROM price_history h
            JOIN products p ON h.product_id = p.product_id
            ORDER BY h.collected_at ASC
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Database connection issue: {e}")
        return pd.DataFrame()

df_dash = load_data()

if df_dash.empty:
    st.warning("⚠️ No data found in the SQLite database. Please run the data collector first!")
else:
    # Define helper variables
    unique_categories = sorted(df_dash["category"].unique())
    all_products = sorted(df_dash["product_name"].unique())

    # =========================================================================
    # SIDEBAR
    # =========================================================================
    st.sidebar.title("Navigation & Filters")
    st.sidebar.markdown("Manage active filters, database parameters, and ingestion runtimes.")

    selected_cat_filter = st.sidebar.selectbox("Category Filter", ["All Categories"] + unique_categories)
    price_min, price_max = float(df_dash["price"].min()), float(df_dash["price"].max())
    selected_price_range = st.sidebar.slider("Price Range ($)", price_min, price_max, (price_min, price_max))
    selected_min_rating = st.sidebar.slider("Minimum Rating", 0.0, 5.0, 0.0, step=0.1)

    st.sidebar.markdown("--- ")
    st.sidebar.markdown("### About App")
    st.sidebar.write("This production-grade intelligence dashboard tracks live product catalogs, models dynamic statistical anomalies, and highlights buying recommendations.")
    st.sidebar.caption("Developer Workspace | Portfolio Build")
    st.sidebar.caption("About Developer | Abdulmalik Tajudeen (CodeCipherHQ)")

    # Apply sidebar filters to global dataset for overall metrics
    filtered_df = df_dash.copy()
    if selected_cat_filter != "All Categories":
        filtered_df = filtered_df[filtered_df["category"] == selected_cat_filter]
    filtered_df = filtered_df[
        (filtered_df["price"] >= selected_price_range[0]) &
        (filtered_df["price"] <= selected_price_range[1]) &
        (filtered_df["rating"] >= selected_min_rating)
    ]

    # =========================================================================
    # HEADER
    # =========================================================================
    st.markdown("## 🛒 E-Commerce Price Intelligence Platform")
    st.markdown("*Monitor active items, isolate volatility anomalies, and generate data-supported purchasing recommendations.*")

    # Dynamic Database-Driven KPI Cards
    total_tracked = len(df_dash["product_id"].unique())
    total_cats = len(unique_categories)
    avg_price = df_dash["price"].mean()
    min_price_val = df_dash["price"].min()
    max_price_val = df_dash["price"].max()
    avg_rating_val = df_dash["rating"].mean()

    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)
    kpi_col1.metric("Products Tracked", f"{total_tracked}")
    kpi_col2.metric("Categories", f"{total_cats}")
    kpi_col3.metric("Avg Price", f"${avg_price:.2f}")
    kpi_col4.metric("Lowest Price", f"${min_price_val:.2f}")
    kpi_col5.metric("Highest Price", f"${max_price_val:.2f}")
    kpi_col6.metric("Avg Rating", f"{avg_rating_val:.2f}/5★")

    st.markdown("--- ")

    # Create tabs for structured discovery
    tab_overview, tab_product, tab_comparator = st.tabs([
        "📊 Global Catalog Overview", 
        "🔍 Deep Product Intelligence", 
        "🔄 Product Comparison Engine"
    ])

    # =========================================================================
    # TAB 1: CATALOG OVERVIEW
    # =========================================================================
    with tab_overview:
        st.subheader("📈 Market-Wide Pricing & Sentiment Distributions")
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            # Price Distribution Histogram
            fig_hist = px.histogram(
                filtered_df, x="price", nbins=15, 
                title="Distribution of Screened Product Prices",
                color_discrete_sequence=["#1f77b4"],
                labels={"price": "Price ($)"}
            )
            fig_hist.update_layout(showlegend=False, margin=dict(t=40, b=40, l=40, r=40))
            st.plotly_chart(fig_hist, use_container_width=True)
            
        with col_chart2:
            # Average price by category
            cat_agg = filtered_df.groupby("category")["price"].mean().reset_index().sort_values("price")
            fig_bar_cat = px.bar(
                cat_agg, x="category", y="price",
                title="Average Unit Price by E-Commerce Category",
                color="price", color_continuous_scale="Blues",
                labels={"price": "Avg Price ($)", "category": "Category"}
            )
            fig_bar_cat.update_layout(margin=dict(t=40, b=40, l=40, r=40))
            st.plotly_chart(fig_bar_cat, use_container_width=True)

        st.markdown("--- ")
        col_table1, col_table2 = st.columns([2, 1])
        
        with col_table1:
            st.markdown("#### 🏷️ Active Screened Catalog Inventory")
            st.dataframe(filtered_df[["product_id", "product_name", "category", "price", "rating", "availability"]].reset_index(drop=True), use_container_width=True)
            
        with col_table2:
            st.markdown("#### 🌟 Elite Rated Products")
            top_rated = filtered_df.sort_values("rating", ascending=False).head(5)
            st.dataframe(top_rated[["product_name", "rating", "price"]].reset_index(drop=True), use_container_width=True)

    # =========================================================================
    # TAB 2: PRODUCT ANALYSIS
    # =========================================================================
    with tab_product:
        col_sel1, col_sel2 = st.columns([1, 2])
        with col_sel1:
            product_cat_select = st.selectbox("Filter Product Category List", ["All"] + unique_categories)
        with col_sel2:
            available_prod_names = sorted(df_dash[df_dash["category"] == product_cat_select]["product_name"].unique()) if product_cat_select != "All" else all_products
            target_product = st.selectbox("Choose Target Product", available_prod_names)

        if target_product:
            prod_series = df_dash[df_dash["product_name"] == target_product].sort_values("collected_at")
            latest_record = prod_series.iloc[-1]
            
            # Retrieve category-wide comparative values
            item_category = latest_record["category"]
            category_avg = df_dash[df_dash["category"] == item_category]["price"].mean()

            # Price calculations
            curr_price = latest_record["price"]
            hist_mean = prod_series["price"].mean()
            hist_min = prod_series["price"].min()
            hist_max = prod_series["price"].max()
            pct_from_hist = ((curr_price - hist_mean) / hist_mean * 100) if hist_mean > 0 else 0.0
            pct_from_cat = ((curr_price - category_avg) / category_avg * 100) if category_avg > 0 else 0.0

            # Dynamic Heuristic Buying Recommendation Logic
            # Score items objectively based on standard deviation margins, category context and product health
            score = 0
            evidence = []

            # Dimension 1: Historical Mean comparisons
            if pct_from_hist < -5.0:
                score += 2
                evidence.append(f"✓ Currently priced {abs(pct_from_hist):.1f}% below its historical average.")
            elif pct_from_hist > 5.0:
                score -= 2
                evidence.append(f"❌ Current price is inflated {pct_from_hist:.1f}% above historical benchmark.")
            else:
                score += 0
                evidence.append(f"ℹ️ Price matches normal historic bands (offset of {pct_from_hist:+.1f}%).")

            # Dimension 2: Category Average comparisons
            if pct_from_cat < -10.0:
                score += 2
                evidence.append(f"✓ Competitively positioned: {abs(pct_from_cat):.1f}% below category average (${category_avg:.2f}).")
            elif pct_from_cat > 10.0:
                score -= 1
                evidence.append(f"⚠️ Premium-level asset pricing: {pct_from_cat:.1f}% above category average.")
            else:
                evidence.append(f"✓ Fairly aligned with category standards (offset of {pct_from_cat:+.1f}%).")

            # Dimension 3: Quality rating signals
            if latest_record["rating"] >= 4.0:
                score += 1
                evidence.append(f"✓ High consumer confidence index: Rating is {latest_record['rating']:.2f}/5.")
            elif latest_record["rating"] < 3.0:
                score -= 1
                evidence.append(f"⚠️ Low ratings indicator ({latest_record['rating']:.2f}/5). risk element.")

            # Dimension 4: Availability context
            if latest_record["availability"].lower() == "in stock":
                evidence.append("✓ Physical stock immediately available to fulfill.")
            else:
                score -= 1
                evidence.append(f"⚠️ Stock issues indicated: Current status '{latest_record['availability']}'.")

            # Assign decisions based on score sum
            if score >= 3:
                rec_status = "BUY NOW"
                rec_style = "background-color: #d4edda; color: #155724; padding: 10px; border-radius: 5px; font-weight: bold; text-align: center; font-size: 24px;"
                rec_summary = f"Excellent buying signal. The item is significantly undervalued against both categorical and individual baselines with highly stable product quality reviews."
            elif score <= -2:
                rec_status = "WAIT"
                rec_style = "background-color: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; font-weight: bold; text-align: center; font-size: 24px;"
                rec_summary = f"We advise waiting. The asset exhibits an elevated premium price, making immediate purchase less cost-effective."
            elif score >= 1:
                rec_status = "GOOD PRICE"
                rec_style = "background-color: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; font-weight: bold; text-align: center; font-size: 24px;"
                rec_summary = "Attractive pricing metrics detected. Not an absolute historical low, but highly competitive compared with typical market alternatives."
            else:
                rec_status = "PRICE IS NORMAL"
                rec_style = "background-color: #e2e3e5; color: #383d41; padding: 10px; border-radius: 5px; font-weight: bold; text-align: center; font-size: 24px;"
                rec_summary = "The product's price remains within normal statistical thresholds. No anomalies or exceptional buying opportunities detected."

            # Display Product Details Card & KPIs
            st.markdown(f"### 📝 Insights Summary: {target_product}")
            
            det1, det2, det3, det4 = st.columns(4)
            det1.metric("Selected Price", f"${curr_price:.2f}")
            det2.metric("Historical Average", f"${hist_mean:.2f}")
            det3.metric("Category Avg Offset", f"{pct_from_cat:+.2f}%")
            det4.metric("Product Rating", f"{latest_record['rating']:.2f}/5★")

            col_rec1, col_rec2 = st.columns([1, 1])
            with col_rec1:
                st.markdown("#### Recommendation Outcome")
                st.markdown(f"<div style='{rec_style}'>{rec_status}</div>", unsafe_allow_html=True)
                st.write(f"*Explanation:* {rec_summary}")

                # Price Position Horizontal Visualization slider
                st.markdown("#### Price Position within Historical Records")
                if hist_max != hist_min:
                    pct_pos = (curr_price - hist_min) / (hist_max - hist_min)
                else:
                    pct_pos = 0.5
                
                slider_width = 20
                dot_idx = int(pct_pos * (slider_width - 1))
                dot_idx = max(0, min(slider_width - 1, dot_idx))
                
                slider_chars = ["-"] * slider_width
                slider_chars[dot_idx] = "●"
                slider_line = "".join(slider_chars)
                
                st.text(f"Historical Low (${hist_min:.2f})  |{slider_line}|  Historical High (${hist_max:.2f})")
                st.caption(f"Current Price: ${curr_price:.2f} (Positioned {pct_pos*100:.1f}% along historical spectrum)")

            with col_rec2:
                st.markdown("#### Why this recommendation?")
                for item_bullet in evidence:
                    st.markdown(item_bullet)

            # Historical Plotting with boundary rules
            st.markdown("--- ")
            st.subheader("📊 Historical Pricing Profile & Volatility Boundaries")
            
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=prod_series["collected_at"], y=prod_series["price"],
                mode='lines+markers', name='Actual Price',
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=8)
            ))
            fig_line.add_trace(go.Scatter(
                x=prod_series["collected_at"], y=[hist_mean]*len(prod_series),
                mode='lines', name='Historical Mean', 
                line=dict(color='rgba(255, 127, 14, 0.8)', dash='dash')
            ))
            fig_line.add_trace(go.Scatter(
                x=prod_series["collected_at"], y=[hist_min]*len(prod_series),
                mode='lines', name='Historical Low',
                line=dict(color='rgba(44, 160, 44, 0.5)', dash='dot')
            ))
            fig_line.add_trace(go.Scatter(
                x=prod_series["collected_at"], y=[hist_max]*len(prod_series),
                mode='lines', name='Historical High',
                line=dict(color='rgba(214, 39, 40, 0.5)', dash='dot')
            ))
            
            fig_line.update_layout(
                title=f"Comprehensive Historical Price Spectrum for {target_product}",
                xaxis_title="Observation Timestamps",
                yaxis_title="Price ($)",
                hovermode="x unified",
                margin=dict(t=40, b=40, l=40, r=40)
            )
            st.plotly_chart(fig_line, use_container_width=True)

            # Multi-observation checks warnings 
            if len(prod_series) <= 1:
                st.warning("⚠️ **Historical signal limit:** Only a single observation is available for this product in the local SQLite db. Time-series variance, sliding averages, and forecasting models require additional sequential data-collection runs.")

    # =========================================================================
    # TAB 3: PRODUCT COMPARATOR
    # =========================================================================
    with tab_comparator:
        st.subheader("🔄 Side-by-Side Product Comparison Module")
        st.markdown("Select up to 4 distinct items to analyze pricing differentials and consumer ratings simultaneously.")
        
        selected_comparisons = st.multiselect(
            "Choose Products to Compare", 
            all_products, 
            default=all_products[:2] if len(all_products) >= 2 else all_products
        )

        if len(selected_comparisons) > 0:
            comp_records = []
            for p_name in selected_comparisons:
                p_hist = df_dash[df_dash["product_name"] == p_name].sort_values("collected_at")
                if not p_hist.empty:
                    lat = p_hist.iloc[-1]
                    # Retrieve parent category avg for benchmark comparison
                    p_cat = lat["category"]
                    p_cat_avg = df_dash[df_dash["category"] == p_cat]["price"].mean()
                    offset = ((lat["price"] - p_cat_avg) / p_cat_avg * 100) if p_cat_avg > 0 else 0.0
                    
                    comp_records.append({
                        "Product Name": lat["product_name"],
                        "Price ($)": lat["price"],
                        "Category": lat["category"],
                        "Rating (5★)": lat["rating"],
                        "Category Avg ($)": round(p_cat_avg, 2),
                        "% Diff vs Cat": round(offset, 2),
                        "Availability": lat["availability"]
                    })
            
            df_comp = pd.DataFrame(comp_records)
            st.dataframe(df_comp, use_container_width=True)

            # Comparative Chart Visual
            fig_comp_chart = px.bar(
                df_comp, x="Product Name", y="Price ($)",
                color="Category",
                title="Direct Price Comparison Overview",
                text_auto='.2f'
            )
            st.plotly_chart(fig_comp_chart, use_container_width=True)
        else:
            st.info("Please select at least one product in the dropdown above to display comparative intelligence analytics.")

    # =========================================================================
    # EXPANDABLE DATA QUALITY / FOOTER INFORMATION
    # =========================================================================
    st.markdown("--- ")
    with st.expander("🗃️ System Metadata & Quality Transparency Information"):
        obs_count = len(df_dash)
        last_ts = df_dash["collected_at"].max()
        unique_count_val = len(df_dash["product_id"].unique())
        st.markdown(f"""
        * **Registered Data Source:** `DummyJSON API (Products Endpoint)`
        * **Product Tracked Catalog:** {unique_count_val} distinct entries
        * **Historical Observation Rows:** {obs_count} total rows
        * **Last Refreshed Timestamp:** `{last_ts}`
        * **System Host Status:** Stable operational SQLite relational backend
        
        **Project Implementation Disclosure:** The dataset uses DummyJSON's product collection. Real market histories are mock-simulated on initial runs unless the pipeline executes continuously to compile live chronological records.
        """)
# Push content to the bottom using a divider line
st.markdown("---")

# Create 3 columns (adjust the middle number to make the center wider/narrower)
left_space, center_content, right_space = st.columns([1, 2, 1])

with center_content:
    # Text block centered via layout columns
    st.write("About Developer | Abdulmalik Tajudeen (CodeCipherHQ)")
    
    # Nested columns to cleanly separate the two clickable icon buttons
    link_col1, link_col2 = st.columns(2)
    
    with link_col1:
        # GitHub icon on top, link directly underneath
        st.write("💻")  # Alternatively use "📁" or "🚀"
        st.link_button("GitHub", "https://github.com/abdulmalik-ade")
        
    with link_col2:
        # LinkedIn icon on top, link directly underneath
        st.write("🌐")  # Alternatively use "💼" or "🤝"
        st.link_button("LinkedIn", "https://www.linkedin.com/in/abdulmalik-tajudeen-86602b38b/")

