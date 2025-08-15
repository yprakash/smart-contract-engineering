// SPDX-License-Identifier: MIT

pragma solidity ^0.8.20;

contract GasDoS {
    mapping(address => bool) public isWhitelisted;
    address[] public whitelistArray;

    function add(address user) public {
        isWhitelisted[user] = true;
        whitelistArray.push(user);
    }

    function removeAll() public {
        for (uint256 i = 0; i < whitelistArray.length; i++) {
            isWhitelisted[whitelistArray[i]] = false;
        }
        delete whitelistArray;
    }
    // Each write costs ~5,000 gas (non-zero → zero)
    // If whitelist grows to 10,000 addresses, removeAll() becomes un-callable
    // because the loop can exceed the block gas limit (~30 million on Ethereum mainnet).
}
