from web3 import Web3

# -----------------------------
# Address & Contract Helpers
# -----------------------------
def to_checksum(addr):
    """Convert any address to checksum format."""
    return Web3.to_checksum_address(addr)

# -----------------------------
# Gas Estimation Helper
# -----------------------------
def estimate_tx_gas(contract_function, from_address):
    """
    Safely estimate gas for a contract function call.
    Returns None if estimation fails.
    """
    try:
        return contract_function.estimate_gas({"from": from_address})
    except Exception:
        return None

# -----------------------------
# Logging Helpers
# -----------------------------
def log_info(msg):
    print(f"[INFO] {msg}")

def log_error(msg):
    print(f"[ERROR] {msg}")
