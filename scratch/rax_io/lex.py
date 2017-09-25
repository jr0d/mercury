import json
from pygments import highlight, lexers, formatters


def format_json(data):
    return highlight(json.dumps(data, sort_keys=True, indent=4),
                     lexers.JsonLexer(), formatters.TerminalFormatter())


def jq(data):
    print(format_json(data))


def pause():
    input('=> ')
