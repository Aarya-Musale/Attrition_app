import streamlit as st
import pandas as pd
import pickle

# Page configuration
st.set_page_config(
    page_title="IBM Employee Attrition Predictor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load the saved model and encoders safely using pickle
@st.cache_resource
def load_artifacts():
    with open('attrition_model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('encoders.pkl', 'rb') as f:
        encoders = pickle.load(f)
    return model, encoders

model, encoders = load_artifacts()

# Initialize session state for tracking session history/statistics
if 'total_preds' not in st.session_state:
    st.session_state.total_preds = 0
if 'high_risk_count' not in st.session_state:
    st.session_state.high_risk_count = 0

# --- SIDEBAR DESIGN ---
with st.sidebar:
    st.markdown("### 🛡️ IBM Attrition Predictor")
    st.markdown("---")
    
    # Model status badge look
    st.success("🟢 Model Loaded & Online")
    
    with st.expander("📁 Feature Descriptions"):
        st.write("This application uses a trained Random Forest classifier to analyze employee parameters and forecast potential turnover risks.")
    
    st.markdown("---")
    st.markdown("### 📊 Session Statistics")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.metric("Total", st.session_state.total_preds)
    with col_s2:
        st.metric("High Risk", st.session_state.high_risk_count)
    
    if st.session_state.total_preds > 0:
        risk_rate = (st.session_state.high_risk_count / st.session_state.total_preds) * 100
        st.caption(f"Attrition Alert Rate: {risk_rate:.1f}%")
    else:
        st.caption("Attrition Alert Rate: N/A")
        
    st.markdown("---")
    
    # Clear history button matching the style
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.total_preds = 0
        st.session_state.high_risk_count = 0
        st.rerun()
        
    st.markdown("---")
    st.caption("v1.0.0 • Built with ❤️ using Streamlit")

# --- MAIN HERO BANNER SECTION ---
st.markdown("""
    <div style="padding: 30px 20px; background: linear-gradient(135deg, #1f1c2c 0%, #928dab 100%); border-radius: 15px; text-align: center; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
        <h1 style="color: white; font-size: 2.5rem; margin-bottom: 10px;">⚡ IBM Employee Attrition Predictor</h1>
        <p style="color: #e0e0e0; font-size: 1.1rem; max-width: 700px; margin: 0 auto;">
            Leverage machine learning to instantly predict whether an employee is likely to <b>stay</b> or <b>leave</b> based on key profile data.
        </p>
        <div style="margin-top: 15px;">
            <span style="background-color: rgba(40, 167, 69, 0.2); color: #28a745; padding: 5px 15px; border-radius: 20px; font-size: 0.85rem; border: 1px solid #28a745;">
                🟢 Model Online – Ready for Predictions
            </span>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- APPLICANT / EMPLOYEE DETAILS FORM LAYOUT ---
st.markdown("### 📝 Employee Details")

col1, col2, col3 = st.columns(3)

with col1:
    age = st.number_input("Age", min_value=18, max_value=70, value=30)
    department = st.selectbox("Department", encoders['Department'].classes_)
    distance_from_home = st.slider("Distance From Home (Miles)", min_value=1, max_value=30, value=5)

with col2:
    education = st.selectbox("Education Level (1-5)", [1, 2, 3, 4, 5])
    education_field = st.selectbox("Education Field", encoders['EducationField'].classes_)
    env_satisfaction = st.slider("Environment Satisfaction (1-4)", min_value=1, max_value=4, value=3)

with col3:
    job_satisfaction = st.slider("Job Satisfaction (1-4)", min_value=1, max_value=4, value=3)
    marital_status = st.selectbox("Marital Status", encoders['MaritalStatus'].classes_)
    monthly_income = st.number_input("Monthly Income ($)", min_value=1000, max_value=25000, value=5000)

col4, col5, col6 = st.columns(3)
with col4:
    num_companies = st.number_input("Number of Companies Worked", min_value=0, max_value=10, value=1)
with col5:
    work_life_balance = st.slider("Work Life Balance (1-4)", min_value=1, max_value=4, value=3)
with col6:
    years_at_company = st.number_input("Years At Company", min_value=0, max_value=40, value=2)

st.markdown("---")

# --- PREDICTION ACTION TRIGGER ---
if st.button("🚀 Run Attrition Prediction", use_container_width=True):
    # Transform categories for model prediction
    input_data = pd.DataFrame({
        'Age': [age],
        'Department': [encoders['Department'].transform([department])[0]],
        'DistanceFromHome': [distance_from_home],
        'Education': [education],
        'EducationField': [encoders['EducationField'].transform([education_field])[0]],
        'EnvironmentSatisfaction': [env_satisfaction],
        'JobSatisfaction': [job_satisfaction],
        'MaritalStatus': [encoders['MaritalStatus'].transform([marital_status])[0]],
        'MonthlyIncome': [monthly_income],
        'NumCompaniesWorked': [num_companies],
        'WorkLifeBalance': [work_life_balance],
        'YearsAtCompany': [years_at_company]
    })

    # Update Session tracking metrics
    st.session_state.total_preds += 1
    
    prediction = model.predict(input_data)[0]
    prediction_proba = model.predict_proba(input_data)[0][1]

    st.markdown("---")
    st.subheader("📊 Diagnostic Outcome")

    res_c1, res_c2 = st.columns([2, 1])

    with res_c1:
        if prediction == 1:
            st.session_state.high_risk_count += 1
            st.error(f"⚠️ **High Risk of Attrition:** This profile exhibits key turnover indicators. The model estimates a **{prediction_proba * 100:.2f}% probability** that this employee will leave.")
            st.markdown("💡 **Actionable Insight:** Consider reviewing compensation alignment, career pathing, or conducting an immediate one-on-one engagement check-in.")
        else:
            st.success(f"✅ **Low Risk of Attrition:** This profile matches patterns typical of retained workers. The model estimates a **{(1 - prediction_proba) * 100:.2f}% probability** that this employee will stay.")
            st.markdown("💡 **Actionable Insight:** Employee stability indicators look healthy. Maintain standard recognition practices.")

    with res_c2:
        st.markdown("#### Risk Confidence Index")
        st.progress(float(prediction_proba))
        st.caption(f"Score Value: {prediction_proba:.4f}")