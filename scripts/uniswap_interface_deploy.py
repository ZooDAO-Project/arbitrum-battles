from brownie import *

def main():
	active_network = network.show_active()
	account = accounts.load(active_network) # brownie account for deploy.

	UniswapInterfaceMulticall.deploy({"from": account}, publish_source=True) # dai address/mock 