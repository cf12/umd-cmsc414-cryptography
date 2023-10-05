from itertools import permutations 
from collections import Counter
from pprint import pprint

BLOCK_SIZE=16
MESSAGE_SIZES={
    "BALANCE": 2,
    "TRANSFER": 5,
    "INVOICE": 4
}

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def parse_data (blocks, mappings):
    i = 0
    res=[]

    while i < len(blocks):
        block = blocks[i]
        msg_block = blocks[i:]

        msg = mappings[block]

        if msg == "BALANCE":
            res.append(Balance(msg_block))
        elif msg == "TRANSFER":
            res.append(Transfer(msg_block))
        elif msg == "INVOICE":
            res.append(Invoice(msg_block))

        i += MESSAGE_SIZES[mappings[block]]
        
    assert i == len(blocks)
    return res

def parse_mappings (blocks):
    possible_mappings = []
    for types in permutations(MESSAGE_SIZES.keys()):
        tmp_types = list(types)
        mapping={}
        i=0

        while i < len(blocks):
            block = blocks[i]

            if block not in mapping:
                if len(tmp_types) == 0:
                    break
                mapping[block] = tmp_types.pop(0)

            i += MESSAGE_SIZES[mapping[block]]
        
        if i == len(blocks) and len(set(mapping.keys())) == len(set(mapping.values())):
            possible_mappings.append(mapping)

    # pprint(possible_mappings)
    if len(possible_mappings) == 0:
        raise Exception("could not determine mapping")
    elif len(possible_mappings) > 1:
        raise Exception("more than one possible mapping")
    else:
        return possible_mappings[0]

def parse (filename):
    f = open(filename, 'rb').read()
    blocks = list(chunks(f, BLOCK_SIZE))
    # blocks = list(map(lambda x: x.hex(), chunks(f, BLOCK_SIZE)))
    mappings = parse_mappings(blocks)
    return f, parse_data(blocks, mappings)

def get_accounts(msgs):
    accs = Counter()

    for msg in msgs:
        if isinstance(msg, Balance):
            accs[msg.acc] += 1
        elif isinstance(msg, Transfer) or isinstance(msg, Invoice):
            accs[msg.acc_to] += 1
            accs[msg.acc_from] += 1

    return accs

class Message():
    def __init__(self, blocks):
        self.type = blocks[0]

    def encode (self):
        return b''.join(vars(self).values())

class Balance(Message):
    def __init__(self, blocks):
        super().__init__(blocks)
        self.acc = blocks[1]
    
    def __str__(self):
        return "BALANCE"

class Transfer(Message):
    def __init__(self, blocks):
        super().__init__(blocks)
        self.acc_from = blocks[1]
        self.acc_to = blocks[2]
        self.amount = blocks[3]
        self.time = blocks[4]

    def __str__(self):
        return "TRANSFER"

class Invoice(Message):
    def __init__(self, blocks):
        super().__init__(blocks)
        self.acc_to = blocks[1]
        self.acc_from = blocks[2]
        self.amount = blocks[3]

    def __str__(self):
        return "INVOICE"
