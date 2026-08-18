import streamlit as st
from database import init_db, get_all_products, add_product

# Initialize database schema on startup
try:
    init_db()
except Exception as e:
    st.error(f"Database initialization failed: {e}")

st.title("🏷️ Web Price Tracker Dashboard")
st.subheader("Product Price History")

# Load and display products
try:
    products = get_all_products()
    if not products:
        st.info("No products tracked yet. Add one from the sidebar!")
    else:
        for product in products:
            st.write(f"**{product.title}** - {product.url}")
except Exception as e:
    st.error(f"Error fetching products: {e}")