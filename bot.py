import os
import sys
from web3 import Web3
from dotenv import load_dotenv
import time
from colorama import init, Fore, Style

init(autoreset=True)
BANNER = """
╔════════════════════════════════════════════════════════════╗
║                    🌟 Pharos Deploy Bot                    ║
║           Automate contract deployment on Pharos           ║
║         Developed by: https://t.me/sentineldiscus          ║
╚════════════════════════════════════════════════════════════╝
"""

print("\033]0;佐賀県産 （𝒀𝑼𝑼𝑹𝑰） 🇯🇵\007", end='', flush=True)
sys.stdout.flush()

load_dotenv()
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
RPC_URL = 'https://testnet.dplabs-internal.com'
CHAIN_ID = 688688
CONTRACT_ADDRESS = '0xFaA3792Ee585E9d4D77A4220daF41D83282e8AaF'
EXPLORER = 'https://testnet.pharosscan.xyz/'
VALUE = 0.05
DATA_HEX = "0xcc6212f20000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000019d6080604052348015600e575f5ffd5b506101818061001c5f395ff3fe608060405234801561000f575f5ffd5b5060043610610034575f3560e01c8063a87d942c14610038578063d09de08a14610056575b5f5ffd5b610040610060565b60405161004d91906100d2565b60405180910390f35b61005e610068565b005b5f5f54905090565b60015f5f8282546100799190610118565b925050819055507f420680a649b45cbb7e97b24365d8ed81598dce543f2a2014d48fe328aa47e8bb5f546040516100b091906100d2565b60405180910390a1565b5f819050919050565b6100cc816100ba565b82525050565b5f6020820190506100e55f8301846100c3565b92915050565b7f4e487b71000000000000000000000000000000000000000000000000000000005f52601160045260245ffd5b5f610122826100ba565b915061012d836100ba565b9250828201905080821115610145576101446100eb565b5b9291505056fea2646970667358221220026327c9216a408963c6805a6ceb008c535843e55a2978c64c2393f525ad36d864736f6c634300081e0033000000"

def print_info(message):
    print(f"{Fore.BLUE}{message}{Style.RESET_ALL}")
    sys.stdout.flush()

def print_success(message):
    print(f"{Fore.GREEN}{message}{Style.RESET_ALL}")
    sys.stdout.flush()

def print_error(message):
    print(f"{Fore.RED}{message}{Style.RESET_ALL}")
    sys.stdout.flush()

def get_balance(address):
    balance_wei = w3.eth.get_balance(address)
    return w3.from_wei(balance_wei, 'ether')

def shorten_address(address):
    return f"{address[:6]}...{address[-4:]}"

def shorten_hash(tx_hash):
    return tx_hash[:6], tx_hash[-4:]

def truncate_url(url, max_length=40):
    if len(url) <= max_length:
        return url
    return f"{url[:max_length-3]}..."

def truncate_message(message, max_length=40):
    return message[:max_length] + "..." if len(message) > max_length else message

def format_box(lines, title, emoji):
    width = 60
    top = f"╔{'═' * (width - 2)}╗"
    bottom = f"╚{'═' * (width - 2)}╝"
    title_line = f"║ {emoji} {title.ljust(width - 4)}║"
    content = [f"║ {line.ljust(width - 2)} ║" for line in lines]
    return [top, title_line] + content + [bottom]

print(BANNER)

if not PRIVATE_KEY:
    print_error("💸 Private key not found in .env file")
    sys.exit(1)

w3 = Web3(Web3.HTTPProvider(RPC_URL))
if not w3.is_connected():
    print_error("💸 Failed to connect to Pharos Testnet")
    sys.exit(1)

try:
    CONTRACT_ADDRESS = w3.to_checksum_address(CONTRACT_ADDRESS)
except ValueError:
    print_error("💸 Invalid contract address")
    sys.exit(1)

try:
    if not PRIVATE_KEY.startswith('0x'):
        PRIVATE_KEY = '0x' + PRIVATE_KEY if len(PRIVATE_KEY) == 64 else PRIVATE_KEY
    account = w3.eth.account.from_key(PRIVATE_KEY)
except Exception as e:
    print_error(f"💸 Error: {truncate_message(str(e))}")
    sys.exit(1)

initial_balance = get_balance(account.address)
nonce_latest = w3.eth.get_transaction_count(account.address, 'latest')
nonce_pending = w3.eth.get_transaction_count(account.address, 'pending')
setup_lines = [
    "💰 Network: Connected to Pharos Testnet",
    f"💳 Wallet: {shorten_address(account.address)}",
    f"💳 Initial Balance: {initial_balance:.4f} PHRS",
    f"💰 Nonce (Latest/Pending): {nonce_latest}/{nonce_pending}"
]
for line in format_box(setup_lines, "Trading Vault Setup", "💰"):
    print_info(line)

try:
    deploy_count = int(input("Enter number of deploys: "))
    if deploy_count <= 0:
        raise ValueError
except ValueError:
    print_error("💸 Invalid input. Please enter a positive number")
    sys.exit(1)

success_count = 0

for i in range(deploy_count):
    sub_lines = []
    try:
        nonce_latest = w3.eth.get_transaction_count(account.address, 'latest')
        nonce_pending = w3.eth.get_transaction_count(account.address, 'pending')
        nonce = max(nonce_latest, nonce_pending)
        sub_lines.append(f"➤ Nonce: {nonce}")
        tx = {
            'from': account.address,
            'to': CONTRACT_ADDRESS,
            'data': DATA_HEX,
            'value': w3.to_wei(VALUE, 'ether'),
            'gas': w3.eth.estimate_gas({
                'from': account.address,
                'to': CONTRACT_ADDRESS,
                'data': DATA_HEX,
                'value': w3.to_wei(VALUE, 'ether')
            }),
            'maxPriorityFeePerGas': w3.to_wei(1, 'gwei'),
            'maxFeePerGas': w3.to_wei(1, 'gwei'),
            'nonce': nonce,
            'chainId': CHAIN_ID
        }
        sub_lines.append(f"➤ Gas Estimate: {tx['gas']}")
        sub_lines.append(f"➤ Value Sent: {VALUE:.4f} PHRS")
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_hash_hex = tx_hash.hex()
        sub_lines.append(f"➤ Tx Sent: {truncate_url(f'{EXPLORER}tx/{tx_hash_hex}')}")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        if receipt.status == 0:
            sub_lines.append("💸 Status: Transaction Failed")
            for line in format_box(sub_lines, f"Deploy #{i+1}", "💹"):
                print_error(line)
            time.sleep(5)
            continue
        sub_lines.append("📈 Status: Transaction Successful")
        hash_part1, hash_part2 = shorten_hash(tx_hash_hex)
        sub_lines.append(f"💲 Tx Hash (1/2): {hash_part1}...")
        sub_lines.append(f"💲 Tx Hash (2/2): ...{hash_part2}")
        try:
            gas_fee = w3.from_wei(receipt.effectiveGasPrice * receipt.gasUsed, 'ether')
            sub_lines.append(f"➤ Gas Fee: {gas_fee:.6f} PHRS")
        except (AttributeError, KeyError):
            sub_lines.append("➤ Gas Fee: N/A")
        time.sleep(5)
        new_balance = get_balance(account.address)
        balance_change = new_balance - initial_balance
        sub_lines.append(f"💳 Balance: {new_balance:.4f} PHRS")
        sub_lines.append(f"💸 Change: {balance_change:.4f} PHRS")
        for line in format_box(sub_lines, f"Deploy #{i+1}", "💹"):
            print_success(line)
        initial_balance = new_balance
        success_count += 1
        time.sleep(5)
    except Exception as e:
        sub_lines.append(f"💸 Error: {truncate_message(str(e))}")
        for line in format_box(sub_lines, f"Deploy #{i+1}", "💹"):
            print_error(line)
        time.sleep(5)

final_lines = [
    f"📈 {'All Deploys Completed' if success_count == deploy_count else f'{success_count}/{deploy_count} Deploys Succeeded'}",
    f"💳 Final Balance: {initial_balance:.4f} PHRS"
]
for line in format_box(final_lines, "Trading Session Closed", "📈"):
    print_success(line)
