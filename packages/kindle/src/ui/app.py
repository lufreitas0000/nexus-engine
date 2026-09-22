import streamlit as st
import os
import shutil
from pathlib import Path
from dotenv import load_dotenv, set_key

# Ensure absolute imports point from project root since streamlit runs from there.
from src.converter.epub_converter import convert_markdown_to_epub
from src.dispatcher.config import load_smtp_config
from src.dispatcher.mailer import dispatch_artifact_to_kindle
from src.domain.registry import KINDLE_MODELS


def load_environment():
    load_dotenv(override=True)


def save_environment(env_vars: dict):
    env_path = Path(".env")
    if not env_path.exists():
        env_path.touch()

    for key, value in env_vars.items():
        set_key(env_path, key, value)

    load_environment()


def setup_sidebar():
    st.sidebar.title("Settings Module")

    with st.sidebar.expander("SMTP & Dispatch Configuration", expanded=True):
        load_environment()

        host = st.text_input(
            "SMTP Host", value=os.getenv("SMTP_HOST", "smtp.gmail.com")
        )
        port = st.text_input("SMTP Port", value=os.getenv("SMTP_PORT", "587"))
        sender = st.text_input("Sender Email", value=os.getenv("SMTP_USER", ""))
        password = st.text_input(
            "App Password", value=os.getenv("SMTP_PASSWORD", ""), type="password"
        )
        destination = st.text_input(
            "Send-to-Kindle Email", value=os.getenv("KINDLE_EMAIL", "")
        )

        if st.button("Save Settings"):
            env_vars = {
                "SMTP_HOST": host,
                "SMTP_PORT": port,
                "SMTP_USER": sender,
                "SMTP_PASSWORD": password,
                "KINDLE_EMAIL": destination,
            }
            save_environment(env_vars)
            st.sidebar.success("Settings Saved!")


def main():
    st.set_page_config(page_title="Kindle Artifact Pipeline", layout="wide")
    st.title("📚 Kindle Artifact Pipeline")

    setup_sidebar()

    # Session State Initialization
    if "step" not in st.session_state:
        st.session_state.step = 1
    if "md_content" not in st.session_state:
        st.session_state.md_content = ""
    if "original_filename" not in st.session_state:
        st.session_state.original_filename = ""

    st.header("Execution Dashboard")

    if st.session_state.step == 1:
        st.subheader("Step 1: Upload Document")
        uploaded_file = st.file_uploader(
            "Upload a document (.md or .pdf)", type=["md", "pdf"]
        )
        selected_model = st.selectbox(
            "Select Target Kindle Model", options=list(KINDLE_MODELS.keys()), index=0
        )

        if uploaded_file is not None:
            if st.button("Process Document"):
                st.session_state.original_filename = uploaded_file.name
                st.session_state.selected_model = selected_model

                temp_dir = Path("temp_upload")
                temp_dir.mkdir(exist_ok=True)
                temp_file_path = temp_dir / uploaded_file.name

                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getvalue())

                if temp_file_path.suffix.lower() == ".pdf":
                    with st.spinner("Converting PDF to Markdown using spliter..."):
                        try:
                            from src.converter.spliter_integration import (
                                convert_pdf_to_md,
                            )

                            md_path = convert_pdf_to_md(temp_file_path)
                            with open(md_path, "r", encoding="utf-8") as f:
                                st.session_state.md_content = f.read()
                            st.session_state.step = 2
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error during PDF conversion: {e}")
                elif temp_file_path.suffix.lower() == ".md":
                    with open(temp_file_path, "r", encoding="utf-8") as f:
                        st.session_state.md_content = f.read()
                    st.session_state.step = 2
                    st.rerun()

    elif st.session_state.step == 2:
        st.subheader("Step 2: Intermediate Review")
        st.info("Review and edit the extracted Markdown before compiling to EPUB.")

        edited_md = st.text_area(
            "Markdown Content", value=st.session_state.md_content, height=400
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Compile and Dispatch"):
                st.session_state.md_content = edited_md
                st.session_state.step = 3
                st.rerun()
        with col2:
            if st.button("Cancel & Start Over"):
                st.session_state.step = 1
                st.session_state.md_content = ""
                st.session_state.original_filename = ""
                st.rerun()

    elif st.session_state.step == 3:
        st.subheader("Step 3: Compiling and Dispatching")

        temp_dir = Path("temp_upload")
        temp_dir.mkdir(exist_ok=True)
        md_filename = Path(st.session_state.original_filename).with_suffix(".md").name
        md_file_path = temp_dir / md_filename

        with open(md_file_path, "w", encoding="utf-8") as f:
            f.write(st.session_state.md_content)

        artifacts_dir = Path("artifacts").resolve()
        artifacts_dir.mkdir(exist_ok=True)

        target_hardware = KINDLE_MODELS[st.session_state.selected_model]

        try:
            config = load_smtp_config()
        except Exception as e:
            st.error(
                f"Configuration Error: {str(e)}\nPlease check your SMTP Settings in the sidebar."
            )
            if st.button("Back"):
                st.session_state.step = 2
                st.rerun()
            return

        with st.spinner("Compiling EPUB..."):
            try:
                epub_path_temp = convert_markdown_to_epub(
                    md_file_path, hardware_constraints=target_hardware
                )
                archived_path = artifacts_dir / epub_path_temp.name
                shutil.move(str(epub_path_temp), str(archived_path))

                size_mb = archived_path.stat().st_size / (1024 * 1024)
                st.write(
                    f"- Compiled Artifact: {archived_path.name} | Size: {size_mb:.2f} MB"
                )

                with st.spinner(f"Dispatching to {config.destination}..."):
                    dispatch_artifact_to_kindle(archived_path, config)

                st.success("Pipeline execution complete. Artifacts dispatched!")

                if st.button("Start Over"):
                    st.session_state.step = 1
                    st.session_state.md_content = ""
                    st.session_state.original_filename = ""
                    if temp_dir.exists():
                        shutil.rmtree(temp_dir)
                    st.rerun()

            except Exception as e:
                st.error(f"Pipeline Terminated with Exception:\n{e}")
                if st.button("Back"):
                    st.session_state.step = 2
                    st.rerun()


if __name__ == "__main__":
    main()
