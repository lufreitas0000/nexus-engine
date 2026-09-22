import streamlit as st
import os
import shutil
from pathlib import Path
from dotenv import load_dotenv, set_key
from pypdf import PdfReader

# Ensure absolute imports point from project root since streamlit runs from there.
from src.converter.epub_converter import convert_markdown_to_epub
from src.dispatcher.config import load_smtp_config, SmtpConfig
from src.dispatcher.mailer import dispatch_artifact_to_kindle
from src.optimizer.domain.types import OptimizerConfig
from src.optimizer.domain.registry import KINDLE_MODELS
from src.optimizer.services.orchestrator import optimize_pdf_for_oasis

def load_environment():
    load_dotenv(override=True)

def save_environment(env_vars: dict):
    env_path = Path('.env')
    if not env_path.exists():
        env_path.touch()

    for key, value in env_vars.items():
        set_key(env_path, key, value)

    load_environment()

def setup_sidebar():
    st.sidebar.title("Settings Module")

    with st.sidebar.expander("SMTP & Dispatch Configuration", expanded=True):
        load_environment()

        host = st.text_input("SMTP Host", value=os.getenv("SMTP_HOST", "smtp.gmail.com"))
        port = st.text_input("SMTP Port", value=os.getenv("SMTP_PORT", "587"))
        sender = st.text_input("Sender Email", value=os.getenv("SMTP_USER", ""))
        password = st.text_input("App Password", value=os.getenv("SMTP_PASSWORD", ""), type="password")
        destination = st.text_input("Send-to-Kindle Email", value=os.getenv("KINDLE_EMAIL", ""))

        if st.button("Save Settings"):
            env_vars = {
                "SMTP_HOST": host,
                "SMTP_PORT": port,
                "SMTP_USER": sender,
                "SMTP_PASSWORD": password,
                "KINDLE_EMAIL": destination
            }
            save_environment(env_vars)
            st.sidebar.success("Settings Saved!")

def execute_pipeline(file_bytes, file_name, selected_model):
    temp_dir = Path("temp_upload")
    temp_dir.mkdir(exist_ok=True)
    temp_file_path = temp_dir / file_name

    with open(temp_file_path, "wb") as f:
        f.write(file_bytes)

    artifacts_dir = Path("artifacts").resolve()
    artifacts_dir.mkdir(exist_ok=True)

    artifacts_to_dispatch = []
    target_hardware = KINDLE_MODELS[selected_model]

    try:
        config = load_smtp_config()
    except Exception as e:
        st.error(f"Configuration Error: {str(e)}\nPlease check your SMTP Settings in the sidebar.")
        return

    try:
        if temp_file_path.suffix.lower() == '.md':
            st.info(f"Initiating EPUB compilation pipeline for: {temp_file_path.name}")
            artifacts_to_dispatch.append(convert_markdown_to_epub(temp_file_path, hardware_constraints=target_hardware))

        elif temp_file_path.suffix.lower() == '.pdf':
            st.info(f"Initiating PDF optimization pipeline for: {temp_file_path.name}")
            opt_config = OptimizerConfig(
                binary_path=os.getenv('K2PDFOPT_PATH', 'k2pdfopt'),
                hardware=target_hardware
            )
            artifacts_to_dispatch.extend(optimize_pdf_for_oasis(temp_file_path, opt_config))
        else:
            st.error(f"Unsupported file extension: {temp_file_path.suffix}")
            return

        archived_paths = []
        for artifact in artifacts_to_dispatch:
            archived_path = artifacts_dir / artifact.name
            shutil.move(str(artifact), str(archived_path))
            archived_paths.append(archived_path)

            size_mb = archived_path.stat().st_size / (1024 * 1024)
            pages = len(PdfReader(archived_path).pages) if archived_path.suffix.lower() == '.pdf' else "N/A"
            st.write(f"- File: {archived_path.name} | Pages: {pages} | Size: {size_mb:.2f} MB")

        st.info(f"Initializing network dispatch to {config.destination}...")
        for artifact in archived_paths:
            dispatch_artifact_to_kindle(artifact, config)

        st.success("Pipeline execution complete. Artifacts dispatched!")

    except Exception as execution_error:
        st.error(f"Pipeline Terminated with Exception:\n{execution_error}")
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


def main():
    st.set_page_config(page_title="Kindle Artifact Pipeline", layout="wide")
    st.title("📚 Kindle Artifact Pipeline")

    setup_sidebar()

    st.header("Execution Dashboard")

    uploaded_file = st.file_uploader("Upload a document (.md or .pdf)", type=["md", "pdf"])
    selected_model = st.selectbox("Select Target Kindle Model", options=list(KINDLE_MODELS.keys()), index=0)

    if uploaded_file is not None:
        if st.button("Process and Dispatch"):
            with st.spinner("Processing..."):
                execute_pipeline(uploaded_file.getvalue(), uploaded_file.name, selected_model)

if __name__ == "__main__":
    main()
