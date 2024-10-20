from django.shortcuts import render, redirect
from django.contrib import messages
from .models import FaucetRequest
from django.utils import timezone
import random, string
from web3 import Web3

# Generate a simple CAPTCHA
def generate_captcha():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Homepage view
def homepage(request):
    captcha_text = generate_captcha()
    request.session['captcha'] = captcha_text
    return render(request, 'home.html', {'captcha': captcha_text})

# View to handle the faucet form submission
def submit_faucet(request):
    if request.method == 'POST':
        wallet_address = request.POST.get('walletAddress')
        captcha_input = request.POST.get('captcha')
        ip_address = request.META.get('REMOTE_ADDR')

        # CAPTCHA validation
        captcha_text = request.session.get('captcha', '')
        if captcha_input != captcha_text:
            messages.error(request, 'Invalid CAPTCHA. Please try again.')
            return redirect('/')

        # Check for recent faucet request
        if FaucetRequest.has_recent_request(wallet_address, ip_address):
            messages.error(request, 'You have already claimed tokens today!')
            return redirect('/')

        # Save the request in the database
        FaucetRequest.objects.create(wallet_address=wallet_address, ip_address=ip_address)

        # Process the token transfer
        try:
            transfer_eth(wallet_address)
            messages.success(request, 'Tokens have been successfully transferred!')
        except Exception as e:
            messages.error(request, f'Error processing transaction: {str(e)}')

        return redirect('/')

    return redirect('/')

# Transfer Ethereum function
def transfer_eth(to_address):
    try:
        # Ethereum connection and transaction logic
        rpc_url = "http://82.180.144.37:8545"
        private_key = "0xc87509a1c067bbde78beb793e6fa76530b6382a4c0241e5e4a9ec0a0f44dc0d3"
        w3 = Web3(Web3.HTTPProvider(rpc_url))

        account = w3.eth.account.from_key(private_key)
        transaction = {
            'to': to_address,
            'value': w3.to_wei(1, 'ether'),
            'gas': 2000000,
            'gasPrice': w3.to_wei('50', 'gwei'),
            'chainId': 147,
            'nonce': w3.eth.get_transaction_count(account.address),
        }

        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
        txn_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
        return txn_receipt
    except Exception as e:
        raise Exception(f"Transaction failed: {str(e)}")
