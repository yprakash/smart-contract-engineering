"""
@author: yprakash
-----------------
Utilities for contract-level operations that do **not require a blockchain connection**.
These helpers are designed for offline compilation, analysis, and preparation of
smart contracts for deployment and verification.

This module focuses on:
- Compiling Solidity contracts with `solcx`
- Extracting essential deployment artifacts (ABI, bytecode)
- Preparing metadata needed for contract verification (e.g., Etherscan API payloads)
"""

import os
import json
import subprocess
import tomllib
import solcx
from typing import List, Dict, Any, Optional

# Constants for solcx output keys
KEY_abi = "abi"
KEY_bin = "bin"
KEY_metadata = "metadata"


def flatten_contract(contract_path: str) -> str:
    """
    Flattens a Solidity contract using Foundry's `forge flatten`.
    Returns the flattened Solidity code as a string.
    """
    try:
        result = subprocess.run(
            ["forge", "flatten", contract_path],
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Flattening failed: {e.stderr}")


def compile_contract(
        contract_path: str,
        version: str,
        contract_name: Optional[str] = None,
        output_values: Optional[List[str]] = None,
        optimize: bool = True,
        optimizer_runs: int = 200,
        toml_file_path: Optional[str] = "foundry.toml"
) -> Dict[str, Any]:
    """
    Compiles a Solidity contract and returns deployment + verification artifacts.

    This function:
    - Reads the Solidity source code from disk
    - Applies Foundry-style import remappings if found (`foundry.toml`)
    - Compiles the contract using the specified `solc` version
    - Extracts the ABI, bytecode, and metadata
    - Prepares additional metadata required for contract verification (e.g., Etherscan API)

    Parameters
    ----------
    contract_path : str
        Path to the Solidity contract file (e.g., "contracts/MyContract.sol").
    version : str
        Solidity compiler version (e.g., "0.8.20"). Must be installed via `solcx.install_solc()`.
    contract_name : Optional[str], default=None
        Specific contract name within the file to compile.
        If `None`, the first contract in the file is used.
    output_values : Optional[List[str]], default=None
        Compilation outputs to retrieve. Defaults to `["abi", "bin"]`.
        "metadata" is always appended internally for debugging & verification.
    optimize : bool, default=True
        Whether to enable Solidity optimizer.
    optimizer_runs : int, default=200
        Number of optimizer runs (used if optimizer is enabled).
    toml_file_path : Optional[str], default=foundry.toml
        Path to `foundry.toml` file to load remappings for import resolution.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing:
        - "contract_name": str -> Name of the compiled contract
        - "compiler_version": str -> Solidity version (e.g., "v0.8.20")
        - "optimize": int -> Optimizer enabled flag (0 or 1)
        - "optimizer_runs": int -> Number of optimizer runs
        - "contract_source": str -> Raw Solidity source code
        - "abi": list -> Contract ABI
        - "bin": str -> Compiled bytecode
        - (any other fields from solcx output)

    Notes
    -----
    - Automatically loads import remappings from `foundry.toml` if present.
    - Adds `metadata` to the compilation outputs internally for richer debugging
      and to extract compiler settings for verification (but removes it from final return).
    - Use the returned dictionary directly for deployment (ABI + bytecode) and
      Etherscan V2 verification API payloads.
    """
    remove_fields = []
    if output_values is None:
        output_values = [KEY_abi, KEY_bin]  # Default to ABI + bytecode
    if KEY_metadata not in output_values:
        output_values.append(KEY_metadata)  # Ensure metadata is always available
        remove_fields.append(KEY_metadata)

    remappings = None
    if os.path.exists(toml_file_path):
        with open(toml_file_path, "rb") as f:
            foundry_config = tomllib.load(f)
            remappings = foundry_config["profile"]["default"].get("remappings", None)
            if remappings:
                print(f'[INFO] Loaded remappings from {toml_file_path}: {remappings}')
            else:
                print(f'[WARN] No remappings found in {toml_file_path}')
    else:
        print(f'[WARN] file {toml_file_path} Not found to load remappings')

    with open(contract_path, 'r', encoding="utf-8") as file:
        contract_source = file.read()

    compiled_sol = solcx.compile_source(
        contract_source,
        import_remappings=remappings,
        output_values=output_values,
        solc_version=version,
        optimize=optimize,
        optimize_runs=optimizer_runs
    )

    # Resolve the contract name (pick the first if not specified)
    if contract_name:
        contract_name = next(key for key in compiled_sol if key.endswith(f":{contract_name}"))
    else:
        contract_name = next(iter(compiled_sol))
    print(f'[INFO] Compiled {contract_path} for contract {contract_name}')

    # Extract metadata for compiler settings (useful for verification)
    metadata = json.loads(compiled_sol[contract_name][KEY_metadata])

    # Prepare result dictionary
    result = {
        "contract_name": contract_name.split(":")[-1],
        "compiler_version": "v" + metadata["compiler"]["version"],
        "optimize": 1 if metadata["settings"]["optimizer"]["enabled"] else 0,
        "optimizer_runs": metadata["settings"]["optimizer"]["runs"],
        "contract_source": contract_source
    }
    # Add all requested fields except metadata
    result.update({k: v for k, v in compiled_sol[contract_name].items() if k not in remove_fields})
    return result
