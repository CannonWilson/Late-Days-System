import json, datetime, time, random, math
from pymongo import MongoClient, ReturnDocument

# Redacted for security
URI = ...
DB_NAME = ...
COLLECTION_NAME = ...
FILE = "P8.ipynb"

def get_num_late_days():
    '''get_num_late_days() returns the datetime difference between the due date of the assignment and
    the time of the submission.
    NOTE: If the submission time is past the due date, the value returned by 
    the get_num_late_days() function will be negative.
    '''
    try:
        with open("/autograder/submission_metadata.json") as f:
            obj = json.load(f)
            submission_time = obj["created_at"].split(".")[0]
            due_time = obj["assignment"]["due_date"].split(".")[0]
            submission_datetime = datetime.datetime.strptime(submission_time,"%Y-%m-%dT%H:%M:%S")
            due_datetime = datetime.datetime.strptime(due_time,"%Y-%m-%dT%H:%M:%S")
            return (due_datetime - submission_datetime)
    except:
        return datetime.timedelta(0)
    
def get_student_emails():
    '''get_student_emails() returns a list of emails of the students listed in the submission's metadata.
    See https://gradescope-autograders.readthedocs.io/en/latest/submission_metadata/'''
    try:
        with open("/autograder/submission_metadata.json") as f:
            obj = json.load(f)
            return [dic["email"] for dic in obj["users"]]
    except:
        return ['amaran@wisc.edu']
    
def update_late_days(netid, proj_num, ld_used):
    """
    Creates a connection to the MongoDB cluster and updates
    the student's late days with a backoff strategy.
    With a maxPoolSize of 399, the maximum number of concurrent 
    connections that can be established to the MongoDB cluster 
    is limited to 399. This ensures that the number of connections
    does not exceed the limit of 500 and does not generate a warning
    (which occurs at 80% of max connections). This helps prevent connection 
    errors or performance degradation. When the function no longer
    needs the connection, it closes it, returning it to the pool.
    Short timeout (5 sec) helps reduce load on the cluster too.

    Parameters:
        netid (str): student whose late days should be updated
        proj_num (int): index of project to update, i.e. 3 for P3
        ld_used (int): number of late days used for project

    Returns:
        late_days (dict): late days dictionary where keys are project
                numbers as ints and values are late days used as ints
                (note that late days can be recorded past 12 total.)
                {
                    '3': 1,
                    '7': 3
                }
        None: if operation fails
    """
    
    max_attempts = 15
    filter_query = {"net_id": netid}
    update_query = {
        "$set": {f"late_days.{proj_num}": ld_used}
    }
    options = {
        "upsert": True,
        "return_document": ReturnDocument.AFTER
    }
    for _ in range(max_attempts):
        time.sleep(random.uniform(1,7))
        try:
            client = MongoClient(
                URI,
                ssl=True,
                tls=True,
                tlsAllowInvalidCertificates=True,
                maxPoolSize=399,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000,
                serverSelectionTimeoutMS=5000,
            )
            collection = client[DB_NAME][COLLECTION_NAME]
            result = collection.find_one_and_update(
                filter_query,
                update_query,
                **options
            )
            return result.get("late_days") if result else None
        except Exception as e:
            print(e)
            if client:
                client.close()
            continue                
    print('Failed to connect to MongoDB Cluster and update late days.')
    return None

def per_student_ld_deduction(netid):
    """
    Given the netID of a student, return the 
    number of uncovered late days that student has used.
    
    Note that the entries in the late_days property
    of the documents in the ld collection in the 
    students database range from 0 to 3 but they can 
    total more than 12. For example, this is a valid 
    document for a student who used 3 late days
    for P2, P3, P4,and P5 and who just submitted
    P6 2 days late:
        {_id: 65ac76e188b4edf2556cb1de,
        net_id: "kgwilson2",
        late_days: {
            2 : 3,
            3 : 3,
            4 : 3,
            5 : 3,
            6 : 2
        }
    In the above case, the 2 late days for P6 will be 
    recorded as 'used' in the database but we handle that 
    in this function so that they are uncovered late days
    that get deducted. 

    Parameters:
        netid (str): the netID of the student

    Returns:
        int: the number of uncovered late days used by the 
            student (0 if something went wrong)
    """
    project_name = FILE.split(".")[0].upper() # like "P2"
    project_num = int(project_name[1:]) # like 2
    
    # Calculate the time difference
    time_diff = get_num_late_days()
    
    # Check if  submission is on time (late submissions have negative time_diff)
    if time_diff.total_seconds() >= 0:
        # Submission is on time, no deductions
        return 0
    
    # If the project is late, update the student's late days
    days_late = math.ceil(-time_diff.total_seconds() / (24 * 3600)) 
    days_used = min(days_late, 3)

    # Update the ld collection on MongoDB
    updated_ld_dict = update_late_days(netid, project_num, days_used)
    if updated_ld_dict is None:
        return 0 # Something went wrong, don't make a deduction
    
    # If the student has used more than 12 late days total, 
    # that means the uncovered_ld needs to be increased.
    uncovered_ld = max(days_late - 3, 0)
    sum_ld_used = sum(updated_ld_dict.values())
    if sum_ld_used > 12:
        uncovered_ld += min(sum_ld_used - 12, days_used)

    return uncovered_ld


def update_late_day_deduction():
    """
    Calculates the late day deduction for each
    student based on the number of late days
    they used. 

    Parameters:
        total_score (int): Total score of the assignment

    Returns:
        (float): Late day deduction
    """
    # Get student info
    submission_emails = get_student_emails()
    student_netids = [email.split("@")[0].lower() for email in submission_emails]

    ld_deducs = []
    for netid in student_netids:
        uncovered_ld = per_student_ld_deduction(netid)
        ld_deducs.append(0.05 * uncovered_ld)
    
    if len(ld_deducs) > 0:
        return min(ld_deducs)
    else: 
        return 0 # Something went wrong, don't make a deduction