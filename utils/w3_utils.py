"""
This module provides utility functions for interacting with the Ethereum blockchain using Web3.py.
It includes functions for compiling Solidity contracts, sending transactions,
encoding constructor arguments, and deploying and verifying contracts on Etherscan.
"""
import json
import os
import time
from time import sleep

import requests
from dotenv import load_dotenv
from eth_abi import encode
from eth_utils import to_hex
from web3 import Web3

from utils.contract_utils import compile_contract, flatten_contract

load_dotenv('.env')

# Initialize Web3 connection
w3 = Web3(Web3.HTTPProvider(os.getenv('PROVIDER_URL')))
if w3.is_connected():
    print("Successfully connected to the provider!")
else:
    print("Failed to connect to the given provider ", os.getenv('PROVIDER_URL'))
    exit()

# Load essential environment variables
_PRIVATE_KEY = os.getenv('PRIVATE_KEY')
ACCOUNT1 = w3.to_checksum_address(os.getenv('ACCOUNT1'))
ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
CHAIN_ID = int(os.getenv("CHAIN_ID", 11155111))  # Default to Sepolia testnet
BASE_URL = f"https://api.etherscan.io/v2/api?chainid={CHAIN_ID}"

# Constants used as keys in transactions and API payloads
KEY_abi = 'abi'
KEY_bin = "bin"
KEY_chainId = 'chainId'
KEY_contractAddress = 'contractAddress'
KEY_from = 'from'
KEY_metadata = "metadata"
KEY_nonce = 'nonce'
KEY_status = 'status'
KEY_to = 'to'
SLEEP_TIME = 5  # Time to wait between retries (in seconds)


def send_tx(transaction, build_tx=True):
    """
    Sends a transaction to the Ethereum blockchain.
    Args:
        transaction (dict): Transaction object to send.
        build_tx (bool): Whether to build the transaction. Defaults to True.
    Returns:
        dict: Transaction receipt containing details of the mined transaction.

    NOTE: It waits til the transaction is mined and returns the receipt.
    We have 1-line .transact() for state changes, but it works only if you are using a local node like Ganache, Anvil
    Or your account is unlocked in the node (like Infura), which is rare in public networks. So we need below steps
    """
    nonce = w3.eth.get_transaction_count(ACCOUNT1, 'pending')  # To include unmined txs, Use pending
    if build_tx:
        transaction = transaction.build_transaction({
            KEY_from: ACCOUNT1,
            KEY_chainId: CHAIN_ID,
            KEY_nonce: nonce
        })
    else:  # For pre-encoded calldata
        transaction[KEY_chainId] = CHAIN_ID
        transaction[KEY_from] = ACCOUNT1
        transaction[KEY_nonce] = nonce

    signed_tx = w3.eth.account.sign_transaction(transaction, private_key=_PRIVATE_KEY)
    txn_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f'Sent transaction to chain {CHAIN_ID} with nonce {nonce} hash {txn_hash}')
    tx_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    assert tx_receipt[KEY_status] == 1
    return tx_receipt


def encode_constructor_args(abi, constructor_args: list = None):
    """
    Encodes constructor arguments for a contract deployment.
    Args:
        abi (list): ABI of the contract containing constructor details. For example
        [{
          "type":"constructor",
          "stateMutability":"payable",
          "inputs":[{
                "type":"address","name":"_logic","internalType":"address"
             }, {
                "type":"bytes","name":"_data","internalType":"bytes"
             }
          ]
        }]
        constructor_args (list, optional): List of arguments for the constructor. Defaults to None.
    Returns:
        str: Hexadecimal string of encoded constructor arguments.
    """

    if constructor_args is None:
        constructor_args = []
    # Constructor arguments must be ABI-encoded manually, based on ABI + your constructor args.
    constructor_inputs = next(
        (item['inputs'] for item in abi if item['type'] == 'constructor'), []
    )
    types = [i['type'] for i in constructor_inputs]
    encoded = encode(types, constructor_args)  # eth_abi.encode
    hex_constructor_args = to_hex(encoded)[2:]  # Remove '0x'
    print(f"hex_constructor_args {hex_constructor_args}")
    return hex_constructor_args


def load_verified_contract(
        contract_address: str,  # The Ethereum address of the contract
        apikey: str = ETHERSCAN_API_KEY,  # Etherscan API key. Defaults to ETHERSCAN_API_KEY from .env
        cache_dir: str = "./.abi_cache"  # Directory to store cached ABI files. Defaults to "./.abi_cache".
):
    """
    Loads a verified contract from Etherscan by its address and caches the ABI locally to avoid repeated API calls.
    Returns: web3.contract.Contract: A Web3 contract object for interacting with the contract.
    Raises: ValueError: If the ABI cannot be fetched from Etherscan.
    """
    contract_address = w3.to_checksum_address(contract_address)
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, f"{contract_address}.json")

    # Load ABI from cache if available
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            abi = json.load(f)
    else:
        # Fetch from Etherscan
        url = f"{BASE_URL}&module=contract&action=getabi&address={contract_address}&apikey={apikey}"
        response = requests.get(url)
        data = response.json()
        if data["status"] != "1":
            raise ValueError(f"Failed to fetch ABI for {contract_address}: {data['result']}")
        abi = json.loads(data["result"])
        with open(cache_path, "w") as f:
            json.dump(abi, f, indent=2)

    return w3.eth.contract(address=contract_address, abi=abi)


def load_deployed_contract(
        contract_address: str,  # The Ethereum address of the deployed contract.
        contract_path: str,  # Relative path to the Solidity contract file.
        version: str,  # Version of the Solidity compiler to use (e.g., '0.8.26')
        contract_name: str = None  # Name of the contract to load. None uses the first contract in the compiled source.
):
    """
    Loads a deployed contract by compiling its source code and associating it with the given address.
    Returns: web3.contract.Contract: A Web3 contract object for interacting with the deployed contract.
    """
    contract_interface = compile_contract(contract_path, version, contract_name, output_values=[KEY_abi])
    contract_address = w3.to_checksum_address(contract_address)
    return w3.eth.contract(address=contract_address, abi=contract_interface[KEY_abi])


def deploy_and_verify(
        contract_path: str,  # Relative contract path
        version: str,  # Solidity version like '0.8.26'
        contract_name: str = None,  # Name of contract if .sol file has dependencies/multiple contracts
        constructor_args: list = None,  # Constructor arguments to deploy
        contract_address: str = None  # Directly verify if contract is already deployed
):
    """
    Deploys a Solidity contract to the Ethereum blockchain and verifies it on Etherscan.
    Args:
        contract_path (str): Relative Path to the Solidity contract file.
        version (str): Version of the Solidity compiler to use.
        contract_name (str, optional): Name of the contract to deploy. Defaults to None.
        constructor_args (list, optional): Arguments for the contract constructor. Defaults to None.
        contract_address (str, optional): Address of an already deployed contract for verification. Defaults to None.
            when None, it deploys the contract first.
    NOTE: flattened .sol file must have already been generated by using 'forge flatten' command and saved in 'flat/'.
    Returns:
        web3.eth.Contract: Web3 contract object for the deployed contract.
    """
    compiled = compile_contract(contract_path, version, contract_name)
    if contract_address:
        print(f"Preparing to verify contract at address {contract_address}")
    else:
        contract = w3.eth.contract(abi=compiled[KEY_abi], bytecode=compiled[KEY_bin])
        if constructor_args:
            tx_receipt = send_tx(contract.constructor(*constructor_args))
        else:
            tx_receipt = send_tx(contract.constructor())
        contract_address = tx_receipt[KEY_contractAddress]
        print('========== ========== NOTE ========== ==========')
        print(f"Deployed {contract_path} Please take a note of contract_address: {contract_address}")
        print('========================================')
        # Once deployed on blockchain
        time.sleep(30)

    payload = {
        "action": "verifysourcecode",
        "codeformat": "solidity-single-file",
        "licenseType": 3,  # MIT
        "module": "contract",
        "contractaddress": contract_address,
        "contractname": compiled["contract_name"],
        "compilerversion": compiled["compiler_version"],
        "optimizationUsed": compiled["optimize"],
        "runs": compiled["optimizer_runs"],
        # "sourceCode": compiled["contract_source"],
        "sourceCode": flatten_contract(contract_path),
        "apikey": ETHERSCAN_API_KEY
    }
    if constructor_args:
        payload["constructorArguments"] = encode_constructor_args(compiled[KEY_abi], constructor_args)
    print(f"Verifying the contract using payload {payload}")

    resp = requests.post(BASE_URL, data=payload)
    result = resp.json()
    print("Initial response:", result)

    if result[KEY_status] != "1":
        raise Exception("Verification submission failed: " + result["result"])
    guid = result["result"]
    print("Verification submission successful, GUID:", guid)

    # Poll for verification result
    for _ in range(10):
        sleep(SLEEP_TIME)
        status_payload = {
            "module": "contract",
            "action": "checkverifystatus",
            "guid": guid,
            "apikey": ETHERSCAN_API_KEY
        }
        status_resp = requests.get(BASE_URL, params=status_payload)
        status = status_resp.json()
        print("Verification check:", status)

        if status[KEY_status] == "1":
            print("✅ Contract verified! status:", status)
            break
        if "Pending" in status["result"]:
            print("🔄 Verification is still pending, waiting...")
            time.sleep(SLEEP_TIME)
        else:
            print("❌ Verification failed:", status)
            raise Exception("❌ Verification failed: " + status["result"])

    return w3.eth.contract(address=contract_address, abi=compiled[KEY_abi])
