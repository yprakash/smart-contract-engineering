import time

from utils.w3_utils import deploy_and_verify, load_deployed_contract, send_tx

contract_address = ''
if contract_address:
    print('Assigning emit_contract object to address', contract_address)
    emit_contract = load_deployed_contract(contract_address, 'src/EventEmitter.sol', '0.8.26')
else:
    emit_contract = deploy_and_verify('src/EventEmitter.sol', '0.8.26')

while True:
    tx_receipt = send_tx(emit_contract.functions.deposit())
    events = emit_contract.events.DepositEvent().process_receipt(tx_receipt)
    print(events)
    time.sleep(1)
    tx_receipt = send_tx(emit_contract.functions.withdraw())
    events = emit_contract.events.WithdrawEvent().process_receipt(tx_receipt)
    print(events)
    time.sleep(2)
