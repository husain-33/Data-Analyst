import streamlit as st

st.set_page_config(
    page_title="Sounce Costing Calculator",
    page_icon="🧮",
    layout="centered"
)

# -----------------------------
# Language Toggle
# -----------------------------
language = st.selectbox(
    "Language / भाषा",
    ["English", "Hinglish"],
    index=0
)

is_hinglish = language == "Hinglish"


def text(en, hi):
    return hi if is_hinglish else en


# -----------------------------
# Helper Function
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
# Title
# -----------------------------
st.title(text(
    "🧮 Sounce Product Costing Calculator",
    "🧮 Sounce Product Costing Calculator"
))

st.caption(text(
    "A simple calculator for RMB costing, landing cost, Clicktech margin and negotiation target.",
    "RMB costing, landing cost, Clicktech margin aur negotiation target ke liye simple calculator."
))

st.markdown("---")

# -----------------------------
# Step 1: Selling Price
# -----------------------------
st.header(text(
    "Step 1: Enter Selling Price",
    "Step 1: Selling Price daalo"
))

selling_price = st.number_input(
    text("Amazon Selling Price (₹)", "Amazon par hum kitne me sell karenge? (₹)"),
    min_value=0.0,
    value=199.0,
    step=1.0
)

clicktech_margin = get_clicktech_margin(selling_price)

st.success(text(
    f"Auto selected Clicktech margin slab: {clicktech_margin}%",
    f"Is selling price par Clicktech margin slab: {clicktech_margin}%"
))

st.markdown("---")

# -----------------------------
# Step 2: RMB Cost
# -----------------------------
st.header(text(
    "Step 2: Enter Supplier RMB Price",
    "Step 2: Supplier RMB price daalo"
))

rmb_price = st.number_input(
    text("Supplier Price in RMB / Yuan", "Supplier ne kitna RMB / Yuan price bola?"),
    min_value=0.0,
    value=5.0,
    step=0.1
)

rmb_rate = st.number_input(
    text("RMB to INR Rate", "RMB rate kya lena hai?"),
    min_value=0.0,
    value=14.5,
    step=0.1,
    help=text(
        "Example: 1 RMB × 14.5 = INR value",
        "Example: 1 RMB × 14.5 = INR value"
    )
)

st.markdown("---")

# -----------------------------
# Step 3: Landing Cost
# -----------------------------
st.header(text(
    "Step 3: Select Landing Cost",
    "Step 3: Landing cost select karo"
))

landing_percent = st.number_input(
    text("Landing / Import Cost %", "Landing cost percentage"),
    min_value=0.0,
    value=16.5,
    step=0.5
)

product_size = st.radio(
    text("Product Size", "Product size kya hai?"),
    [
        text("Small Product = ₹6", "Small product = ₹6"),
        text("Big Product = ₹15", "Big product = ₹15"),
        text("Custom Amount", "Custom amount")
    ]
)

if product_size in ["Small Product = ₹6", "Small product = ₹6"]:
    size_cost = 6.0
elif product_size in ["Big Product = ₹15", "Big product = ₹15"]:
    size_cost = 15.0
else:
    size_cost = st.number_input(
        text("Enter Custom Landing Amount (₹)", "Custom landing amount daalo (₹)"),
        min_value=0.0,
        value=6.0,
        step=1.0
    )

st.info(text(
    f"Selected extra landing cost: ₹{size_cost:.2f}",
    f"Selected extra landing cost: ₹{size_cost:.2f}"
))

st.markdown("---")

# -----------------------------
# Step 4: GST and Profit
# -----------------------------
st.header(text(
    "Step 4: GST and Profit Settings",
    "Step 4: GST aur Profit Settings"
))

gst_percent = st.number_input(
    text("GST %", "GST %"),
    min_value=0.0,
    value=18.0,
    step=1.0
)

profit_percent = st.number_input(
    text("Required Profit %", "Required profit %"),
    min_value=0.0,
    value=35.0,
    step=1.0
)

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

if rmb_rate > 0:
    max_rmb = max((target_landed_cost - size_cost) / ((1 + landing_percent / 100) * rmb_rate), 0)
else:
    max_rmb = 0

# -----------------------------
# Final Result
# -----------------------------
st.markdown("---")
st.header(text("Final Result", "Final Result"))

col1, col2 = st.columns(2)

with col1:
    st.metric(
        text("Target Landed Cost", "Target landed cost"),
        f"₹{target_landed_cost:.2f}"
    )

with col2:
    st.metric(
        text("Actual Landed Cost", "Actual landing cost"),
        f"₹{actual_landed_cost:.2f}"
    )

st.metric(
    text("Difference", "Difference"),
    f"₹{difference:.2f}"
)

if actual_landed_cost <= target_landed_cost:
    st.success(text(
        "✅ Product is workable. Supplier cost fits within target price.",
        "✅ Product workable hai. Cost target ke andar hai."
    ))
else:
    st.error(text(
        "❌ Product is costly. Need to negotiate with supplier.",
        "❌ Product abhi costly hai. Supplier se negotiate karna padega."
    ))

st.info(text(
    f"Safe negotiation target with supplier: approx ¥{max_rmb:.2f} RMB or below.",
    f"Supplier se approx max ¥{max_rmb:.2f} RMB tak deal karna safe rahega."
))

# -----------------------------
# Breakdown
# -----------------------------
st.markdown("---")
st.header(text("Easy Breakdown", "Easy Breakdown"))

st.subheader(text("A. Clicktech Side Calculation", "A. Clicktech side calculation"))
st.write(text("Selling Price", "Selling price"), f"= ₹{selling_price:.2f}")
st.write(text("Clicktech Slab", "Clicktech slab"), f"= {clicktech_margin}%")
st.write(text("Amount after Clicktech Margin", "Clicktech ke baad amount"), f"= ₹{clicktech_amount_after_margin:.2f}")
st.write(text("After GST Removal", "GST remove karne ke baad"), f"= ₹{price_after_gst_remove:.2f}")
st.write(text("Target Landed Cost after Profit", "Profit ke baad target landed cost"), f"= ₹{target_landed_cost:.2f}")

st.subheader(text("B. Supplier Side Calculation", "B. Supplier side calculation"))
st.write(text("RMB Price", "RMB price"), f"= ¥{rmb_price:.2f}")
st.write(text("RMB Rate", "RMB rate"), f"= ₹{rmb_rate:.2f}")
st.write(text("RMB to INR", "RMB to INR"), f"= ₹{base_inr:.2f}")
st.write(text("Landing Cost Amount", "Landing cost amount"), f"= ₹{landing_amount:.2f}")
st.write(text("Size Cost", "Size cost"), f"= ₹{size_cost:.2f}")
st.write(text("Final Actual Landed Cost", "Final actual landed cost"), f"= ₹{actual_landed_cost:.2f}")

# -----------------------------
# Formula
# -----------------------------
st.markdown("---")
st.header(text("Formula", "Formula"))

st.code(
    "Target Cost = Selling Price × Remaining Clicktech % ÷ GST Multiplier ÷ Profit Multiplier",
    language="text"
)

st.code(
    "Actual Cost = (RMB Price × RMB Rate) + Landing % Amount + Size Cost",
    language="text"
)

st.caption(text(
    "Rule: If actual landed cost is lower than target landed cost, product is workable.",
    "Rule: Actual landed cost agar target landed cost se kam hai, product workable hai."
))
