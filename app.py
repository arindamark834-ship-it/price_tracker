import streamlit as st
from database import init_db, get_all_products, add_product

# Initialize database schema on startup
try:
    init_db()
except Exception as e:
    st.error(f"Database initialization failed: {e}")

st.title("🏷️ Web Price Tracker Dashboard")
st.subheader("Product Price History")

# --- Sidebar Inputs for Adding Products ---
st.sidebar.header("Add New Product")

with st.sidebar.form("add_product_form"):
    title = st.text_input("Product Name")
    url = st.text_input("Product URL")
    selector = st.text_input("Target Price Selector (CSS)")
    submit_button = st.form_submit_button("Add Product")

    if submit_button:
        if title and url and selector:
            try:
                add_product(title, url, selector)
                st.sidebar.success(f"Successfully added {title}!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Error adding product: {e}")
        else:
            st.sidebar.warning("Please fill in all fields.")

# --- Main Display: Load and display products ---
try:
    products = get_all_products()
    if not products:
        st.info("No products tracked yet. Add one using the sidebar!")
    else:
        for product in products:
            st.write(f"**{product.title}**")
            st.write(f"Link: {product.url}")
            st.write(f"Selector: `{product.target_price_selector}`")
            st.markdown("---")
except Exception as e:
    st.error(f"Error fetching products: {e}")