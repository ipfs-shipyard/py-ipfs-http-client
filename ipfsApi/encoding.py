import json



class Encoding(object):
    
    def parse(self, string):
        raise NotImplemented

    def encode(self, obj):
        raise NotImplemented


class Json(object):
    name = 'json'

    def __init__(self):
        self.encoder = json.JSONEncoder()
        self.decoder = json.JSONDecoder()

    def parse(self, json_string):
        results = []

        obj, idx = self.decoder.raw_decode(json_string)
        results.append(obj)
        cur = idx
        while cur < len(json_string)-1:
            obj, idx = self.decoder.raw_decode(json_string[cur:])
            results.append(obj) 
            cur += idx

        if len(results)==1:
            return results[0]
        return results


class Protobuf(Encoding):
    pass



__encodings = {
        'json': Json
        }

def get_encoding(name):
    try:
        return __encodings[name.lower()]()
    except KeyError:
        return None
