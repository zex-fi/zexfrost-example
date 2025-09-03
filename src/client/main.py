import asyncio
import json
import os
import time

from aptos_sdk.account import Account, ed25519
from aptos_sdk.account_address import AccountAddress
from aptos_sdk.async_client import FaucetClient, RestClient
from aptos_sdk.authenticator import Authenticator, Ed25519Authenticator
from aptos_sdk.bcs import Serializer
from aptos_sdk.transactions import (
    EntryFunction,
    RawTransaction,
    SignedTransaction,
    TransactionArgument,
    TransactionPayload,
)
from aptos_sdk.type_tag import StructTag, TypeTag
from frost_lib import ed25519 as frost
from zexfrost.client.dkg import DKG
from zexfrost.client.sa import SA
from zexfrost.custom_types import PublicKeyPackage, UserSigningData

from src.shared.party import party
from src.shared.repository import Repo

NODE_URL = "https://fullnode.devnet.aptoslabs.com/v1"
FAUCET_URL = "https://faucet.devnet.aptoslabs.com"


def compute_tweaked_pubkey(pubkey_package: PublicKeyPackage, salt: int) -> PublicKeyPackage:
    from frost_lib import ed25519 as frost

    tweak_by = salt.to_bytes(8, "big")

    # Tweak the public key package
    pubkey_package_tweaked = frost.pubkey_package_tweak(pubkey_package, tweak_by)

    return pubkey_package_tweaked


def load_pubkey_package() -> PublicKeyPackage | None:
    """Load the public key package from a file"""
    try:
        file_path = "pubkey_package.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)
                return PublicKeyPackage(**data)
        return None
    except Exception as e:
        print(f"Error loading public key package: {e}")
        return None


def store_pubkey_package(pubkey_package: PublicKeyPackage) -> None:
    """Store the public key package in a file"""
    try:
        file_path = "pubkey_package.json"
        with open(file_path, "w") as f:
            # Convert the PublicKeyPackage object to a dictionary
            data = pubkey_package.model_dump(mode="json")
            json.dump(data, f, indent=2)
        print(f"Public key package stored in {file_path}")
    except Exception as e:
        print(f"Error storing public key package: {e}")


async def dkg_main(dkg: DKG) -> PublicKeyPackage:
    pubkey_package = load_pubkey_package()
    if pubkey_package is not None:
        return pubkey_package
    while True:
        pubkey_package = await dkg.run()
        print(int(pubkey_package.verifying_key, 16))
        if (
            int(pubkey_package.verifying_key[2:], 16)
            < 57896044618658097711785492504343953926418782139537452191302581570759080747169
        ):
            break
    store_pubkey_package(pubkey_package)
    return pubkey_package


async def main(sa: SA):
    pubkey_package = sa.pubkey_package
    tweak_by = b"sample merkle root"
    tweaked_pubkey_package = frost.pubkey_package_tweak(pubkey_package, tweak_by)
    pubkey = ed25519.PublicKey.from_str(tweaked_pubkey_package.verifying_key)
    tweaked_address = AccountAddress.from_key(pubkey)
    print("Tweak address:", tweaked_address)

    # Generate accounts
    alice = Account.generate()

    # make connection
    rest_client = RestClient(NODE_URL)
    faucet_client = FaucetClient(FAUCET_URL, rest_client)

    # Fund tweaked wallet
    await faucet_client.fund_account(tweaked_address, 10_000_000)

    entry_function = EntryFunction.natural(
        module="0x1::coin",
        function="transfer",
        ty_args=[TypeTag(StructTag.from_str("0x1::aptos_coin::AptosCoin"))],
        args=[
            TransactionArgument(alice.address(), Serializer.struct),
            TransactionArgument(100, Serializer.u64),
        ],
    )
    # Build the raw transaction
    chain_id = await rest_client.chain_id()

    sequence_number = await rest_client.account_sequence_number(tweaked_address)

    raw_transaction = RawTransaction(
        sender=tweaked_address,
        sequence_number=sequence_number,
        payload=TransactionPayload(entry_function),
        max_gas_amount=2000,
        gas_unit_price=100,
        expiration_timestamps_secs=int(time.time()) + 600,
        chain_id=chain_id,
    )
    print(raw_transaction)
    data = {
        "1": UserSigningData(
            data={"message": raw_transaction.keyed().hex()}, message=raw_transaction.keyed(), tweak_by=tweak_by
        ),
    }
    frost_signature = await sa.sign("sign/sign", data)
    print("signature:", frost_signature)

    # Create the authenticator with our multisig configuration
    authenticator = Authenticator(
        Ed25519Authenticator(
            ed25519.PublicKey.from_str(tweaked_pubkey_package.verifying_key),
            ed25519.Signature.from_str(frost_signature["1"]),
        )
    )

    signed_transaction = SignedTransaction(raw_transaction, authenticator)

    print("\n=== Submitting transfer transaction ===")
    print(signed_transaction)
    tx_hash = await rest_client.submit_bcs_transaction(signed_transaction)
    await rest_client.wait_for_transaction(tx_hash)
    print(f"Transaction hash: {tx_hash}")

    # Check balances
    tweaked_balance = await rest_client.account_balance(tweaked_address)
    alice_balance = await rest_client.account_balance(alice.address())

    print(f"Tweaked balance: {tweaked_balance}")
    print(f"Alice balance: {alice_balance}")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    dkg = DKG(
        curve=frost,
        party=party,
        max_signers=3,
        min_singers=2,
        repository=Repo(),
        loop=loop,
    )
    task = loop.create_task(dkg_main(dkg))
    pubkey_package = loop.run_until_complete(task)
    sa = SA(
        curve=frost,
        party=party,
        pubkey_package=pubkey_package,
        loop=loop,
    )
    loop.run_until_complete(main(sa))
