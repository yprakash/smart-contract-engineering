import time

from utils.w3_utils import w3, deploy_and_verify, load_deployed_contract

contract_address = '0xAc4a7733e0A663d1fddA3a1C817119ba60D7DfD7'
DEPOSIT_SIG = w3.keccak(text="DepositEvent(address)")
WITHDRAW_SIG = w3.keccak(text="WithdrawEvent(address)")

if contract_address:
    print('Assigning watcher_contract object to address', contract_address)
    watcher_contract = load_deployed_contract(contract_address, 'src/EventWatcher.sol', '0.8.26')
else:
    watcher_contract = deploy_and_verify('src/EventWatcher.sol', '0.8.26')
    print(watcher_contract)


def decode_event_sig(event_sig: bytes) -> str:
    if event_sig == DEPOSIT_SIG:
        return "DepositEvent"
    elif event_sig == WITHDRAW_SIG:
        return "WithdrawEvent"
    return "UnknownEvent"


def handle_event(event):
    log = watcher_contract.events.UpkeepPerformed().process_log(event)
    logSender = log['args']['by']
    event_sig = decode_event_sig(log['args']['eventSig'])
    upkeepNumber = log['args']['upkeepNumber']
    print(f"[NEW UPKEEP] #{upkeepNumber} by {logSender} | EventSig: {event_sig} | Block: {event['blockNumber']}")


def main():
    event_filter = w3.eth.filter({
        "address": watcher_contract.address,
        "topics": [watcher_contract.events.UpkeepPerformed().build_filter().topics[0]]
        # "topics": [w3.keccak(text="UpkeepPerformed(address,bytes32,uint256)").to_0x_hex()]  # indexed params only
    })
    while True:
        print("Polling for new events...")
        for event in event_filter.get_new_entries():
            # print(f"New event: {event}")
            handle_event(event)
        time.sleep(5)  # Poll every 2 seconds


if __name__ == "__main__":
    main()
