// SPDX-License-Identifier: MIT

pragma solidity ^0.8.26;

import { Log, ILogAutomation } from "@chainlink/contracts/src/v0.8/automation/interfaces/ILogAutomation.sol";

/// @author yprakash
/// @title EventWatcher
/// @notice A Chainlink Log Trigger Automation consumer contract.
/// @dev Listens for DepositEvent and WithdrawEvent logs, and determines whether upkeep (on-chain action) is needed
contract EventWatcher is ILogAutomation {
    /// @notice Emitted when upkeep is performed on-chain
    event UpkeepPerformed(address indexed by, bytes32 indexed eventSig, uint256 upkeepNumber);

    /// @dev Precomputed keccak256 signatures of the watched events.
    bytes32 public constant DEPOSIT_SIG = keccak256("DepositEvent(address)");
    bytes32 public constant WITHDRAW_SIG = keccak256("WithdrawEvent(address)");
    uint256 public depositCount;
    uint256 public withdrawCount;
    uint256 public upkeepsCheckedOffChain;
    uint256 public upkeepsPerformedOnChain;

    constructor() {
        depositCount = 0;
        withdrawCount = 0;
        upkeepsCheckedOffChain = 0;
        upkeepsPerformedOnChain = 0;
    }

    function bytes32ToAddress(bytes32 _address) internal pure returns (address) {
        return address(uint160(uint256(_address)));
    }

    /**
     * @notice Called off-chain by Chainlink Automation nodes when a log is detected.
     * @dev Determines whether upkeep is needed based on event type and count parity.
     * @param log The log data emitted by the EventEmitter contract.
     * @param (unused) Reserved for future use (extra data).
     * @return upkeepNeeded Whether upkeep should be performed.
     * @return performData Encoded data to be passed into performUpkeep().
     */
    function checkLog(Log calldata log, bytes memory)
        external override returns(bool upkeepNeeded, bytes memory performData)
    {
        unchecked { upkeepsCheckedOffChain++; }
        bytes32 eventSignature = log.topics[0];
        if (eventSignature == DEPOSIT_SIG) {
            unchecked { depositCount++; }
            upkeepNeeded = depositCount % 2 == 1;  // act only for odd-numbered deposits
            address logSender = bytes32ToAddress(log.topics[1]); // Extracting the sender address from the log
            performData = abi.encode(eventSignature, logSender);
        } else if (eventSignature == WITHDRAW_SIG) {
            unchecked { withdrawCount++; }
            upkeepNeeded = withdrawCount % 2 == 0;  // act only for even-numbered withdrawals
            address logSender = bytes32ToAddress(log.topics[1]);
            performData = abi.encode(eventSignature, logSender);
        } else {
            upkeepNeeded = false; // Unknown event - no action
            performData = "";
        }
    }

    function performUpkeep(bytes calldata performData) external override {
        unchecked { upkeepsPerformedOnChain++; }
        (bytes32 eventSig, address logSender) = abi.decode(performData, (bytes32, address));
        emit UpkeepPerformed(logSender, eventSig, upkeepsPerformedOnChain);
    }
}
