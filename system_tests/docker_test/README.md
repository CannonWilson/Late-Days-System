# Docker Test

## Description

This folder contains the code to concurrently test the 
recording of late days for many simultaneous late submissions.
This is important because re-running the autograder can cause
many submissions to be made at once. To run the test, 
update the due date of an existing assignment on GradeScope 
(preferably for a past semester) and use the `get_ld_ag.zip` file
as the autograder.

## Content

This folder contains the following files and directories:

- `README.md`: This file provides an overview of the repository.
- `setup.sh`: This file is run when setting up the Docker image for the autograder. It installs Python and pip and then installs all of the dependencies in `requirements.txt`.
- `requirements.txt`: Contains all of the pip packages used by the project.
- `run_autograder`: Triggered by GradeScope whenever a submission is made.
- `run_tests.py`: Runs the tests in the `tests` directory using GradeScope's JSONTestRunner
- `tests/test_ld.py`: The only test in the project. It connects to MongoDB, gets the student's late days, and prints them out in a nice format.
- `get_ld_ag.zip`: The .zip file for uploading to GradeScope as an autograder for an assignment. It is the zipped contents of this folder.

## Notes

If things stop working, check that the database name and the collection name 
in `tests/test_ld.py` in the setUp function are accurate. You'll need to change 
the URI if you make any changes to the user on MongoDB or if you drop 
any database.
