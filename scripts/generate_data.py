# type: ignore

import json
import random
import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = '.data'
N = 10

def main():
    with open(f'{THIS_DIR}/objects.txt', 'r') as f:
        objects = f.readlines()
    with open(f'{THIS_DIR}/fields.txt', 'r') as f:
        fields = f.readlines()
    with open(f'{THIS_DIR}/values.txt', 'r') as f:
        values = f.readlines()

    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    def _gen(obj, n=0):
        for k in [o.strip() for o in random.choices(objects, k=N)]:
            obj[k] = {}
        for field in obj.keys():
            in_field = random.choice(fields).strip()
            if in_field in obj[field]:
                continue
            obj[field][in_field] = {}
            if n < 1 and random.randint(0, 1) == 0:
                if random.randint(0, 1) == 0:
                    obj[field][in_field] = _gen(obj[field][in_field], n=n+1)
                else:
                    obj[field][in_field] = [_gen({}, n=n+1)]
        return obj

    def _fill(obj, n=0):
        for k, v in obj.items():
            if isinstance(v, dict):
                if len(v.keys()) > 0:
                    obj[k] = _fill(v, n=n+1)
                else:
                    if random.randint(0, 2) == 0:
                        if random.randint(0, 1) == 0:
                            obj[k] = random.randint(-999, 999)
                        else:
                            obj[k] = random.uniform(-999, 999)
                    else:
                        obj[k] = random.choice(values).strip()
            elif isinstance(v, list):
                if len(v) > 0:
                    el = v[0]
                    for _ in range(random.randint(1, 5)):
                        v.append(el.copy())
                    for i in range(len(v)):
                        v[i] = _fill(v[i], n=n+1)

                else:
                    obj[k] = [_fill({}, n=n+1) for _ in range(random.randint(1, 5))]
        return obj
    
    struct = _gen({})

    for i in range(N):
        obj = json.loads(json.dumps(struct))
        obj = _fill(obj)

        with open(f'{OUTPUT_DIR}/object_{i}.json', 'w') as f:
            json.dump(obj, f, indent=4)
        

if __name__ == '__main__':
    main()
