// SPDX-License-Identifier: MIT

pragma solidity ^0.8.20;

contract CalldataVsMemoryGas {
    function process1(uint256[] memory arr) public pure returns (uint256 sum) {
        for (uint256 i = 0; i < arr.length; i++) {
            sum += arr[i];
        }
    }

    function process2(uint256[] calldata arr) public pure returns (uint256 sum) {
        for (uint256 i = 0; i < arr.length; i++) {
            sum += arr[i];
        }
    }
    // Both are same functions with same logic, only arr param is memory vs calldata
    // If arr comes from a transaction input and is read-only inside the loop, calldata is the most gas-efficient
    // memory parameters require a full copy from calldata into memory when the function starts.
    // calldata parameters are read-only and accessed directly from the transaction payload — no copy needed.
    // For large arrays, avoiding the copy can save thousands of gas.
    // Extra benefit: calldata also makes your intent explicit — the array won’t be mutated.
}
