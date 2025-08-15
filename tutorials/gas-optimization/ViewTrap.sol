// SPDX-License-Identifier: MIT

pragma solidity ^0.8.20;

contract ViewTrap {
    uint256 public counter;
    function getDouble() public view returns (uint256) {
        return counter * 2;
    }
    /**
     * view functions are only “free” when called off-chain via eth_call — this is a local simulation that doesn’t alter the blockchain state.
     * When a view function is invoked inside a transaction (e.g., from another contract), it still executes on-chain and consumes gas exactly like any other function.
     */
}
