import streamlit as st
import streamlit_authenticator as stauth
from database import init_db, add_product, get_user_products

# Initialize Database
init_db()

# User Accounts Setup
names = ['User One', 'User Two']
usernames = ['user1', 'user2']

# Pre-hashed passwords for test accounts ('password123' for user1, 'secret123' for user2)
passwords = [
    '$2b$12$eImiTXuWVxfM37uY4JANjO5E.5R0zZk2yC9qM4oY2f0u3Y4aZ5y6C', 
    '$2b$12$eImiTXuWVxfM37uY4JANjO5E.5R0zZk2yC9qM4oY2f0u3Y4aZ5y6C'
]

credentials = {
    'usernames': {
        usernames[0]: {'name': names[0], 'password': passwords[0]},
        usernames[1]: {'name': names[1], 'password': passwords[1]}
    }
}

authenticator = stauth.Authenticate(
    credentials,
    'price_tracker_cookie',
    'auth_key_12345',
    cookie_expiry_days=30
)

# Render Login Widget
name, authentication_status, username = authenticator.login('main')

if authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')
elif authentication_status:
    authenticator.logout('Logout', 'sidebar')
    st.sidebar.title(f"Welcome {name}!")

    st.title("🏷️ Web Price Tracker Dashboard")

    # Sidebar: Add New Product
    st.sidebar.header("Add New Product")
    product_name = st.sidebar.text_input("Product Name")
    product_url = st.sidebar.text_input("Product URL")
    selector = st.sidebar.text_input("Target Price Selector (CSS)")

    if st.sidebar.button("Add Product"):
        if product_name and product_url and selector:
            add_product(username, product_name, product_url, selector)
            st.sidebar.success("Product added successfully!")
            st.rerun()
        else:
            st.sidebar.warning("Please fill in all fields.")

    # Main Area: Product History for current user
    st.subheader("Your Tracked Products")
    products = get_user_products(username)

    if not products:
        st.info("No products tracked yet. Add one using the sidebar!")
    else:
        for p in products:
            st.write(f"**{p[1]}**")
            st.write(f"Link: {p[2]}")
            st.write(f"Selector: `{p[3]}`")
            st.markdown("---")