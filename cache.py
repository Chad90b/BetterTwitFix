from configHandler import config
import pymongo
from datetime import date,datetime
import json
import os

link_cache_system = config['config']['link_cache']

if link_cache_system == "json":
    link_cache = {}
    if not os.path.exists("links.json"):
        with open("links.json", "w") as outfile:
            default_link_cache = {}
            json.dump(default_link_cache, outfile)
    try:
        f = open('links.json',)
        link_cache = json.load(f)
    except json.decoder.JSONDecodeError:
        print(" ➤ [ X ] Failed to load cache JSON file. Creating new file.")
        link_cache = {}
    except FileNotFoundError:
        print(" ➤ [ X ] Failed to load cache JSON file. Creating new file.")
        link_cache = {}
    finally:
        f.close()
        
elif link_cache_system == "db":
    client = pymongo.MongoClient(config['config']['database'], connect=False)
    table = config['config']['table']
    db = client[table]

def serializeUnknown(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

def addVnfToLinkCache(video_link, vnf):
    try:
        if link_cache_system == "db":
                out = db.linkCache.insert_one(vnf)
                print(" ➤ [ + ] Link added to DB cache ")
                return True
        elif link_cache_system == "json":
            link_cache[video_link] = vnf
            with open("links.json", "w") as outfile: 
                json.dump(link_cache, outfile, indent=4, sort_keys=True, default=serializeUnknown)
                return None
    except Exception:
        print(" ➤ [ X ] Failed to add link to DB cache")
        return None

def getVnfFromLinkCache(video_link):
    if link_cache_system == "db":
        collection = db.linkCache
        vnf        = collection.find_one({'tweet': video_link})
        # print(vnf)
        if vnf != None: 
            hits   = ( vnf['hits'] + 1 ) 
            print(" ➤ [ ✔ ] Link located in DB cache. " + "hits on this link so far: [" + str(hits) + "]")
            query  = { 'tweet': video_link }
            change = { "$set" : { "hits" : hits } }
            out    = db.linkCache.update_one(query, change)
            return vnf
        else:
            print(" ➤ [ X ] Link not in DB cache")
            return None
    elif link_cache_system == "json":
        if video_link in link_cache:
            print("Link located in json cache")
            vnf = link_cache[video_link]
            return vnf
        else:
            print(" ➤ [ X ] Link not in json cache")
            return None
    elif link_cache_system == "none":
        return None