# Late Day System for CS220

These are the local tests to make sure the MongoDB system is working correctly and accepting connections. It should help to troubleshoot any issues if something goes wrong. Please run these tests before testing with the system in docker_test on GradeScope.

## Installation

1. Install the required dependencies:

    ```bash
    python3.12 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2. Configure the MongoDB connection:

    Update the MongoDB connection string in a new `.env` file to point to your MongoDB instance so that it has the following text:

    ```
    URI=mongodb+srv://<user>:<password>@<cluster>.fr7f8yc.mongodb.net/?retryWrites=true&w=majority
    ```

3. Run the tests:

    ```bash
    pytest
    ```

## Status

As of 1/21/2024 before the Spring semester, all tests pass.
