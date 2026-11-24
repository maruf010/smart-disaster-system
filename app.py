import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Import local modules & algorithms
from database import get_connection, init_db
from algorithms.risk_score import calculate_risk
from algorithms.dijkstra import build_graph, shortest_path
from algorithms.resource_allocation import proportional_allocation
from utils.helper import format_datetime

# ==========================================
# 1. PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="SDERMS - Smart Disaster System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern enterprise aesthetic
st.markdown("""
<style>
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 26px;
        font-weight: 700;
        color: #4F46E5;
    }
    .status-badge-critical {
        background-color: #FEE2E2;
        color: #DC2626;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }
    .status-badge-high {
        background-color: #FEF3C7;
        color: #D97706;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }
    .status-badge-moderate {
        background-color: #E0F2FE;
        color: #0284C7;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }
    .status-badge-low {
        background-color: #D1FAE5;
        color: #059669;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }
    .route-box {
        background-color: #F8FAFC;
        border: 1px solid #CBD5E1;
        border-left: 5px solid #10B981;
        padding: 14px 18px;
        border-radius: 8px;
        margin: 10px 0;
        font-size: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Ensure database is initialized
init_db()

# ==========================================
# 2. SIDEBAR NAVIGATION
# ==========================================
st.sidebar.markdown("## 🛡️ **SDERMS**")
st.sidebar.caption("Smart Disaster & Emergency Resource Management System  \n*BUBT Dept. of CSE • SDP-200*")
st.sidebar.divider()

portal_mode = st.sidebar.radio(
    "Select Portal Mode",
    ["👥 Citizen Portal (Public Access)", "🔒 Admin Command Center (Control Room)"],
    index=0
)

# Helper function to query DB as Pandas DataFrame
def query_df(query, params=()):
    conn = get_connection()
    try:
        df = pd.read_sql_query(query, conn, params=params)
        return df
    finally:
        conn.close()

# ==========================================
# 3. CITIZEN PORTAL (PUBLIC USER PANEL)
# ==========================================
if portal_mode.startswith("👥"):
    st.title("🛡️ Citizen Emergency Response Portal")
    st.caption("Public access channel for emergency SOS dispatch, request tracking, shelter lookup, and community volunteer enlisting.")

    # Check for active field advisories
    conn = get_connection()
    active_disaster = conn.execute("SELECT * FROM disasters WHERE status='ACTIVE' ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()

    if active_disaster:
        st.error(f"⚠️ **ACTIVE FIELD ADVISORY:** {active_disaster['name']} ({active_disaster['type']}) reported in **{active_disaster['area']}** with **{active_disaster['severity']}** severity! Please take refuge in designated safe shelters.")
    else:
        st.info("ℹ️ **FIELD STATUS:** No major active disaster alerts reported right now. System operational for public emergency assistance.")

    citizen_tabs = st.tabs([
        "🚨 Send Emergency SOS",
        "📍 Track My Requests",
        "🏕️ Find Safe Shelters",
        "🤝 Join as Volunteer"
    ])

    # ---------- TAB 1: SEND EMERGENCY SOS ----------
    with citizen_tabs[0]:
        st.subheader("Send Emergency SOS Alert")
        st.markdown("If you or people near you are trapped or in danger, fill in this form. The system will compute a dynamic priority score for immediate dispatch.")

        col_form, col_score = st.columns([1.5, 1])

        with col_form:
            with st.form("sos_form", clear_on_submit=False):
                req_name = st.text_input("Your Full Name / Caller Name", placeholder="e.g. Tanvir Ahmed")
                req_phone = st.text_input("Phone Number / Emergency Contact", placeholder="e.g. 01712345678")
                req_loc = st.text_input("Exact Location / Landmark / Node *", placeholder="e.g. Mirpur-2, Road 5, Dhaka")
                req_type = st.selectbox(
                    "Emergency Category",
                    ["Flash Flood Trapped", "Building Collapse / Trapped", "Cyclone Shelter Needed", "Severe Fire / Burn Hazard", "Medical / Critical Injury", "Water / Food Emergency", "Landslide Hazard", "Other Incident"]
                )

                st.markdown("**Incident Details & Vulnerability:**")
                c_aff, c_inj, c_chld = st.columns(3)
                with c_aff:
                    affected_count = st.number_input("Total People Trapped", min_value=1, value=5, step=1)
                with c_inj:
                    injured_count = st.number_input("Injured Count", min_value=0, value=1, step=1)
                with c_chld:
                    child_count = st.number_input("Children / Elderly", min_value=0, value=2, step=1)

                c_chk1, c_chk2 = st.columns(2)
                with c_chk1:
                    is_life = st.checkbox("Immediate Life Threat Risk", value=True)
                with c_chk2:
                    is_shortage = st.checkbox("Critical Supply Shortage", value=False)

                submit_sos = st.form_submit_button("🚨 DISPATCH EMERGENCY SOS NOW", use_container_width=True, type="primary")

                if submit_sos:
                    if not req_loc.strip():
                        st.error("Please provide your current location or landmark.")
                    else:
                        score, level = calculate_risk(is_life, injured_count, child_count, affected_count, is_shortage)
                        full_requester = f"{req_name} ({req_phone})" if req_phone else req_name
                        conn = get_connection()
                        cur = conn.cursor()
                        cur.execute("""
                            INSERT INTO emergency_requests(
                                requester_name, location, emergency_type,
                                people_affected, injured, children_elderly,
                                life_threat, resource_shortage, priority_score, priority_level
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            full_requester, req_loc, req_type,
                            affected_count, injured_count, child_count,
                            int(is_life), int(is_shortage), score, level
                        ))
                        req_id = cur.lastrowid
                        conn.commit()
                        conn.close()

                        st.success(f"✅ Emergency SOS Dispatched Successfully! Ticket ID: **ER-{req_id:04d}** (Assigned Priority: **{level}**, Score: **{score}/100**).")
                        st.balloons()

        with col_score:
            st.markdown("### 📊 Automated Risk Prioritizer")
            st.markdown("Our system calculates incoming emergency urgency using multi-criteria weighted scoring:")
            
            # Interactive formula test
            calc_score, calc_level = calculate_risk(is_life, injured_count, child_count, affected_count, is_shortage)
            
            st.metric("Estimated Risk Rating", f"{calc_score} / 100", f"Level: {calc_level}")
            st.progress(calc_score / 100.0)

            st.markdown("""
            **Priority Classification Guidelines:**
            - 🔴 **CRITICAL (71–100):** Immediate paramedic & boat squad deployment.
            - 🟠 **HIGH (51–70):** Urgent evacuation dispatch.
            - 🔵 **MODERATE (31–50):** Relief distribution queue.
            - 🟢 **LOW (0–30):** Monitored advisory.
            """)

    # ---------- TAB 2: TRACK SOS REQUESTS ----------
    with citizen_tabs[1]:
        st.subheader("My Emergency Requests & Resolution Tracker")
        search_query = st.text_input("🔍 Search tickets by location, caller or emergency type:", "")

        query = "SELECT id, requester_name, location, emergency_type, people_affected, injured, priority_score, priority_level, status, created_at FROM emergency_requests"
        if search_query:
            query += f" WHERE location LIKE '%{search_query}%' OR requester_name LIKE '%{search_query}%' OR emergency_type LIKE '%{search_query}%'"
        query += " ORDER BY id DESC"

        df_reqs = query_df(query)

        if df_reqs.empty:
            st.info("No matching emergency requests recorded.")
        else:
            for _, r in df_reqs.iterrows():
                with st.expander(f"Ticket ER-{r['id']:04d} • {r['emergency_type']} ({r['location']}) — Status: {r['status']}", expanded=(r['status'] == 'PENDING')):
                    c1, c2, c3, c4 = st.columns(4)
                    c1.markdown(f"**Caller:** {r['requester_name'] or 'Anonymous'}")
                    c2.markdown(f"**Location:** {r['location']}")
                    c3.markdown(f"**Casualties:** {r['people_affected']} (Injured: {r['injured']})")
                    c4.markdown(f"**Reported:** {format_datetime(r['created_at'])}")
                    
                    st.markdown(f"**Assigned Priority:** `{r['priority_level']}` (Risk Score: `{r['priority_score']}/100`)")
                    if r['status'] == 'RESOLVED':
                        st.success("● RESCUE ASSISTED / SAFE (Incident Resolved)")
                    else:
                        st.warning("● DISPATCH IN PROGRESS (Rescue Squad Mobilizing)")

    # ---------- TAB 3: FIND SAFE SHELTERS ----------
    with citizen_tabs[2]:
        st.subheader("Nearby Safe Evacuation Shelters")
        st.caption("Live shelter facilities with verified bed capacity, current occupancy, and available room.")

        shelter_filter = st.selectbox("Filter Shelter Availability", ["All Shelters", "Available Only", "Full Only"])

        df_shelters = query_df("SELECT * FROM shelters ORDER BY id ASC")
        if not df_shelters.empty:
            df_shelters["Available"] = df_shelters["capacity"] - df_shelters["occupied"]
            df_shelters["Occupancy_Pct"] = (df_shelters["occupied"] / df_shelters["capacity"]) * 100

            if shelter_filter == "Available Only":
                df_shelters = df_shelters[df_shelters["Available"] > 0]
            elif shelter_filter == "Full Only":
                df_shelters = df_shelters[df_shelters["Available"] <= 0]

            for _, sh in df_shelters.iterrows():
                with st.container():
                    col_info, col_bar = st.columns([2, 1.2])
                    with col_info:
                        st.markdown(f"### 🏕️ {sh['name']}")
                        st.markdown(f"📍 **Location:** {sh['location']}  \n🛏️ **Available Beds:** **{sh['Available']}** free (Total: {sh['capacity']} | Occupied: {sh['occupied']})")
                    with col_bar:
                        st.write(f"Occupancy: **{sh['Occupancy_Pct']:.1f}%**")
                        prog = min(1.0, max(0.0, sh['Occupancy_Pct'] / 100.0))
                        st.progress(prog)
                        if sh['Available'] <= 0:
                            st.error("FULL")
                        elif sh['Occupancy_Pct'] >= 80:
                            st.warning("ALMOST FULL")
                        else:
                            st.success("AVAILABLE")
                    st.divider()

    # ---------- TAB 4: VOLUNTEER REGISTRATION ----------
    with citizen_tabs[3]:
        st.subheader("Join Community Emergency Volunteer Network")
        st.markdown("Civilian volunteers provide invaluable frontline support in packaging relief, first-aid treatment, boat driving, and tech support.")

        with st.form("volunteer_form", clear_on_submit=True):
            v_name = st.text_input("Full Name *", placeholder="e.g. Masud Rana")
            v_phone = st.text_input("Contact Phone Number *", placeholder="e.g. 01812345678")
            v_loc = st.text_input("Current Safe Base / Area *", placeholder="e.g. BUBT Campus, Mirpur, Dhaka")
            v_skill = st.selectbox(
                "Primary Skillset",
                ["First Aid / CPR / Paramedic", "Boat Operator / Rescue Swimming", "Relief Packaging & Warehouse Logistics", "Commercial Driver / Trucker", "Tech & Radio Communications", "Search & Debris Support"]
            )
            v_submit = st.form_submit_button("Enlist as Civilian Volunteer", type="primary")

            if v_submit:
                if not v_name or not v_phone or not v_loc:
                    st.error("Please fill in all required fields.")
                else:
                    conn = get_connection()
                    conn.execute("INSERT INTO volunteers(name, skill, location, contact, availability) VALUES (?, ?, ?, ?, 'YES')", (v_name, v_skill, v_loc, v_phone))
                    conn.commit()
                    conn.close()
                    st.success("Thank you! You have been successfully enlisted in the SDERMS Volunteer Directory. Control Room can reach you during emergencies.")

# ==========================================
# 4. ADMIN COMMAND CENTER (CONTROL ROOM)
# ==========================================
else:
    st.sidebar.markdown("### 🔒 Control Room Security")
    
    # Simple secure session toggle
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False

    if not st.session_state.admin_logged_in:
        st.title("🔒 Disaster Control Room Login")
        st.caption("Restricted access for Emergency Command, Fleet Dispatch, and Algorithm Solvers.")

        with st.form("admin_login_form"):
            adm_user = st.text_input("Admin Username", value="admin")
            adm_pass = st.text_input("Admin Password", type="password", value="admin123")
            btn_login = st.form_submit_button("Access Command Center", type="primary")

            if btn_login:
                if adm_user == "admin" and adm_pass == "admin123":
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid admin credentials. Please try again.")
        st.stop()
    else:
        if st.sidebar.button("🚪 Sign Out (Admin)"):
            st.session_state.admin_logged_in = False
            st.rerun()

    st.title("🛡️ Disaster Operations Command Center")
    st.caption("Real-time decision support system: Automated triage queue, Dijkstra shortest route finder, Greedy shelter matching, and Proportional relief distribution.")

    admin_menu = st.sidebar.selectbox(
        "Navigate Operations",
        [
            "📊 Executive Dashboard",
            "🌪️ Disaster Monitoring",
            "🚨 Emergency Triage Queue",
            "🏕️ Shelter Operations & Best-Fit",
            "📦 Relief Supplies & Proportional Solver",
            "🚑 Rescue Squads Fleet",
            "🤝 Civilian Volunteers Directory",
            "🧭 Dijkstra Safe Route Solver",
            "📈 Audit Reports & CSV Export"
        ]
    )

    # ---------- 1. EXECUTIVE DASHBOARD ----------
    if admin_menu == "📊 Executive Dashboard":
        st.subheader("Real-Time Operational Telemetry & KPI Metrics")

        conn = get_connection()
        total_active_disasters = conn.execute("SELECT COUNT(*) c FROM disasters WHERE status='ACTIVE'").fetchone()["c"]
        total_affected = conn.execute("SELECT COALESCE(SUM(affected_people), 0) s FROM disasters WHERE status='ACTIVE'").fetchone()["s"]
        critical_requests = conn.execute("SELECT COUNT(*) c FROM emergency_requests WHERE priority_level='CRITICAL' AND status!='RESOLVED'").fetchone()["c"]
        pending_requests = conn.execute("SELECT COUNT(*) c FROM emergency_requests WHERE status='PENDING'").fetchone()["c"]
        resolved_requests = conn.execute("SELECT COUNT(*) c FROM emergency_requests WHERE status='RESOLVED'").fetchone()["c"]
        total_cap = conn.execute("SELECT COALESCE(SUM(capacity), 0) s FROM shelters").fetchone()["s"]
        total_occ = conn.execute("SELECT COALESCE(SUM(occupied), 0) s FROM shelters").fetchone()["s"]
        avail_squads = conn.execute("SELECT COUNT(*) c FROM rescue_teams WHERE status='AVAILABLE'").fetchone()["c"]
        ready_vols = conn.execute("SELECT COUNT(*) c FROM volunteers WHERE availability='YES'").fetchone()["c"]
        conn.close()

        # Top KPI cards
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Active Disasters", total_active_disasters, "Live Monitoring")
        k2.metric("Total Casualties", f"{total_affected:,}", "Affected Population")
        k3.metric("Critical SOS Queue", critical_requests, "Immediate Action")
        k4.metric("Pending Triage", pending_requests, "Awaiting Dispatch")

        k5, k6, k7, k8 = st.columns(4)
        k5.metric("Shelter Capacity", f"{total_occ:,} / {total_cap:,}", f"{(total_occ/total_cap*100) if total_cap else 0:.1f}% Occupied")
        k6.metric("Available Squads", avail_squads, "Ready for Deployment")
        k7.metric("Civilian Volunteers", ready_vols, "Enlisted Ready")
        k8.metric("Resolved Incidents", resolved_requests, "Safe Assistance")

        st.divider()

        # Visual Telemetry Charts
        st.subheader("📊 Visual Analytics & Telemetry")
        c_ch1, c_ch2 = st.columns(2)
        with c_ch1:
            st.markdown("##### 🚨 Emergency Severity Distribution")
            df_risk_dist = query_df("SELECT priority_level, COUNT(*) as Incidents FROM emergency_requests WHERE status != 'RESOLVED' GROUP BY priority_level")
            if not df_risk_dist.empty:
                st.bar_chart(df_risk_dist.set_index("priority_level"), color="#ef4444")
            else:
                st.info("No active emergency incidents in queue.")

        with c_ch2:
            st.markdown("##### 🏢 Shelter Occupancy Breakdown")
            df_sh_dist = query_df("SELECT name, occupied, capacity FROM shelters LIMIT 6")
            if not df_sh_dist.empty:
                st.bar_chart(df_sh_dist.set_index("name")[["occupied", "capacity"]])
            else:
                st.info("No active shelters found.")

        st.divider()

        # High priority live crisis alerts
        st.subheader("🚨 Critical & High-Priority Emergency Triage Queue")
        df_top_crises = query_df("""
            SELECT id, requester_name, location, emergency_type, priority_score, priority_level, status, created_at
            FROM emergency_requests
            WHERE status != 'RESOLVED'
            ORDER BY priority_score DESC, id ASC
            LIMIT 5
        """)
        if df_top_crises.empty:
            st.success("🎉 No active high-priority emergency incidents in the queue.")
        else:
            st.dataframe(df_top_crises, use_container_width=True)

    # ---------- 2. DISASTER MONITORING ----------
    elif admin_menu == "🌪️ Disaster Monitoring":
        st.subheader("Disaster Incident Command & Tracking")

        with st.expander("➕ Register New Disaster / Calamity Event", expanded=False):
            with st.form("new_disaster_form", clear_on_submit=True):
                d_name = st.text_input("Disaster Title", placeholder="e.g. Cyclone Remal 2026")
                d_type = st.selectbox("Category", ["Cyclone", "Flash Flood", "Earthquake", "Building Fire", "Tsunami", "Landslide", "Other"])
                d_area = st.text_input("Affected Geographic Area / Region", placeholder="e.g. Coastal Zone, Cox's Bazar")
                d_sev = st.selectbox("Severity Rating", ["CRITICAL", "HIGH", "MODERATE", "LOW"])
                d_pop = st.number_input("Estimated Affected Population", min_value=0, value=25000, step=1000)
                
                if st.form_submit_button("Register Disaster Event", type="primary"):
                    conn = get_connection()
                    conn.execute("INSERT INTO disasters(name, type, area, severity, affected_people, status) VALUES (?, ?, ?, ?, ?, 'ACTIVE')", (d_name, d_type, d_area, d_sev, d_pop))
                    conn.commit()
                    conn.close()
                    st.success("Disaster registered successfully.")
                    st.rerun()

        df_disasters = query_df("SELECT * FROM disasters ORDER BY id DESC")
        st.dataframe(df_disasters, use_container_width=True)

        st.markdown("#### Toggle Disaster Resolution Status:")
        if not df_disasters.empty:
            sel_d_id = st.selectbox("Select Disaster to Toggle", df_disasters["id"].tolist(), format_func=lambda x: f"DIS-{x}: {df_disasters[df_disasters['id']==x]['name'].values[0]}")
            if st.button("Toggle Status (ACTIVE / CONTAINED)"):
                conn = get_connection()
                cur_status = conn.execute("SELECT status FROM disasters WHERE id=?", (sel_d_id,)).fetchone()["status"]
                new_status = "CONTAINED" if cur_status == "ACTIVE" else "ACTIVE"
                conn.execute("UPDATE disasters SET status=? WHERE id=?", (new_status, sel_d_id))
                conn.commit()
                conn.close()
                st.success(f"Status changed to {new_status}!")
                st.rerun()

    # ---------- 3. EMERGENCY TRIAGE QUEUE ----------
    elif admin_menu == "🚨 Emergency Triage Queue":
        st.subheader("Automated Multi-Criteria Risk Triage Queue")
        st.caption("Requests are ranked automatically by computed mathematical risk scores (0–100).")

        df_emergencies = query_df("SELECT * FROM emergency_requests ORDER BY priority_score DESC, id ASC")
        st.dataframe(df_emergencies, use_container_width=True)

        st.markdown("#### Mark Incident as Resolved:")
        pending_ids = df_emergencies[df_emergencies["status"] == "PENDING"]["id"].tolist()
        if pending_ids:
            col_sel, col_btn = st.columns([2, 1])
            with col_sel:
                res_id = st.selectbox("Select Pending Emergency Ticket to Resolve", pending_ids, format_func=lambda x: f"ER-{x:04d}")
            with col_btn:
                st.write("")
                st.write("")
                if st.button("Mark Resolved & Safe ✅", type="primary"):
                    conn = get_connection()
                    conn.execute("UPDATE emergency_requests SET status='RESOLVED' WHERE id=?", (res_id,))
                    conn.commit()
                    conn.close()
                    st.success(f"Ticket ER-{res_id:04d} marked as RESOLVED!")
                    st.rerun()
        else:
            st.info("No pending requests requiring resolution.")

    # ---------- 4. SHELTER OPERATIONS & BEST-FIT ----------
    elif admin_menu == "🏕️ Shelter Operations & Best-Fit":
        st.subheader("Evacuation Shelters & Algorithmic Best-Fit Matching")

        col_rec, col_add = st.columns([1.5, 1])

        with col_rec:
            st.markdown("### 🎯 Best-Fit Shelter Recommender Algorithm")
            st.caption("Finds the tightest-fit shelter matching requested evacuees without wasting large capacity on small groups.")
            
            req_beds = st.number_input("Number of Evacuees Needing Beds", min_value=1, value=120, step=10)
            if st.button("Calculate Optimal Best-Fit Shelter", type="primary"):
                conn = get_connection()
                shelters = conn.execute("SELECT * FROM shelters").fetchall()
                conn.close()

                candidates = []
                for s in shelters:
                    free_beds = s["capacity"] - s["occupied"]
                    if free_beds >= req_beds:
                        candidates.append((free_beds, s))

                if not candidates:
                    st.error(f"❌ No single shelter has {req_beds} available beds remaining.")
                else:
                    # Greedy Best-Fit: minimum surplus capacity
                    candidates.sort(key=lambda x: x[0])
                    avail, best_sh = candidates[0]
                    surplus = avail - req_beds
                    st.success(f"✅ **Optimal Recommended Shelter:** **{best_sh['name']}** ({best_sh['location']})  \n- Free Capacity: **{avail}** beds (Surplus: {surplus} beds remaining after placement).")

        with col_add:
            st.markdown("### ➕ Register New Shelter Center")
            with st.form("new_shelter_form", clear_on_submit=True):
                sh_name = st.text_input("Shelter Facility Name")
                sh_loc = st.text_input("Location / Ward")
                sh_cap = st.number_input("Total Bed Capacity", min_value=10, value=300, step=50)
                sh_occ = st.number_input("Currently Occupied", min_value=0, value=0, step=10)
                
                if st.form_submit_button("Register Shelter"):
                    conn = get_connection()
                    conn.execute("INSERT INTO shelters(name, location, capacity, occupied) VALUES (?, ?, ?, ?)", (sh_name, sh_loc, sh_cap, sh_occ))
                    conn.commit()
                    conn.close()
                    st.success("Shelter registered successfully.")
                    st.rerun()

        st.divider()
        df_sh = query_df("SELECT * FROM shelters")
        st.dataframe(df_sh, use_container_width=True)

    # ---------- 5. RELIEF SUPPLIES & PROPORTIONAL SOLVER ----------
    elif admin_menu == "📦 Relief Supplies & Proportional Solver":
        st.subheader("Relief Supplies & Proportional Quota Allocation Solver")

        st.markdown("### ⚖️ Smart Proportional Allocation Solver")
        st.caption("Computes mathematically fair supply distribution across relief camps based on respective affected populations.")

        conn = get_connection()
        resources = conn.execute("SELECT * FROM resources WHERE quantity > 0").fetchall()
        conn.close()

        if not resources:
            st.warning("No resources currently available in stock.")
        else:
            res_dict = {r["id"]: f"{r['name']} ({r['quantity']} {r['unit']} available)" for r in resources}
            sel_res_id = st.selectbox("Select Supply Item to Distribute", list(res_dict.keys()), format_func=lambda x: res_dict[x])
            selected_res = next(r for r in resources if r["id"] == sel_res_id)

            alloc_amount = st.number_input(f"Amount of {selected_res['name']} to Distribute ({selected_res['unit']})", min_value=1.0, max_value=float(selected_res["quantity"]), value=min(1000.0, float(selected_res["quantity"])))

            st.markdown("**Enter Affected Area Populations:**")
            p_c1, p_c2, p_c3 = st.columns(3)
            with p_c1:
                pop_a = st.number_input("Area 1 (e.g. Ward 1)", min_value=100, value=5000, step=500)
            with p_c2:
                pop_b = st.number_input("Area 2 (e.g. Ward 2)", min_value=100, value=8000, step=500)
            with p_c3:
                pop_c = st.number_input("Area 3 (e.g. Ward 3)", min_value=100, value=3000, step=500)

            if st.button("Calculate Fair Proportional Quotas", type="primary"):
                pop_dict = {"Ward 1": pop_a, "Ward 2": pop_b, "Ward 3": pop_c}
                plan = proportional_allocation(alloc_amount, pop_dict)

                st.success(f"✅ **Fair Proportional Plan for {alloc_amount} {selected_res['unit']} of {selected_res['name']}:**")
                tot_pop = sum(pop_dict.values())
                for area, qty in plan.items():
                    share_pct = (pop_dict[area] / tot_pop) * 100
                    st.write(f"- **{area}** (Population: {pop_dict[area]:,}, Share: **{share_pct:.1f}%**): **{qty} {selected_res['unit']}**")

        st.divider()
        st.markdown("### 📋 Current Supplies Inventory")
        df_res = query_df("SELECT * FROM resources")
        st.dataframe(df_res, use_container_width=True)

    # ---------- 6. RESCUE SQUADS FLEET ----------
    elif admin_menu == "🚑 Rescue Squads Fleet":
        st.subheader("Specialized Rescue Squads Deployment & Coordination")

        df_rescue = query_df("SELECT * FROM rescue_teams ORDER BY id ASC")
        st.dataframe(df_rescue, use_container_width=True)

        st.markdown("#### Dispatch or Recall Squad:")
        if not df_rescue.empty:
            sel_squad = st.selectbox("Select Squad", df_rescue["id"].tolist(), format_func=lambda x: f"Squad {x}: {df_rescue[df_rescue['id']==x]['name'].values[0]}")
            if st.button("Toggle Squad Availability"):
                conn = get_connection()
                cur_st = conn.execute("SELECT status FROM rescue_teams WHERE id=?", (sel_squad,)).fetchone()["status"]
                new_st = "DISPATCHED" if cur_st == "AVAILABLE" else "AVAILABLE"
                conn.execute("UPDATE rescue_teams SET status=? WHERE id=?", (new_st, sel_squad))
                conn.commit()
                conn.close()
                st.success(f"Status changed to {new_st}!")
                st.rerun()

    # ---------- 7. CIVILIAN VOLUNTEERS DIRECTORY ----------
    elif admin_menu == "🤝 Civilian Volunteers Directory":
        st.subheader("Civilian Volunteers Roster & Skills Directory")

        df_vols = query_df("SELECT * FROM volunteers ORDER BY id DESC")
        st.dataframe(df_vols, use_container_width=True)

    # ---------- 8. DIJKSTRA SAFE ROUTE SOLVER ----------
    elif admin_menu == "🧭 Dijkstra Safe Route Solver":
        st.subheader("Dijkstra Shortest Route Solver & Road Blockade Bypass")
        st.caption("Computes lowest-latency path for ambulances and relief trucks while intelligently bypassing road obstructions.")

        conn = get_connection()
        roads = conn.execute("SELECT * FROM roads").fetchall()
        conn.close()

        df_roads = query_df("SELECT * FROM roads")
        
        c_map, c_solve = st.columns([1.5, 1.2])

        with c_map:
            st.markdown("### 🛣️ Road Network & Blockade Controller")
            st.dataframe(df_roads, use_container_width=True)

            st.markdown("**Toggle Road Blockade / Flood Obstruction:**")
            sel_road_id = st.selectbox("Select Road Edge", df_roads["id"].tolist(), format_func=lambda x: f"Edge {x}: Node {df_roads[df_roads['id']==x]['from_location'].values[0]} ⇄ Node {df_roads[df_roads['id']==x]['to_location'].values[0]} ({df_roads[df_roads['id']==x]['status'].values[0]})")
            if st.button("Toggle Obstruction (OPEN / BLOCKED)"):
                conn = get_connection()
                cur_r_st = conn.execute("SELECT status FROM roads WHERE id=?", (sel_road_id,)).fetchone()["status"]
                new_r_st = "BLOCKED" if cur_r_st.upper() == "OPEN" else "OPEN"
                conn.execute("UPDATE roads SET status=? WHERE id=?", (new_r_st, sel_road_id))
                conn.commit()
                conn.close()
                st.success(f"Road {sel_road_id} is now {new_r_st}!")
                st.rerun()

        with c_solve:
            st.markdown("### 🧭 Dijkstra Route Pathfinder")
            nodes = sorted(list(set(df_roads["from_location"].tolist() + df_roads["to_location"].tolist())))
            
            c_start, c_end = st.columns(2)
            with c_start:
                start_node = st.selectbox("Start Node (Origin)", nodes, index=0)
            with c_end:
                end_node = st.selectbox("End Node (Destination)", nodes, index=min(3, len(nodes)-1))

            calc_pressed = st.button("🚀 Calculate Shortest Safe Route", type="primary")
            active_path = None

            if calc_pressed:
                conn = get_connection()
                active_roads = conn.execute("SELECT * FROM roads").fetchall()
                conn.close()

                graph = build_graph(active_roads)
                cost, path = shortest_path(graph, start_node, end_node)
                active_path = path

                if cost is None:
                    st.error(f"❌ No passable route exists between Node {start_node} and Node {end_node}! (Roads may be BLOCKED).")
                else:
                    path_str = " ➔ ".join([f"**[Node {n}]**" for n in path])
                    st.markdown(f"""
                    <div class="route-box">
                        <b>Optimal Navigation Path:</b><br/>
                        {path_str}<br/><br/>
                        🎯 <b>Total Distance:</b> {cost:g} KM
                    </div>
                    """, unsafe_allow_html=True)

            # Interactive Topology Graph Visualization
            st.markdown("#### 🗺️ Live Road Topology Graph")
            dot_lines = [
                "graph G {",
                "layout=neato;",
                "bgcolor=\"transparent\";",
                "node [style=filled, fontname=\"Helvetica\", shape=circle, fillcolor=\"#1e293b\", fontcolor=\"#ffffff\", width=0.6, fixedsize=true];",
                "edge [fontname=\"Helvetica\", fontsize=10, fontcolor=\"#94a3b8\", color=\"#475569\", penwidth=1.8];"
            ]
            path_pairs = set()
            if active_path and len(active_path) > 1:
                for idx in range(len(active_path) - 1):
                    path_pairs.add((active_path[idx].upper(), active_path[idx+1].upper()))
                    path_pairs.add((active_path[idx+1].upper(), active_path[idx].upper()))

            for _, r in df_roads.iterrows():
                u = str(r["from_location"]).upper()
                v = str(r["to_location"]).upper()
                dist = r["distance"]
                is_bl = (r["status"] == "BLOCKED")
                is_pt = (u, v) in path_pairs

                if is_pt:
                    dot_lines.append(f'"{u}" -- "{v}" [label="{dist:g}km", color="#10b981", penwidth=4.0, fontcolor="#34d399"];')
                elif is_bl:
                    dot_lines.append(f'"{u}" -- "{v}" [label="BLOCKED", color="#ef4444", style=dashed, penwidth=2.0, fontcolor="#f87171"];')
                else:
                    dot_lines.append(f'"{u}" -- "{v}" [label="{dist:g}km"];')

            if active_path:
                for n in active_path:
                    dot_lines.append(f'"{n}" [fillcolor="#065f46", color="#10b981", penwidth=3.0, fontcolor="#ffffff"];')

            dot_lines.append("}")
            st.graphviz_chart("\n".join(dot_lines))

    # ---------- 9. AUDIT REPORTS & CSV EXPORT ----------
    elif admin_menu == "📈 Audit Reports & CSV Export":
        st.subheader("Audit Intelligence & Incident Logs")
        st.caption("Official emergency log for disaster management authorities and humanitarian compliance.")

        df_audit = query_df("SELECT * FROM emergency_requests ORDER BY id DESC")
        st.dataframe(df_audit, use_container_width=True)

        csv_data = df_audit.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Full Audit Log (.CSV Spreadsheet)",
            data=csv_data,
            file_name=f"SDERMS_Audit_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            type="primary"
        )

st.sidebar.divider()
st.sidebar.caption("© 2026 SDERMS • BUBT Department of CSE • Software Development Project (SDP-200)")
