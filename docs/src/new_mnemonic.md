# new-mnemonic

{{#include ./snippet/warning_message.md}}

## Description
Generates a new BIP-39 mnemonic along with validator keystore and deposit files depending on how many validators you wish to create.

## Optional Arguments

- **`--mnemonic_language`**: The language of the BIP-39 mnemonic. Options are: 'chinese_simplified', 'chinese_traditional', 'czech', 'english', 'french', 'italian', 'japanese', 'korean', 'portuguese', 'spanish'.

- **`--chain`**: The chain to use for generating the deposit data. Options are: 'mainnet', 'holesky', etc...

- **`--num_validators`**: Number of validators to create.

- **`--keystore_password`**: The password that is used to encrypt the provided keystore. Note: It's not your mnemonic password. <span class="warning"></span>

- **`--withdrawal_address`**: The Ethereum execution address for validator withdrawals.

- **`--pbkdf2`**: Will use pbkdf2 key derivation instead of scrypt for generated keystore files as defined in [EIP-2335](https://eips.ethereum.org/EIPS/eip-2335#decryption-key). This can be a good alternative if you intend to work with a large number of keys, as it can improve performance however it is less secure. You should only use this option if you understand the associated risks and have familiarity with encryption.

- **`--folder`**: The folder where keystore and deposit data files will be saved.

## Example Usage

```sh
./deposit new-mnemonic
```
