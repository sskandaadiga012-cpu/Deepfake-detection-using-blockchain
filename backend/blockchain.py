from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
import hashlib, json

# ── Connect ───────────────────────────────────────────────────────────────────
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

account          = "0x557C00620eCdcDE7dAc0722b0Cf6b26c434733C3"
contract_address = "0xb292CEBe9787716Ea3A095a730Ab7d8819e5a6Ed"
with open(r"D:\blockchain\DeepfakeVerifier_abi.json") as f:
    abi = json.load(f)

contract = w3.eth.contract(
    address=Web3.to_checksum_address(contract_address),
    abi=abi
)

# ── Functions ─────────────────────────────────────────────────────────────────
def compute_hash(data) -> str:
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).hexdigest()

def log_result(features, metadata: str, result: str) -> str:
    video_hash = compute_hash(str(features) + metadata)
    is_fake    = result.lower() in ("deepfake", "fake")
    detector   = f"ResNeXt+LSTM | {metadata}"
    tx_hash = contract.functions.storeResult(
        video_hash, is_fake, detector
    ).transact({"from": account, "gas": 200000, "gasPrice": w3.to_wei(1, "gwei")})
    w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"[Blockchain] Logged! tx={tx_hash.hex()[:16]}...")
    return tx_hash.hex()

def store_result(video_hash: str, is_fake: bool, detector: str) -> str:
    tx_hash = contract.functions.storeResult(
        video_hash, is_fake, detector
    ).transact({"from": account, "gas": 200000, "gasPrice": w3.to_wei(1, "gwei")})
    w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_hash.hex()

def get_result(video_hash: str) -> dict:
    is_fake, timestamp, detector = contract.functions.getResult(video_hash).call(
        {"from": account}
    )
    return {
        "video_hash": video_hash,
        "is_fake":    is_fake,
        "result":     "Deepfake" if is_fake else "Real",
        "timestamp":  timestamp,
        "detector":   detector,
    }