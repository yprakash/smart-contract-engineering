# xChainTx – Cross‑Chain Token Transfers with Chainlink CCIP

**xChainTx** is a minimal yet production‑minded project demonstrating **secure cross‑chain ERC‑20 transfers** using [Chainlink CCIP](https://chain.link/cross-chain).  
It shows how to structure, fund, and execute a **token‑only CCIP message** across EVM chains with automation via Python.

> **Why this matters:**  
> As blockchain ecosystems fragment across chains, reliable cross‑chain messaging becomes a core infrastructure skill.  
> This project demonstrates practical integration of **Chainlink CCIP**, **proxy‑based ERC‑20s**, and **cross‑chain fee management** — skills relevant to **protocol engineers, infra teams, and smart contract auditors**.
---

## Features

- **CCIP‑enabled Solidity contract**  
  - [`CCIPTokenSender.sol`](src/CCIPTokenSender.sol) builds a `Client.EVM2AnyMessage` for token‑only transfers.
  - Supports funding via **LINK** (ERC‑20) to pay CCIP fees.
- **Automated Python deployment & orchestration**  
  - Deploys & verifies the CCIP contract.
  - **Funds with LINK**, **approves USDC**, and **initiates cross‑chain transfers**.
  - Waits for confirmation on the source chain.
- **Proxy‑aware ERC‑20 interaction**  
  - Reads **implementation contracts** (like USDC) behind proxies for correct ABI calls.
- **Idempotent & production‑minded**  
  - Skips redundant LINK/USDC transfers if already funded/approved.
  - Asserts balances & allowances before executing.
---
## Tech Stack

- **Solidity** `0.8.26` (Foundry‑ready)  
- **Chainlink CCIP** client libraries  
- **Python** `web3.py` orchestration scripts  
- **Etherscan API** for contract verification  
- **Sepolia ↔ Base Sepolia** test networks  

---

## Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/yprakash/smart-contract-engineering.git
cd smart-contract-engineering
pip install -r utils/requirements.txt
```

### 2. Install dependencies
```bash
cd xChainTx
forge init --force --no-git
forge install smartcontractkit/chainlink-brownie-contracts@1.3.0 --no-commit
forge install OpenZeppelin/openzeppelin-contracts@5.4.0 --no-commit
forge build
```

### 3. Configure Environment
```ini
PROVIDER_URL=https://sepolia.infura.io/v3/...
ACCOUNT1=0x...
PRIVATE_KEY=0x...
ETHERSCAN_API_KEY=...
CHAIN_ID=11155111  # Sepolia
```

### 4. Deploy & Fund
Run the Python orchestrator:

```ini
python3 scripts/cross_chain_transfer.py
```
This will:
1. Deploy (or attach to) the CCIPTokenSender contract.
2. Fund it with 1 LINK for CCIP fees.
3. Approve 1 USDC for transfer.
4. Execute a cross‑chain transfer (Sepolia → Base Sepolia).
5. Wait for confirmation on the source chain.
---
### Example Transaction
> Cross‑chain USDC transfer (Sepolia → Base Sepolia):  
> [View on Etherscan](https://sepolia.etherscan.io/tx/0x418aa209aba49b1ceb98367d75440681d8076a8c51d341fa02d6940e7171e2f8)

---
## Next Steps
- Delivery monitoring: Add event listeners for CCIP message confirmation on the destination chain.
- Multi‑token batching: Extend to support multi‑asset cross‑chain transfers.
- Native fee mode: Switch between LINK and native token fees dynamically.  
---
## Author  
Prakash — Backend Engineer & Blockchain Developer  
- [LinkedIn](https://www.linkedin.com/in/yprakash)  
- [GitHub](https://github.com/yprakash)  
> “My goal is to build infrastructure that enables secure, scalable, and interoperable DeFi systems — this project is a step toward that vision.”
---