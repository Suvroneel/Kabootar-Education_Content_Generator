"""
Kabootar - Educational Content Generator
Multi-Agent System for generating and reviewing educational content
"""

import streamlit as st
import json
import time
import os

from agents.generator_agent import GeneratorAgent
from agents.reviewer_agent import ReviewerAgent
from utils.analytics import AnalyticsTracker
from utils.export import ContentExporter
from utils.validator import AdvancedValidator

# Page config
st.set_page_config(
    page_title="Kabootar ",
    page_icon="assets/logo.png",
    layout="centered"
)

# Custom CSS with global scaling (simulating 125%-150% zoom feeling) and permanent light mode
st.markdown("""
    <style>
    :root {
        color-scheme: light;
    }
    .stApp {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-size: 1.15rem !important; /* Global scale-up for 125%+ feeling */
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Wider Centered Layout Container for zoomed presence */
    .centered-container {
        max-width: 860px;
        margin: 0 auto;
        padding: 0 1.5rem;
    }

    /* Hero Header */
    .hero-section {
        text-align: center;
        padding: 3.5rem 0 2rem 0;
    }
    .hero-badge {
        display: inline-block;
        background-color: #fff4f0;
        color: #ff751f;
        font-size: 0.95rem;
        font-weight: 600;
        padding: 0.35rem 0.9rem;
        border-radius: 20px;
        border: 1px solid #ffd8cc;
        margin-bottom: 1.2rem;
    }
    .hero-title {
        font-size: 3.5rem !important;
        font-weight: 800;
        color: #1a1a1a;
        letter-spacing: -1px;
        margin: 0 0 0.5rem 0;
    }
    .hero-subtitle {
        font-size: 1.25rem !important;
        color: #586069;
        line-height: 1.5;
        margin: 0;
    }

    /* Section Titles */
    .section-title {
        font-size: 1.35rem !important;
        font-weight: 700;
        color: #1a1a1a;
        margin-top: 2.5rem;
        margin-bottom: 0.85rem;
    }

    /* Streamlit Input Labels & Fields scaling */
    .stSelectbox label, .stTextInput label {
        font-size: 1.05rem !important;
        font-weight: 600 !important;
    }

    /* Primary Button Styling */
    div.stButton > button:first-child {
        background-color: #ff751f;
        color: white;
        font-weight: 700;
        border: none;
        border-radius: 10px;
        padding: 0.9rem 1.8rem;
        width: 100%;
        font-size: 1.15rem !important;
        box-shadow: 0 3px 8px rgba(255, 117, 31, 0.25);
        transition: all 0.2s ease;
        margin-top: 1.2rem;
    }
    div.stButton > button:first-child:hover {
        background-color: #e56717;
        box-shadow: 0 5px 14px rgba(255, 117, 31, 0.35);
        color: white;
    }

    /* Results Elements */
    .mcq-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        margin: 1.2rem 0;
        border-radius: 10px;
        border: 1px solid #e1e4e8;
    }
    .correct-badge {
        background-color: #e6f4ea;
        color: #137333;
        padding: 0.4rem 0.85rem;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
        margin-top: 0.85rem;
        font-size: 1rem !important;
    }
    .status-pass {
        color: #137333;
        background-color: #e6f4ea;
        padding: 0.3rem 0.85rem;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
    }
    .status-fail {
        color: #c5221f;
        background-color: #fce8e6;
        padding: 0.3rem 0.85rem;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
    }
    .feedback-box {
        background-color: #fff8f5;
        border-left: 4px solid #ff751f;
        padding: 0.85rem 1.2rem;
        margin: 0.6rem 0;
        border-radius: 0 6px 6px 0;
        font-size: 1.05rem !important;
        color: #333333;
    }

    /* Workflow Cards */
    .workflow-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.2rem;
        margin-top: 1.5rem;
    }
    .workflow-step {
        background: #f8f9fa;
        border: 1px solid #e1e4e8;
        border-radius: 10px;
        padding: 1.5rem;
    }
    .step-number {
        color: #ff751f;
        font-weight: 800;
        font-size: 1rem;
        margin-bottom: 0.3rem;
    }
    .step-title {
        font-weight: 700;
        font-size: 1.1rem;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }
    .step-desc {
        color: #586069;
        font-size: 0.95rem;
        line-height: 1.4;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'generator' not in st.session_state:
    st.session_state.generator = GeneratorAgent()
if 'reviewer' not in st.session_state:
    st.session_state.reviewer = ReviewerAgent()
if 'analytics' not in st.session_state:
    st.session_state.analytics = AnalyticsTracker()
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = None
if 'review_result' not in st.session_state:
    st.session_state.review_result = None
if 'refined_content' not in st.session_state:
    st.session_state.refined_content = None
if 'refined_review' not in st.session_state:
    st.session_state.refined_review = None
if 'advanced_validation' not in st.session_state:
    st.session_state.advanced_validation = None


def display_content(content, title="Generated Content"):
    st.markdown(f"### {title}")
    st.markdown("#### Explanation")
    st.write(content['explanation'])
    st.markdown("---")
    st.markdown("#### Assessment Questions")
    for i, mcq in enumerate(content['mcqs'], 1):
        st.markdown(f'<div class="mcq-box">', unsafe_allow_html=True)
        st.markdown(f"**Question {i}: {mcq['question']}**")
        for option in mcq['options']:
            st.write(f"   {option}")
        st.markdown(f'<div class="correct-badge">Correct Answer: {mcq["answer"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


def display_review(review, title="Review Evaluation"):
    st.markdown(f"### {title}")
    status = review['status']
    if status == "pass":
        st.markdown('<div class="status-pass">Status: PASS</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-fail">Status: FAIL</div>', unsafe_allow_html=True)

    st.markdown("<br>#### Evaluator Feedback", unsafe_allow_html=True)
    for feedback_item in review['feedback']:
        st.markdown(f'<div class="feedback-box">{feedback_item}</div>', unsafe_allow_html=True)


# Main Centered Wrapper
st.markdown('<div class="centered-container">', unsafe_allow_html=True)

# Hero Header with Logo & Title centered block
col_logo, col_title = st.columns([1, 5], gap="small")
with col_logo:
    logo_path = "assets/logo.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=95)
    else:
        st.markdown("<div style='font-size: 3rem; text-align: right;'>🦉</div>", unsafe_allow_html=True)

with col_title:
    st.markdown("""
        <div style="padding-top: 0.3rem;">
            <h1 style="font-size: 3rem; font-weight: 800; color: #1a1a1a; margin: 0; letter-spacing: -0.5px; line-height: 1.1;">Kabootar</h1>
            <p style="font-size: 1.1rem; color: #586069; margin: 0.3rem 0 0 0;">Your 24x7 intelligent AI question bank and content generator.</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin: 2.5rem 0; border: none; border-top: 1px solid #eaecef;'>", unsafe_allow_html=True)

# Generation Parameters Form Section
st.markdown('<div class="section-title">Configure Parameters</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    grade = st.selectbox(
        "Select Grade Level",
        options=list(range(1, 13)),
        index=3,
        help="Target student grade level (Grades 1 to 12)"
    )

with col2:
    common_topics = [
        "Custom (type your own)",
        "Types of angles",
        "Photosynthesis",
        "Fractions and decimals",
        "Water cycle",
        "Solar system",
        "Parts of speech",
        "Addition and subtraction",
        "Pythagorean theorem",
        "Food chains"
    ]

    selected_topic = st.selectbox(
        "Select Topic",
        options=common_topics,
        help="Choose a pre-defined topic or select custom entry"
    )

if selected_topic == "Custom (type your own)":
    topic = st.text_input(
        "Enter Custom Topic",
        value="",
        placeholder="e.g., Quantum computing basics"
    )
else:
    topic = selected_topic

generate_clicked = st.button("Generate Educational Content")

# Pipeline Execution Handler
if generate_clicked:
    if not topic.strip():
        st.error("Please enter a valid topic before running the generator.")
    else:
        start_time = time.time()

        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text("Generator Agent is structuring content...")
        progress_bar.progress(25)

        gen_start = time.time()
        with st.spinner("Generating core content..."):
            generated_content = st.session_state.generator.generate_content(grade, topic)
            st.session_state.generated_content = generated_content
        gen_time = time.time() - gen_start

        progress_bar.progress(50)

        status_text.text("Reviewer Agent is auditing quality and age-appropriateness...")
        review_start = time.time()
        with st.spinner("Running quality checks..."):
            review_result = st.session_state.reviewer.review_content(
                generated_content, grade, topic
            )
            st.session_state.review_result = review_result
        review_time = time.time() - review_start

        advanced_val = AdvancedValidator.comprehensive_validation(
            generated_content, grade, topic
        )
        st.session_state.advanced_validation = advanced_val

        progress_bar.progress(75)

        refinement_needed = review_result['status'] == 'fail'
        refinement_improved = None

        if refinement_needed:
            status_text.text("Refining content based on evaluator feedback...")
            with st.spinner("Refining content..."):
                feedback_list = review_result['feedback']
                refined_content = st.session_state.generator.generate_content(
                    grade, topic, feedback=feedback_list
                )
                st.session_state.refined_content = refined_content

                refined_review = st.session_state.reviewer.review_content(
                    refined_content, grade, topic
                )
                st.session_state.refined_review = refined_review
                refinement_improved = refined_review['status'] == 'pass'

        progress_bar.progress(100)
        status_text.text("Execution complete")
        total_time = time.time() - start_time

        st.session_state.analytics.log_session({
            "grade": grade,
            "topic": topic,
            "generation_time": gen_time,
            "review_time": review_time,
            "total_time": total_time,
            "review_status": review_result['status'],
            "feedback_count": len(review_result.get('feedback', [])),
            "refinement_needed": refinement_needed,
            "refinement_improved": refinement_improved,
            "mcq_count": len(generated_content.get('mcqs', [])),
            "explanation_length": len(generated_content.get('explanation', ''))
        })

        st.success(f"Content generation completed successfully in {total_time:.2f}s")

# Results Display Section
if st.session_state.generated_content is not None:
    st.markdown("<hr style='margin: 3rem 0; border: none; border-top: 1px solid #eaecef;'>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "Generated Content",
        "Review & Feedback",
        "Refinement Loop",
        "Advanced Metrics"
    ])

    exporter = ContentExporter()

    with tab1:
        display_content(st.session_state.generated_content, "Primary Content Package")

        st.markdown("<br><h4>Export Options</h4>", unsafe_allow_html=True)
        export_cols = st.columns(4)

        with export_cols[0]:
            st.download_button(
                label="JSON",
                data=exporter.to_json(st.session_state.generated_content, {"grade": grade, "topic": topic}),
                file_name=f"content_grade{grade}_{topic.replace(' ', '_')}.json",
                mime="application/json",
                use_container_width=True
            )
        with export_cols[1]:
            st.download_button(
                label="Text",
                data=exporter.to_text(st.session_state.generated_content, grade, topic),
                file_name=f"content_grade{grade}_{topic.replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with export_cols[2]:
            st.download_button(
                label="Markdown",
                data=exporter.to_markdown(st.session_state.generated_content, grade, topic,
                                          st.session_state.review_result),
                file_name=f"content_grade{grade}_{topic.replace(' ', '_')}.md",
                mime="application/markdown",
                use_container_width=True
            )
        with export_cols[3]:
            st.download_button(
                label="Study Guide",
                data=exporter.to_study_guide(st.session_state.generated_content, grade, topic),
                file_name=f"study_guide_grade{grade}_{topic.replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )

    with tab2:
        if st.session_state.review_result is not None:
            display_review(st.session_state.review_result, "Quality Audit Report")

    with tab3:
        if st.session_state.refined_content is not None:
            st.info("Content was automatically adjusted based on the Reviewer Agent's feedback loop.")
            col_ref1, col_ref2 = st.columns(2)
            with col_ref1:
                display_content(st.session_state.refined_content, "Refined Content Version")
            with col_ref2:
                if st.session_state.refined_review is not None:
                    display_review(st.session_state.refined_review, "Final Review Status")
        else:
            st.success("No refinement needed. Initial generation successfully passed all quality checks.")

    with tab4:
        if st.session_state.advanced_validation is not None:
            st.markdown("### Advanced Quality Validation Metrics")
            validation = st.session_state.advanced_validation
            if validation['valid']:
                st.success("Passed all NLP and structural validation gates.")
            else:
                st.warning("Some validation checks flagged warnings.")

            for check_name, check_data in validation.get('checks', {}).items():
                display_name = check_name.replace('_', ' ').title()
                if check_data.get('passed', False):
                    st.write(f"Passed: {display_name}")
                else:
                    st.write(f"Review: {display_name}")

# Analytics Section
if st.session_state.analytics.get_statistics()['total_generations'] > 0:
    st.markdown("<hr style='margin: 3rem 0; border: none; border-top: 1px solid #eaecef;'>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">System Performance Analytics</div>', unsafe_allow_html=True)
    stats = st.session_state.analytics.get_statistics()

    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    with stat_col1:
        st.metric("Total Generations", stats['total_generations'])
    with stat_col2:
        st.metric("Pass Rate", f"{stats['pass_rate']:.1f}%")
    with stat_col3:
        st.metric("Avg Generation Time", f"{stats['avg_generation_time']:.1f}s")
    with stat_col4:
        st.metric("Refinement Rate", f"{stats['refinement_rate']:.1f}%")

# How It Works Explanation Section
st.markdown("<hr style='margin: 3rem 0; border: none; border-top: 1px solid #eaecef;'>", unsafe_allow_html=True)
st.markdown(
    '<div class="section-title" style="text-align: center; margin-bottom: 1.5rem;">How Kabootar Works Behind the Scenes</div>',
    unsafe_allow_html=True)

st.markdown("""
    <div class="workflow-grid">
        <div class="workflow-step">
            <div class="step-number">01</div>
            <div class="step-title">Generator Agent</div>
            <div class="step-desc">Accepts parameters to build custom prompts via Hugging Face inference models.</div>
        </div>
        <div class="workflow-step">
            <div class="step-number">02</div>
            <div class="step-title">Reviewer Agent</div>
            <div class="step-desc">Validates vocabulary complexity, structural integrity, and MCQ accuracy.</div>
        </div>
        <div class="workflow-step">
            <div class="step-number">03</div>
            <div class="step-title">Refinement Loop</div>
            <div class="step-desc">Channels feedback back into the generator model for optimized output quality.</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Footer
# Footer
st.markdown("""
<div style='text-align: center; color: #6a737d; padding: 3rem 0 2rem 0; font-size: 0.95rem; line-height: 1.6;'>
    <p style='margin-bottom: 0.4rem; color: #1a1a1a; font-weight: 500;'>
        Enjoying Kabootar? Support the project by giving it a star on 
        <a href="https://github.com/Suvroneel/Kabootar-Educational-Content-Generator" target="_blank" style="color: #ff751f; font-weight: 700; text-decoration: none;">GitHub</a>.
    </p>
    <p style='margin: 0; font-size: 0.85rem; color: #8c959f;'>
        Kabootar Multi-Agent Educational Content Generator | 100% Free & Open Source
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
