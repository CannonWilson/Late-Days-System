# Repository Documentation

## Description

This is the code for the Docker Image used as the autograder for 
the Get Late Days assignment for CS220. To deploy it, create a new assignment
on GradeScope that is open for the duration of the course, 
and then upload the .zip file in this folder (or create a new .zip file if you have
changed the contents of this project), as the autograder for the
assignment. Students will be able to submit anything to the 
assignment and get back how many late days they have used this semester.
Student privacy is protected by using the submission metadata from 
GradeScope in order to verify the student's email/NetID.

## Contents

This project contains the following files and directories:

- `README.md`: This file provides an overview of the repository.
- `setup.sh`: This file is run when setting up the Docker image for the autograder. It installs Python and pip and then installs all of the dependencies in `requirements.txt`.
- `requirements.txt`: Contains all of the pip packages used by the project.
- `run_autograder`: Triggered by GradeScope whenever a submission is made.
- `run_tests.py`: Runs the tests in the `tests` directory using GradeScope's JSONTestRunner
- `tests/test_ld.py`: The only test in the project. It connects to MongoDB, gets the student's late days, and prints them out in a nice format.
- `ld_ag.zip`: The autograder .zip file.

## Notes

If things stop working, check that the database name and the collection name 
in `tests/test_ld.py` in the setUp function are accurate. You'll need to change 
the URI if you make any changes to the uwcs220 user on MongoDB or if you drop 
any database.
