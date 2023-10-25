# type: ignore

import json
import random
import os
import datetime

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = '.data'
N = 10
MAX_DEPTH = 1
MAX_ARRAY_LEN = 4
DROP_CHANCE = 6

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
            obj[field] = {}
            if n < MAX_DEPTH and random.randint(0, 1) == 0:
                if random.randint(0, 1) == 0:
                    obj[field] = _gen(obj[field], n=n+1)
                else:
                    obj[field] = [_gen({}, n=n+1)]
        
        return obj

    def _fill(obj, n=0):
        drop_q = []
        for k, v in obj.items():
            if isinstance(v, dict):
                if random.randint(0, DROP_CHANCE) == 0:
                    drop_q.append(k)
                    continue
                if len(v.keys()) > 0:
                    obj[k] = _fill(v, n=n+1)
                else:
                    type = random.randint(0, 5)
                    if type == 0:
                        obj[k] = random.randint(-999, 999)
                    elif type == 1:
                        obj[k] = random.uniform(-999, 999)
                    elif type == 2:
                        obj[k] = random.choice(values).strip()
                    elif type == 3:
                        obj[k] = random.randint(0, 1) == 0
                    elif type == 4:
                        obj[k] = None
                    elif type == 5:
                        if random.randint(0, 1) == 0:
                            obj[k] = datetime.datetime.now().isoformat()
                        else:
                            obj[k] = datetime.datetime.now().time().isoformat()
            elif isinstance(v, list):
                if len(v) > 0:
                    el = v[0]
                    for _ in range(random.randint(0, MAX_ARRAY_LEN)):
                        v.append(el.copy())
                    for i in range(len(v)):
                        v[i] = _fill(v[i], n=n+1)

                else:
                    obj[k] = [_fill({}, n=n+1) for _ in range(random.randint(1, 5))]
        
        for k in drop_q:
            del obj[k]

        return obj
    
    struct = _gen({})

    for i in range(N):
        obj = json.loads(json.dumps(struct))
        obj = _fill(obj)

        with open(f'{OUTPUT_DIR}/object_{i}.json', 'w') as f:
            json.dump({
                'data': obj,
                'metadata': {
                    'id': i,
                    'name': f'Object {i}',
                    'generated_at': datetime.datetime.now().isoformat(),
                }
            }, f, indent=4)
        

if __name__ == '__main__':
    main()
