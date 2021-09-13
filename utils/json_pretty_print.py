import json

from deepdiff.model import PrettyOrderedSet


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (set, PrettyOrderedSet)):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


def dict_pretty_print(json_text):
    return json.dumps(json_text,
                      indent=4,
                      sort_keys=True,
                      default=SetEncoder,
                      ensure_ascii=False)


def json_pretty_print(json_text):
    return json.dumps(json.loads(json_text),
                      indent=4,
                      sort_keys=True,
                      default=SetEncoder,
                      ensure_ascii=False)
