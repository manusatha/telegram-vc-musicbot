from pymongo import MongoClient
from config import MONGO_URI

mongo = MongoClient(MONGO_URI)
db = mongo.musicbot

chats = db.chats
history = db.history
