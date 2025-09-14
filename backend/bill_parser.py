import json

def parse_bill(path):
    with open(path, "r") as f:
        bill = json.load(f)
    return bill