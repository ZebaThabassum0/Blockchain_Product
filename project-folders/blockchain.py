from web3 import Web3

infura_url = "https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID"
w3 = Web3(Web3.HTTPProvider(infura_url))

contract_address = "YOUR_CONTRACT_ADDRESS"
contract_abi = [
    {
        "constant": True,
        "inputs": [{"name": "productId", "type": "uint256"}],
        "name": "isProductAuthentic",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    }
]

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

def verify_product_on_blockchain(product_id):
    return contract.functions.isProductAuthentic(product_id).call()