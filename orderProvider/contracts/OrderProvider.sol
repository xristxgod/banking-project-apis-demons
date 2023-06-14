// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";


contract OrderProvider is Ownable {
    event TransferNative(uint16 orderId, uint amount, address _address);
    event TransferStableCoin(uint16 orderId, address tokenAddress, uint amount, address _address);

    address public centralWallet;
    mapping (uint8 => address) public stableCoins;

    constructor () {
        centralWallet = msg.sender;
    }

    receive () external payable {
        payable(centralWallet).transfer(msg.value);
    }

    fallback() external payable {}

    function setupStableCoin(uint8 id, address _address) external onlyOwner {
        stableCoins[id] = _address;
    }

    function emergencyTokenWithdraw(uint8 stableCoinId) external onlyOwner {
        require(stableCoins[stableCoinId] != address(0), 'Error stable coin id');
        IERC20 stableCoin = IERC20(stableCoins[stableCoinId]);

        uint amount = stableCoin.balanceOf(address(this));

        stableCoin.transfer(centralWallet, amount);
    }

    function updateCentralWallet(address _address) external onlyOwner {
        require(_address != address(0), 'Invalid address');
        centralWallet = _address;
    }

    function transferNative(uint16 orderId) external payable {
        payable(centralWallet).transfer(msg.value);
        emit TransferNative(orderId, msg.value, msg.sender);
    }

    function transferStableCoin(uint8 stableCoinId, uint16 orderId, uint amount) external {
        require(stableCoins[stableCoinId] != address(0), 'Error stable coin id');
        IERC20 stableCoin = IERC20(stableCoins[stableCoinId]);

        require(stableCoin.allowance(msg.sender, address(this)) >= amount, 'Error allowance');
        
        stableCoin.transferFrom(msg.sender, centralWallet, amount);
        emit TransferStableCoin(orderId, stableCoins[stableCoinId], amount, msg.sender);
    }

}