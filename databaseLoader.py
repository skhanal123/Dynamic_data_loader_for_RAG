import os
import json
from os.path import isfile, join
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
import hashlib
import shutil
from fileReader import (
    pdf_reader,
    docx_reader,
    pptx_reader,
    txt_reader,
    xlsx_reader,
    temporary_folder_path,
)


def get_embeddings():
    embeddings = OpenAIEmbeddings(api_key=os.environ["OPENAI_API_KEY"])
    return embeddings


def get_db_client(folder_path):
    data_folder = os.path.basename(folder_path)
    persistent_directory = os.path.join("databases", data_folder)

    vectordb_client = Chroma(
        persist_directory=persistent_directory,
    )

    return vectordb_client


def load_file_by_file(dbName, folder_path):
    onlyfiles = [
        file for file in os.listdir(folder_path) if isfile(join(folder_path, file))
    ]

    for file_name in onlyfiles:
        load_file_to_db(folder_path, file_name, dbName)


def load_file_to_db(folder_path, file_name, dbName):
    """
    Read file based on the extention and load the content
    to db
    """
    file_path = join(folder_path, file_name)
    if file_name.endswith(".pdf"):
        documents = pdf_reader(file_path, file_name)
    elif file_name.endswith(".pptx"):
        documents = pptx_reader(file_path, file_name)
    elif file_name.endswith(".docx"):
        documents = docx_reader(file_path, file_name)
    elif file_name.endswith(".txt"):
        documents = txt_reader(file_path, file_name)
    elif file_name.endswith(".xlsx"):
        documents = xlsx_reader(file_path, file_name)

    load_db(documents, file_name, dbName)


def load_db(documents, file_name, dbName):
    embeddings = get_embeddings()

    number_of_documents = len(documents)
    doc_hash_values_list = create_filename_hash(number_of_documents, file_name)

    # data_folder = os.path.basename(folder_path)
    persistent_directory = os.path.join("databases", dbName)

    batch_size = 5
    for i in range(0, len(documents), batch_size):
        if i + batch_size < len(documents):
            Chroma.from_documents(
                documents[i : i + batch_size],
                ids=doc_hash_values_list[i : i + batch_size],
                persist_directory=persistent_directory,
                embedding=embeddings,
            )
        else:
            Chroma.from_documents(
                documents[i : len(documents) + 1],
                ids=doc_hash_values_list[i : len(documents) + 1],
                persist_directory=persistent_directory,
                embedding=embeddings,
            )

    datapipeline_path = os.path.join("pipeline", dbName)
    temporary_path = temporary_folder_path()

    if not os.path.isdir(datapipeline_path):
        os.mkdir(datapipeline_path)

    for file_name in os.listdir(temporary_path):
        shutil.move(os.path.join(temporary_path, file_name), datapipeline_path)


def create_filename_hash(number_of_documents, file_name):
    """
    Obtain hash value of the file based on its name
    It is used to track document and provide id in the db
    It is also used to update the db
    """
    hash_value = hashlib.sha256(file_name.encode()).hexdigest()
    hash_value_list = [f"{hash_value}_{i}" for i in range(number_of_documents)]
    return hash_value_list


def track_database(databaseName, folderPath):

    databaseRecord = {databaseName: folderPath}

    if not os.path.isdir("dataTracker"):
        os.makedir("dataTracker")

    if os.path.isfile(os.path.join("dataTracker", "databaseTracker.json")):
        with open(
            os.path.join("dataTracker", "databaseTracker.json"), "r+"
        ) as database_file:
            data = json.load(database_file)
            data.update(databaseRecord)

        with open(
            os.path.join("dataTracker", "databaseTracker.json"), "w"
        ) as database_file:
            json.dump(data, database_file)

    else:
        with open(
            os.path.join("dataTracker", "databaseTracker.json"), "w"
        ) as database_file:
            json.dump(databaseRecord, database_file)


def get_database_records():
    if os.path.isfile(os.path.join("dataTracker", "databaseTracker.json")):
        with open(
            os.path.join("dataTracker", "databaseTracker.json"), "r+"
        ) as database_file:
            data = json.load(database_file)

        return data
    else:
        return None
