// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ProductRegistry {
    struct Product {
        string qrCode;
        bool isReal;
    }

    mapping(string => Product) private products;
    address public owner;

    event ProductRegistered(string qrCode, bool isReal);

    constructor() {
        owner = msg.sender;
    }

    function registerProduct(string memory _qrCode, bool _isReal) public {
        require(msg.sender == owner, "Only owner can register products");
        products[_qrCode] = Product(_qrCode, _isReal);
        emit ProductRegistered(_qrCode, _isReal);
    }

    function verifyProduct(string memory _qrCode) public view returns (bool) {
        return products[_qrCode].isReal;
    }
}