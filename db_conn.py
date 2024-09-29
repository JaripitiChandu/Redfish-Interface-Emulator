import json
from pprint import pprint

from boltdb import BoltDB
from boltdb.bucket import Bucket


class DataBase(BoltDB):
    """
    A class representing a database wrapper for BoltDB.

    Attributes:
        db_filepath (str): The file path to the BoltDB database.
    """

    def __init__(self, db_filepath) -> None:
        """
        Initializes the DataBase object.

        Args:
            db_filepath (str): The file path to the BoltDB database.
        """
        super().__init__(db_filepath)

    def add_bucket(self, tx, data):
        """
        Recursively adds data to the BoltDB bucket.

        Args:
            tx (Transaction): The transaction object.
            data (dict): The data to be added to the bucket.
        """
        for k, v in data.items():
            if isinstance(v, dict):
                # If value is a dictionary, create a new bucket and add its contents
                b = tx.create_bucket(k.encode("utf-8"))
                self.add_bucket(b, v)
            else:
                # If value is not a dictionary, store it as key-value pair
                tx.put(k.encode(), str(v).encode())

    def post_to_db(self, data):
        """
        Posts data to the database.

        Args:
            data (dict): The data to be posted to the database.
        """
        with self.update() as tx:
            id = data['@odata.id']
            b = tx.create_bucket(id.encode("utf-8"))
            self.add_bucket(b, data)

    def extract_bucket(self, b):
        """
        Recursively extracts data from a bucket.

        Args:
            b (Bucket): The bucket from which data is to be extracted.

        Returns:
            dict: The extracted data from the bucket.
        """
        result = {}
        for k, v in b:
            if not v:
                if b.bucket(k):
                    result[k.decode('utf-8')] = self.extract_bucket(b.bucket(k))
                else:
                    result[k.decode('utf-8')] = None
            else:
                result[k.decode('utf-8')] = v.decode('utf-8') if v else None
        return result

    def get_from_db(self, data_id=None):
        """
        Retrieves data from the database.

        Args:
            data_id (str, optional): The ID of the data to be retrieved. Defaults to None.

        Returns:
            dict: The retrieved data from the database.
        """
        result = {}
        with self.view() as tx:
            b = tx.bucket(data_id.encode())
            if not b:
                return
            result = self.extract_bucket(b)            
            return result


    def print_db(self, bucket: Bucket = None):
        elbow = "└──"
        pipe = "│  "
        tee = "├──"
        blank = "   "
        def print_subbucket(b, name, last=True, header=''):

            # print(lenb)
            print((header + (elbow if last else tee) + name))
            if isinstance(b, Bucket):
                lenb = 0
                for k,_ in b:
                    lenb+=1
                for i, (k, _) in enumerate(b):
                    if isinstance(b.bucket(k), Bucket):
                        print_subbucket(b.bucket(k), k.decode(), header = header + (blank if last else pipe), last= i == lenb-1)
                    else:                        
                        # print(header + (elbow if last else tee), f"{k.decode()} -> index")
                        print_subbucket(k.decode(), k.decode(), header = header + (blank if last else pipe), last= i == lenb-1)

        with self.view() as tx:
            if bucket:
                print_subbucket(bucket, "bucket")
            else:
                print_subbucket(tx.bucket(), "root")
