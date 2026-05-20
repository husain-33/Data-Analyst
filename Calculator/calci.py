import streamlit as st

st.set_page_config(page_title="Simple Product Cost Calculator", page_icon="🧮", layout="centered")

st.title("🧮 Simple Product Cost Calculator")
st.caption("Sounce ke liye easy RMB + Clicktech costing calculator")

st.markdown("---")

# -----------------------------
# Helper Functions
# -----------------------------
def get_clicktech_margin(price):
    if price <= 199:
        return 43
    elif price <= 498:
        return 39
    elif price <= 998:
        return 33
    return 28

# -----------------------------
# Section 1: Selling Price
# -----------------------------
st.header("Step 1: Selling Price daalo")

selling_price = st.number_input(
    "Amazon par hum kitne me sell karenge?",
    min_value=0.0,
    value=199.0,
    step=1.0
)

clicktech_margin = get_clicktech_margin(selling_price)

st.success(f"Is selling price par Clicktech margin slab: {clicktech_margin}%")

# -----------------------------
# Section 2: RMB Cost
# -----------------------------
st.markdown("---")
st.header("Step 2: Supplier RMB price daalo")

rmb_price = st.number_input(
    "Supplier ne kitna RMB / Yuan price bola?",
    min_value=0.0,
    value=5.0,
    step=0.1
)

rmb_rate = st.number_input(
    "RMB rate kya lena hai?",
    min_value=0.0,
    value=14.5,
    step=0.1
)

# -----------------------------
# Section 3: Landing Cost
# -----------------------------
st.markdown("---")
st.header("Step 3: Landing cost select karo")

landing_percent = st.number_input(
    "Landing cost percentage",
    min_value=0.0,
    value=16.5,
    step=0.5
)

product_size = st.radio(
    "Product size kya hai?",
    ["Small product = ₹6", "Big product = ₹15", "Custom amount"]
)

if product_size == "Small product = ₹6":
    size_cost = 6.0
elif product_size == "Big product = ₹15":
    size_cost = 15.0
else:
    size_cost = st.number_input("Custom landing amount daalo", min_value=0.0, value=6.0, step=1.0)

# -----------------------------
# Section 4: Profit Settings
# -----------------------------
st.markdown("---")
st.header("Step 4: Profit aur GST")

gst_percent = st.number_input("GST %", min_value=0.0, value=18.0, step=1.0)
profit_percent = st.number_input("Required profit %", min_value=0.0, value=35.0, step=1.0)

# -----------------------------
# Calculations
# -----------------------------
clicktech_amount_after_margin = selling_price * (1 - clicktech_margin / 100)
price_after_gst_remove = clicktech_amount_after_margin / (1 + gst_percent / 100)
target_landed_cost = price_after_gst_remove / (1 + profit_percent / 100)

base_inr = rmb_price * rmb_rate
landing_amount = base_inr * landing_percent / 100
actual_landed_cost = base_inr + landing_amount + size_cost

difference = target_landed_cost - actual_landed_cost

max_rmb = 0
if rmb_rate > 0:
    max_rmb = max((target_landed_cost - size_cost) / ((1 + landing_percent / 100) * rmb_rate), 0)

# -----------------------------
# Final Result
# -----------------------------
st.markdown("---")
st.header("Final Result")

st.subheader("Target vs Actual")

col1, col2 = st.columns(2)

with col1:
    st.metric("Target landing cost", f"₹{target_landed_cost:.2f}")

with col2:
    st.metric("Actual landing cost", f"₹{actual_landed_cost:.2f}")

if actual_landed_cost <= target_landed_cost:
    st.success("✅ Product workable hai. Cost target ke andar hai.")
else:
    st.error("❌ Product abhi costly hai. Supplier se negotiate karna padega.")

st.info(f"Supplier se approx max ¥{max_rmb:.2f} RMB tak deal karna safe rahega.")

# -----------------------------
# Simple Breakdown
# -----------------------------
st.markdown("---")
st.header("Easy Breakdown")

st.write("### A. Clicktech side calculation")
st.write(f"Selling price = ₹{selling_price:.2f}")
st.write(f"Clicktech slab = {clicktech_margin}%")
st.write(f"Clicktech ke baad amount = ₹{clicktech_amount_after_margin:.2f}")
st.write(f"GST remove karne ke baad = ₹{price_after_gst_remove:.2f}")
st.write(f"35% profit ke baad target landed cost = ₹{target_landed_cost:.2f}")

st.write("### B. Supplier side calculation")
st.write(f"RMB price = ¥{rmb_price:.2f}")
st.write(f"RMB rate = ₹{rmb_rate:.2f}")
st.write(f"RMB to INR = ₹{base_inr:.2f}")
st.write(f"Landing {landing_percent}% = ₹{landing_amount:.2f}")
st.write(f"Size cost = ₹{size_cost:.2f}")
st.write(f"Final actual landed cost = ₹{actual_landed_cost:.2f}")

st.markdown("---")
st.header("Simple Formula")

st.code("Target Cost = Selling Price × Remaining Clicktech % ÷ GST ÷ Profit", language="text")
st.code("Actual Cost = RMB Price × RMB Rate + Landing % + Size Cost", language="text")

st.caption("Rule: Actual landed cost agar Target landed cost se kam hai, product workable hai.")