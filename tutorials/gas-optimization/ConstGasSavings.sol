// SPDX-License-Identifier: MIT

pragma solidity ^0.8.20;

contract ConstGasSavings {
    uint256 public constant FEE = 3;
    uint256 public fee = 3;

    function calcFEE(uint256 x) public pure returns (uint256) {
        return x * FEE;
    }

    /**
     * calcFEE() above is generally cheaper than calcFee() below.
     * constant variables are inlined by the compiler — they don’t occupy a storage slot at all.
     * This means accessing them costs 0 gas beyond the base instruction, because the compiler literally replaces FEE with 3 in the bytecode.
     * In contrast, fee is a storage variable, so reading it costs an SLOAD (~2,100 gas first read, ~100 gas subsequent reads in the same transaction).
     */
    function calcFee(uint256 x) public view returns (uint256) {
        return x * fee;
    }
}