# -*- coding: utf-8 -*-

import csv
import json
import sys


def produce_key(*args):
    """
    Produce key.
    Returns:
        str: key
    """
    key = ""
    for arg in args:
        if arg == "":
            break
        key += arg + "."

    if key.endswith('.'):
        key = key[:-1]
    return key


def make_key_value_pair(key, value):
    """
    Make key value pair.
        key (str): Key
        value (str): Value
    Returns:
        dict: Key-value pair.
    """
    return key, {"tr": key + " - " + value, "en": ""}

if __name__ == "__main__":
    """
        Pass an arg to script for filename.
    """
    if len(sys.argv) >= 2:
        csv_file_name = sys.argv[1]
    else:
        raise ValueError("Please, enter a valid file.")

    json_payload = {"tasinir_kodlari": {}}

    with open(csv_file_name) as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')

        for row in reader:
            key = produce_key(*row[:-1])
            value = row[-1]
            payload = make_key_value_pair(key, value)
            json_payload["tasinir_kodlari"][payload[0]] = payload[1]

    fp = open("tasinir_kodlari.json", "w")
    fp.write(json.dumps(json_payload))
    fp.close()
