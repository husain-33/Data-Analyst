# 📊 Customer Churn Prediction (Logistic Regression)

This project predicts whether a customer will churn (i.e., stop using a service) based on their service usage, demographics, and account details. The goal is to help telecom companies retain valuable customers by identifying who is at risk of leaving.

---

## 🧠 Problem Statement
Customer churn is a major issue for subscription-based services. Identifying which customers are likely to leave allows companies to take action — offering discounts, personalized support, or special offers to keep them.

---

## 📂 Dataset
- **Source**: `Telecom.csv`
- **Features**: Tenure, MonthlyCharges, Contract, TechSupport, InternetService, etc.
- **Target**: `Churn` (Yes = 1, No = 0)

---

## 🛠️ Tools & Technologies
- **Python**
- **Pandas, NumPy** for data manipulation
- **Matplotlib, Seaborn** for data visualization
- **Scikit-learn** for logistic regression and evaluation
- **Jupyter Notebook** for development

---

## 🔍 EDA Highlights
- Explored the correlation between churn and features like contract type, support, and charges
- Identified patterns indicating that month-to-month contracts and higher charges lead to higher churn

---

## 🧪 Model
- **Logistic Regression** was used for binary classification
- Model was trained and tested on an 80/20 split of the data
- Evaluation was done using accuracy, confusion matrix, and classification report

---

## 📈 Results
- Achieved ~80% accuracy
- Found that customers with short tenure, no tech support, and high charges are more likely to churn

---

## 🚀 Future Improvements
- Test other models like Random Forest and XGBoost
- Handle class imbalance with SMOTE
- Deploy using Streamlit or Flask

---

## 📌 How to Use
Clone this repo, install dependencies from `requirements.txt`, and run the Jupyter notebook.

---

## 🤝 Connect with Me
Feel free to connect or follow for more machine learning projects!


