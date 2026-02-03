import os
import json
import hashlib
from web3 import Web3


GANACHE_URL = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(GANACHE_URL))

if web3.is_connected():
    print("Connected to Ganache blockchain")
else:
    print("Ganache not connected, blockchain functionality will fallback to database")


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
abi_path = os.path.join(BASE_DIR, 'authentication_app', 'abi', 'DrugContract.json')

with open(abi_path) as f:
    abi = json.load(f)


CONTRACT_ADDRESS = Web3.to_checksum_address("0x36cb291A088d9Fa979e4e7AaC46D0477a7450DF5")
contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)


SYSTEM_ACCOUNT = web3.eth.accounts[0] if web3.is_connected() else None
print(f"SYSTEM_ACCOUNT: {SYSTEM_ACCOUNT}")


def register_drug(name, batch, manufacturer, expiry):
    """
    Registers a drug on the blockchain using SYSTEM_ACCOUNT.
    Returns dict: {"drug_id": ..., "tx_hash": ...}
    """
    # fallback hash for offline mode
    drug_string = f"{name}{batch}{manufacturer}{expiry}"
    fallback_hash = hashlib.sha256(drug_string.encode()).hexdigest()

    if not web3.is_connected() or not SYSTEM_ACCOUNT:
        print("Web3 not connected or SYSTEM_ACCOUNT missing. Using SHA256 fallback.")
        return {"drug_id": fallback_hash, "tx_hash": fallback_hash}

    try:
        # send transaction
        tx_hash = contract.functions.registerDrug(
            name, batch, manufacturer, expiry
        ).transact({'from': SYSTEM_ACCOUNT})

        # wait for transaction to be mined
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        tx_hash_hex = tx_hash.hex()
        print(f"Tx mined. Hash: {tx_hash_hex}")

        # extract event DrugRegistered
        events = contract.events.DrugRegistered().process_receipt(receipt)
        if events:
            blockchain_drug_id = events[0]['args']['drugId'].hex()
            print(f"Blockchain Drug ID: {blockchain_drug_id}")
            return {"drug_id": blockchain_drug_id, "tx_hash": tx_hash_hex}
        else:
            print("No DrugRegistered event found, fallback to SHA256")
            return {"drug_id": fallback_hash, "tx_hash": tx_hash_hex}

    except Exception as e:
        print(f"Blockchain registration failed: {e}")
        return {"drug_id": fallback_hash, "tx_hash": fallback_hash}


def get_drug_from_blockchain(tx_hash):
    """
    Fetch medicine using blockchain tx_hash.
    Returns dict with keys: name, batch, manufacturer, expiry, tx_hash
    Fallbacks to DB if blockchain fails.
    """
    from .models import Medicine

    if not tx_hash:
        return None

    if web3.is_connected():
        try:
            # Blockchain lookup: you may need the tx_hash to get receipt or event
            receipt = web3.eth.get_transaction_receipt(tx_hash)
            events = contract.events.DrugRegistered().process_receipt(receipt)
            if events:
                event = events[0]['args']
                return {
                    "name": event.get("name", "Unknown"),
                    "batch": event.get("batch", "Unknown"),
                    "manufacturer": event.get("manufacturer", "Unknown"),
                    "expiry": event.get("expiry", "Unknown"),
                    "tx_hash": tx_hash
                }
        except Exception as e:
            print(f"Blockchain fetch failed: {e}")

    # fallback to database
    try:
        db_medicine = Medicine.objects.get(tx_hash=tx_hash)
        return {
            "name": db_medicine.name,
            "batch": db_medicine.batch,
            "manufacturer": db_medicine.manufacturer.name,
            "expiry": db_medicine.expiry,
            "tx_hash": db_medicine.tx_hash
        }
    except Medicine.DoesNotExist:
        return None
