import os
import click
from typing import (
    Any,
    Callable,
)

from eth_typing import HexAddress
from ethstaker_deposit.credentials import (
    CredentialList,
)
from ethstaker_deposit.exceptions import ValidationError
from ethstaker_deposit.utils.validation import (
    verify_deposit_data_json,
    validate_int_range,
    validate_password_strength,
    validate_withdrawal_address,
)
from ethstaker_deposit.utils.constants import (
    MAX_DEPOSIT_AMOUNT,
    DEFAULT_VALIDATOR_KEYS_FOLDER_NAME,
)
from ethstaker_deposit.utils.ascii_art import RHINO_0
from ethstaker_deposit.utils.click import (
    captive_prompt_callback,
    choice_prompt_func,
    jit_option,
)
from ethstaker_deposit.utils.intl import (
    closest_match,
    load_text,
)
from ethstaker_deposit.settings import (
    MAINNET,
    ALL_CHAIN_KEYS,
    get_chain_setting,
)


def get_password(text: str) -> str:
    return click.prompt(text, hide_input=True, show_default=False, type=str)


def generate_keys_arguments_decorator(function: Callable[..., Any]) -> Callable[..., Any]:
    '''
    This is a decorator that, when applied to a parent-command, implements the
    to obtain the necessary arguments for the generate_keys() subcommand.
    '''
    decorators = [
        jit_option(
            callback=captive_prompt_callback(
                lambda num: validate_int_range(num, 1, 2**32),
                lambda: load_text(['num_validators', 'prompt'], func='generate_keys_arguments_decorator')
            ),
            help=lambda: load_text(['num_validators', 'help'], func='generate_keys_arguments_decorator'),
            param_decls="--num_validators",
            prompt=lambda: load_text(['num_validators', 'prompt'], func='generate_keys_arguments_decorator'),
        ),
        jit_option(
            default=os.getcwd(),
            help=lambda: load_text(['folder', 'help'], func='generate_keys_arguments_decorator'),
            param_decls='--folder',
            type=click.Path(exists=True, file_okay=False, dir_okay=True),
        ),
        jit_option(
            callback=captive_prompt_callback(
                lambda x: closest_match(x, ALL_CHAIN_KEYS),
                choice_prompt_func(
                    lambda: load_text(['chain', 'prompt'], func='generate_keys_arguments_decorator'),
                    ALL_CHAIN_KEYS
                ),
                default=MAINNET,
            ),
            default=MAINNET,
            help=lambda: load_text(['chain', 'help'], func='generate_keys_arguments_decorator'),
            param_decls='--chain',
            prompt=choice_prompt_func(
                lambda: load_text(['chain', 'prompt'], func='generate_keys_arguments_decorator'),
                ALL_CHAIN_KEYS
            ),
        ),
        jit_option(
            callback=captive_prompt_callback(
                validate_password_strength,
                lambda: load_text(['keystore_password', 'prompt'], func='generate_keys_arguments_decorator'),
                lambda: load_text(['keystore_password', 'confirm'], func='generate_keys_arguments_decorator'),
                lambda: load_text(['keystore_password', 'mismatch'], func='generate_keys_arguments_decorator'),
                True,
            ),
            help=lambda: load_text(['keystore_password', 'help'], func='generate_keys_arguments_decorator'),
            hide_input=True,
            param_decls='--keystore_password',
            prompt=lambda: load_text(['keystore_password', 'prompt'], func='generate_keys_arguments_decorator'),
        ),
        jit_option(
            callback=captive_prompt_callback(
                lambda address: validate_withdrawal_address(None, None, address),
                lambda: load_text(['arg_withdrawal_address', 'prompt'], func='generate_keys_arguments_decorator'),
                lambda: load_text(['arg_withdrawal_address', 'confirm'], func='generate_keys_arguments_decorator'),
                lambda: load_text(['arg_withdrawal_address', 'mismatch'], func='generate_keys_arguments_decorator'),
                default="",
            ),
            default="",
            help=lambda: load_text(['arg_withdrawal_address', 'help'], func='generate_keys_arguments_decorator'),
            param_decls=['--withdrawal_address'],
            prompt=lambda: load_text(['arg_withdrawal_address', 'prompt'], func='generate_keys_arguments_decorator'),
        ),
        jit_option(
            default=False,
            is_flag=True,
            param_decls='--pbkdf2',
            help=lambda: load_text(['arg_pbkdf2', 'help'], func='generate_keys_arguments_decorator'),
        ),
    ]
    for decorator in reversed(decorators):
        function = decorator(function)
    return function


@click.command()
@click.pass_context
def generate_keys(ctx: click.Context, validator_start_index: int,
                  num_validators: int, folder: str, chain: str, keystore_password: str,
                  withdrawal_address: HexAddress, pbkdf2: bool, **kwargs: Any) -> None:
    mnemonic = ctx.obj['mnemonic']
    mnemonic_password = ctx.obj['mnemonic_password']
    amounts = [MAX_DEPOSIT_AMOUNT] * num_validators
    folder = os.path.join(folder, DEFAULT_VALIDATOR_KEYS_FOLDER_NAME)
    chain_setting = get_chain_setting(chain)
    if not os.path.exists(folder):
        os.mkdir(folder)
    click.clear()
    click.echo(RHINO_0)
    click.echo(load_text(['msg_key_creation']))
    credentials = CredentialList.from_mnemonic(
        mnemonic=mnemonic,
        mnemonic_password=mnemonic_password,
        num_keys=num_validators,
        amounts=amounts,
        chain_setting=chain_setting,
        start_index=validator_start_index,
        hex_withdrawal_address=withdrawal_address,
        use_pbkdf2=pbkdf2
    )
    keystore_filefolders = credentials.export_keystores(password=keystore_password, folder=folder)
    deposits_file = credentials.export_deposit_data_json(folder=folder)
    if not credentials.verify_keystores(keystore_filefolders=keystore_filefolders, password=keystore_password):
        raise ValidationError(load_text(['err_verify_keystores']))
    if not verify_deposit_data_json(deposits_file, credentials.credentials):
        raise ValidationError(load_text(['err_verify_deposit']))
    click.echo(load_text(['msg_creation_success']) + folder)
    click.pause(load_text(['msg_pause']))
