// SPDX-License-Identifier: MIT

pragma solidity ^0.8.20;

contract StoragePointerAliasing {
    uint256 public value;
    uint256[] public mainArray;
    function setValue(uint256 _value) public {
        value = _value;
    }
    function getMainArray() public returns (uint256[] memory) {
        mainArray.push(value);
        value += 1;
        return mainArray;
    }

    // temp itself is not a separate variable stored on-chain — it’s a storage pointer (reference) to mainArray.
    // what that means precisely: mainArray lives on-chain, occupying specific storage slots.
    // temp is just a function-scoped reference (like a pointer in C) to those same slots.
    // The pointer temp exists only in memory while the function runs — it’s never persisted to storage.
    // But any changes you make via temp (temp.push(...), temp[0] = 123, etc.) will directly modify mainArray
    // in storage, because they both point to the same storage location.
    function aliasingBug() external {
        uint256[] storage temp = mainArray;
        uint256[] storage another = temp;
        another[0] = 999; // Oops! mainArray[0] also changes
    }
}
