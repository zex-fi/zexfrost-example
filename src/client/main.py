import asyncio

from frost_lib import secp256k1_tr
from zexfrost.client.dkg import DKG
from zexfrost.client.sa import SA
from zexfrost.custom_types import PublicKeyPackage, SigningData

from src.shared.party import party
from src.shared.repository import Repo


async def dkg_main(dkg: DKG) -> PublicKeyPackage:
    result = await dkg.run()
    return result


async def main(sa: SA):
    message = "hello"
    tweak_by = b"tweak"
    commitments = await sa.commitment(tweak_by.hex())
    signature = await sa.sign_with_tweak(
        route="sign/sign-tweak",
        data={tweak_by.hex(): SigningData(data={"message": message})},
        commitments=commitments,
        message={tweak_by.hex(): message.encode()},
    )
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
