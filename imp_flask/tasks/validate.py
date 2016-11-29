import jsonschema
import simplejson as json


def validate(obj, schemafile):
    with open("validators/"+schemafile+".json") as f:
        schema = json.load(f)
    jsonschema.validate(obj, schema)