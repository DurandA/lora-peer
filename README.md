# lora-peer

This project enables LoRaWAN network server resolving using an Ethereum smart contract. It is compatible with the [packet forwarder project](https://github.com/Lora-net/packet_forwarder).

## Setup

This project requires Python >= 3.5.3.

Install required packages:

```
sudo pip3 install -r requirements.txt
```

## Usage

```
usage: run_server.py [-h] [--json-rpc URI] contract

positional arguments:
  contract        contract address

optional arguments:
  -h, --help      show this help message and exit
  --json-rpc URI  host on ethereum node (default: http://localhost:8545)
```

## Registering a JoinEUI
See [Wiki](https://github.com/DurandA/lora-peer/wiki).
