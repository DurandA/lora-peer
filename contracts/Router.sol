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
    mapping (uint64 => address) public appEuis;
    uint nonce = 1337;

    function registerAppEui() returns (uint64) {
        nonce++;
        uint64 appEui = uint64(sha3(nonce));
        appEuis[appEui] = msg.sender;
        AppEuiRegistered(msg.sender, appEui);
        return appEui;
    }

    event AppEuiRegistered(address indexed registrant, uint64 indexed appEui);
}
