// SPDX-License-Identifier: MIT

pragma solidity ^0.8.24;

import { ERC20 } from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import { AccessControl } from "@openzeppelin/contracts/access/AccessControl.sol";

contract LogicContract {
    uint256 public value; // storage slot 0

    function setValue(uint256 _v) public {
        value = _v;
    }
}

contract MyERC20 is ERC20, AccessControl {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    address public logic; // stored at slot 0! COLLIDES with ERC20's _balances

    constructor(address _logic) ERC20("Test", "TST") {
        logic = _logic;
    }

    function callSetValue(uint256 x) external {
        (bool success, ) = logic.delegatecall(
            abi.encodeWithSignature("setValue(uint256)", x)
        );
        require(success, "delegatecall failed");
    }
}

/* What Goes Wrong:
- logic is stored at slot 0, but ERC20 already uses slot 0 for _balances.
- When LogicContract.setValue(x) runs via delegatecall, it writes to slot 0.
- So instead of updating value, you corrupt your ERC20 _balances mapping!
This is real-world dangerous and auditor-critical knowledge.
 */