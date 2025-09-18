# ⚡ Understanding viem: A TypeScript-First Ethereum Library

As blockchain engineers, we live close to the EVM — thinking in opcodes, calldata, gas, storage, and state.
But once you step into **full-stack dApp development**, you need a frontend-friendly way
to talk to contracts, wallets, and nodes. That’s where **[viem](https://viem.sh/)** comes in.

This guide gives an overview of viem: its client types, how to use them, and the main actions you can perform.

---
## 🧩 What is viem?

- A **TypeScript-first Ethereum library**.
- Alternative to `ethers.js` and `web3.js`.
- Provides **strong typing**, **modular architecture**, and a **modern developer experience**.
- Works in **browsers, Node.js, and frameworks** (Next.js, Vite, etc.).

Think of viem as your **toolbox for encoding calldata, sending transactions, and reading state** —
but with TypeScript safety baked in.

---
## 🔑 Key Concepts: Clients
Viem organizes everything into **clients**. Each client type gives you a specific set of capabilities.

#### 1. `publicClient`
- Read-only RPC connection to a blockchain.
- Used for fetching data from nodes.
- Doesn’t require a signer.

Common actions:
```ts
import { createPublicClient, http } from "viem"
import { mainnet } from "viem/chains"

const publicClient = createPublicClient({
  chain: mainnet,
  transport: http(),
})

// Example: get latest block number
const blockNumber = await publicClient.getBlockNumber()

// Example: read contract balance
const balance = await publicClient.getBalance({
  address: "0xabc...",
})
```
#### 2. walletClient
- Represents a signing wallet (like MetaMask, Ledger, or a local private key).
- Used for transactions and state changes.
- Needs a signer (browser extension or injected key).

Common actions:
```ts
import { createWalletClient, custom } from "viem"

const walletClient = createWalletClient({
  transport: custom(window.ethereum), // MetaMask
})

const accounts = await walletClient.requestAddresses()

await walletClient.sendTransaction({
  account: accounts[0],
  to: "0xdef...",
  value: parseEther("0.1"),
})
```
#### 3. testClient
- Special client for local dev environments like **Anvil** or **Hardhat**.
- Lets you manipulate the chain state directly (snapshots, mining, impersonation).

Example:
```ts
import { createTestClient, http } from "viem"
import { anvil } from "viem/chains"

const testClient = createTestClient({
  mode: "anvil",
  chain: anvil,
  transport: http(),
})

// Example: mine a block
await testClient.mine({ blocks: 1 })
```
#### 4. fallbackClient
- Wraps multiple transports (RPCs) and falls back if one fails.
- Useful for production apps where you don’t want downtime.

---
### 🛠️ Actions You Can Perform
#### 🔹 Contract Interactions
- Read (no gas, static call):
```ts
const data = await publicClient.readContract({
  address: "0xContract",
  abi,
  functionName: "getValue",
})
```
- Write (transaction with signer):
```ts
const { request } = await publicClient.simulateContract({
  address: "0xContract",
  abi,
  functionName: "setValue",
  args: [42],
  account,
})
await walletClient.writeContract(request)
```
### 🔹 Chain Information
- `getBlockNumber()`
- `getChainId()`
- `getTransaction()`
- `getLogs()`

### 🔹 Wallet Actions
- `requestAddresses()`
- `sendTransaction()`
- `writeContract()`

These map directly to **EIP-1193 provider actions** (`eth_requestAccounts`, `eth_sendTransaction`, etc.),
but viem adds typesafety and helpers.

### 🔹 Testing Actions
On local chains:
- `mine({ blocks: 1 })`
- `setBalance({ address, value })`
- `impersonateAccount()`

---
## 🔮 Why Blockchain Experts Will Like viem
- **Typed calldata/ABI** → no more mismatched arguments at runtime.
- **Composable clients** → clear separation between “read-only RPC” and “signing wallet”.
- **Simulation before broadcast** → catch errors before spending gas.
- **Modern DX** → designed with TypeScript-first mindset, making full-stack dApp development smoother.

## ✅ Summary
- `publicClient` = RPC connection (read data).
- `walletClient` = Signer + wallet (write transactions).
- `testClient` = Chain control for local testing.
- `fallbackClient` = Multi-RPC reliability.

Viem isn’t “just another ethers.js.” It’s a **modern, safer, and more composable way**
to connect contracts, wallets, and apps.  
If you’re stepping into full-stack dApp building, mastering viem is one of the best investments you can make.
