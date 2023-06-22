// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract OrderProvider is Ownable {
    event TransferToken(uint orderId, address tokenAddress, uint amount, address user);
    event TransferNative(uint orderId, uint amount, address user);
    
    address public _owner;
    mapping (uint8 => address) public tokens;

    constructor(address owner) {
        _owner = owner != address(0) ? owner : msg.sender; 
    }

    receive() external payable {
        payable(_owner).transfer(msg.value);
    }

    fallback() external payable {}

    function setupToken(uint8 id, address _address) external onlyOwner {
        tokens[id] = _address;
    }

    function updateOwner(address _address) external onlyOwner {
        require(_owner != address(0));
        _owner = _address;
    }

    function withdrawTokens(address _contractAddress, address _toAddress) external onlyOwner {
        IERC20 token = IERC20(_contractAddress);
        token.transfer(_toAddress, token.balanceOf(address(this)));
    }

    function transferNative(uint orderId, uint amount) external payable {
        uint amountInTx = msg.value;
        require(amountInTx == amount, 'Error amount');
        payable(_owner).transfer(amountInTx);
        emit TransferNative(orderId, amount, msg.sender);
    }

    function transferNative(uint orderId, uint amount, uint8 tokenId) external {
        require(tokens[tokenId] != address(0), 'Error token id');
        IERC20 token = IERC20(tokens[tokenId]);

        require(token.allowance(msg.sender, _owner) <= amount, 'Error allowance');
        
        token.transferFrom(msg.sender, _owner, amount);
        emit TransferToken(orderId, tokens[tokenId], amount, msg.sender);
    }

}
