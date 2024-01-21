import unittest
from gradescope_utils.autograder_utils.decorators import weight, number
import time, random, json
from pymongo.mongo_client import MongoClient


class TestLD(unittest.TestCase):

    def setUp(self): # Redacted for security
        self.URI = ...
        self.DB_NAME = ...
        self.COLLECTION_NAME = ...

    def get_late_days_by_netid(self, net_id):
        """
        Finds a student document in the students collection by netid.
        Uses a simple backoff system to ensure that the connection is made
        even under high load.
        With a maxPoolSize of 399, the maximum number of concurrent 
        connections that can be established to the MongoDB cluster 
        is limited to 399. This ensures that the number of connections
        does not exceed the limit of 500 and does not generate a warning
        (which occurs at 80% of max connections). This helps prevent connection 
        errors or performance degradation. When the function no longer
        needs the connection, it closes it, returning it to the pool.
        Short timeout (5 sec) helps reduce load on the cluster too.

        Parameters:
            net_id (str): NetID of student, like "kgwilson2"

        Returns:
            late_days (dict): late days dict if found
            None: if student is not found
        """

        max_attempts = 15
        for _ in range(max_attempts):
            time.sleep(random.uniform(0,2))
            try:
                client = MongoClient(
                    self.URI,
                    ssl=True,
                    tls=True,
                    tlsAllowInvalidCertificates=True,
                    maxPoolSize=399,
                    connectTimeoutMS=5000,
                    socketTimeoutMS=5000,
                    serverSelectionTimeoutMS=5000,
                )
                collection = client[self.DB_NAME][self.COLLECTION_NAME]
                student = collection.find_one({"net_id" : net_id})
                if student is None:
                    return {}
                else:
                    return student.get("late_days", {})

            except Exception:
                if client:
                    client.close()
                continue                
        print('Failed to connect to cluster and get late days. Please post on Piazza.')
        return None
        
    def get_netid(self):
        """
        get_student_emails() returns a list of emails of the students 
        listed in the submission's metadata.
        See https://gradescope-autograders.readthedocs.io/en/latest/submission_metadata/

        Returns:
            net_id (str): NetID of student, like "kgwilson2"
        """
        try:
            with open("/autograder/submission_metadata.json") as f:
                obj = json.load(f)
                return [dic["email"] for dic in obj["users"]][0].split('@')[0].lower()
        except:
            return "kgwilson2"

    def print_ld(self, late_days):
        """
        Prints out the late days in a column
        format like 
        P1 : 0
        P2 : 2
        . . .

        Parameters:
            late_days (dict): late days dictionary where keys are project
                numbers as strings and values are late days used as ints
                (note that late days can be recorded past 12 total so this 
                print statement should reflect that). Ex:
                {
                    '3': 1,
                    '7': 3
                }
        """
        print("Keep in mind that you cannot use more than 3 late days on a single project, and that you cannot use more than 12 late days total.")
        descriptors = ["P1","P2","P3","P4","P5","P6","P7","P8","P9","P10","P11","P12","P13"]
        total = 0
        exceeded_12 = False
        for i, descriptor in enumerate(descriptors):
            proj_num = str(i+1) # Important: project numbers are 1-indexed, and keys in MongoDB objects are strings
            if proj_num in late_days:
                ld = late_days[proj_num]
                total += ld
                if exceeded_12:
                    ld = 0
                elif total > 12:
                    ld = 12 - (total - ld)
                    exceeded_12 = True
            else:
                ld = 0
            
            print(f"{descriptor} : {ld}")

    @weight(0)
    @number("1.0")
    def test_get_ld(self):
        """
        Your used late days are shown below:
        """
        net_id = self.get_netid()
        print(f"Showing used late days for student with NetID: {net_id}.")
        late_days = self.get_late_days_by_netid(net_id)
        self.print_ld(late_days)

