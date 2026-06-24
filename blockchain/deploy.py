"""
deploy.py - Deploy DeepfakeVerifier contract using Python + web3
Run: python deploy.py
"""
import json, sys
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

# ── Connect ───────────────────────────────────────────────────────────────────
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
if not w3.is_connected():
    print("ERROR: Cannot connect to Geth node!")
    sys.exit(1)

account = Web3.to_checksum_address("0x557C00620eCdcDE7dAc0722b0Cf6b26c434733C3")
print(f"Connected! Block #{w3.eth.block_number}")
print(f"Account  : {account}")
print(f"Balance  : {w3.from_wei(w3.eth.get_balance(account), 'ether')} ETH")

# ── Compile using py-solc-x ───────────────────────────────────────────────────
try:
    from solcx import compile_source, install_solc, get_installed_solc_versions
except ImportError:
    print("Installing py-solc-x...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "py-solc-x"])
    from solcx import compile_source, install_solc, get_installed_solc_versions

SOLC_VERSION = "0.7.6"
installed = [str(v) for v in get_installed_solc_versions()]
if SOLC_VERSION not in installed:
    print(f"Installing solc {SOLC_VERSION}...")
    install_solc(SOLC_VERSION)

print("Compiling DeepfakeVerifier.sol...")
source = open("DeepfakeVerifier.sol").read()

compiled = compile_source(
    source,
    solc_version=SOLC_VERSION,
    output_values=["abi", "bin"],
    optimize=True,
    optimize_runs=200,
)

key     = next(k for k in compiled if "DeepfakeVerifier" in k)
abi     = compiled[key]["abi"]
bytecode = compiled[key]["bin"]

print(f"Compiled! Bytecode size: {len(bytecode)//2} bytes")

# ── Deploy ────────────────────────────────────────────────────────────────────
print("Deploying contract...")

Contract = w3.eth.contract(abi=abi, bytecode=bytecode)

tx_hash = Contract.constructor().transact({
    "from":     account,
    "gas":      5_000_000,
    "gasPrice": w3.to_wei(1, "gwei"),
})

print(f"Tx sent: {tx_hash.hex()}")
print("Waiting for receipt...")

receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
address = receipt["contractAddress"]

print()
print("=" * 50)
print("  Contract deployed successfully!")
print("=" * 50)
print(f"  Address  : {address}")
print(f"  Block    : #{receipt['blockNumber']}")
print(f"  Gas used : {receipt['gasUsed']}")
print("=" * 50)
print()
print("Next step:")
print(f'  Open blockchain.py and set:')
print(f'  contract_address = "{address}"')

# Save outputs
json.dump(abi, open("DeepfakeVerifier_abi.json", "w"), indent=2)
open("DeepfakeVerifier_address.txt", "w").write(address)
print()
print("Saved: DeepfakeVerifier_abi.json")
print("Saved: DeepfakeVerifier_address.txt")