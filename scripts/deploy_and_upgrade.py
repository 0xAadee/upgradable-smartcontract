from brownie import (
    Box,
    BoxV2,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
    network,
    config,
)
from scripts.helper_scripts import (
    get_account,
    encode_function_data,
    upgrade,
)


def main():
    account = get_account()
    print(f"Active network: {network.show_active()}")
    box = Box.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()].get(
            "verify",
            False,
        ),
    )
    print(f"Box deployed at: {box.address}")

    proxy_admin = ProxyAdmin.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()].get(
            "verify",
            False,
        ),
    )

    # initializer = box.store, 1
    box_encoded_initializer_function = encode_function_data()

    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from": account},
        publish_source=config["networks"][network.show_active()].get(
            "verify",
            False,
        ),
    )
    print(f"Proxy deployed at: {proxy.address}")

    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    print(proxy_box.retrieve())
    tx = proxy_box.store(420, {"from": account})
    tx.wait(1)
    print(proxy_box.retrieve())

    # Upgrade the proxy
    box_v2 = BoxV2.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()].get(
            "verify",
            False,
        ),
    )
    upgrade_tx = upgrade(
        account,
        proxy,
        box_v2.address,
        proxy_admin_contract=proxy_admin,
    )
    upgrade_tx.wait(1)
    print("Proxy has been upgraded!")
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    tx = proxy_box.increment({"from": account})
    tx.wait(1)
    print(proxy_box.retrieve())