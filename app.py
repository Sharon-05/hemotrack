import streamlit as st
import pandas as pd
from datetime import datetime
import math

# Page config
st.set_page_config(
    page_title="HEMOTRACK - Real-Time Blood Availability in Kerala",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Enhanced Beautiful Design
st.markdown("""
    <style>
    /* Main Colors */
    :root {
        --primary: #c0392b;
        --primary-light: #e74c3c;
        --success: #27ae60;
        --warning: #f39c12;
        --danger: #e74c3c;
        --info: #3498db;
        --light: #ecf0f1;
        --dark: #2c3e50;
    }
    
    /* Typography */
    h1, h2, h3 { color: var(--dark); font-weight: 700; }
    
    /* Header Section */
    .header-section {
        background: linear-gradient(135deg, #c0392b 0%, #e74c3c 100%);
        padding: 50px 30px;
        border-radius: 15px;
        color: white;
        margin-bottom: 40px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(192, 57, 43, 0.2);
    }
    
    .header-section h1 { 
        margin: 0; 
        font-size: 3rem; 
        font-weight: 800;
        letter-spacing: -1px;
    }
    
    .header-section p { 
        margin: 15px 0 0 0; 
        font-size: 1.2rem; 
        opacity: 0.95;
        font-weight: 300;
    }
    
    .header-stats {
        display: flex;
        justify-content: space-around;
        margin-top: 30px;
        gap: 20px;
    }
    
    .stat-box {
        background: rgba(255, 255, 255, 0.15);
        padding: 15px 25px;
        border-radius: 10px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .stat-box-num { font-size: 2.5rem; font-weight: 800; }
    .stat-box-label { font-size: 0.9rem; opacity: 0.8; margin-top: 5px; }
    
    /* Filter Section */
    .filter-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 30px;
        border-radius: 12px;
        margin-bottom: 30px;
        border: 1px solid #dee2e6;
    }
    
    /* Hospital Card */
    .hospital-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .hospital-card:hover {
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        transform: translateY(-2px);
        border-color: #c0392b;
    }
    
    .hospital-header {
        display: flex;
        justify-content: space-between;
        align-items: start;
        margin-bottom: 20px;
        border-bottom: 2px solid #f0f0f0;
        padding-bottom: 15px;
    }
    
    .hospital-name {
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--dark);
        margin: 0;
    }
    
    .hospital-location {
        font-size: 0.95rem;
        color: #7f8c8d;
        margin-top: 5px;
    }
    
    /* Status Badge */
    .status-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .status-available {
        background: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .status-low {
        background: #fff3cd;
        color: #856404;
        border: 1px solid #ffeaa7;
    }
    
    .status-out {
        background: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    
    .status-not-verified {
        background: #e2e3e5;
        color: #383d41;
        border: 1px solid #d6d8db;
    }
    
    /* Info Grid */
    .info-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 15px;
        margin: 20px 0;
    }
    
    .info-item {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #c0392b;
    }
    
    .info-item-label {
        font-size: 0.8rem;
        color: #7f8c8d;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    
    .info-item-value {
        font-size: 1.2rem;
        font-weight: 700;
        color: var(--dark);
    }
    
    /* Progress Bar */
    .progress-bar {
        width: 100%;
        height: 8px;
        background: #e0e0e0;
        border-radius: 4px;
        overflow: hidden;
        margin-top: 8px;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #27ae60 0%, #2ecc71 100%);
        border-radius: 4px;
        transition: width 0.3s ease;
    }
    
    /* Action Buttons */
    .action-buttons {
        display: flex;
        gap: 10px;
        margin-top: 20px;
        flex-wrap: wrap;
    }
    
    .btn-primary {
        background: linear-gradient(135deg, #c0392b 0%, #e74c3c 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
        border: none;
        cursor: pointer;
        transition: all 0.3s;
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
    
    .btn-primary:hover {
        box-shadow: 0 4px 12px rgba(192, 57, 43, 0.3);
        transform: translateY(-2px);
    }
    
    .btn-secondary {
        background: white;
        color: var(--dark);
        padding: 10px 20px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
        border: 2px solid #c0392b;
        cursor: pointer;
        transition: all 0.3s;
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
    
    .btn-secondary:hover {
        background: #f5f5f5;
    }
    
    /* Stats Section */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-bottom: 30px;
    }
    
    .stat-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #c0392b;
    }
    
    .stat-card h3 { margin: 0 0 10px 0; color: #7f8c8d; font-size: 0.9rem; }
    .stat-card .number { font-size: 2.5rem; font-weight: 800; color: #c0392b; }
    
    /* Demo Badge */
    .demo-badge {
        display: inline-block;
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(52, 152, 219, 0.3);
    }
    
    /* Blood Component Breakdown */
    .component-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 12px;
        margin: 15px 0;
    }
    
    .component-item {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 12px;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #dee2e6;
    }
    
    .component-name { font-size: 0.85rem; color: #7f8c8d; margin-bottom: 5px; }
    .component-units { font-size: 1.4rem; font-weight: 700; color: #c0392b; }
    
    /* Footer */
    .footer-section {
        background: #2c3e50;
        color: white;
        padding: 30px;
        border-radius: 10px;
        margin-top: 40px;
        text-align: center;
    }
    
    .footer-section p { margin: 5px 0; opacity: 0.8; }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .hospital-card {
        animation: fadeIn 0.3s ease-out;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .header-section h1 { font-size: 2rem; }
        .header-stats { flex-direction: column; }
        .info-grid { grid-template-columns: 1fr 1fr; }
    }
    </style>
""", unsafe_allow_html=True)

# Import data
from data_demo import BLOOD_BANKS, BLOOD_STOCK, KERALA_DISTRICTS, BLOOD_GROUPS, BLOOD_COMPONENTS

# Initialize session state
if "search_triggered" not in st.session_state:
    st.session_state.search_triggered = False
if "selected_hospital" not in st.session_state:
    st.session_state.selected_hospital = None

# ===== HEADER SECTION =====
st.markdown("""
    <div class="header-section">
        <h1>🩸 HEMOTRACK</h1>
        <p>Real-Time Blood Availability in Kerala</p>
        <div class="header-stats">
            <div class="stat-box">
                <div class="stat-box-num">15</div>
                <div class="stat-box-label">Blood Banks (Ernakulam)</div>
            </div>
            <div class="stat-box">
                <div class="stat-box-num">8</div>
                <div class="stat-box-label">Blood Groups</div>
            </div>
            <div class="stat-box">
                <div class="stat-box-num">4</div>
                <div class="stat-box-label">Components</div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown('<div class="demo-badge">⚠️ DEMO MODE — Sample data for testing. Always confirm availability before visiting.</div>', unsafe_allow_html=True)

# ===== FILTER SECTION =====
st.markdown('<div class="filter-section">', unsafe_allow_html=True)
st.markdown("## 🔍 Search Blood Availability")

col1, col2, col3, col4 = st.columns(4, gap="medium")

with col1:
    state = st.selectbox("🗺️ State", ["Kerala"], disabled=True, label_visibility="collapsed")

with col2:
    district = st.selectbox(
        "📍 District",
        ["Select District..."] + KERALA_DISTRICTS,
        label_visibility="collapsed",
        index=0
    )

with col3:
    blood_group = st.selectbox(
        "🩸 Blood Group",
        ["Select Blood Group..."] + BLOOD_GROUPS[1:],
        label_visibility="collapsed",
        index=0
    )

with col4:
    component = st.selectbox(
        "🧪 Component",
        ["Select Component..."] + BLOOD_COMPONENTS[1:],
        label_visibility="collapsed",
        index=0
    )

# Search and Reset buttons
col_search1, col_search2, col_search3 = st.columns([2, 1, 1], gap="small")
with col_search1:
    if st.button("🔎 Search Blood Availability", use_container_width=True, type="primary"):
        st.session_state.search_triggered = True
with col_search2:
    if st.button("🔄 Reset", use_container_width=True):
        st.session_state.search_triggered = False
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ===== RESULTS SECTION =====
if st.session_state.search_triggered:
    if district == "Select District..." or blood_group == "Select Blood Group..." or component == "Select Component...":
        st.error("❌ Please complete all selections to search")
        st.info("💡 Select District, Blood Group, and Blood Component")
    else:
        # Merge and filter data
        merged_data = BLOOD_STOCK.merge(BLOOD_BANKS, left_on="hospital_id", right_on="id", how="inner")
        filtered_stock = merged_data[
            (merged_data["district"] == district) &
            (merged_data["blood_group"] == blood_group) &
            (merged_data["component"] == component)
        ]
        
        if filtered_stock.empty:
            col1, col2 = st.columns([1, 1])
            with col1:
                st.warning(f"❌ No {blood_group} {component} available in {district}")
            with col2:
                st.info("💡 Try a different district or blood component")
        else:
            # Stats Section
            hospital_ids = filtered_stock["hospital_id"].unique()
            available_count = len(filtered_stock[filtered_stock["units_available"] > 0])
            
            st.markdown(f"### 📊 Results: {blood_group} • {component} • {district}")
            
            stat_col1, stat_col2, stat_col3 = st.columns(3)
            with stat_col1:
                st.markdown(f'<div class="stat-card"><h3>Hospitals</h3><div class="number">{len(hospital_ids)}</div></div>', unsafe_allow_html=True)
            with stat_col2:
                st.markdown(f'<div class="stat-card"><h3>In Stock</h3><div class="number">{available_count}</div></div>', unsafe_allow_html=True)
            with stat_col3:
                total_units = filtered_stock["units_available"].sum()
                st.markdown(f'<div class="stat-card"><h3>Total Units</h3><div class="number">{total_units}</div></div>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Display each hospital with enhanced design
            for idx, (_, stock_row) in enumerate(filtered_stock.sort_values("units_available", ascending=False).iterrows()):
                hospital_id = stock_row["hospital_id"]
                units = int(stock_row["units_available"])
                max_units = 30  # For progress bar
                
                hospital = {
                    "name": stock_row["name"],
                    "address": stock_row["address"],
                    "district": stock_row["district"],
                    "phone": stock_row["phone"],
                    "google_maps_link": stock_row["google_maps_link"]
                }
                
                # Determine status
                if stock_row["verification_status"] == "not_verified":
                    status_html = '🔲 Not Verified'
                    status_class = 'status-not-verified'
                    units_display = "—"
                    progress_pct = 0
                elif units == 0:
                    status_html = '❌ Out of Stock'
                    status_class = 'status-out'
                    units_display = "0 units"
                    progress_pct = 0
                elif units < 5:
                    status_html = '⚠️ Low Stock'
                    status_class = 'status-low'
                    units_display = f"{units} units"
                    progress_pct = (units / max_units) * 100
                else:
                    status_html = '✅ Available'
                    status_class = 'status-available'
                    units_display = f"{units} units"
                    progress_pct = min((units / max_units) * 100, 100)
                
                # Build HTML string carefully
                hospital_name_html = hospital['name']
                hospital_addr_html = hospital['address']
                blood_group_html = stock_row['blood_group']
                component_html = stock_row['component'][:12]
                expiry_html = stock_row['expiry_date'][:10]
                updated_html = stock_row['update_time'][:10]
                source_html = stock_row['source']
                
                # Enhanced Hospital Card
                card_html = f"""
                <div class="hospital-card">
                    <div class="hospital-header">
                        <div>
                            <h2 class="hospital-name">{hospital_name_html}</h2>
                            <p class="hospital-location">📍 {hospital_addr_html}</p>
                        </div>
                        <div><span class="status-badge {status_class}">{status_html}</span></div>
                    </div>
                    
                    <div class="info-grid">
                        <div class="info-item">
                            <div class="info-item-label">Stock Level</div>
                            <div class="info-item-value">{units_display}</div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {progress_pct}%;"></div>
                            </div>
                        </div>
                        <div class="info-item">
                            <div class="info-item-label">Blood Group</div>
                            <div class="info-item-value">{blood_group_html}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-item-label">Component</div>
                            <div class="info-item-value">{component_html}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-item-label">Expiry Date</div>
                            <div class="info-item-value">{expiry_html}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-item-label">Last Updated</div>
                            <div class="info-item-value">{updated_html}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-item-label">Data Source</div>
                            <div class="info-item-value">{source_html}</div>
                        </div>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
                
                # Action buttons
                col_contact, col_maps, col_info = st.columns([1.5, 1.5, 1.5], gap="small")
                
                with col_contact:
                    st.markdown(f"""
                    <a href="tel:{hospital['phone'].replace('+91-', '').replace('-', '')}" class="btn-primary">
                        ☎️ Call Now
                    </a>
                    """, unsafe_allow_html=True)
                
                with col_maps:
                    st.markdown(f"""
                    <a href="{hospital['google_maps_link']}" target="_blank" class="btn-secondary">
                        📍 Get Directions
                    </a>
                    """, unsafe_allow_html=True)
                
                with col_info:
                    if st.button(f"ℹ️ Details", key=f"info_{hospital_id}_{idx}"):
                        with st.expander("Hospital Information", expanded=True):
                            st.write(f"""
                            **Hospital Name:** {hospital['name']}  
                            **Address:** {hospital['address']}  
                            **Phone:** {hospital['phone']}  
                            **Verification:** {stock_row['verification_status'].replace('_', ' ').title()}  
                            **Last Verified:** {stock_row['update_time'][:10]}  
                            **Data Source:** {stock_row['source']}
                            """)
                
                st.markdown("---")

# ===== FOOTER SECTION =====
st.markdown("""
    <div class="footer-section">
        <h3>🩸 HEMOTRACK - Blood Bank Finder</h3>
        <p><strong>Data Source:</strong> eRaktKosh (Demo Mode)</p>
        <p><strong>Coverage:</strong> Kerala - Currently Ernakulam (15 hospitals)</p>
        <p><strong>⚠️ Important Disclaimer:</strong></p>
        <p style="font-size: 0.9rem; margin: 10px 0;">
            This is a <strong>DEMO application</strong> for testing and demonstration purposes only.  
            Always confirm blood availability <strong>directly with the blood bank</strong> by calling them before visiting.  
            Stock levels may change throughout the day. Arriving at a blood bank without confirmation may result in disappointment.
        </p>
        <p style="margin-top: 20px; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 15px;">
            Built with ❤️ using Streamlit | Data: eRaktKosh Portal  
            <br><small>© 2026 HEMOTRACK. In partnership with Government of India - Blood Bank Directory</small>
        </p>
    </div>
""", unsafe_allow_html=True)
