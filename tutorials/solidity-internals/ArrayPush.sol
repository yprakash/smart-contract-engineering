// SPDX-License-Identifier: MIT

pragma solidity ^0.8.20;

contract ArrayPush {
    uint256[] public arr;

    function pushOne() public {
        uint256[] memory temp = arr;
        // In Solidity, you can copy a storage array to a memory array.
        // This creates a new array in memory with the same contents as arr at the time of copying.
        // This is not a reference — it’s a deep copy.
        // But push() is only available for storage arrays, not memory arrays.
        // Memory arrays in Solidity have a fixed size once created.
        temp.push(1);  // TypeError: Member "push" is not available in uint256[] memory outside of storage.
        // To push to a memory array, you need to create a new storage array.
        // Uses of memory arrays in Solidity:
        // 1. Temporary storage for calculations but don’t need it after.
        // 2. Returning arrays from functions (must be memory).
        // 3. Passing arrays to functions that require memory arrays.
    }
}
