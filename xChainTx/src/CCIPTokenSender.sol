// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import { Ownable } from "@openzeppelin/contracts/access/Ownable.sol";
// Library with data structures for CCIP messages
import {Client} from "@chainlink/contracts/src/v0.8/ccip/libraries/Client.sol";
// Interface for the CCIP Router that handles cross-chain messaging
import { IRouterClient } from "@chainlink/contracts/src/v0.8/ccip/interfaces/IRouterClient.sol";
// Standard interface for interacting with ERC20 tokens (USDC and LINK)
import { IERC20 } from "@chainlink/contracts/src/v0.8/vendor/openzeppelin-solidity/v4.8.3/contracts/token/ERC20/IERC20.sol";
// Enhanced functions for safer ERC20 token handling
import { SafeERC20 } from "@chainlink/contracts/src/v0.8/vendor/openzeppelin-solidity/v4.8.3/contracts/token/ERC20/utils/SafeERC20.sol";

contract CCIPTokenSender is Ownable {
    using SafeERC20 for IERC20;

    error CCIPTokenSender__InsufficientBalance(
        IERC20 token,  // The token that has insufficient balance
        uint256 currentBalance,  // The current balance of the sender
        uint256 requiredAmount  // The amount that was attempted to be sent
    );
    error CCIPTokenSender__NothingToWithdraw();

    event USDCTransferred(
        bytes32 messageId,  // Unique identifier for the cross-chain transfer
        uint64 indexed destinationChainSelector,  // The selector for the destination chain (Base Sepolia)
        address indexed receiver,  // The address that will receive the USDC tokens on Base Sepolia
        uint256 amount,  // The amount of USDC tokens transferred
        uint256 ccipFee  // The fee paid in LINK for the CCIP transfer
    );

    // https://docs.chain.link/ccip/directory/testnet/chain/ethereum-testnet-sepolia
    IRouterClient private constant CCIP_ROUTER = IRouterClient(0x0BF3dE8c5D3e8A2B34D2BEeB17ABfCeBaf363A59);
    IERC20 private constant LINK_TOKEN = IERC20(0x779877A7B0D9E8603169DdbD7836e478b4624789);
    IERC20 private constant USDC_TOKEN = IERC20(0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238);

    // https://docs.chain.link/ccip/directory/testnet/chain/ethereum-testnet-sepolia-base-1
    uint64 private constant DESTINATION_CHAIN_SELECTOR = 10344971235874465080;

    constructor() Ownable(msg.sender) {}

    function transferTokens(
        address _receiver,  // The address that will receive tokens on Base Sepolia
        uint256 _amount  // How many USDC tokens to transfer
    ) external returns (
        bytes32 messageId  // returns A unique identifier for tracking the cross-chain transfer
    ) {
        // Check if the address calling the function has a USDC balance of at least the amount they are trying to bridge.
        if (_amount > USDC_TOKEN.balanceOf(msg.sender)) {
            revert CCIPTokenSender__InsufficientBalance(USDC_TOKEN, USDC_TOKEN.balanceOf(msg.sender), _amount);
        }

        Client.EVMTokenAmount memory tokenAmount = Client.EVMTokenAmount({
            token: address(USDC_TOKEN),  // The address of the USDC token contract
            amount: _amount  // The amount of USDC tokens to transfer
        });
        Client.EVMTokenAmount[] memory tokenAmounts = new Client.EVMTokenAmount[](1);
        tokenAmounts[0] = tokenAmount;

        Client.EVM2AnyMessage memory message = Client.EVM2AnyMessage({
            receiver: abi.encode(_receiver),  // The destination address on Base Sepolia
            data: "",  // No additional data is sent with the transfer
            tokenAmounts: tokenAmounts,  // The array of token amounts to transfer
            feeToken: address(LINK_TOKEN),  // The token used to pay for the CCIP fees (LINK)
            extraArgs: Client._argsToBytes(Client.EVMExtraArgsV2({  // Extra arguments for the message
                // allowOutOfOrderExecution: false,  // Indicates that the message should not be executed out of order
                gasLimit: 0  // Gas limit for the callback on the destination chain. Setting gasLimit to 0 because:
                // 1. This is a token-only transfer to an EOA (external owned account)
                // 2. No contract execution is happening on the receiving end
                // 3. needed only when the receiver is a contract that needs to execute code upon receiving the message
            }))
        });

        uint256 ccipFee = CCIP_ROUTER.getFee(
            DESTINATION_CHAIN_SELECTOR,  // The destination chain selector for Base Sepolia
            message  // The message to be sent
        );
        if (ccipFee > LINK_TOKEN.balanceOf(address(this))) {
            revert CCIPTokenSender__InsufficientBalance(LINK_TOKEN, LINK_TOKEN.balanceOf(address(this)), ccipFee);
        }

        LINK_TOKEN.approve(address(CCIP_ROUTER), ccipFee);

        USDC_TOKEN.safeTransferFrom(msg.sender, address(this), _amount);
        USDC_TOKEN.approve(address(CCIP_ROUTER), _amount);

        // Send CCIP Message
        messageId = CCIP_ROUTER.ccipSend(DESTINATION_CHAIN_SELECTOR, message);

        emit USDCTransferred(
            messageId,
            DESTINATION_CHAIN_SELECTOR,
            _receiver,
            _amount,
            ccipFee
        );
    }

    function withdrawToken(address _beneficiary) public onlyOwner {
        uint256 amount = IERC20(USDC_TOKEN).balanceOf(address(this));
        if (amount == 0) {
            revert CCIPTokenSender__NothingToWithdraw();
        }
        IERC20(USDC_TOKEN).transfer(_beneficiary, amount);
    }
}
