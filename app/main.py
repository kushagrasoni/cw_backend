import sys
import uuid
import pandas as pd

import uvicorn
from fastapi import FastAPI, UploadFile, File, Request, Response, HTTPException, Form

import os

from fastapi.middleware.cors import CORSMiddleware

from app.services import azure_openai, openai_api



app = FastAPI()

origins = ["http://localhost:3000"]  # Replace with allowed origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Allow cookies and other credentials
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...),
                      target_table: str = Form(...)):
    """
    Uploads a CSV file, processes it, generates PySpark code using OpenAI,
    and saves the code to a temporary file.

    Parameters:
        file (UploadFile): The uploaded CSV file.
        target_table (Form): The Target Table Name

    Returns:
        dict: A response containing the generated code preview and additional information.
    """

    try:
        # Process CSV
        source_tables, source_columns, transformations, target_columns = process_csv(file)

        # Generate prompt for OpenAI
        prompt = generate_prompt(source_tables, source_columns, transformations, target_table, target_columns)

        print(prompt)

        # Use direct OpenAI to generate PySpark code
        # pyspark_code = openai_api.get_output(prompt)

        # Use Azure OpenAI to generate PySpark Code
        pyspark_code = azure_openai.get_output(prompt)

        print(f"PySpark Code Generate: \n\n{pyspark_code}")

        # Create a unique filename for the generated code
        filename = f"generated_code.code"

        # Save PySpark code to a temporary file
        with open(f"app/data/code/{filename}", "w") as f:
            f.write(pyspark_code)

        return {
            'prompt': prompt,
            "code": pyspark_code,
            "filename": filename,
        }

        # return {
        #     "prompt": prompt,
        # }

    except Exception as e:
        print(f"Error uploading file and generating code: {e}")
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        raise HTTPException(status_code=422,
                            detail=f"Error uploading file and generating code: {e}"
                            )


@app.get("/api/retrieve")
async def retrieve_code():
    """
    Retrieves the generated PySpark code from a temporary file.

    Parameters:
        filename (str): The filename of the generated code.

    Returns:
        str: The PySpark code, or an error message if the file is not found.
    """
    filename = f"generated_code.code"

    try:
        with open(f"app/data/code/{filename}", "r") as f:
            code = f.read()
        return {"code": code}

    except FileNotFoundError:
        return Response(content="Generated code not found", status_code=404)


# Helper functions to process CSV, generate prompt, and implement more features
def process_csv(file: UploadFile):
    """Processes a CSV file using Pandas and extracts relevant data.

    Args:
        file: An UploadFile object representing the uploaded CSV file.

    Returns:
        tuple: A tuple containing lists of source tables, source columns,
            transformations, and target columns, extracted from the CSV.

    Raises:
        ValueError: If the CSV file is empty or invalid.
        Exception: If any other error occurs during processing.
    """

    try:
        # Read CSV content into a Pandas DataFrame
        df = pd.read_csv(file.file)

        # Check for empty DataFrame
        if df.empty:
            raise ValueError("Empty or invalid CSV data.")

        # Extract relevant columns
        source_tables = df["Source Table"].tolist()
        source_columns = df["Source Attribute"].tolist()
        transformations = df["Transformation"].tolist()
        target_columns = df["Target attribute"].tolist()

        return source_tables, source_columns, transformations, target_columns

    except Exception as e:
        print(f"Error processing CSV file: {e}")
        raise  # Re-raise the exception for proper handling in the API endpoint


def generate_prompt(source_tables, source_columns, transformations, target_table, target_columns):
    # Construct a clear and concise prompt for OpenAI
    # Consider including relevant information like table names, column names,
    # and desired transformations
    prompt = f"Write PySpark code to transform data from the following tables and corresponding columns " \
             f"and then write the transformed data it into a Hive table named '{target_table}':\n"
    for i in range(len(source_tables)):
        prompt += f"- {source_tables[i]}.{source_columns[i]}\n"
    prompt += "\nApply the following transformations:\n"
    for i in range(len(transformations)):
        prompt += f"- {transformations[i]}\n"
    prompt += "\nAnd store the results in the following columns:\n"
    for i in range(len(target_columns)):
        prompt += f"- {target_columns[i]}\n"
    return prompt


def write_code_to_file(pyspark_code):
    """
    Writes PySpark code to a secure location.

    Args:
        pyspark_code (str): The PySpark code to be written.

    Returns:
        bool: True if the code was written successfully, False otherwise.
    """

    try:
        # Create a secure directory for generated code (consider access control)
        base_dir = "app/data/code"
        os.makedirs(base_dir, exist_ok=True)

        # Generate a random filename to avoid conflicts
        filename = f"{uuid.uuid4()}.py"
        filepath = os.path.join(base_dir, filename)

        # Write PySpark code to the file with appropriate permissions
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(pyspark_code)
            os.chmod(filepath, 0o600)  # Set file permissions to owner-read/write only

        print(f"PySpark code written to: {filepath}")
        return True

    except Exception as e:
        print(f"Error writing code: {e}")
        return False


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=5000)
