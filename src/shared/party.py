from zexfrost.custom_types import Node

party = (
    Node(
        id="0000000000000000000000000000000000000000000000000000000000000001",
        host="http://localhost",  # type: ignore
        port=8001,
        public_key="0236c68a0aa21e42fa3295af3c0fd655b8e3ec54ba22de2f147d184c7a0855b1a2",
    ),
    Node(
        id="0000000000000000000000000000000000000000000000000000000000000002",
        host="http://localhost",  # type: ignore
        port=8002,
        public_key="0236c68a0aa21e42fa3295af3c0fd655b8e3ec54ba22de2f147d184c7a0855b1a2",
    ),
    Node(
        id="0000000000000000000000000000000000000000000000000000000000000003",
        host="http://localhost",  # type: ignore
        port=8003,
        public_key="0236c68a0aa21e42fa3295af3c0fd655b8e3ec54ba22de2f147d184c7a0855b1a2",
    ),
)
