from jsonschema import Draft3Validator
import simplejson as json
import os


class Validator:
    def __init__(self):
        self.validators = {}
        
    def try_load_scheme(self, folder, fname):
        try:
            with open(os.path.join(folder, fname)) as f:
                scheme = Draft3Validator(json.load(f))
            name = fname.split('.')[0]
        except:
            return
        self.validators[name] = scheme
        
    def init_app(self, app, path="."):    
        for fi in os.listdir(path):
            if fi.endswith(".json"):
                self.try_load_scheme(path, fi)
                
    def __call__(self, obj, schema, get_errors=False):
        if schema not in self.validators:
            raise Exception("Programmer error, schema does not exist: " + schema)
        try:
            self.validators[schema].validate(obj)
        except:
            if get_errors:
                return [error for error in sorted(self.validators[schema].iter_errors(obj), key=str)]
            return False
        return True
