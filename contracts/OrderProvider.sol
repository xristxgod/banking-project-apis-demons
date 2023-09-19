// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IERC20} from "./libs/IERC20.sol";
import {Ownable} from "./libs/Ownable.sol";

contract OrderProvider is Ownable {
    event Transfer(uint256 orderId, uint256 amount, address _address);
    event TransferToken(uint256 orderId, address token, uint256 amount, address _address);

    address public centralWallet;
    mapping (uint256 => address) public tokens;

    constructor(address _centralWallet) {
        centralWallet = _centralWallet;
    }

    receive() external payable {
        payable(centralWallet).transfer(msg.value);
    }

    fallback() external payable {}

    function setupToken(uint256 id, address _address) external onlyOwner returns (bool) {
        tokens[id] = _address;
        return true;
    }

    function emergencyWithdraw(address tokenAddress, address wallet) external onlyOwner returns (bool) {
        IERC20 token = IERC20(tokenAddress);
        uint256 amount = token.balanceOf(address(this));

        token.transfer(wallet, amount);
        return true;
    }

    function setupCentralWallet(address _newCentralWallet) external onlyOwner returns (bool) {
        require(_newCentralWallet != address(0));
        centralWallet = _newCentralWallet;
        return true;
    }

    function transfer(uint256 orderId, uint256 amount) external payable returns (bool) {
        uint256 amountInTrx = msg.value;
        require(amountInTrx == amount, 'Error amount');
        payable(centralWallet).transfer(amountInTrx);
        emit Transfer(orderId, amountInTrx, msg.sender);
        return true;
    }

    function transferToken(uint256 orderId, uint256 amount, uint256 tokenId) external returns (bool) {
        require(tokens[tokenId] != address(0), 'Error token id');
        IERC20 token = IERC20(tokens[tokenId]);

        require(token.allowance(msg.sender, address(this)) >= amount, 'Error allowed amount');

        token.transferFrom(msg.sender, centralWallet, amount);
        emit TransferToken(orderId, tokens[tokenId], amount, msg.sender);
        return true;
    }
}
