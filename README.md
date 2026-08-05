# Neural XGBoost Disaster Prediction and Management

## Overview
The **Neural XGBoost Disaster Prediction and Management** system is a Django-based web application that predicts disaster types using a hybrid Machine Learning approach combining **Neural Networks** and **XGBoost**. The system analyzes disaster-related data to provide accurate predictions and helps users visualize model performance through graphs and accuracy comparisons.

---

## Features

- User Registration and Login
- Secure Authentication
- Disaster Prediction
- Dashboard
- Dataset Upload and Management
- Data Preprocessing
- SMOTE for Class Balancing
- Neural Network + XGBoost Hybrid Model
- Comparison with Existing Algorithms
  - Random Forest
  - Support Vector Machine (SVM)
  - Logistic Regression
- Accuracy Comparison
- Graphical Visualization
- User Profile Management

---

## Technologies Used

### Frontend
- HTML
- CSS
- JavaScript
- Bootstrap

### Backend
- Python
- Django

### Machine Learning
- PyTorch
- XGBoost
- Scikit-learn
- Pandas
- NumPy

### Database
- SQLite

---

## Project Structure

```
Source_Code/
│
├── admins/
├── agriculture_project/
├── disaster_app/
├── ml_models/
├── ml_models1/
├── ml_models2/
├── static/
├── templates/
├── users/
├── manage.py
└── requirements.txt
```

---

## Workflow

1. User Login
2. Dataset Upload
3. Data Preprocessing
4. SMOTE for Data Balancing
5. Feature Extraction using Neural Network
6. Disaster Prediction using XGBoost
7. Accuracy Evaluation
8. Graph Generation
9. Prediction Result Display

---

## Existing Algorithms

- Random Forest
- Support Vector Machine (SVM)
- Logistic Regression

---

## Proposed Algorithm

- Hybrid Neural Network + XGBoost

---

## Dataset

The project uses disaster-related datasets containing environmental and historical information such as rainfall, temperature, humidity, wind speed, and disaster categories.

---

## Future Enhancements

- Real-time weather data integration
- IoT sensor support
- GIS-based disaster visualization
- Mobile application support
- SMS and Email alerts
- Live disaster monitoring dashboard

---

## Installation

Clone the repository

```bash
git clone https://github.com/santoshiappanapalli/neural-xgboost-disaster-prediction-management.git
```

Go to the project directory

```bash
cd neural-xgboost-disaster-prediction-management
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the project

```bash
python manage.py runserver
```

Open your browser

```
http://127.0.0.1:8000/
```

---

## Author

**Appanapalli Santoshi**

Computer Science Engineering Student

GitHub:
https://github.com/santoshiappanapalli

---

## License

This project is developed for academic and educational purposes.
