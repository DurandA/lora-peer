pragma solidity ^0.4.15;

contract addressable {
    mapping (address => uint32) public ipv4Addrs;
    mapping (address => uint128) public ipv6Addrs;

    function setIpv4(uint32 addr) {
        ipv4Addrs[msg.sender] = addr;
    }

    function setIpv6(uint128 addr) {
        ipv6Addrs[msg.sender] = addr;
    }

    function deleteIpv4() {
        delete ipv4Addrs[msg.sender];
    }

    function deleteIpv6() {
        delete ipv6Addrs[msg.sender];
    }
}

contract LoraRouter is addressable {
    mapping (uint64 => address) public joinEuis;
    uint nonce = 1337;

    function registerJoinEui() returns (uint64) {
        uint lastBlockHash = uint(block.blockhash(block.number - 1));
        uint64 joinEui = uint64(sha3(lastBlockHash, nonce));
        nonce = joinEui;
        joinEuis[joinEui] = msg.sender;
        JoinEuiRegistered(msg.sender, joinEui);
        return joinEui;
    }

    event JoinEuiRegistered(address indexed registrant, uint64 indexed joinEui);
}
