from coinbase.wallet.client import Client

client = Client("C8mapM8SHbJygZlb", "4oRfOCefh9eQkcXc6ZLloxeaddDZ2cm9", api_version="2018-10-18")
primary_account = client.get_primary_account()

tx = primary_account.get_transaction("68e04b2f-9cf4-5c86-912a-766984b1d199")

print(tx)
