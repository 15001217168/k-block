
# -*- coding:utf-8 -*-

#modules
import hashlib
import json
from time import time
from uuid import uuid4
from urllib.parse import urlparse
import requests

#BlockChain类用来管理链条，它能存储交易，加入新块等
class BlockChain(object):
    def __init__(self):
        self.chain=[]
        self.current_transactions=[]
        # 创建新的节点
        self.new_block(proof=100,previous_hash=1)
        self.nodes=set()
    '''
        注册节点
        :param address: <string> 地址
    '''
    def register_node(self,address):
        url=urlparse(address)
        self.nodes.add(url.netloc)
    '''
        验证区块链是否有效
        :param chain: <list> 区块链
        :return: <bool> 结果
    '''
    def valid_chain(self,chain):
        last_block=chain[0]
        current_index=1
        while current_index<len(chain):
            block=chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False
            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False
            last_block = block
            current_index += 1
        return True
    '''
        共识算法解决冲突
        使用网络中最长的链.
        :return: <bool> True 如果链被取代, 否则为False
    '''
    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None
        # We're only looking for chains longer than ours
        max_length = len(self.chain)
        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True
        return False
    """
        生成新块
        :param proof: <int> 工作量证明
        :param previous_hash: <string> 上一个区块链的hash值
        :return: <dict> 返回新的区块
    """
    def new_block(self,proof, previous_hash=None):
        #创建新的区块链
        block={
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []
        self.chain.append(block)
        return block
    """
        生成新交易信息，信息将加入到下一个待挖的区块中
        :param sender: <string> 发送方地址
        :param recipient: <string> 接收方地址
        :param amount: <int> 金额
        :return: <int> 返回该记录将被添加到的区块(下一个待挖掘的区块)的索引
    """
    def new_transaction(self,sender,recipient,amount):
        #创建新的交易
        self.current_transactions.append({
            'sender':sender,
            'recipient':recipient,
            'amount':amount
        })
        return self.last_block['index']+1
    """
        生成块的 SHA-256 hash值
        :param block: <dict> 区块
        :return: <str> hash值
    """
    @staticmethod
    def hash(block):
        #对一个区块进行hash计算
        block_string=json.dumps(block,sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    @property
    def last_block(self):
      return self.chain[-1]
    
    '''
    简单工作量证明
        - 查找一个 p' 使得 hash(pp') 以4个0开头
         - p 是上一个块的证明,  p' 是当前的证明
        :param last_proof: <int>
        :return: <int>
    '''
    def proof_of_work(self,last_proof):
        proof=0
        while self.valid_proof(last_proof,proof) is False:
            proof+=1
        return proof
    """
        验证证明: 是否hash(last_proof, proof)以4个0开头?
        :param last_proof: <int> 上一个证明
        :param proof: <int> 当前的证明
        :return: <bool>结果
    """
    @staticmethod
    def valid_proof(last_proof, proof):       
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

