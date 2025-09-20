import { contractAddress, abi } from "./constants-js.js"
import {
    createWalletClient,
    custom,
    formatEther,
    parseEther,
    defineChain,
    createPublicClient,
} from "https://esm.sh/viem"

const connectButton = document.getElementById("connectButton")
const fundButton = document.getElementById("fundButton")
const balanceButton = document.getElementById("balanceButton")
const withdrawButton = document.getElementById("withdrawButton")
const ethAmountInput = document.getElementById("ethAmount")
const balanceValue = document.getElementById("balanceValue")

let walletClient
let publicClient
let connectedAccounts
let wallet

connectButton.onclick = connect
fundButton.onclick = fund
withdrawButton.onclick = withdraw
balanceButton.onclick = getBalance

async function init() {
    if (typeof window.ethereum == "undefined") {
        alert("Please install MetaMask!")
        throw new Error("MetaMask not installed")
    }
    if (!walletClient) {
        walletClient = createWalletClient({
            transport: custom(window.ethereum)
        })
        connectedAccounts = await walletClient.requestAddresses()
        console.log("Connected Accounts:", connectedAccounts)
        console.log("Connected chainId:", await walletClient.getChainId())
    }
    if (!publicClient) {
        publicClient = createPublicClient({
            transport: custom(window.ethereum)
        })
    }
    connectButton.innerHTML = "Connected!"
}

async function getBalance() {
    await init()
    const balance = formatEther(await publicClient.getBalance({
        address: contractAddress
    }))
    console.log(balance)
    // alert(`Balance: ${formatEther(balance)} ETH`)
    balanceValue.innerText = `${balance} ETH`
}

async function connect() {
    await init()
}

async function fund() {
    await init()
    const ethAmount = ethAmountInput.value
    if (ethAmount <= 0) {
        alert("Please enter a valid amount")
        return
    }
    wallet = connectedAccounts[0]
    console.log(`Funding with ${ethAmount} ETH= ${parseEther(ethAmount)} wei...`)

    const {request} = await publicClient.simulateContract({
        address: contractAddress,
        abi: abi,
        functionName: "fund",
        account: wallet,
        chain: await getCurrentChain(walletClient),
        value: parseEther(ethAmount)
    })
    console.log("Fund Request:", request)
    const hash = await walletClient.writeContract(request)
    console.log("Transaction Hash:", hash)
    await publicClient.waitForTransactionReceipt({hash})
    alert("Funding Complete!")
    ethAmountInput.value = ""
}

async function withdraw() {
    await init()
    wallet = connectedAccounts[0]
    // console.log(`Withdrawing with ${ethAmount} ETH= ${parseEther(ethAmount)} wei...`)

    const {request} = await publicClient.simulateContract({
        address: contractAddress,
        abi: abi,
        functionName: "withdraw",
        account: wallet,
        chain: await getCurrentChain(walletClient)
    })
    console.log("Withdraw Request:", request)
    const hash = await walletClient.writeContract(request)
    console.log("Transaction Hash:", hash)
    await publicClient.waitForTransactionReceipt({hash})
    alert("Withdraw Complete!")
}

async function getCurrentChain(client) {
    const chainId = await client.getChainId()
    const currentChain = defineChain({
        id: chainId,
        name: "Local Chain",
        nativeCurrency: {
            name: "Ether",
            symbol: "ETH",
            decimals: 18,
        },
        rpcUrls: {
            default: {
                http: ["http://localhost:8545"],
            },
        },
    })
    return currentChain
}
