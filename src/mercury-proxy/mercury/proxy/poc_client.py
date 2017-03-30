from mercury.common.inventory_client import InventoryClient

client = InventoryClient('tcp://0.0.0.0:9006')

r = client.query({})

print(r)
