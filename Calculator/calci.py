import streamlit as st

st.set_page_config(page_title="Sounce Costing Calculator", page_icon="🧮", layout="wide")

# -----------------------------
# Helpers
# -----------------------------
def get_clicktech_margin(price):
    if price <= 199:
        return 43
    elif price <= 498:
        return 39
    elif price <= 998:
        return 33
    return 28


def txt(en, hi, hinglish):
    return hi if hinglish else en


# -----------------------------
# Top Bar
# -----------------------------
left, right = st.columns([3, 1])

with left:
    st.title("🧮 Sounce Costing Calculator")

with right:
    language = st.selectbox("Language", ["English", "Hinglish"], index=0)

is_hinglish = language == "Hinglish"

st.caption(txt(
    "One-page calculator for RMB cost, duty, landing cost, Clicktech margin and supplier negotiation target.",
    "RMB cost, duty, landing cost, Clicktech margin aur supplier negotiation target ke liye one-page calculator.",
    is_hinglish
))

st.markdown("---")

# -----------------------------
# Input Panel
# -----------------------------
st.subheader(txt("Enter Details", "Details daalo", is_hinglish))

col1, col2, col3, col4 = st.columns(4)

with col1:
    selling_price = st.number_input(
        txt("Selling Price ₹", "Selling price ₹", is_hinglish),
        min_value=0.0,
        value=199.0,
        step=1.0
    )

    rmb_price = st.number_input(
        txt("Supplier RMB / Yuan", "Supplier RMB / Yuan", is_hinglish),
        min_value=0.0,
        value=5.0,
        step=0.1
    )

with col2:
    rmb_rate = st.number_input(
        txt("RMB Rate", "RMB rate", is_hinglish),
        min_value=0.0,
        value=14.5,
        step=0.1
    )

    duty_option = st.selectbox(
        txt("Duty / Landing %", "Duty / Landing %", is_hinglish),
        ["Free", "11%", "16.5%", "22%", "Custom"],
        index=2
    )

    if duty_option == "Free":
        duty_percent = 0.0
    elif duty_option == "11%":
        duty_percent = 11.0
    elif duty_option == "16.5%":
        duty_percent = 16.5
    elif duty_option == "22%":
        duty_percent = 22.0
    else:
        duty_percent = st.number_input(
            txt("Custom Duty %", "Custom duty %", is_hinglish),
            min_value=0.0,
            value=16.5,
            step=0.5
        )

with col3:
    product_size = st.selectbox(
        txt("Size Cost", "Size cost", is_hinglish),
        ["Small ₹6", "Big ₹15", "Custom"],
        index=0
    )

    if product_size == "Small ₹6":
        size_cost = 6.0
    elif product_size == "Big ₹15":
        size_cost = 15.0
    else:
        size_cost = st.number_input(
            txt("Custom Size Cost ₹", "Custom size cost ₹", is_hinglish),
            min_value=0.0,
            value=6.0,
            step=1.0
        )

    gst_percent = st.number_input(
        "GST %",
        min_value=0.0,
        value=18.0,
        step=1.0
    )

with col4:
    profit_percent = st.number_input(
        txt("Required Profit %", "Required profit %", is_hinglish),
        min_value=0.0,
        value=35.0,
        step=1.0
    )

    clicktech_margin = get_clicktech_margin(selling_price)
    st.info(txt(
        f"Clicktech Slab: {clicktech_margin}%",
        f"Clicktech slab: {clicktech_margin}%",
        is_hinglish
    ))

# -----------------------------
# Calculations
# -----------------------------
clicktech_after_margin = selling_price * (1 - clicktech_margin / 100)
after_gst_remove = clicktech_after_margin / (1 + gst_percent / 100)
target_landed_cost = after_gst_remove / (1 + profit_percent / 100)

base_inr = rmb_price * rmb_rate
duty_amount = base_inr * duty_percent / 100
actual_landed_cost = base_inr + duty_amount + size_cost

difference = target_landed_cost - actual_landed_cost

max_rmb = 0
if rmb_rate > 0:
    max_rmb = max((target_landed_cost - size_cost) / ((1 + duty_percent / 100) * rmb_rate), 0)

# -----------------------------
# Result Cards
# -----------------------------
st.markdown("---")
st.subheader(txt("Final Result", "Final result", is_hinglish))

r1, r2, r3, r4 = st.columns(4)

r1.metric(txt("Target Cost", "Target cost", is_hinglish), f"₹{target_landed_cost:.2f}")
r2.metric(txt("Actual Cost", "Actual cost", is_hinglish), f"₹{actual_landed_cost:.2f}")
r3.metric(txt("Difference", "Difference", is_hinglish), f"₹{difference:.2f}")
r4.metric(txt("Max RMB Deal", "Max RMB deal", is_hinglish), f"¥{max_rmb:.2f}")

if actual_landed_cost <= target_landed_cost:
    st.success(txt(
        "✅ Workable: Supplier cost is within target.",
        "✅ Workable: Supplier cost target ke andar hai.",
        is_hinglish
    ))
else:
    st.error(txt(
        "❌ Not workable yet: Negotiate with supplier.",
        "❌ Abhi workable nahi: Supplier se negotiate karo.",
        is_hinglish
    ))

# -----------------------------
# Compact Breakdown
# -----------------------------
with st.expander(txt("Show Calculation Breakdown", "Calculation breakdown dekho", is_hinglish)):
    b1, b2 = st.columns(2)

    with b1:
        st.write("### Clicktech")
        st.write(f"Selling Price = ₹{selling_price:.2f}")
        st.write(f"Clicktech Slab = {clicktech_margin}%")
        st.write(f"After Clicktech = ₹{clicktech_after_margin:.2f}")
        st.write(f"After GST Remove = ₹{after_gst_remove:.2f}")
        st.write(f"Target Cost = ₹{target_landed_cost:.2f}")

    with b2:
        st.write("### Supplier / RMB")
        st.write(f"RMB Price = ¥{rmb_price:.2f}")
        st.write(f"RMB Rate = ₹{rmb_rate:.2f}")
        st.write(f"Base INR = ₹{base_inr:.2f}")
        st.write(f"Duty {duty_percent}% = ₹{duty_amount:.2f}")
        st.write(f"Size Cost = ₹{size_cost:.2f}")
        st.write(f"Actual Cost = ₹{actual_landed_cost:.2f}")

st.caption(txt(
    "Rule: Actual Cost should be less than or equal to Target Cost.",
    "Rule: Actual cost target cost se kam ya equal hona chahiye.",
    is_hinglish
))
