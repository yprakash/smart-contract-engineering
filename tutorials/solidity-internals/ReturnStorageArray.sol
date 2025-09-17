// SPDX-License-Identifier: MIT

pragma solidity ^0.8.20;

contract ReturnStorageArray {
    uint256[] public stored;

    // Solidity can’t directly return a storage array to the outside world — it must be copied to memory first.
    // function getData() external view returns (uint256[]) {
    // TypeError: Data location must be "memory" or "calldata" for return parameter in function, but none was given.

    function getData() external view returns (uint256[] memory) {
        // This function returns a storage array as a memory array.
        // The returned array is a copy of the storage array.
        // It is not a reference to the original storage array.
        return stored;
    }
}
