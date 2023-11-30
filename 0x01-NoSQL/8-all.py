#!/usr/bin/env python3
"""8. List all documents in Python
"""
from pymongo import MongoClient


def list_all(mongo_collection):
    """lists all documents in a collection
    """
    docs = mongo_collection.find()

    return docs if len(docs) >= 0 else []
