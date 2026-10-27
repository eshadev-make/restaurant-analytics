import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="Restaurant Performance Analysis Hub",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Data Generator for 5 Branches
@st.cache_data
def generate_data():
    branches = ["starbugs", "Urban Bistro", "Coastal Grill", "Sweet Basil", "The Golden Fork"]
    categories = ["Main Course", "Appetizer", "Beverages", "Dessert"]
    order_types = ["Dine-In", "Delivery"]
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    # Detailed branch metrics over months
    monthly_records = []
    np.random.seed(42)
    for b in branches:
        for m in months:
            monthly_records.append({
                "Branch": b,
                "Month": m,
                "Monthly_Orders": np.random.randint(1100, 3800),
                "Customer_Rating": round(np.random.uniform(3.8, 4.9), 1),
                "Satisfaction_Score": np.random.randint(75, 98),  # CSAT %
                "Cleaning_Hygiene_Score": round(np.random.uniform(4.0, 5.0), 1)
            })
            
    # Transactional data for detailed breakdown
    item_records = []
    items = {
        "Main Course": ["Paneer special Masala", "Pasta ", " Burger"],
        "Appetizer": ["Garlic Bread", "Spring Rolls", "Crispy Corn"],
        "Beverages": ["Cold Coffee", "Fresh Lime Soda", "Iced Tea"],
        "Dessert": ["Sizzling Brownie", "Gulab Jamun", "Cheesecake"]
    }
    
    for b in branches:
        for day in days:
            for cat, item_list in items.items():
                for item in item_list:
                    for ot in order_types:
                        item_records.append({
                            "Branch": b,
                            "Day_of_Week": day,
                            "Category": cat,
                            "Item_Name": item,
                            "Order_Type": ot,
                            "Peak_Hour": np.random.choice(["12 PM - 3 PM (Lunch)", "7 PM - 11 PM (Dinner)", "4 PM - 6 PM (Snack)"]),
                            "Revenue": np.random.randint(5000, 25000),
                            "Quantity_Sold": np.random.randint(40, 200)
                        })

    return pd.DataFrame(monthly_records), pd.DataFrame(item_records)

df_monthly, df_items = generate_data()

# 3. Session State for Navigation
if "selected_branch" not in st.session_state:
    st.session_state.selected_branch = None

# --- SIDEBAR & NAVIGATION ---
st.sidebar.title("🍽️ Navigation")

selected_branch = st.sidebar.selectbox(
    "Select Restaurant Branch:",
    ["All Branches (Home Overview)"] + list(df_monthly["Branch"].unique()),
    index=0 if st.session_state.selected_branch is None else list(df_monthly["Branch"].unique()).index(st.session_state.selected_branch) + 1
)

# Reset or set branch state
if selected_branch == "All Branches (Home Overview)":
    st.session_state.selected_branch = None
else:
    st.session_state.selected_branch = selected_branch


# ==============================================================================
# LANDING PAGE: ALL BRANCHES OVERVIEW
# ==============================================================================
if st.session_state.selected_branch is None:
    st.title("📊 Restaurant Performance Analysis Hub")
    st.markdown("Select a branch below or from the sidebar to view detailed operational graphs.")
    st.divider()

    st.subheader("🏢 Choose a Branch Dashboard")
    
    # 5 Clickable Action Cards for Branches
    cols = st.columns(5)
    branch_list = list(df_monthly["Branch"].unique())
    
    for i, b_name in enumerate(branch_list):
        with cols[i]:
            st.markdown(f"### {b_name}")
            avg_rating = df_monthly[df_monthly["Branch"] == b_name]["Customer_Rating"].mean()
            tot_orders = df_monthly[df_monthly["Branch"] == b_name]["Monthly_Orders"].sum()
            
            st.metric("Avg Rating", f"{avg_rating:.1f} ⭐")
            st.metric("Total Orders", f"{tot_orders:,}")
            
            if st.button(f"View {b_name}", key=f"btn_{i}"):
                st.session_state.selected_branch = b_name
                st.rerun()

    st.divider()
    st.subheader("🌐 Comparative Overview across All Branches")
    
    # Overview chart comparing monthly orders of all branches
    fig_comp = px.line(
        df_monthly, x="Month", y="Monthly_Orders", color="Branch",
        title="Monthly Order Trends Across Branches", markers=True
    )
    st.plotly_chart(fig_comp, use_container_width=True)


# ==============================================================================
# BRANCH DASHBOARD PAGE (Detailed Parameters from Notes)
# ==============================================================================
else:
    branch = st.session_state.selected_branch
    
    # Back Button
    if st.button("⬅️ Back to All Branches"):
        st.session_state.selected_branch = None
        st.rerun()
        
    st.title(f"📌 Branch Performance: {branch}")
    st.markdown("Detailed breakdown of sales, peak hours, customer scores, and hygiene standard.")
    st.divider()

    # Filtered Data
    b_monthly = df_monthly[df_monthly["Branch"] == branch]
    b_items = df_items[df_items["Branch"] == branch]

    # --- TOP ROW: KPI SUMMARY CARDS ---
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Annual Orders", f"{b_monthly['Monthly_Orders'].sum():,}")
    k2.metric("Customer Rating", f"{b_monthly['Customer_Rating'].mean():.1f} / 5.0 ⭐")
    k3.metric("CSAT Score", f"{b_monthly['Satisfaction_Score'].mean():.0f}%")
    k4.metric("Hygiene Score", f"{b_monthly['Cleaning_Hygiene_Score'].mean():.1f} / 5.0 🧼")
    
    total_rev = b_items["Revenue"].sum()
    k5.metric("Total Revenue", f"₹{total_rev:,.0f}")

    st.divider()

    # --- CLICKABLE FILTERS (USER ACTIONS) ---
    st.sidebar.markdown("### 🎛️ Interactive Filters")
    selected_order_type = st.sidebar.multiselect(
        "Filter Order Type:", 
        options=["Dine-In", "Delivery"], 
        default=["Dine-In", "Delivery"]
    )
    
    selected_category = st.sidebar.selectbox(
        "Filter Category for Item Sales:",
        options=["All"] + list(b_items["Category"].unique())
    )

    # Apply Filters to items data
    filtered_items = b_items[b_items["Order_Type"].isin(selected_order_type)]
    if selected_category != "All":
        filtered_items = filtered_items[filtered_items["Category"] == selected_category]

    # --- DETAILED ANALYSIS SECTIONS (FROM HANDWRITTEN NOTES) ---
    
    # TAB LAYOUT FOR ORGANIZED GRAPH PRESENTATION
    tab1, tab2, tab3, tab4 = st.tabs([
        "🍽️ Menu & Revenue", 
        "⏰ Peak Hours & Days", 
        "⭐ Satisfaction & Ratings", 
        "🧹 Cleaning & Hygiene"
    ])

    # ---------------- TAB 1: Menu & Revenue + Delivery vs Dine-in ----------------
    with tab1:
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("1. Top-Selling Menu Items & Category Revenue")
            cat_rev = filtered_items.groupby("Category")["Revenue"].sum().reset_index()
            fig_cat = px.bar(
                cat_rev, x="Category", y="Revenue", color="Category",
                title="Revenue Generation by Category", text_auto=True
            )
            st.plotly_chart(fig_cat, use_container_width=True)

        with c2:
            st.subheader("4. Delivery vs. Dine-in Sales Performance")
            del_vs_dine = filtered_items.groupby("Order_Type")["Revenue"].sum().reset_index()
            fig_pie = px.pie(
                del_vs_dine, names="Order_Type", values="Revenue", hole=0.4,
                title="Revenue Share: Delivery vs Dine-in",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        st.subheader("Top Selling Items List")
        item_sales = filtered_items.groupby(["Item_Name", "Category"])["Revenue"].sum().reset_index().sort_values(by="Revenue", ascending=False)
        fig_items = px.bar(
            item_sales, x="Revenue", y="Item_Name", color="Category", orientation="h",
            title="Revenue by Specific Menu Item"
        )
        st.plotly_chart(fig_items, use_container_width=True)

    # ---------------- TAB 2: Operating Hours & Monthly Orders ----------------
    with tab2:
        c3, c4 = st.columns(2)
        
        with c3:
            st.subheader("2. Busy Days of the Week & Peak Operating Hours")
            day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            day_sales = filtered_items.groupby("Day_of_Week")["Revenue"].sum().reindex(day_order).reset_index()
            fig_days = px.bar(
                day_sales, x="Day_of_Week", y="Revenue",
                title="Total Revenue by Day of Week",
                color_discrete_sequence=["#FF7F0E"]
            )
            st.plotly_chart(fig_days, use_container_width=True)

        with c4:
            st.subheader("5. Monthly Orders Trend")
            fig_monthly_orders = px.line(
                b_monthly, x="Month", y="Monthly_Orders", markers=True,
                title="Monthly Order Volume (Jan - Dec)",
                color_discrete_sequence=["#2CA02C"]
            )
            st.plotly_chart(fig_monthly_orders, use_container_width=True)

        # Peak Hour Heatmap / Distribution
        st.subheader("Peak Operating Hours Breakdown")
        peak_df = filtered_items.groupby(["Peak_Hour", "Order_Type"])["Revenue"].sum().reset_index()
        fig_peak = px.bar(
            peak_df, x="Peak_Hour", y="Revenue", color="Order_Type", barmode="group",
            title="Revenue Distribution by Operating Time Slots"
        )
        st.plotly_chart(fig_peak, use_container_width=True)

    # ---------------- TAB 3: Satisfaction & Ratings ----------------
    with tab3:
        c5, c6 = st.columns(2)
        
        with c5:
            st.subheader("3. Customer Ratings Trend")
            fig_rating = px.line(
                b_monthly, x="Month", y="Customer_Rating", markers=True,
                title="Monthly Average Rating (out of 5.0)",
                color_discrete_sequence=["#D62728"]
            )
            st.plotly_chart(fig_rating, use_container_width=True)

        with c6:
            st.subheader("Customer Satisfaction Score (CSAT %)")
            fig_csat = px.bar(
                b_monthly, x="Month", y="Satisfaction_Score",
                title="Monthly CSAT % Trend",
                color_discrete_sequence=["#9467BD"]
            )
            st.plotly_chart(fig_csat, use_container_width=True)

    # ---------------- TAB 4: Cleaning / Hygiene Score ----------------
    with tab4:
        st.subheader("6. Cleaning / Hygiene Audit Score")
        fig_hygiene = px.area(
            b_monthly, x="Month", y="Cleaning_Hygiene_Score", markers=True,
            title="Monthly Hygiene Audit Score Trend (Scale 1.0 - 5.0)",
            color_discrete_sequence=["#17BECF"]
        )
        fig_hygiene.update_yaxes(range=[3.5, 5.0])
        st.plotly_chart(fig_hygiene, use_container_width=True)