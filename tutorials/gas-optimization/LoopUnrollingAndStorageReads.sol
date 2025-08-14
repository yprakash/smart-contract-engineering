// SPDX-License-Identifier: MIT

pragma solidity ^0.8.20;

contract LoopUnrollingAndStorageReads {
    uint256 public total;
    uint256[] public arr = [1, 2, 3, 4, 5];

    function sum() public {
        for (uint256 i = 0; i < arr.length; i++) {
            total += arr[i];
        }
    }
    // Which optimization would most reduce gas in sum() without changing logic?
    // 1. Each arr.length read is a storage read (SLOAD), which costs ~2,100 gas the first time (and ~100 gas
    // afterward in the same transaction). Reading it once into a local variable avoids repeated SLOADs
    // 2. Writing to storage (SSTORE) is very expensive (~20,000 gas for a new value, ~5,000 for updating a non-zero slot).
    // By caching total in a local variable and updating it in memory, you perform only one SSTORE instead of multiple inside the loop.
}
