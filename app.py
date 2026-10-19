import streamlit as st
import pandas as pd
from datetime import datetime

# Page config
st.set_page_config(
    page_title="HEMOTRACK - Blood Bank Finder",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 2rem; }
    
    .result-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
        background: #f9f9f9;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s;
    }
    
    .result-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        background: #fff;
    }
    
    .status-available { color: #27ae60; font-weight: bold; }
    .status-low { color: #f39c12; font-weight: bold; }
    .status-not-verified { color: #95a5a6; font-weight: bold; }
    
    .demo-badge {
        display: inline-block;
        background: #3498db;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-bottom: 20px;
    }
    
    .header-section {
        background: linear-gradient(135deg, #c0392b 0%, #e74c3c 100%);
        padding: 40px 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 30px;
        text-align: center;
    }
    
    .header-section h1 { margin: 0; font-size: 2.5rem; }
    .header-section p { margin: 10px 0 0 0; font-size: 1.1rem; opacity: 0.95; }
    </style>
""", unsafe_allow_html=True)

# Mock data
from data_demo import BLOOD_BANKS, BLOOD_STOCK, KERALA_DISTRICTS, BLOOD_GROUPS, BLOOD_COMPONENTS

# Initialize session state
if "search_triggered" not in st.session_state:
    st.session_state.search_triggered = False

# Header
st.markdown("""
    <div class="header-section">
        <h1>🩸 HEMOTRACK</h1>
        <p>Real-time Blood Availability Finder for Kerala</p>
    </div>
""", unsafe_allow_html=True)

st.markdown('<div class="demo-badge">⚠️ DEMO MODE — Using sample data for illustration</div>', unsafe_allow_html=True)

# Filters section
st.subheader("🔍 Find Blood Banks")

col1, col2, col3, col4 = st.columns(4, gap="medium")

with col1:
    state = st.selectbox("State", ["Kerala"], label_visibility="collapsed", disabled=True)
    st.caption("🗺️ State")

with col2:
    district = st.selectbox(
        "District",
        ["Select District..."] + KERALA_DISTRICTS,
        label_visibility="collapsed",
        index=0
    )
    st.caption("📍 District")

with col3:
    blood_group = st.selectbox(
        "Blood Group",
        ["Select Blood Group..."] + BLOOD_GROUPS[1:],  # Skip "All Blood Groups"
        label_visibility="collapsed",
        index=0
    )
    st.caption("🩸 Blood Group")

with col4:
    component = st.selectbox(
        "Blood Component",
        ["Select Component..."] + BLOOD_COMPONENTS[1:],  # Skip "All Components"
        label_visibility="collapsed",
        index=0
    )
    st.caption("🧪 Component")

# Search button
search_col1, search_col2, search_col3 = st.columns([1, 1, 2])
with search_col1:
    if st.button("🔎 Search", use_container_width=True, type="primary"):
        st.session_state.search_triggered = True

with search_col2:
    if st.button("🔄 Reset", use_container_width=True):
        st.session_state.search_triggered = False
        st.rerun()

# Display results
if st.session_state.search_triggered:
    # Validate selections
    if district == "Select District..." or blood_group == "Select Blood Group..." or component == "Select Component...":
        st.error("❌ Please select District, Blood Group, and Blood Component to search.")
    else:
        # Merge stock with hospital info, then filter
        merged_data = BLOOD_STOCK.merge(BLOOD_BANKS, left_on="hospital_id", right_on="id", how="inner")
        
        # Filter logic
        filtered_stock = merged_data[
            (merged_data["district"] == district) &
            (merged_data["blood_group"] == blood_group) &
            (merged_data["component"] == component)
        ]
        
        if filtered_stock.empty:
            st.warning(f"❌ No results found for {blood_group}, {component} in {district}.")
            st.info("💡 Try a different district or blood component.")
        else:
            # Get hospital info
            hospital_ids = filtered_stock["hospital_id"].unique()
            
            col_metric1, col_metric2, col_metric3 = st.columns(3)
            with col_metric1:
                st.metric("Hospitals Found", len(hospital_ids))
            with col_metric2:
                available_count = len(filtered_stock[filtered_stock["units_available"] > 0])
                st.metric("Stock Available", available_count)
            with col_metric3:
                st.metric("Last Updated", "Today")
            
            st.divider()
            st.subheader(f"Results: {blood_group} ({component})")
            
            # Display each hospital
            for idx, (_, stock_row) in enumerate(filtered_stock.iterrows()):
                hospital_id = stock_row["hospital_id"]
                # Hospital info is already in stock_row from the merge
                hospital = {
                    "name": stock_row["name"],
                    "address": stock_row["address"],
                    "district": stock_row["district"],
                    "phone": stock_row["phone"],
                    "google_maps_link": stock_row["google_maps_link"]
                }
                
                # Status color
                if stock_row["verification_status"] == "not_verified":
                    status = "🔲 Stock Not Verified"
                    status_class = "status-not-verified"
                    units_display = "—"
                elif stock_row["units_available"] == 0:
                    status = "❌ Out of Stock"
                    status_class = "status-low"
                    units_display = "0"
                elif stock_row["units_available"] < 5:
                    status = "⚠️ Low Stock"
                    status_class = "status-low"
                    units_display = f"{stock_row['units_available']} units"
                else:
                    status = "✅ Available"
                    status_class = "status-available"
                    units_display = f"{stock_row['units_available']} units"
                
                # Card layout
                with st.container(border=True):
                    col_name, col_status = st.columns([3, 1])
                    
                    with col_name:
                        st.markdown(f"### {hospital['name']}")
                        st.caption(f"📍 {hospital['address']} · {hospital['district']}")
                    
                    with col_status:
                        st.markdown(f'<p class="{status_class}">{status}</p>', unsafe_allow_html=True)
                    
                    st.divider()
                    
                    col_detail1, col_detail2, col_detail3, col_detail4 = st.columns(4)
                    
                    with col_detail1:
                        st.metric("Stock", units_display)
                    
                    with col_detail2:
                        st.metric("Expiry", stock_row["expiry_date"][:10])
                    
                    with col_detail3:
                        st.metric("Updated", stock_row["update_time"][:10])
                    
                    with col_detail4:
                        st.metric("Source", stock_row["source"][:15])
                    
                    st.divider()
                    
                    col_action1, col_action2, col_action3, col_action4 = st.columns([1.2, 1, 1, 1], gap="small")
                    
                    with col_action1:
                        st.markdown(f"**📞 {hospital['phone']}**")
                    
                    with col_action2:
                        # Open Maps link
                        st.markdown(
                            f"<a href='{hospital['google_maps_link']}' target='_blank' style='display:inline-block;padding:8px 12px;background-color:#4285F4;color:white;text-decoration:none;border-radius:4px;font-weight:bold;'>📍 Maps</a>",
                            unsafe_allow_html=True
                        )
                    
                    with col_action3:
                        if st.button("ℹ️ Info", key=f"info_{hospital_id}", use_container_width=True):
                            st.write(f"""
                            **Hospital Details**
                            - Type: Blood Bank
                            - Verified: ✅ {stock_row['verification_status'].replace('_', ' ').title()}
                            - Contact: {hospital['phone']}
                            - District: {hospital['district']}
                            """)
                    
                    with col_action4:
                        if st.button("☎️ Call", key=f"call_{hospital_id}", use_container_width=True):
                            st.success(f"Call {hospital['phone']}")

# Footer
st.divider()
st.caption("🔗 **Data Sources:** eRaktKosh (Demo) · **Last Updated:** Today · **Built with:** Streamlit")
st.caption("⚠️ **Disclaimer:** Always confirm availability directly with the blood bank before visiting. This is a demo application.")