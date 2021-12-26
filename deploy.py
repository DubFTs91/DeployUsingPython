from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

with open("./MyStorage.sol", "r") as file:
    my_storage_file = file.read()
    # print(my_storage_file)


# Compile the solidity code
install_solc("0.6.0")
myStorage_compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"MyStorage.sol": {"content": my_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)
# print(myStorage_compiled_sol)

with open("compiled_code.json", "w") as file:
    json.dump(myStorage_compiled_sol, file)

# Deply

# Get ByteCode
bytecode = myStorage_compiled_sol["contracts"]["MyStorage.sol"]["MyStorage"]["evm"][
    "bytecode"
]["object"]

# Get ABI
abi = myStorage_compiled_sol["contracts"]["MyStorage.sol"]["MyStorage"]["abi"]

# connect to Rinkeby blockchain
w3 = Web3(
    Web3.HTTPProvider("https://rinkeby.infura.io/v3/6e4b4abfc3224ed591bdaa206c4f63ae")
)
chain_id = 4
my_address = "0xe3355515f114c1A879416fd024E249E1040E7027"
private_key = os.getenv("PRIVATE_KEY")


# Create Contract
MyStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# print(MyStorage)

# Get Lastest Transaction
nonce = w3.eth.getTransactionCount(my_address)
# print(nonce)

# 1. Build Transaction
# 2. Sign Transaction
# 3. Send Transaction
transaction = MyStorage.constructor().buildTransaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce}
)
nonce += 1
# print(transaction)

print("Deploying contract...")
signed_trans = w3.eth.account.sign_transaction(transaction, private_key=private_key)
# print(signed_trans)

# Send transaction to Blockchain
trans_hash = w3.eth.sendRawTransaction(signed_trans.rawTransaction)
trans_recipt = w3.eth.wait_for_transaction_receipt(trans_hash)

print("Deploy Complete...")
# Work with Contract
# Contract Address
# Contract ABI
my_storage = w3.eth.contract(address=trans_recipt.contractAddress, abi=abi)

# Call > Read Only
# Transact > State Change

# intial value of fav number
print(my_storage.functions.retrieve().call())
store_trans = my_storage.functions.store(77).buildTransaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce}
)

print("Updating contract...")

signed_store_trans = w3.eth.account.sign_transaction(
    store_trans, private_key=private_key
)
store_trans_hash = w3.eth.send_raw_transaction(signed_store_trans.rawTransaction)
sotre_trans_recipt = w3.eth.wait_for_transaction_receipt(store_trans_hash)

print("Update complete...")

# updated value of fav number
print(my_storage.functions.retrieve().call())
