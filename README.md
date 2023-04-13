# VehShare




### File Structure

```
VehShare/
├── README.md                                   //  Introduction
├── BSPEFB                                      //  BaseLine1
│   ├── BSPEFB.py
│   └── BSPEFB.sol
├── dataset
│   ├── dataset_1K
│   ├── dataset_2K
│   ├── dataset_3K
│   ├── dataset_4K
│   └── dataset_5K
└── OurScheme                                   //  OurScheme
    ├── vehshare.py
    └── vehshare.sol                                 
```



### Baseline

BSPEFB： Chen, Biwen, et al. "A blockchain-based searchable public-key encryption with forward and backward privacy for cloud-assisted vehicular social networks." *IEEE Transactions on Vehicular Technology* 69.6 (2019): 5813-5825.



### Prepare Environment

#### a. Hardware environment

 Intel(R) Core(TM) i7-10700 CPU@2.60GHz  ，16GB RAM

Ubuntu 18.04 Server

#### b. Software environment

Python 3.6, Solidity 0.4.22, Dev - Ganache Provider ，Docker version 20.10.7  build 20.10.7-0ubuntu5~18.04.3

Package ： 

​	Connect with solidity ：web3	5.31.3, 

​	Cryptographic functions ：cryptography	2.1.4

​	Computations on groups supporting bilinear pairings ： bplib	0.0.6

​	Support multiple-precision arithmetic ： gmpy2	2.1.5



### Building Procedure 1

```shell
# Procedure for vehshare

# In Remix
# Deploy the smart contract vehshare.sol
# Paste Abi and Address in vehshare.py

# Start testRPC on Linux using docker
$ docker run --detach --publish 8545:8545 trufflesuite/ganache-cli:latest
$ docker ps -a #查看是否成功
# Deploy smart contract on testRPC
$ cd OurScheme 
$ python3.6 vehshare.py

# BSPEFB same as vehshare
```


### Building Procedure 2
```shell
# Procedure for vehshare2
# Start up a blockchain
ganache-cli -g 1 -l 9007199254740991 --db ./RDBlockchain -s 1234 -a 2
# Compile contracts
# open a new terminal tab 
truffle compile
# Run apps
cd app
# make sure ganache-cli has showen "Listening on 127.0.0.1:8545"
python3.6 vehshare.py

```
