import asyncio
import json
import os

from frost_lib import secp256k1_tr
from zexfrost.client.dkg import DKG
from zexfrost.client.sa import SA
from zexfrost.custom_types import PublicKeyPackage, UserSigningData

from src.shared.party import party
from src.shared.repository import Repo


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
    pubkey_package = await dkg.run()
    store_pubkey_package(pubkey_package)
    return pubkey_package


async def main(sa: SA):
    data = {
        "1": UserSigningData(tweak_by=b"hello".hex(), data={"message": "message"}, message=b"message"),
        "2": UserSigningData(tweak_by=b"hello".hex(), data={"message": "message"}, message=b"message"),
    }
    signature = await sa.sign("sign/sign", data)
    print(signature)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    dkg = DKG(
        curve=secp256k1_tr,
        party=party,
        max_signers=3,
        min_singers=2,
        repository=Repo(),
        loop=loop,
    )
    task = loop.create_task(dkg_main(dkg))
    pubkey_package = loop.run_until_complete(task)
    sa = SA(
        curve=secp256k1_tr,
        party=party,
        pubkey_package=pubkey_package,
        loop=loop,
    )
    loop.run_until_complete(main(sa))
