# ☕ Buy Me a Coffee dApp
## Full-Stack Walkthrough with Foundry, Anvil & viem

This is a **“Buy Me a Coffee” decentralized application (dApp)**.  
The idea is simple: anyone can tip ETH into a contract as if they were buying you a coffee.  
As the contract owner, you can later withdraw the collected funds.

This project is a great **end-to-end Web3 demo**:
- A Solidity smart contract deployed locally with **Foundry**.
- A local blockchain simulated with **Anvil**.
- A frontend written in **HTML + JavaScript** using **viem** for wallet connections and contract interactions.

---
## 🛠 Main Technical Concepts

### 1. **Smart Contracts (Backend of dApps)**
- Written in Solidity.
- Stores ETH contributions.
- Exposes `fund()` (tip with ETH) and `withdraw()` (owner withdraws).

### 2. **Anvil (Local Ethereum Node)**
- Local blockchain for testing.
- Comes with pre-funded accounts and private keys.
- Supports `--dump-state` / `--load-state` to save & restore deployments.

### 3. **Foundry (Deployment Toolchain)**
- `forge` compiles and deploys the contract.
- Deployment scripts written in Solidity (`DeployFundMe.s.sol`).
- Works seamlessly with Anvil.

### 4. **Frontend with viem**
Instead of directly using `ethers.js` or `web3.js`, this project uses **viem**, a modern TypeScript-first Ethereum library.

Functions implemented in `index-js.js`:
- `connect()` → Connect wallet via MetaMask.
- `fund()` → Call `fund()` function on contract with entered ETH amount.
- `getBalance()` → Query contract balance.
- `withdraw()` → Owner withdraws ETH.
- Utility: `getCurrentChain()` → Ensures viem connects to Anvil’s chain.

---
### 🚀 Step 1. Start Local Blockchain
In one terminal tab:
```bash
anvil
```
- Runs at http://127.0.0.1:8545
- Provides 10 test accounts (10,000 ETH each)

### 🚀 Step 2. Deploy the Smart Contract
In another terminal:
```bash
forge script script/DeployFundMe.s.sol:DeployFundMe \
  --rpc-url http://127.0.0.1:8545 \
  --broadcast
```
Copy the deployed contract address — you’ll need it in constants-js.js.

### 🚀 Step 3. Save Deployment (Optional Snapshot)
Snapshot the state after deployment:
```bash
anvil --dump-state buy-coffee-anvil.json
```
Later, instead of redeploying:
```bash
anvil --load-state buy-coffee-anvil.json
```

### 🎮 Step 4. Interact via Frontend
#### 1. Setup constants-js.js
Create a file in your project root:
```js
export const contractAddress = "0xYOUR_DEPLOYED_ADDRESS"
export const abi = [
  // Paste ABI from out/FundMe.sol/FundMe.json
]
```

#### 2. Serve frontend
Open index.html in your browser (MetaMask must be installed).  
Ensure MetaMask is connected to Localhost 8545 network.

#### 3. Use the buttons
- Connect → Prompts MetaMask connection.
- Get Balance → Calls getBalance() via viem.
- Buy Coffee → Sends ETH to contract by calling fund().
- Withdraw → Owner withdraws funds (only works if your connected account is the deployer).

---
## 🧩 How It Works (Behind the Scenes)
### 1. Wallet Connection
```js
walletClient = createWalletClient({ transport: custom(window.ethereum) })
await walletClient.requestAddresses()
```
### 2. Funding the Contract
```js
const { request } = await publicClient.simulateContract({
  address: contractAddress,
  abi,
  functionName: "fund",
  account,
  chain: currentChain,
  value: parseEther("0.1"),
})
await walletClient.writeContract(request)
```

### 3. Balance Query
```js
const balance = await publicClient.getBalance({ address: contractAddress })
console.log(formatEther(balance))
```

### 4. Withdrawal (Owner Only)
```js
const { request } = await publicClient.simulateContract({
  account,
  address: contractAddress,
  abi,
  functionName: "withdraw",
  chain: currentChain,
})
await walletClient.writeContract(request)
```
---
## 🔑 Key Takeaways
- **dApp stack** = Smart Contract + Blockchain Node + Wallet + Frontend Library.
- **Anvil** makes it trivial to test dApps locally.
- **Foundry** gives you fast compilation + deployment scripting.
- **viem** is a modern alternative to ethers/web3 for frontend contract interactions.
- This project is a perfect starter full-stack Web3 playground for learning local dev workflow.
