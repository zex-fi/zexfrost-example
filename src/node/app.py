from fastapi import FastAPI
from zexfrost.custom_types import SigningRequest, SigningResponse
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
from src.shared.repository import RedisRepo


def create_app() -> FastAPI:
    app = FastAPI()
    set_party(party)
    set_dkg_repository(RedisRepo())  # type: ignore
    set_key_repository(RedisRepo())
    set_nonce_repository(RedisRepo())
    app.include_router(dkg_router)
    app.include_router(sign_router)
    return app


def data_to_bytes(data: dict) -> bytes:
    return data["message"].encode()


@sign_router.post("/sign", response_model=SigningResponse)
async def sign(sign_request: SigningRequest) -> SigningResponse:
    resp = {}
    for sig_id, sig_data in sign_request.signings_data.items():
        resp[sig_id] = signature_sign(
            curve=get_curve(sig_data.curve),
            node_id=settings.ID,
            message=data_to_bytes(sig_data.data),
            pubkey_package=sig_data.pubkey_package,
            key_repo=get_key_repository(),
            nonce_repo=get_nonce_repository(),
            commitments=sig_data.commitments,
            tweak_by=sig_data.tweak_by,
        )
    return resp


app = create_app()
