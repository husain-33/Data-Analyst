# Sounce Product Research Automation Web App - Advanced Version

This is a proper business web app for electronics e-commerce product research automation.

## Added Advanced Features
1. Competitor Opportunity Detector
2. Customer Review Analyzer
3. AI Recommendation Engine
4. Dead Product Detector
5. Hidden Gem Detector
6. Bundle Suggestions
7. Executive Summary
8. Lifecycle Tags

## What it does
The company uploads CSV data and the app automatically:
- Cleans data
- Calculates KPIs
- Shows sales and revenue dashboard
- Compares competitor pricing
- Detects risky/dead products
- Finds hidden gem products
- Analyzes review sentiment
- Suggests product bundles
- Generates executive summary
- Tags product lifecycle
- Exports Excel report

## Required CSV columns
Date, Product, Category, Selling_Price, Cost_Price, Units_Sold, Units_Returned, Rating, Competitor_Price

## Optional CSV column
Review_Text

## How to run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Interview explanation
I built this as a business automation tool for an electronics e-commerce company. The user can upload product data and the app automatically generates product research metrics, competitor insights, review analysis and recommendations.