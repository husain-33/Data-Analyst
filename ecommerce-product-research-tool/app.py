import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

st.set_page_config(page_title="Sounce Product Research Automation", page_icon="📦", layout="wide")
st.markdown("""
<style>
.insight {
    padding:14px 16px;
    border-radius:14px;
    margin-bottom:10px;
    background:#fff8e6;
    border-left:5px solid #ffb300;
    color:#111827;
}

.reco {
    padding:14px 16px;
    border-radius:14px;
    margin-bottom:10px;
    background:#eaf7ee;
    border-left:5px solid #22a35a;
    color:#111827;
}

.risk {
    padding:14px 16px;
    border-radius:14px;
    margin-bottom:10px;
    background:#fff1f0;
    border-left:5px solid #e53935;
    color:#111827;
}

.gem {
    padding:14px 16px;
    border-radius:14px;
    margin-bottom:10px;
    background:#eef5ff;
    border-left:5px solid #2f80ed;
    color:#111827;
}

.summary {
    padding:18px;
    border-radius:18px;
    background:#f7f7f9;
    border:1px solid #e8e8e8;
    color:#111827;
}
</style>
""", unsafe_allow_html=True)

REQUIRED_COLUMNS = [
    "Date", "Product", "Category", "Selling_Price", "Cost_Price",
    "Units_Sold", "Units_Returned", "Rating", "Competitor_Price"
]

def clean_data(data):
    data = data.copy()
    data.columns = [c.strip().replace(" ", "_") for c in data.columns]
    data = data.drop_duplicates()
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")

    numeric_cols = ["Selling_Price", "Cost_Price", "Units_Sold", "Units_Returned", "Rating", "Competitor_Price"]
    for col in numeric_cols:
        data[col] = pd.to_numeric(data[col], errors="coerce")
        data[col] = data[col].fillna(data[col].median())

    if "Review_Text" not in data.columns:
        data["Review_Text"] = ""

    data = data.dropna(subset=["Date", "Product", "Category"])
    data["Revenue"] = data["Selling_Price"] * data["Units_Sold"]
    data["Profit"] = (data["Selling_Price"] - data["Cost_Price"]) * data["Units_Sold"]
    data["Margin_%"] = ((data["Selling_Price"] - data["Cost_Price"]) / data["Selling_Price"] * 100).round(2)
    data["Return_Rate_%"] = (data["Units_Returned"] / data["Units_Sold"] * 100).replace([float("inf")], 0).fillna(0).round(2)
    data["Price_Gap_vs_Competitor"] = data["Selling_Price"] - data["Competitor_Price"]
    return data

def sentiment_score(text):
    text = str(text).lower()

    positive = [
        "good", "excellent", "premium", "sturdy", "durable", "useful",
        "value", "clear", "fast", "quality", "happy", "satisfied",
        "best", "amazing", "nice", "love", "perfect"
    ]

    negative = [
        "bad", "poor", "slow", "heating", "heat", "stopped", "issue",
        "not worth", "loose", "damage", "not happy", "unhappy",
        "worst", "terrible", "broken", "defective", "waste",
        "refund", "return", "disappointed", "problem"
    ]

    # handle negative phrase first
    negative_phrases = ["not happy", "not good", "not working", "not satisfied", "not worth"]

    for phrase in negative_phrases:
        if phrase in text:
            return "Negative"

    pos = sum(word in text for word in positive)
    neg = sum(word in text for word in negative)

    if pos > neg:
        return "Positive"
    elif neg > pos:
        return "Negative"
    return "Neutral"

def lifecycle(row):
    if row["Return_Rate_%"] >= 10 or row["Rating"] < 3.8:
        return "Risky Product"
    if row["Opportunity_Score"] >= 75 and row["Revenue"] >= row["Revenue_Median"]:
        return "Rising Star"
    if row["Revenue"] < row["Revenue_Median"] and row["Margin_%"] >= 35 and row["Rating"] >= 4.2:
        return "Hidden Gem"
    if row["Revenue"] >= row["Revenue_Median"] and row["Return_Rate_%"] < 8:
        return "Stable Performer"
    return "Needs Monitoring"

def product_summary(data):
    data["Review_Sentiment"] = data["Review_Text"].apply(sentiment_score)

    summary = data.groupby(["Product", "Category"], as_index=False).agg({
        "Units_Sold": "sum",
        "Units_Returned": "sum",
        "Revenue": "sum",
        "Profit": "sum",
        "Rating": "mean",
        "Margin_%": "mean",
        "Return_Rate_%": "mean",
        "Selling_Price": "mean",
        "Competitor_Price": "mean",
        "Price_Gap_vs_Competitor": "mean"
    })

    negative_reviews = data[data["Review_Sentiment"] == "Negative"].groupby("Product").size().reset_index(name="Negative_Review_Count")
    positive_reviews = data[data["Review_Sentiment"] == "Positive"].groupby("Product").size().reset_index(name="Positive_Review_Count")

    summary = summary.merge(negative_reviews, on="Product", how="left").merge(positive_reviews, on="Product", how="left")
    summary[["Negative_Review_Count", "Positive_Review_Count"]] = summary[["Negative_Review_Count", "Positive_Review_Count"]].fillna(0)

    summary["Rating"] = summary["Rating"].round(2)
    summary["Margin_%"] = summary["Margin_%"].round(2)
    summary["Return_Rate_%"] = summary["Return_Rate_%"].round(2)
    summary["Price_Gap_vs_Competitor"] = summary["Price_Gap_vs_Competitor"].round(2)

    summary["Revenue_Score"] = summary["Revenue"].rank(pct=True) * 30
    summary["Margin_Score"] = summary["Margin_%"].rank(pct=True) * 25
    summary["Rating_Score"] = summary["Rating"].rank(pct=True) * 20
    summary["Low_Return_Score"] = (1 - summary["Return_Rate_%"].rank(pct=True)) * 15
    summary["Competition_Score"] = (1 - abs(summary["Price_Gap_vs_Competitor"]).rank(pct=True)) * 10
    summary["Opportunity_Score"] = (
        summary["Revenue_Score"] + summary["Margin_Score"] + summary["Rating_Score"] +
        summary["Low_Return_Score"] + summary["Competition_Score"]
    ).round(1)

    summary["Revenue_Median"] = summary["Revenue"].median()
    summary["Lifecycle_Tag"] = summary.apply(lifecycle, axis=1)
    summary = summary.drop(columns=["Revenue_Median"])
    return summary, data

def make_excel_report(data, summary):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        data.to_excel(writer, index=False, sheet_name="Cleaned Data")
        summary.to_excel(writer, index=False, sheet_name="Product Report")
    return output.getvalue()

def generate_bundle_suggestions(summary):
    suggestions = []
    products = summary["Product"].tolist()
    def has(name):
        return any(name.lower() in p.lower() for p in products)

    if has("charger") and has("cable"):
        suggestions.append("Fast Charger + Type-C Cable bundle to increase Average Order Value.")
    if has("laptop stand") and has("usb hub"):
        suggestions.append("Laptop Stand + USB Hub bundle for work-from-home and office users.")
    if has("mobile holder") and has("car charger"):
        suggestions.append("Mobile Holder + Car Charger combo for travel and daily commute users.")
    if has("wireless charger") and has("cable"):
        suggestions.append("Wireless Charger + Backup Cable bundle for premium users.")
    if not suggestions:
        top_two = summary.sort_values("Revenue", ascending=False).head(2)["Product"].tolist()
        suggestions.append(f"Bundle {top_two[0]} + {top_two[1]} based on top revenue performance.")
    return suggestions

with st.sidebar:
    st.header("📤 Upload Data")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    st.caption("Required: Date, Product, Category, Selling_Price, Cost_Price, Units_Sold, Units_Returned, Rating, Competitor_Price. Optional: Review_Text")
    st.divider()
    page = st.radio(
        "Navigation",
        ["Dashboard", "Advanced Intelligence", "Review Analyzer", "Product Research", "Executive Summary", "Data Preview"]
    )

if uploaded_file:
    raw_df = pd.read_csv(uploaded_file)
else:
    st.info("Using sample electronics accessories data. Upload your CSV to automate your own analysis.")
    raw_df = pd.read_csv("sample_sounce_electronics_data_advanced.csv")

raw_df.columns = [c.strip().replace(" ", "_") for c in raw_df.columns]
missing = [c for c in REQUIRED_COLUMNS if c not in raw_df.columns]
if missing:
    st.error(f"Your CSV is missing these required columns: {missing}")
    st.stop()

df = clean_data(raw_df)

with st.sidebar:
    st.header("🔎 Filters")
    categories = sorted(df["Category"].unique())
    selected_categories = st.multiselect("Category", categories, default=categories)
    date_range = st.date_input("Date range", [df["Date"].min().date(), df["Date"].max().date()])

if len(date_range) == 2:
    start_date, end_date = date_range
    df = df[(df["Date"].dt.date >= start_date) & (df["Date"].dt.date <= end_date)]

df = df[df["Category"].isin(selected_categories)]
summary, df = product_summary(df)

if df.empty:
    st.warning("No data available for selected filters.")
    st.stop()

total_revenue = df["Revenue"].sum()
total_profit = df["Profit"].sum()
units_sold = df["Units_Sold"].sum()
return_rate = (df["Units_Returned"].sum() / df["Units_Sold"].sum() * 100) if units_sold else 0
avg_rating = df["Rating"].mean()
best_product = summary.sort_values("Revenue", ascending=False).iloc[0]["Product"]

top_revenue = summary.sort_values("Revenue", ascending=False).iloc[0]
top_margin = summary.sort_values("Margin_%", ascending=False).iloc[0]
high_return = summary.sort_values("Return_Rate_%", ascending=False).iloc[0]
low_rating = summary.sort_values("Rating", ascending=True).iloc[0]
best_opportunity = summary.sort_values("Opportunity_Score", ascending=False).iloc[0]

if page == "Dashboard":
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Revenue", f"₹{total_revenue:,.0f}")
    c2.metric("Total Profit", f"₹{total_profit:,.0f}")
    c3.metric("Units Sold", f"{units_sold:,.0f}")
    c4.metric("Return Rate", f"{return_rate:.2f}%")
    c5.metric("Avg Rating", f"{avg_rating:.2f}")

    st.markdown(f"### Best Revenue Product: **{best_product}**")

    left, right = st.columns(2)
    with left:
        fig = px.bar(summary.sort_values("Revenue", ascending=False), x="Product", y="Revenue", text_auto=True, title="Revenue by Product")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        daily = df.groupby("Date", as_index=False)["Revenue"].sum()
        fig = px.line(daily, x="Date", y="Revenue", markers=True, title="Revenue Trend")
        st.plotly_chart(fig, use_container_width=True)

    left2, right2 = st.columns(2)
    with left2:
        category_revenue = df.groupby("Category", as_index=False)["Revenue"].sum()
        fig = px.pie(category_revenue, names="Category", values="Revenue", title="Category Revenue Share")
        st.plotly_chart(fig, use_container_width=True)
    with right2:
        fig = px.scatter(summary, x="Rating", y="Return_Rate_%", size="Revenue", color="Lifecycle_Tag", hover_name="Product", title="Rating vs Return Risk Map")
        st.plotly_chart(fig, use_container_width=True)

elif page == "Advanced Intelligence":
    st.markdown("### Competitor Opportunity Detector")
    competitor_alerts = []
    for _, r in summary.iterrows():
        if r["Price_Gap_vs_Competitor"] > 50 and r["Return_Rate_%"] > 8:
            competitor_alerts.append(f"{r['Product']} is priced higher than competitor and has high returns. Review pricing and quality.")
        elif r["Price_Gap_vs_Competitor"] < -50 and r["Rating"] >= 4.2:
            competitor_alerts.append(f"{r['Product']} is cheaper than competitor with good rating. There may be room for premium pricing.")
        elif abs(r["Price_Gap_vs_Competitor"]) <= 30 and r["Rating"] >= 4.3:
            competitor_alerts.append(f"{r['Product']} is competitively priced and well-rated. Good product to promote.")

    for item in competitor_alerts:
        st.markdown(f'<div class="insight">🎯 {item}</div>', unsafe_allow_html=True)

    st.markdown("### Dead Product Detector")
    dead = summary[(summary["Revenue"] < summary["Revenue"].median()) & ((summary["Rating"] < 3.8) | (summary["Return_Rate_%"] > 10) | (summary["Margin_%"] < 20))]
    if dead.empty:
        st.success("No dead products detected based on current rules.")
    else:
        for _, r in dead.iterrows():
            st.markdown(f'<div class="risk">☠️ {r["Product"]} is underperforming. Low revenue with risk factors like rating, returns or margin.</div>', unsafe_allow_html=True)

    st.markdown("### Hidden Gem Detector")
    gems = summary[(summary["Revenue"] < summary["Revenue"].median()) & (summary["Rating"] >= 4.2) & (summary["Margin_%"] >= 35) & (summary["Return_Rate_%"] < 8)]
    if gems.empty:
        st.info("No hidden gems detected right now.")
    else:
        for _, r in gems.iterrows():
            st.markdown(f'<div class="gem">💎 {r["Product"]} has good rating, strong margin and low return risk. Increase promotion.</div>', unsafe_allow_html=True)

    st.markdown("### Lifecycle Tags")
    st.dataframe(summary[["Product", "Category", "Revenue", "Rating", "Return_Rate_%", "Margin_%", "Opportunity_Score", "Lifecycle_Tag"]], use_container_width=True)

elif page == "Review Analyzer":
    st.markdown("### Customer Review Analyzer")
    sentiment_count = df.groupby(["Product", "Review_Sentiment"]).size().reset_index(name="Count")
    fig = px.bar(sentiment_count, x="Product", y="Count", color="Review_Sentiment", title="Review Sentiment by Product", barmode="group")
    st.plotly_chart(fig, use_container_width=True)

    negative_df = df[df["Review_Sentiment"] == "Negative"]
    st.markdown("### Products with Negative Review Signals")
    if negative_df.empty:
        st.success("No negative reviews detected.")
    else:
        neg_summary = negative_df.groupby("Product").agg(
            Negative_Review_Count=("Review_Sentiment", "count"),
            Common_Review_Text=("Review_Text", lambda x: ", ".join(pd.Series(x).astype(str).head(3)))
        ).reset_index().sort_values("Negative_Review_Count", ascending=False)
        st.dataframe(neg_summary, use_container_width=True)

    st.markdown("### Paste Review Text for Quick Sentiment")
    review_input = st.text_area("Paste customer review here")
    if review_input:
        result = sentiment_score(review_input)
        st.success(f"Detected Sentiment: {result}")

elif page == "Product Research":
    st.markdown("### Product Opportunity Ranking")
    st.dataframe(summary.sort_values("Opportunity_Score", ascending=False)[[
        "Product", "Category", "Revenue", "Profit", "Margin_%", "Rating",
        "Return_Rate_%", "Selling_Price", "Competitor_Price",
        "Price_Gap_vs_Competitor", "Opportunity_Score", "Lifecycle_Tag"
    ]], use_container_width=True)

    left, right = st.columns(2)
    with left:
        fig = px.bar(summary.sort_values("Opportunity_Score", ascending=False), x="Product", y="Opportunity_Score", title="Opportunity Score", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        fig = px.bar(summary.sort_values("Price_Gap_vs_Competitor", ascending=False), x="Product", y="Price_Gap_vs_Competitor", title="Price Gap vs Competitor", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)

elif page == "Executive Summary":
    st.markdown("### Executive Summary")
    summary_text = f"""
    Total revenue is ₹{total_revenue:,.0f} with total profit of ₹{total_profit:,.0f}. 
    The strongest revenue product is {top_revenue['Product']}. 
    The highest margin product is {top_margin['Product']} with {top_margin['Margin_%']:.1f}% margin.
    {high_return['Product']} needs attention because it has the highest return rate of {high_return['Return_Rate_%']:.1f}%.
    The best opportunity product based on scoring is {best_opportunity['Product']} with score {best_opportunity['Opportunity_Score']}/100.
    """
    st.markdown(f'<div class="summary">{summary_text}</div>', unsafe_allow_html=True)

    st.markdown("### AI Recommendation Engine")
    recommendations = [
        f"Prioritize {best_opportunity['Product']} because it has the best combined opportunity score.",
        f"Increase inventory and marketing focus on {top_revenue['Product']} because it drives highest revenue.",
        f"Promote {top_margin['Product']} because it improves profitability.",
        f"Investigate {high_return['Product']} due to high returns and possible customer dissatisfaction.",
        f"Check reviews of {low_rating['Product']} because it has the lowest rating.",
        "Use competitor price gap before launching discounts or price changes."
    ]

    for item in recommendations:
        st.markdown(f'<div class="reco">✅ {item}</div>', unsafe_allow_html=True)

    st.markdown("### Bundle Suggestions")
    for item in generate_bundle_suggestions(summary):
        st.markdown(f'<div class="gem">🎁 {item}</div>', unsafe_allow_html=True)

    report = make_excel_report(df, summary)
    st.download_button(
        label="📥 Download Excel Report",
        data=report,
        file_name="advanced_product_research_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

elif page == "Data Preview":
    st.markdown("### Cleaned Data")
    st.dataframe(df, use_container_width=True)
    st.markdown("### Product Summary")
    st.dataframe(summary, use_container_width=True)