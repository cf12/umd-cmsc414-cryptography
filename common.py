from itertools import permutations 
from collections import Counter

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

        msg = mappings[block]

        if msg == "BALANCE":
            res.append(Balance(block, blocks[i+1]))
        elif msg == "TRANSFER":
            res.append(Transfer(
                block,
                blocks[i+1],
                blocks[i+2],
                blocks[i+3],
                blocks[i+4],
            ))
        elif msg == "INVOICE":
            res.append(Invoice(
                block,
                blocks[i+1],
                blocks[i+2],
                blocks[i+3]
            ))

        i += MESSAGE_SIZES[mappings[block]]
        
    assert i == len(blocks)
    return res

def parse_mappings (blocks):
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
        
        if i == len(blocks):
            return mapping

    raise Exception("could not determine mapping")

def parse (filename):
    f = open(filename, 'rb').read()
    blocks = list(chunks(f, BLOCK_SIZE))
    # blocks = list(map(lambda x: x.hex(), chunks(f, BLOCK_SIZE)))
    mappings = parse_mappings(blocks)
    return f, parse_data(blocks, mappings)

class Message():
    def __init__(self, type) -> None:
        self.type = type

    def encode (self):
        return b''.join(vars(self).values())

class Balance(Message):
    def __init__(self, type, acc) -> None:
        super().__init__(type)
        self.acc = acc
    
    def __str__(self) -> str:
        return "BALANCE"

class Transfer(Message):
    def __init__(self, type, acc_from, acc_to, amount, time) -> None:
        super().__init__(type)
        self.acc_from = acc_from
        self.acc_to = acc_to
        self.amount = amount
        self.time = time

    def __str__(self) -> str:
        return "TRANSFER"

class Invoice(Message):
    def __init__(self, type, acc_from, acc_to, amount) -> None:
        super().__init__(type)
        self.acc_from = acc_from
        self.acc_to = acc_to
        self.amount = amount

    def __str__(self) -> str:
        return "INVOICE"


def parse_t3 (self, acc):
    i = 0

    while i < len(self.blocks):
        block = self.blocks[i]
        msg = self.mapping[block]

        if msg == "TRANSFER" and self.blocks[i + 2] == acc:
            return self.blocks[i + 3]

        i += MESSAGE_SIZES[self.mapping[block]]
        
    raise Exception("no $10 transaction found")