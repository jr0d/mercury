import bson

from mercury.common.mongo import get_collection


def convert_all_cpu():
    collection = get_collection('mercury', 'inventory')
    c = collection.find({})
    for i in c:
        old_cpu = i.get('cpu')
        if old_cpu and isinstance(old_cpu, dict):
            collection.update_one(
                {'_id': bson.ObjectId(i['_id'])}, {'$set': {'cpu': convert_cpu(old_cpu)}})


def convert_cpu(old_cpu):
    new_cpu = list(old_cpu.values())
    new_cpu.sort(key=lambda k: k['physical_id'])
    return new_cpu
