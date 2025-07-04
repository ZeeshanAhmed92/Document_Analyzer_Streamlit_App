
import os
from extractors.pdf_extractor import extract_pdf_as_markdown, extract_docx_as_markdown
import numpy as np


def extract_file_as_markdown(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_pdf_as_markdown(file_path)
    elif ext == ".docx":
        return extract_docx_as_markdown(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def read_folder_and_join_markdown(folder_path, file_list=None):
    all_markdown = []
    normalized_file_list = set(os.path.normpath(f).lower() for f in file_list) if file_list else None

    for root, _, files in os.walk(folder_path):
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            if ext not in [".pdf", ".docx"]:
                continue

            file_path = os.path.join(root, filename)
            relative_path = os.path.relpath(file_path, folder_path)
            normalized_relative_path = os.path.normpath(relative_path).lower()

            if normalized_file_list and normalized_relative_path not in normalized_file_list:
                continue

            try:
                markdown = extract_file_as_markdown(file_path)
                all_markdown.append(f"## File: {relative_path}\n\n{markdown}")
            except Exception as e:
                print(f"❌ Error processing {file_path}: {e}")

    return "\n\n---\n\n".join(all_markdown)

def read_folder_and_join_markdown_exclude(folder_path, exclude_file_list=None):
    all_markdown = []
    normalized_exclude_list = set(os.path.normpath(f).lower() for f in exclude_file_list) if exclude_file_list else set()

    for root, _, files in os.walk(folder_path):
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            if ext not in [".pdf", ".docx"]:
                continue

            file_path = os.path.join(root, filename)
            relative_path = os.path.relpath(file_path, folder_path)
            normalized_relative_path = os.path.normpath(relative_path).lower()

            if normalized_relative_path in normalized_exclude_list:
                continue

            try:
                markdown = extract_file_as_markdown(file_path)
                all_markdown.append(f"## File: {relative_path}\n\n{markdown}")
            except Exception as e:
                print(f"❌ Error processing {file_path}: {e}")

    return "\n\n---\n\n".join(all_markdown)


def get_controls(controls):
    n = len(controls)
    part_size = n // 5
    remainder = n % 5

    # Calculate split indices
    sizes = [part_size + (1 if i < remainder else 0) for i in range(5)]
    indices = np.cumsum([0] + sizes)

    dfs = [controls.iloc[indices[i]:indices[i+1]].reset_index(drop=True) for i in range(5)]
    return dfs