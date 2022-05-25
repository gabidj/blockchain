# Module 1 - Create the blockchain

import datetime
import hashlib
import json
import requests
from flask import Flask, jsonify

from uuid import uuid4
from urllib.parse import urlparse

# class Serializable:
#     def __dict__(self):
#         # YOUR CUSTOM CODE HERE
#         #    you probably just want to do:
#         #        return self.__dict__
#         return self.__dict__

def to_dict(obj):
    return obj.__dict__

class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = [] # transactions to add within block
        self.genesys = self.create_block(proof=1, previous_hash='0')
        self.nodes = set() # empty set

    ## HASH
    def is_hash_valid(self, hash):
        # dc = 646576636861696e
        # dc2 = 33824246
        # dc3 = 39007306)
        return hash[:4] == '0000'

    def hash_op(self, proof, previous_proof):
        return hashlib.sha256(
            str(
                proof ** 2 - previous_proof ** 2
            ).encode()).hexdigest()

    ## BLOCKS
    def create_block(self, proof, previous_hash, transactions=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,  # the nonce
            # 'data': value,
            'previous_hash': previous_hash,
            'transactions': self.transactions
        }
        self.transactions = []
        self.chain.append(block)
        return block

    def hash_block(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def get_previous_block(self):
        # return self.chain[len(self.chain) - 1]
        return self.chain[-1]

    ## POW
    def get_proof_of_work(self, previous_proof):
        new_proof = 1

        while 1:
            hash_op_result = self.hash_op(new_proof, previous_proof)
            #if self.is_hash_valid(hash_op_result) is True:
            if self.is_hash_valid(hash_op_result) is True:
                return new_proof
            new_proof += 1

    ## CHAIN
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash_block(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = self.hash_op(proof, previous_proof)
            if self.is_hash_valid(hash_operation) is False:
                return False
            previous_block = block
            block_index += 1
        return True

    ## Transaction
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount
        })

        previous_block = self.get_previous_block()
        return previous_block['index'] + 1

    ## Nodes
    def addNode(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        return

    ### consensus


###################
# Pt. 2 - Mining our blockchain
# Create web app

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Create blockchain
blockchain = Blockchain()


@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.get_proof_of_work(previous_proof)
    previous_hash = blockchain.hash_block(previous_block)
    block = blockchain.create_block(proof, previous_hash)

    response = {
        'message': 'Block mined',
        'block': block
    }
    return response, 200


@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {
        'message': 'Block mined',
        'blockchain': to_dict(blockchain),
        'length': len(blockchain.chain)
    }

    return jsonify(response), 200


@app.route('/is_valid', methods=['GET'])
def is_blockchain_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    response = {
        'message': 'Chain is valid' if is_valid else 'Chain is invalid',
        'blockchain': to_dict(blockchain),
        'length': len(blockchain.chain)
    }

    return jsonify(response), 200 if is_valid else 400


@app.route('/hello', methods=['GET'])
def hello():
    response = {
        'message': 'Hello',
    }

    return jsonify(response), 200


app.run(host='0.0.0.0', port=5001)
