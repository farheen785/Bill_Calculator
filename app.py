import streamlit as st
from fpdf import FPDF

# --- PDF Generation Function ---
def create_pdf(name, month, rent, ssgc, motor, wifi, total, formula):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("helvetica", 'B', 16)
    pdf.cell(0, 15, txt=f"OFFICIAL UTILITY RECEIPT", ln=True, align='C')
    pdf.set_font("helvetica", '', 10)
    pdf.cell(0, 5, txt=f"Billing Month: {month}", ln=True, align='C')
    pdf.ln(10)
    
    # User Info
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, txt=f"Recipient: {name}", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    # Details Table
    pdf.set_font("helvetica", '', 11)
    def add_row(label, value):
        pdf.cell(100, 10, txt=label)
        pdf.cell(0, 10, txt=value, align='R', ln=True)

    add_row("Base Rent", f"Rs {rent:,}")
    add_row("SSGC (Gas) Share", f"Rs {ssgc:,.2f}")
    add_row("Motor (Water) Share", f"Rs {motor:,.2f}")
    add_row("WiFi Charges", f"Rs {wifi:,.2f}")
    
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    
    # Total
    pdf.set_font("helvetica", 'B', 12)
    pdf.set_text_color(200, 0, 0) # Red Total
    add_row("GRAND TOTAL", f"Rs {total:,.2f}")
    
    # Footer Logic
    pdf.ln(20)
    pdf.set_font("helvetica", 'I', 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, txt=f"Calculation: {formula}", ln=True, align='C')
    
    # CRITICAL FIX: Convert bytearray to bytes for Streamlit
    return bytes(pdf.output())

# --- UI Setup ---
st.set_page_config(page_title="Utility Pro", layout="wide")

st.markdown("""
    <style>
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3em;
        background-color: #2ecc71; color: white; transition: 0.3s;
    }
    .receipt-card {
        background: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1); border-top: 6px solid #2ecc71;
        color: black;
    }
    .metric-card {
        background: white; padding: 15px; border-radius: 10px;
        border-left: 5px solid #2ecc71; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        color: black;
    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("⚙️ Settings")
    month_val = st.text_input("Month", "April 2026")
    
    st.subheader("🔥 SSGC")
    total_ssgc = st.number_input("Total Gas Bill", min_value=0.0)
    ssgc_final = (total_ssgc / 3) - 200 if total_ssgc > 0 else 0.0
    
    st.subheader("⚡ Motor")
    last_u = st.number_input("Last Month Unit", min_value=0.0)
    curr_u = st.number_input("Current Month Unit", min_value=0.0)
    price_u = st.number_input("Unit Price", min_value=0.0)
    
    # Logic: (Current - Last) * Price / 4 - 200
    net_u = curr_u - last_u
    motor_final = ((net_u * price_u) / 4) - 200 if curr_u > last_u else 0.0

# --- Dashboard ---
st.title("🏙️ Utility Billing Hub")

c1, c2, c3 = st.columns(3)
with c1: st.markdown(f"<div class='metric-card'><b>Month</b><br>{month_val}</div>", unsafe_allow_html=True)
with c2: st.markdown(f"<div class='metric-card'><b>Gas Share</b><br>Rs {ssgc_final:,.2f}</div>", unsafe_allow_html=True)
with c3: st.markdown(f"<div class='metric-card'><b>Motor Share</b><br>Rs {motor_final:,.2f}</div>", unsafe_allow_html=True)

st.divider()

# WiFi & Receipts
users = {"Faiza": 8500, "Ambreen": 15500, "Bushra": 17500}
wifi_vals = {}
w_cols = st.columns(len(users))
for i, name in enumerate(users):
    with w_cols[i]:
        wifi_vals[name] = st.number_input(f"WiFi: {name}", min_value=0.0, key=f"wifi_{name}")

if st.button("✨ Generate & Download Receipts"):
    st.balloons()
    r_cols = st.columns(len(users))
    formula_str = f"(({curr_u} - {last_u}) * {price_u}) / 4 - 200"

    for i, (name, rent) in enumerate(users.items()):
        wifi = wifi_vals[name]
        grand_total = float(rent) + float(ssgc_final) + float(motor_final) + float(wifi)
        
        with r_cols[i]:
            st.markdown(f"""
                <div class="receipt-card">
                    <h3 style="text-align:center;">{name}</h3>
                    <hr>
                    <p>Rent: <b>Rs {rent:,}</b></p>
                    <p>Gas: <b>Rs {ssgc_final:,.2f}</b></p>
                    <p>Motor: <b>Rs {motor_final:,.2f}</b></p>
                    <p>WiFi: <b>Rs {wifi:,.2f}</b></p>
                    <hr>
                    <h4 style="color:red; text-align:center;">Total: Rs {grand_total:,.2f}</h4>
                </div>
            """, unsafe_allow_html=True)
            
            # The Fix: The create_pdf function now returns 'bytes' which solves the error
            pdf_bytes = create_pdf(name, month_val, rent, ssgc_final, motor_final, wifi, grand_total, formula_str)
            st.download_button(
                label=f"📥 PDF for {name}",
                data=pdf_bytes,
                file_name=f"{name}_Receipt_{month_val}.pdf",
                mime="application/pdf",
                key=f"dl_{name}"
            )