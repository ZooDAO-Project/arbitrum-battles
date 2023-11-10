from brownie import *
import time
from web3 import Web3

def main(ve_zoo):

	active_network = network.show_active()
	account = accounts.load(active_network)

	fp = 'scripts/collections.txt'

	collectionIds = []

	with open(fp, 'r') as f:
		for line in f:
			cf= ','.join(part.strip() for part in line.split(','))
			collectionIds.append(cf)

	addressNumber = len(collectionIds)

	index = addressNumber//25
	remained = addressNumber%25

	treasury = ['0x1ada350F59ff5cFd1b0ABA004F63a0892FA93858']

	for x in range(index):
	
		addressesToBatch = collectionIds[x*25:(x+1)*25]
		
		checksumAddresses = list(map(lambda x: Web3.toChecksumAddress(x) , addressesToBatch))

		royalteRecipients = [ item for item in treasury for _ in range(len(checksumAddresses)) ]

		ve_zoo.batchAllowNewContract(checksumAddresses, royalteRecipients, {"from": account})
		print(f"Allow collection, Ids: {checksumAddresses}")
		time.sleep(2)
	
	if remained != 0:
	
		addressesToBatch = collectionIds[len(collectionIds)-remained:]

		checksumAddresses = list(map(lambda x: Web3.toChecksumAddress(x) , addressesToBatch))

		royalteRecipients = [ item for item in treasury for _ in range(len(checksumAddresses)) ]

		ve_zoo.batchAllowNewContract(checksumAddresses, royalteRecipients, {"from": account})
		print(f"Allow collection, Ids: {checksumAddresses}")
		time.sleep(2)