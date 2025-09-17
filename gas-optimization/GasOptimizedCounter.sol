// SPDX-License-Identifier: MIT
pragma solidity ^0.8.25;

contract GasOptimizedCounter {
    uint256 public counter;
    // Gas-inefficient
    function increment() public {
        counter += 1;
    }
    // Gas-efficient (using inline assembly)
    function incrementOptimized(uint256 value) public {
        assembly {
            sstore(counter.slot, add(sload(counter.slot), value))
        }
    }
}

