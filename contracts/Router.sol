pragma solidity 0.4.25;

contract addressable {
    mapping (address => uint32) public ipv4Addrs;
    mapping (address => uint128) public ipv6Addrs;

    function setIpv4(uint32 addr) public {
        ipv4Addrs[msg.sender] = addr;
    }

    function setIpv6(uint128 addr) public {
        ipv6Addrs[msg.sender] = addr;
    }

    function deleteIpv4() public {
        delete ipv4Addrs[msg.sender];
    }

    function deleteIpv6() public {
        delete ipv6Addrs[msg.sender];
    }
}

contract LoraRouter is addressable {
    mapping (uint64 => address) public joinEuis;
    uint nonce = 1337;

    function registerJoinEui() public returns (uint64) {
        uint lastBlockHash = uint(blockhash(block.number - 1));
        uint64 joinEui = uint64(keccak256(
            abi.encodePacked(lastBlockHash, nonce)
        ));
        require(joinEuis[joinEui] == 0, "JoinEUI already registered");
        nonce = joinEui;
        joinEuis[joinEui] = msg.sender;
        emit JoinEuiRegistered(msg.sender, joinEui);
        return joinEui;
    }

    event JoinEuiRegistered(address indexed registrant, uint64 indexed joinEui);
}
