import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Price Tracker Dashboard", layout="wide")
st.title("🏷️ Web Price Tracker Dashboard")

# Sidebar - Add Product
st.sidebar.header("Add New Product")
title = st.sidebar.text_input("Product Title")
url = st.sidebar.text_input("Product URL")
selector = st.sidebar.text_input("CSS Selector", value="p.price_color")

if st.sidebar.button("Track Product"):
    if title and url and selector:
        payload = {"title": title, "url": url, "target_price_selector": selector}
        res = requests.post(f"{API_BASE_URL}/products/", json=payload)
        if res.status_code == 201:
            st.sidebar.success(f"Started tracking '{title}'!")
            st.rerun()
        else:
            st.sidebar.error("Failed to add product.")
    else:
        st.sidebar.warning("Please fill out all fields.")

# Main View - Select Product
st.header("Product Price History")

try:
    # Fetch all tracked products
    products_res = requests.get(f"{API_BASE_URL}/products/")
    if products_res.status_code == 200:
        products = products_res.json()
        
        if products:
            # Dropdown menu containing all products
            product_options = {f"{p['title']} (ID: {p['id']})": p['id'] for p in products}
            selected_label = st.selectbox("Select Product to Inspect", list(product_options.keys()))
            selected_id = product_options[selected_label]

            # Action Buttons
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("🔄 Trigger Scrape Now"):
                    scrape_res = requests.post(f"{API_BASE_URL}/products/{selected_id}/scrape")
                    if scrape_res.status_code == 200:
                        st.success("Scrape initiated! Wait 5 seconds and refresh.")
                    else:
                        st.error("Error triggering scrape.")

            # Load History for Selected Product
            history_res = requests.get(f"{API_BASE_URL}/products/{selected_id}/history")
            if history_res.status_code == 200:
                data = history_res.json()
                if data:
                    df = pd.DataFrame(data)
                    df["timestamp"] = pd.to_datetime(df["timestamp"])

                    with col2:
                        csv_data = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Export Price Logs (CSV)",
                            data=csv_data,
                            file_name=f"product_{selected_id}_history.csv",
                            mime="text/csv"
                        )

                    # Price History Chart
                    fig = px.line(
                        df, 
                        x="timestamp", 
                        y="price", 
                        markers=True, 
                        title=f"Price Trend: {selected_label}"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    st.subheader("Price Logs Table")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No price history recorded for this product yet.")
        else:
            st.info("No products currently tracked. Add one using the sidebar!")
    else:
        st.error("Unable to load product list from server.")

except Exception as e:
    st.error(f"Cannot connect to server at {API_BASE_URL}. Ensure uvicorn is running.")