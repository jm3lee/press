import json
import sys

from xmera.utils import read_json

from .render_template import create_env


def main():
    index_json = read_json(sys.argv[1])
    study_json = read_json(sys.argv[2])
    env = create_env()
    result = []
    for mc in study_json:
        q = mc["q"]
        q = env.from_string(q).render(**index_json)
        c = [env.from_string(c).render(**index_json) for c in mc["c"]]
        a = [mc["a"][0], env.from_string(mc["a"][1]).render(**index_json)]
        result.append({"q": q, "c": c, "a": a})
    print(json.dumps(result))


if __name__ == "__main__":
    main()
