import boto3
from trp import Document
import json
from dotenv import load_dotenv
import os
from PyPDF2 import PdfReader, PdfWriter
from fileReader import temporary_folder_path
from awsextractParser import extract_text
from textractor import Textractor
from textractor.data.constants import TextractFeatures
from textractor.data.text_linearization_config import TextLinearizationConfig


def split_pdf_into_pages(folder_path, file_name):
    output_folder_path = temporary_folder_path(folder_name="output_pages")

    # Read the input PDF
    reader = PdfReader(os.path.join(folder_path, file_name))
    base_file_name = file_name.split(".")[0]
    print(file_name)
    print(base_file_name)

    output_paths = []
    for i, page in enumerate(reader.pages, start=1):
        writer = PdfWriter()
        writer.add_page(page)

        # Save the single-page PDF
        output_pdf_path = os.path.join(
            output_folder_path, f"{base_file_name}_page_{i}.pdf"
        )
        with open(output_pdf_path, "wb") as out_file:
            writer.write(out_file)
            output_paths.append((output_pdf_path, f"{base_file_name}_page_{i}"))

    return output_paths


def awsextract_pdf(folder_path, file_name):
    load_dotenv()
    client = boto3.client(
        "textract",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name="us-east-1",
    )

    splitted_pdf_files = split_pdf_into_pages(folder_path, file_name)

    output_folder_path = temporary_folder_path(folder_name="output_pages")
    for file in splitted_pdf_files:
        with open(file[0], "rb") as document:
            response = client.analyze_document(
                Document={
                    "Bytes": document.read(),
                },
                FeatureTypes=["TABLES", "FORMS", "LAYOUT"],
            )
        raw_text = extract_text(response, extract_by="LINE")

        with open(os.path.join(output_folder_path, f"{file[1]}.txt"), "w") as text_file:
            text_file.write(("\n").join(raw_text))
            text_file.close()


## Test Call
# awsextract_pdf(
#     "C:\\Users\\skhan\\Documents\\GITHUB\\LANGCHAIN\\Data_Loader", "resume.pdf"
# )


def textractor_pdf(file_path):

    extractor = Textractor(profile_name="ml_user")

    config = TextLinearizationConfig(
        hide_figure_layout=True, title_prefix="# ", section_header_prefix="## "
    )

    document = extractor.analyze_document(
        file_source=file_path, features=[TextractFeatures.LAYOUT], save_image=True
    )

    return document.get_text(config=config)


# file_path = "C:\\Users\\skhan\\Documents\\GITHUB\\LANGCHAIN\\Data_Loader\\pipeline\\output_pages\\resume_page_1.pdf"
# textractor_pdf(file_path)
