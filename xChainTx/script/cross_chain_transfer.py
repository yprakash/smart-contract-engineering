import time

from utils.w3_utils import ACCOUNT1, w3, send_tx, \
    deploy_and_verify, load_deployed_contract, load_verified_contract, load_impl_contract_from_proxy_address

LINK_TOKEN = w3.to_checksum_address("0x779877A7B0D9E8603169DdbD7836e478b4624789")
USDC_TOKEN = w3.to_checksum_address("0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238")

ccip_contract_address = '0x377Ba277c7223c7aFB2cb95b226479347A6BB071'
cc_tx_hash = '0x418aa209aba49b1ceb98367d75440681d8076a8c51d341fa02d6940e7171e2f8'

if ccip_contract_address:
    print('Assigning ccip_contract object to address', ccip_contract_address)
    ccip_contract_address = w3.to_checksum_address(ccip_contract_address)
    ccip_contract = load_deployed_contract(ccip_contract_address, 'src/CCIPTokenSender.sol', '0.8.26')
else:
    ccip_contract = deploy_and_verify('src/CCIPTokenSender.sol', '0.8.26')

# To send tokens cross-chain, we need to fund our CCIPTokenSender function with LINK tokens to pay for the cross-chain transfer.
link_contract = load_verified_contract(LINK_TOKEN)
link_decimals = link_contract.functions.decimals().call()
ccip_link_bal = 1 * 10**link_decimals  # 1 LINK tokens

usdc_contract = load_impl_contract_from_proxy_address(USDC_TOKEN)
transfer_amount = 1000000  # Amount of USDC to transfer, 1 USDC

if link_contract.functions.balanceOf(ccip_contract_address).call() == 0:
    _ = send_tx(link_contract.functions.transfer(ccip_contract_address, ccip_link_bal))
else:
    n = link_contract.functions.balanceOf(ccip_contract_address).call()
    print(f'CCIP contract already has {n} LINK tokens, no need to transfer again')

if link_contract.functions.balanceOf(ccip_contract_address).call() == ccip_link_bal:
    print("Assert success: link_contract.functions.balanceOf(ccip_contract_address).call() == ccip_link_bal")
else:
    print("Assert failed: link_contract.functions.balanceOf(ccip_contract_address).call() == ccip_link_bal")
# assert link_contract.functions.balanceOf(ccip_contract_address).call() == \
#        ccip_link_bal, "CCIP contract did not receive LINK tokens"

if usdc_contract.functions.allowance(ACCOUNT1, ccip_contract_address).call() == 0:
    # Approve CCIPTokenSender to spend USDC
    _ = send_tx(usdc_contract.functions.approve(ccip_contract_address, transfer_amount))
if usdc_contract.functions.allowance(ACCOUNT1, ccip_contract_address).call() == transfer_amount:
    print("Assert success: usdc_contract.functions.allowance(ACCOUNT1, ccip_contract_address).call() == transfer_amount")
else:
    print("Assert failed: usdc_contract.functions.allowance(ACCOUNT1, ccip_contract_address).call() == transfer_amount")
# assert usdc_contract.functions.allowance(ACCOUNT1, ccip_contract_address).call() == \
#        transfer_amount, "CCIP contract did not receive USDC approval"

if cc_tx_hash:
    print('Loading previous cross-chain transfer transaction hash:', cc_tx_hash)
else:
    tx = send_tx(ccip_contract.functions.transferTokens(ACCOUNT1, transfer_amount))
    cc_tx_hash = tx['transactionHash'].hex()  # .hex() converts the HexBytes object to the standard 0x... string.
    print('========== ========== NOTE ========== ==========')
    print(f"Successfully initiated a cross-chain transfer, check with tx hash: {cc_tx_hash}")
    print('========================================')

while w3.eth.get_transaction_receipt(cc_tx_hash) is None:
    print('Waiting for the transaction to be mined...')
    time.sleep(5)
print(f"Transaction mined successfully! {cc_tx_hash}")
