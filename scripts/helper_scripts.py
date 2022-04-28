import eth_utils
from brownie import (
    accounts,
    network,
    config,
)

LOCAL_BLOCKCHAIN_ENVIRONMENT = ["development", "ganache-local"]
FORKED_LOCAL_ENVIRONMENT = ["mainnet-fork"]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    elif id:
        return accounts.get(id)
    elif (network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENT
          or network.show_active() in FORKED_LOCAL_ENVIRONMENT):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])


def encode_function_data(initializer=None, *args):
    if not initializer or len(args) == 0:
        return eth_utils.to_bytes(hexstr="0x")
    return initializer.encode_input(*args)


def upgrade(
    account,
    proxy,
    new_implementation_address,
    proxy_admin_contract=None,
    initializer=None,
    *args,
):
    if proxy_admin_contract:
        if initializer:
            encoded_function_call = encode_function_data(initializer, *args)
            tx = proxy_admin_contract.upgradeAndCall(
                proxy.address,
                new_implementation_address,
                encoded_function_call,
                {"from": account},
            )
        else:
            tx = proxy_admin_contract.upgrade(
                proxy.address,
                new_implementation_address,
                {"from": account},
            )
    else:
        if initializer:
            encoded_function_call = encode_function_data(initializer, *args)
            tx = proxy.upgradeToAndCall(
                new_implementation_address,
                encoded_function_call,
                {"from": account},
            )
        else:
            tx = proxy.upgradeTo(
                new_implementation_address,
                {"from": account},
            )
    return tx