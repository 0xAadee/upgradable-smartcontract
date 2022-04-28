import pytest
from brownie import (
    Box,
    BoxV2,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
    network,
    exceptions,
)
from scripts.helper_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENT,
    get_account,
    encode_function_data,
    upgrade,
)


def test_proxy_upgrade():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENT:
        pytest.skip("This test requires local blockchain environment")
    account = get_account()
    box = Box.deploy({"from": account})
    proxy_admin = ProxyAdmin.deploy({"from": account})
    box_encoded_initializer_function = encode_function_data()
    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from": account},
    )

    # Upgrade to BoxV2
    box_v2 = BoxV2.deploy({"from": account})
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    with pytest.raises(exceptions.VirtualMachineError):
        proxy_box.increment({"from": account})
    upgrade_tx = upgrade(
        account,
        proxy,
        box_v2,
        proxy_admin_contract=proxy_admin,
    )
    upgrade_tx.wait(1)
    assert proxy_box.retrieve() == 0
    proxy_box.increment({"from": account})
    assert proxy_box.retrieve() == 1