// SPDX-License-Identifier: MIT

pragma solidity ^0.8.20;

contract GasOptimizedNonReentrant {
    mapping(address => uint256) public balances;

    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "Not enough balance");

        // External call
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");

        // State update
        balances[msg.sender] -= amount;
    }
    // Swap the order — update balanceOf before msg.sender.call (single change)
    // reduces reentrancy risk (Checks-Effects-Interactions pattern) and improves gas efficiency.
    // Writing to storage before the external call means if the external call fails, the revert will undo it anyway.
    // But importantly, it reduces the number of expensive SLOAD/SSTORE operations in some patterns
}
