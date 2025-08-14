// SPDX-License-Identifier: MIT

pragma solidity ^0.8.20;

contract StorageMemoryRef {
    struct Data { uint256 x; }
    Data[] public list;

    function bad(uint256 _x) public {
        Data memory d = list[0];  // creates a separate memory instance
        d.x = _x;  // and modifying d.x changes only the memory copy, not the storage.
    }
    // If list initially has one element { x: 1 }, and bad(99) is called, what will list[0].x be afterward? 1
}