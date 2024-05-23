
from boltdb import BoltDB


def add_bucket(tx, data):
    for k, v in data.items():
        print(isinstance(v, dict))
        if isinstance(v, dict):
            b = tx.create_bucket(k.encode("utf-8"))
            print('creating bucket', k)
            add_bucket(b, v)
        else:
            tx.put(k.encode(), str(v).encode())


def post_to_db(data):
    db = BoltDB("sample_bolt.db")
    with db.update() as tx:
        id = data['@odata.id']
        b = tx.create_bucket(id.encode("utf-8"))
        add_bucket(b, data)


def extract_bucket(b):
    result = {}
    for k, v in b:
        print(k, v)
        if not v:
            if b.bucket(k):
                result[k.decode('utf-8')] = extract_bucket(b.bucket(k))
            else:
                result[k.decode('utf-8')] = None
        else:
            result[k.decode('utf-8')] = v.decode('utf-8') if v else None

    return result

def get_from_db(data_id=None):
    db = BoltDB("sample_bolt.db")
    result = {}
    with db.view() as tx:
        b = tx.bucket(data_id.encode())
        result = extract_bucket(b)            
        return result