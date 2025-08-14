// SPDX-License-Identifier: MIT

pragma solidity ^0.8.20;

// If someone tries to send ETH via selfdestruct(otherContract) targeting this contract
// selfdestruct(address) forces the transfer of ETH to the target address at the EVM level.
// This bypasses all function execution — including receive() and fallback() — and therefore ignores any revert logic.
// The target contract gets ETH whether it wants it or not.
contract SelfDestruct {
    receive() external payable {
        require(false, "No ETH accepted");
    }
}
