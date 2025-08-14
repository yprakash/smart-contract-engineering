// SPDX-License-Identifier: MIT

pragma solidity ^0.8.20;

contract VariableShadowing {
    uint256 public balance;
    function deposit(uint256 amount) public {
        uint256 balance = balance;
        // creates a new local variable named balance in memory, shadowing the state variable balance.
        // The right-hand balance refers to the state variable (value 0 initially).
        // The left-hand balance is the new local variable.
        // Any changes to this local variable do not persist to storage.
        // So after balance += _amount; executes, only the local copy changes — the storage variable remains 0.
        balance += amount;
        // Warning: Function state mutability can be restricted to view
    }

    // real-world “reward logic” incident in 2020
    // Users were told they got rewards (probably via logs/events) But their actual on-chain balance never changed.
    // Funds were essentially “credited” in a phantom memory world. it was hard to detect until payouts failed.
    function creditReward(address user, uint256 reward) public {
        uint256 balances = balances[user]; // shadows mapping, makes a new memory var
        balances += reward;                // updates memory only
    }
}
