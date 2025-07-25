# Event-Driven Automation with Chainlink Log Triggers

This mini-project demonstrates **event-driven smart contract automation** using **Chainlink Log Triggers**. It consists of two contracts:
- **EventEmitter**: A simple contract that emits `DepositEvent` and `WithdrawEvent` logs.
- **EventWatcher**: A Chainlink Automation consumer that listens to these logs and decides whether upkeep (on-chain action) is needed.

---

## What This Project Does

- **Event Monitoring**: Watches `DepositEvent` and `WithdrawEvent` emitted by `EventEmitter`.
- **Decision Logic in `checkLog()`**:
  - For **deposits**: Only act on **odd-numbered** deposits.
  - For **withdrawals**: Only act on **even-numbered** withdrawals.
- **Passes Context to `performUpkeep()`**: Uses `performData` to encode action type (`"deposit"`, `"withdraw"`, or `"NO_ACTION"`) and the event source.

---

## Why Use `checkLog()` and `performUpkeep()`?

- **Gas Efficiency**: `checkLog()` runs **off-chain** on Chainlink nodes to decide if upkeep is needed. Only when necessary does the network trigger `performUpkeep()` on-chain (saving gas).
- **Context Passing**: `checkLog()` prepares `performData`, which is then decoded by `performUpkeep()` for precise on-chain execution.

---

## Contracts

### EventEmitter.sol
A utility contract that emits two types of events:
```solidity
event DepositEvent(address indexed msgSender);
event WithdrawEvent(address indexed msgSender);

function deposit() public {
    emit DepositEvent(msg.sender);
}

function withdraw() public {
    emit WithdrawEvent(msg.sender);
}
```

### EventWatcher.sol
A Chainlink Automation consumer implementing `ILogAutomation`:
- **Event filtering** using precomputed event signatures:
```solidity
bytes32 constant DEPOSIT_SIG = keccak256("DepositEvent(address)");
bytes32 constant WITHDRAW_SIG = keccak256("WithdrawEvent(address)");
```
- **Conditional action**:
    - Deposits: Only act on odd-numbered counts.
    - Withdrawals: Only act on even-numbered counts.
- **Pass context** to `performUpkeep()` via `performData`.

---

## Setup
1. Install dependencies:
```bash
forge install smartcontractkit/chainlink-brownie-contracts@1.3.0 --no-commit
```
2. Compile contracts:
```bash
forge build
```
3. Deploy contracts:
```bash
forge create src/EventEmitter.sol:EventEmitter --rpc-url <RPC> --private-key <KEY>
forge create src/EventWatcher.sol:EventWatcher --rpc-url <RPC> --private-key <KEY>
```
> you can use `script/deploy.py` for a more automated deployment.
4. Register upkeep:
   - Go to Chainlink Automation UI
   - Set trigger to DepositEvent & WithdrawEvent
   - Set callback to performUpkeep() of EventWatcher
   - Adjust gas limit to cover upkeep execution.

---

### Use Cases
- Real-time Transfer Tracking: Monitor deposits/withdrawals for specific addresses.
- Swap Monitoring: Watch DEX swap events and trigger automated responses.
- Alerting & Hedging Bots: Trigger off-chain actions when specific patterns occur.

Why This Matters
Event-driven automation is a core skill for modern blockchain developers:

Build real-time bots for DeFi.

Automate vault management or risk controls.

Enhance MEV strategies with instant event responses.

Next Steps
Extend EventWatcher to:

Track ERC20 transfers for a whitelist of addresses.

Decode swap events from DEX pools.

Add a Python off-chain listener for analytics and notifications.

Write Foundry tests to simulate end-to-end event automation.

Author: [yprakash]
Tech Stack: Solidity, Foundry, Chainlink Automation