from fastapi import FastAPI
from zexfrost.custom_types import (
    HexStr,
    SharePackage,
    SigningData,
    SignRequest,
    SignTweakRequest,
)
from zexfrost.node.party import set_party
from zexfrost.node.repository import (
    get_key_repository,
    get_nonce_repository,
    set_dkg_repository,
    set_key_repository,
    set_nonce_repository,
)
from zexfrost.node.router import dkg_router, sign_router
from zexfrost.node.settings import node_settings as settings
from zexfrost.node.sign import sign as signature_sign
from zexfrost.utils import get_curve

from src.shared.party import party
from src.shared.repository import Repo


def create_app() -> FastAPI:
    app = FastAPI()
    set_party(party)
    set_dkg_repository(Repo())
    set_key_repository(Repo())
    set_nonce_repository(Repo())
    app.include_router(dkg_router)
    app.include_router(sign_router)
    return app


def data_to_bytes(data: SigningData) -> bytes:
    return data.data["message"].encode()


@sign_router.post("/sign", response_model=SharePackage)
async def sign(sign_request: SignRequest):
    return signature_sign(
        curve=get_curve(sign_request.curve),
        node_id=settings.ID,
        message=data_to_bytes(sign_request.data),
        pubkey_package=sign_request.pubkey_package,
        key_repo=get_key_repository(),
        nonce_repo=get_nonce_repository(),
        commitments=sign_request.commitments,
    )


@sign_router.post("/sign-tweak", response_model=dict[HexStr, SharePackage])
async def sign_with_teak(sign_request: SignTweakRequest):
    result = {}
    for tweak_by, sign_data in sign_request.data.items():
        result[tweak_by] = signature_sign(
            curve=get_curve(sign_request.curve),
            node_id=settings.ID,
            message=data_to_bytes(sign_data),
            pubkey_package=sign_request.pubkey_package,
            key_repo=get_key_repository(),
            nonce_repo=get_nonce_repository(),
            commitments=sign_request.commitments,
            tweak_by=tweak_by,
        )
    return result


app = create_app()
