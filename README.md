# AWS S3 Storage Shell (S5)

This is a Python-based shell for interacting with AWS S3 storage.

## Prerequisites

- Python 3.10.2 installed
- AWS CLI configured with the necessary permissions
- S5-S3.conf is configured for your IAM user and is located in root directory of this project

## Setup

1. (Optional) Create a virtual environment:

   ```bash
   python3 -m venv venv
   ```

2. Activate the virtual environment:

   - On Windows:

     ```bash
     .\venv\Scripts\activate
     ```

   - On Unix or MacOS:

     ```bash
     source venv/bin/activate
     ```

3. Install boto3 and ensure AWS CLI is installed:

   ```bash
   pip install boto3
   ```

4. Run the S3 Storage Shell:

   ```bash
   python3 s5_shell.py
   ```

5. (Optional) Deactivate the virtual environment:

   ```bash
   deactivate
   ```

## Usage

- Use the provided commands within the shell to interact with your AWS S3 storage.
- Follow the on-screen instructions and command syntax.

## Notes

- Make sure your AWS CLI is properly configured with the necessary permissions.
- If using a virtual environment, activate it before running the shell.
- Make an S5-S3.conf file is created and stored in the root directory of the project and is configured for your IAM user
