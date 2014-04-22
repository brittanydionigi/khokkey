import pymongo

from pymongo import MongoClient
client = MongoClient()


def db_insert(table, data):
  try:
    table.insert(data)
  except pymongo.errors.DuplicateKeyError:
    print "Duplicate Key, Skipping for now"
  except pymongo.errors.OperationFailure:
    print "fail"