import streamlit as st
from analyzer import ResumeAnalyzer

st.set_page_config(page_title="Dual ATS Analyzer", layout="wide")
st.title("📊 Dual ATS Resume Analyzer")

analyzer = ResumeAnalyzer()

# ---------- UI Inputs ----------
mode = st.radio(
    "Select ATS Analysis Mode",
    ["Resume Only (No Job Description)", "Resume vs Job Description"]
)

uploaded_resume = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

job_description = ""
if mode == "Resume vs Job Description":
    job_description = st.text_area(
        "Paste Job Description",
        height=250,
        placeholder="Paste target job description here..."
    )

# ---------- Run Analysis ----------
if st.button("🚀 Run ATS Analysis"):

    if not uploaded_resume:
        st.warning("Please upload your resume.")
        st.stop()


    try:
        resume_text = analyzer.extract_text_from_pdf(uploaded_resume)
    except ValueError as e:
        st.error(str(e))
        st.stop()


    with st.spinner("Running ATS evaluation..."):

        if mode == "Resume Only (No Job Description)":
            result = analyzer.analyze_resume_only(resume_text)

        else:
            if not job_description:
                st.warning("Please provide a job description.")
                st.stop()
            result = analyzer.analyze_with_job_description(resume_text, job_description)

    # ---------- Results ----------
    st.divider()
    score = result["overall_ats_score"]

    st.header(f"Overall ATS Score: {score}%")
    st.progress(score / 100)

    st.subheader("📊 Parameter Breakdown")
    st.bar_chart(result["parameter_breakdown"])

    # ---------- Insights ----------
    st.divider()

    if result["mode"] == "resume_vs_jd":
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("❌ Missing Keywords")
            if result["missing_keywords"]:
                for kw in result["missing_keywords"]:
                    st.error(kw)
            else:
                st.success("No major keywords missing 🎯")

        with col2:
            st.subheader("📝 Action Plan")
            for step in result["action_plan"]:
                st.write(f"👉 {step}")

    else:
        st.subheader("🛠 Improvement Suggestions")
        for tip in result["improvement_suggestions"]:
            st.write(f"👉 {tip}")
