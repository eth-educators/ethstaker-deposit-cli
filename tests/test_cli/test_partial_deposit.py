import json
import os
import pytest
import time

from click.testing import CliRunner

from eth_utils import to_normalized_address

from ethstaker_deposit.credentials import Credential
from ethstaker_deposit.deposit import cli
from ethstaker_deposit.settings import get_chain_setting
from ethstaker_deposit.utils.constants import (
    DEFAULT_PARTIAL_DEPOSIT_FOLDER_NAME,
    DEFAULT_VALIDATOR_KEYS_FOLDER_NAME,
)
from .helpers import clean_folder, clean_key_folder, clean_partial_deposit_folder, get_permissions


@pytest.mark.parametrize(
    'amount',
    [
        ("32"),
        ("1"),
        ("432.123456789"),
        ("18446744073.709551615"),
    ]
)
def test_partial_deposit(amount: str) -> None:
    my_folder_path = os.path.join(os.getcwd(), 'TESTING_TEMP_FOLDER')
    partial_deposit_folder = os.path.join(my_folder_path, DEFAULT_PARTIAL_DEPOSIT_FOLDER_NAME)
    clean_partial_deposit_folder(my_folder_path)
    if not os.path.exists(my_folder_path):
        os.mkdir(my_folder_path)
    if not os.path.exists(partial_deposit_folder):
        os.mkdir(partial_deposit_folder)

    chain_settings = get_chain_setting()
    password = "Password1"
    withdrawal_address = "0xcd60A5f152724480c3a95E4Ff4dacEEf4074854d"
    mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"

    credential = Credential(mnemonic=mnemonic,
                            mnemonic_password="",
                            index=0,
                            amount=32000000000,
                            chain_setting=chain_settings,
                            hex_withdrawal_address=to_normalized_address(withdrawal_address))

    keystore_file_folder = credential.save_signing_keystore(password, partial_deposit_folder, time.time())

    runner = CliRunner()
    inputs = ['english', 'mainnet', password, amount, withdrawal_address, withdrawal_address]
    data = '\n'.join(inputs)
    arguments = [
        '--ignore_connectivity',
        'partial-deposit',
        '--keystore', keystore_file_folder,
        '--output_folder', my_folder_path,
    ]
    result = runner.invoke(cli, arguments, input=data)
    assert result.exit_code == 0

    _, _, folder_files = next(os.walk(partial_deposit_folder))

    deposit_files = [deposit_file for deposit_file in folder_files if deposit_file.startswith('deposit')]

    assert len(deposit_files) == 1

    if os.name == 'posix':
        assert get_permissions(partial_deposit_folder, deposit_files[0]) == '0o440'

    clean_partial_deposit_folder(my_folder_path)


def test_partial_deposit_matches_existing_mnemonic_deposit() -> None:
    my_folder_path = os.path.join(os.getcwd(), 'TESTING_TEMP_FOLDER')
    validator_key_folder = os.path.join(my_folder_path, DEFAULT_VALIDATOR_KEYS_FOLDER_NAME)
    partial_deposit_folder = os.path.join(my_folder_path, DEFAULT_PARTIAL_DEPOSIT_FOLDER_NAME)
    clean_partial_deposit_folder(my_folder_path)
    clean_key_folder(my_folder_path)
    if not os.path.exists(my_folder_path):
        os.mkdir(my_folder_path)

    password = "Password1"
    withdrawal_address = "0xcd60A5f152724480c3a95E4Ff4dacEEf4074854d"

    runner = CliRunner()
    arguments = [
        '--language', 'english',
        '--non_interactive',
        'existing-mnemonic',
        '--num_validators', '1',
        '--mnemonic', "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about",
        '--validator_start_index', '1',
        '--chain', 'mainnet',
        '--keystore_password', password,
        '--withdrawal_address', f"{withdrawal_address}",
        '--folder', my_folder_path,
    ]
    result = runner.invoke(cli, arguments)
    assert result.exit_code == 0

    _, _, validator_key_files = next(os.walk(validator_key_folder))

    key_files = [key_file for key_file in validator_key_files if key_file.startswith('keystore')]

    deposit_files = [key_file for key_file in validator_key_files if key_file.startswith('deposit')]

    assert len(key_files) == 1
    assert len(deposit_files) == 1
    key_file_location = os.path.join(validator_key_folder, key_files[0])

    inputs = ['english', 'mainnet', password, "32", withdrawal_address, withdrawal_address]
    data = '\n'.join(inputs)
    arguments = [
        '--ignore_connectivity',
        'partial-deposit',
        '--keystore', key_file_location,
        '--output_folder', my_folder_path,
    ]
    result = runner.invoke(cli, arguments, input=data)
    assert result.exit_code == 0

    _, _, folder_files = next(os.walk(partial_deposit_folder))

    partial_deposit_files = [deposit_file for deposit_file in folder_files if deposit_file.startswith('deposit')]

    assert len(partial_deposit_files) == 1

    with open(os.path.join(validator_key_folder, deposit_files[0]), 'r') as file1:
        deposit_contents = file1.read()

    with open(os.path.join(partial_deposit_folder, partial_deposit_files[0]), 'r') as file2:
        partial_deposit_contents = file2.read()

    assert deposit_contents == partial_deposit_contents

    if os.name == 'posix':
        assert get_permissions(partial_deposit_folder, partial_deposit_files[0]) == '0o440'

    clean_folder(my_folder_path, validator_key_folder, True)
    clean_partial_deposit_folder(my_folder_path)


def test_partial_deposit_does_not_match_if_amount_differs() -> None:
    my_folder_path = os.path.join(os.getcwd(), 'TESTING_TEMP_FOLDER')
    validator_key_folder = os.path.join(my_folder_path, DEFAULT_VALIDATOR_KEYS_FOLDER_NAME)
    partial_deposit_folder = os.path.join(my_folder_path, DEFAULT_PARTIAL_DEPOSIT_FOLDER_NAME)
    clean_partial_deposit_folder(my_folder_path)
    clean_key_folder(my_folder_path)
    if not os.path.exists(my_folder_path):
        os.mkdir(my_folder_path)

    password = "Password1"
    withdrawal_address = "0xcd60A5f152724480c3a95E4Ff4dacEEf4074854d"

    runner = CliRunner()
    arguments = [
        '--language', 'english',
        '--non_interactive',
        'existing-mnemonic',
        '--num_validators', '1',
        '--mnemonic', "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about",
        '--validator_start_index', '1',
        '--chain', 'mainnet',
        '--keystore_password', password,
        '--withdrawal_address', f"{withdrawal_address}",
        '--folder', my_folder_path,
    ]
    result = runner.invoke(cli, arguments)
    assert result.exit_code == 0

    _, _, validator_key_files = next(os.walk(validator_key_folder))

    key_files = [key_file for key_file in validator_key_files if key_file.startswith('keystore')]

    deposit_files = [key_file for key_file in validator_key_files if key_file.startswith('deposit')]

    assert len(key_files) == 1
    assert len(deposit_files) == 1
    key_file_location = os.path.join(validator_key_folder, key_files[0])

    inputs = ['english', 'mainnet', password, "33", withdrawal_address, withdrawal_address]
    data = '\n'.join(inputs)
    arguments = [
        '--ignore_connectivity',
        'partial-deposit',
        '--keystore', key_file_location,
        '--output_folder', my_folder_path,
    ]
    result = runner.invoke(cli, arguments, input=data)
    assert result.exit_code == 0

    _, _, folder_files = next(os.walk(partial_deposit_folder))

    partial_deposit_files = [deposit_file for deposit_file in folder_files if deposit_file.startswith('deposit')]

    assert len(partial_deposit_files) == 1

    with open(os.path.join(validator_key_folder, deposit_files[0]), 'r') as file1:
        deposit_contents = file1.read()

    with open(os.path.join(partial_deposit_folder, partial_deposit_files[0]), 'r') as file2:
        partial_deposit_contents = file2.read()

    assert deposit_contents != partial_deposit_contents
    deposit_contents_dict = json.loads(deposit_contents)[0]
    partial_deposit_contents_dict = json.loads(partial_deposit_contents)[0]
    assert deposit_contents_dict["pubkey"] == partial_deposit_contents_dict["pubkey"]
    assert deposit_contents_dict["withdrawal_credentials"] == partial_deposit_contents_dict["withdrawal_credentials"]
    assert deposit_contents_dict["amount"] != partial_deposit_contents_dict["amount"]
    assert deposit_contents_dict["signature"] != partial_deposit_contents_dict["signature"]
    assert deposit_contents_dict["deposit_message_root"] != partial_deposit_contents_dict["deposit_message_root"]
    assert deposit_contents_dict["deposit_data_root"] != partial_deposit_contents_dict["deposit_data_root"]
    assert deposit_contents_dict["fork_version"] == partial_deposit_contents_dict["fork_version"]
    assert deposit_contents_dict["network_name"] == partial_deposit_contents_dict["network_name"]
    assert deposit_contents_dict["deposit_cli_version"] == partial_deposit_contents_dict["deposit_cli_version"]

    if os.name == 'posix':
        assert get_permissions(partial_deposit_folder, partial_deposit_files[0]) == '0o440'

    clean_folder(my_folder_path, validator_key_folder, True)
    clean_partial_deposit_folder(my_folder_path)
