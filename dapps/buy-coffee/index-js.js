import { createWalletClient, custom } from "https://esm.sh/viem"

const connectButton = document.getElementById("connectButton")

let walletClient

connectButton.onclick = connect

async function connect() {
    if (typeof window.ethereum == "undefined") {
        connectButton.innerHTML = "Please install MetaMask!"
    } else {
        walletClient = createWalletClient({
            transport: custom(window.ethereum)
        })
        const accounts = await walletClient.requestAddresses()
        console.log(accounts)
        connectButton.innerHTML = "Connected!"
    }
}
