from itertools import permutations 
from collections import Counter

BLOCK_SIZE=16
MESSAGES={
    "BALANCE": 2,
    "TRANSFER": 5,
    "INVOICE": 4
}

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

class Attacker ():
    def __init__(self, filename):
        self.data = open(filename, 'rb').read()
        # self.blocks = list(map(lambda x: x.hex(), chunks(self.data, BLOCK_SIZE)))
        self.blocks = list(chunks(self.data, BLOCK_SIZE))
        self.mapping = self.parse_mapping()

    def parse (self):
        i = 0

        while i < len(self.data):
            block = self.data[i:i+BLOCK_SIZE]

            print(self.mapping[block])
            i += BLOCK_SIZE * MESSAGES[self.mapping[block]]
            
        assert i == len(self.data)

    def parse_mapping (self):
        for types in permutations(MESSAGES.keys()):
            tmp_types = list(types)
            mapping={}
            i=0

            while i < len(self.blocks):
                block = self.blocks[i]

                if block not in mapping:
                    if len(tmp_types) == 0:
                        break
                    mapping[block] = tmp_types.pop(0)

                i += MESSAGES[mapping[block]]
            
            if i == len(self.blocks):
                return mapping

        raise Exception("could not determine mapping")

    def parse_accounts (self):
        accs = Counter()
        i = 0

        while i < len(self.blocks):
            block = self.blocks[i]
            msg = self.mapping[block]

            print(self.mapping[block])
            if msg == "BALANCE":
                accs[self.blocks[i + 1]] += 1
            elif msg == "TRANSFER" or msg == "INVOICE":
                accs[self.blocks[i + 1]] += 1
                accs[self.blocks[i + 2]] += 1
            else:
                raise Exception(f"invalid block: 0x{block}")

            i += MESSAGES[self.mapping[block]]
            
        assert i == len(self.blocks)

        return accs

    def find_transaction (self, acc):
        i = 0

        while i < len(self.blocks):
            block = self.blocks[i]
            msg = self.mapping[block]

            if msg == "TRANSFER":
                # print(blocks[i])
                # print(blocks[i + 2])
                if self.blocks[i + 2] == acc:
                    return b''.join(self.blocks[i:i+MESSAGES["TRANSFER"]])

            i += MESSAGES[self.mapping[block]]
            
        return None


    def parse_t3 (self, acc):
        i = 0

        while i < len(self.blocks):
            block = self.blocks[i]
            msg = self.mapping[block]

            if msg == "TRANSFER" and self.blocks[i + 2] == acc:
                return self.blocks[i + 3]

            i += MESSAGES[self.mapping[block]]
            
        raise Exception("no $100 transaction found")