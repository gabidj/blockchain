# Module 1 - Create the blockchain

import datetime
import hashlib
import json

import requests
from flask import Flask, jsonify, request

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
        self.transactions = []  # transactions to add within block
        self.genesys = self.create_block(proof=1, previous_hash='0')
        self.nodes = [] #was set() #not serializable # empty set

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
        '''

        :param block:
        :return:
        '''
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
            # if self.is_hash_valid(hash_op_result) is True:
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
    def add_node(self, address):
        # gets an URL object
        parsed_url = urlparse(address)
        # netloc -> ip:port
        self.nodes.append(parsed_url.netloc)
        return

    ### consensus
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)

        for nodes in network:
            # f'string' converts the 'http://' + nodes + '/get_chain'
            # f'http://{nodes}/get_chain'
            response = requests.get(f'http://{nodes}/get_chain')
            if response.status_code == 200:
                current_length = response.json()['length']
                current_chain = response.json()['blockchain']['chain']

                if current_length > max_length and self.is_chain_valid(current_chain):
                    max_length = current_length
                    longest_chain = current_chain

        if longest_chain:
            self.chain = longest_chain
            return True

        return False


# Pt. 2 - Mining our blockchain
# Create web app

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Create address for the node on port 5000
node_address = str(uuid4()).replace('-', '')

# Create blockchain
blockchain = Blockchain()


@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    blockchain.add_transaction(sender=node_address, receiver='Miner', amount=1)
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

@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    response = {
        'message': 'Chain was replaced' if is_chain_replaced else 'Chain was not replaced',
        'blockchain': to_dict(blockchain),
        'length': len(blockchain.chain)
    }

    return jsonify(response), 200 if is_chain_replaced else 400

#@app.post('/add_transaction')
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    response_data = request.get_json()

    transaction_keys = ['sender', 'receiver', 'amount']

    if not all (key in response_data for key in transaction_keys):
        return jsonify({
            'message': 'Missing keys in transaction'
        }), 400

    index = blockchain.add_transaction(response_data['sender'], response_data['receiver'], response_data['amount'])

    return {
        'message': f'Transaction will be added to block id {index}',
        'index': index
    }, 201

@app.route('/connect_node', methods = ['POST'])
def connect_node():
    response_data = request.get_json()
    nodes = response_data.get('nodes')
    if nodes is None:
        return jsonify({'message': 'No nodes'}), 400
    for node in nodes:
        blockchain.add_node(node)

    return jsonify({
        'message': 'All nodes are now connected',
        'total_ndoes': list(blockchain.nodes)
    }), 201


@app.route('/hello', methods=['GET'])
def hello():
    response = {
        'message': 'Hello',
    }

    return jsonify(response), 200


def start_app(port=5000):
    try:
        app.run(host='0.0.0.0', port=port)
    except:
        start_app(port + 1)


start_app(5001)
