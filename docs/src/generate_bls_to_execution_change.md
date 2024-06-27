# generate-bls-to-execution-change

{{#include ./snippet/warning_message.md}}

## Description
Generates a BLS to execution address change message.

## Optional Arguments

- **`--bls_to_execution_changes_folder`**: The path to store the change JSON file.

- **`--chain`**: The chain to use for generating the deposit data. Options are: 'mainnet', 'holesky', etc.

- **`--mnemonic`**: The mnemonic you used to create withdrawal credentials. <span class="warning"></span>

- **`--mnemonic_password`**: The mnemonic password you used in your key generation. Note: It's not the keystore password. <span class="warning"></span>

- **`--validator_start_index`**: The index position for the keys to start generating withdrawal credentials for.

- **`--validator_indices`**: A list of the chosen validator index number(s) as identified on the beacon chain. Split multiple items with whitespaces or commas.

- **`--bls_withdrawal_credentials_list`**: A list of the old BLS withdrawal credentials of the given validator(s). It is for confirming you are using the correct keys. Split multiple items with whitespaces or commas.

- **`--withdrawal_address`**: If this field is set and valid, the given Ethereum execution address will be used to create the withdrawal credentials. Otherwise it will generate withdrawal credentials with the mnemonic-derived withdrawal public key.

- **`--devnet_chain_setting`**: The custom chain setting of a devnet or testnet. Note that it will override your `--chain` choice.

## Example Usage

```sh
./deposit generate-bls-to-execution-change
```
