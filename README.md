# Warren

Trading order book for Uniswap v3.

## Dependencies

* [python3](https://www.python.org/downloads/release/python-3105/) version 3.10.5.
* This app was tested on MacOS and Linux only. Probably, it won’t work on Windows if you will not provide configuration directory manually. 

## Supported swaps

* [ETH](https://coinmarketcap.com/currencies/ethereum/) to [DAI](https://coinmarketcap.com/currencies/multi-collateral-dai/) (Ethereum Mainnet)
* [DAI](https://coinmarketcap.com/currencies/multi-collateral-dai/) to [ETH](https://coinmarketcap.com/currencies/ethereum/) (Ethereum Mainnet)
* [ETH](https://coinmarketcap.com/currencies/ethereum/) to [WBTC](https://coinmarketcap.com/currencies/wrapped-bitcoin/) (Ethereum Mainnet)
* [WBTC](https://coinmarketcap.com/currencies/wrapped-bitcoin/) to [ETH](https://coinmarketcap.com/currencies/ethereum/) (Ethereum Mainnet)
* [ETH](https://coinmarketcap.com/currencies/ethereum/) to [USDC](https://coinmarketcap.com/currencies/usd-coin/) (Ethereum Mainnet)
* [USDC](https://coinmarketcap.com/currencies/usd-coin/) to [ETH](https://coinmarketcap.com/currencies/ethereum/) (Ethereum Mainnet)
* More to be added.


## Supported DEX’s

* [Uniswap v2](https://uniswap.org/) (Ethereum Mainnet)
* [Uniswap v3](https://uniswap.org/) (Ethereum Mainnet)
* [Sushi](https://www.sushi.com/) (Ethereum Mainnet)
* [PancakeSwap](https://pancakeswap.finance/?chain=eth) (Ethereum Mainnet)


## Commands

To display all available commands run:

```
python -m warren --help
```

## Quickstart

Warren can be installed (preferably in a virtualenv) using `make` as follows:

```bash
make install
python -m warren setup
```

> If you run into problems during installation, you might have a broken environment. Try setting up a clean environment.

You will be asked to provide an Ethereum API. If you don’t have your own node you can use one of those many providers:

* https://www.infura.io/
* https://moralis.io/
* https://www.quicknode.com/

Once you provide all necessary information application will create a new wallet which will be used to execute transactions in your favor (real tokens will be involved).

```
Your wallet credentials has been saved in <HOME_DIR>/.warren-the-cryptobot

Your wallet address is 0x0000000000000000000000000000000000000000
```

You will need to transfer tokens into this wallet to perform transactions. 

### Important

You should backup wallet credentials created by Warren. If you lose it you will lose access to your tokens. You can find wallet credentials and all configuration files in `.warren-the-cryptobot` path in your home directory (unless other path given during setup).


Once the application is setup, and you transfered Ether into your wallet you will need to wrap Ether into Wrapped Ether. Otherwise Warren will not be able to perform transactions.

```bash
python -m warren wrap-ether
````

> Remember to leave some Ether "unwrapped". Otherwise Warren won’t be able to pay transaction fees and your swaps will fail. 

Now you can create your first order.

```
python -m warren create-order
```

Example:
```
0) Stop Loss
1) Take Profit
Choose order type [0/1]: 0
0) WETH9/DAI
Choose token pair [0]: 0
Trigger price (DAI): 1400
Percent of tokens to flip (excluding gas fees) (100):
The new order has been created.
```

Now you can start up the application.

```
python -m warren start
```

Have in mind this application needs to be always running. If it is down it won’t execute orders. You should consider running in on virtual machine or cloud.

## Need help?

Feel free to start a discussion or file an issue. You can also ping me on [Twitter](https://twitter.com/msokola). 