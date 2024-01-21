# Late Days System Tests

These are the tests for a late day system implementation for UW-Madison's CS220 introductory data science course. The system tracks late days using MongoDB and incorporates a backoff strategy to handle a high volume of student submissions.
This project consists of two main components: `docker_test` and `local_tests`.


## Features

- MongoDB Integration: The system utilizes MongoDB as the database to store and manage late day information for students.
- Backoff Strategy: The system implements a backoff strategy to handle up to 1000 late student submissions at one time, ensuring that the system stays within the specified limits of 500 active connections and under 100 CRUD ops/sec.


## Contents

The `docker_test` component is a test that is used as a Docker image on GradeScope when creating an autograder for an assignment. The purpose of this test is to update the late days used for 1000+ late assignments. This test ensures that our late days system can scale to handle many late assignments for a given project.

Please follow the instructions below to run the tests:

1. Run the `local_tests` component first to verify the functionality of the MongoDB database.
2. Once the `local_tests` pass successfully, proceed to run the `docker_test` component by downloading the autograder .zip file and uploading it on GradeScope.
3. Monitor the execution of the `docker_test` component on MongoDB Atlas and check the graded student submissions to ensure that the late days for all the late assignments are updated correctly.

For any issues or questions related to this project, please check the late days docs on our Google Drive and then reach out to the project team for assistance.
