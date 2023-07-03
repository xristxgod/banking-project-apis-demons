// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "./CentralWallet.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract OrderProvider {
    // CentralWallet.sol
    address payable public centralWalletAddress;
    CentralWallet private centralWallet;

    event AcceptNative(uint orderId, uint amount, address sender);
    event AcceptStableCoin(uint orderId, uint amount, address stableCoinAddress, address sender);

    modifier onlyOwner() {
        require(centralWallet.isOwner(msg.sender), "not owner");
        _;
    }

    constructor (address _centralWallet) {
        centralWalletAddress = payable(_centralWallet);
        centralWallet = CentralWallet(_centralWallet);
    }

    receive() external payable {
        centralWalletAddress.transfer(msg.value);
    }

    fallback() external payable {}

    // Owner functions

    function setNewCentralWallet(address _newCentralWallet) external onlyOwner {
        require(_newCentralWallet != address(0), 'invalid address');
        centralWallet = CentralWallet(_newCentralWallet);
    }

    function withdrawStableCoin(address _stableCoinAddress) external onlyOwner {
        require(_stableCoinAddress != address(0), 'invalid address');

        IERC20 stableCoin = IERC20(_stableCoinAddress);

        uint _value = stableCoin.balanceOf(address(this));
        uint _balance = stableCoin.balanceOf(centralWalletAddress);

        stableCoin.transfer(address(centralWallet), _value);
        centralWallet.depositStableCoin(address(this), _stableCoinAddress, _value, _balance + _value);
    }
    
    // Functionals

    function acceptNative(uint orderId, uint _value) external payable {
        require(msg.value == _value, 'invalid amount');

        centralWalletAddress.transfer(_value);

        emit AcceptNative(orderId, _value, msg.sender);
    }

    function acceptStableCoin(uint orderId, uint _value, address _stableCoinAddress) external {
        IERC20 stableCoin = IERC20(_stableCoinAddress);

        require(stableCoin.balanceOf(msg.sender) >= _value, 'not enough balance');
        require(stableCoin.allownace(msg.sender, centralWalletAddress), 'not approved');

        stableCoin.transferFrom(msg.sender, centralWalletAddress, _value);

        emit AcceptStableCoin(orderId, _value, _stableCoinAddress, msg.sender);

        uint _balance = stableCoin.balanceOf(centralWalletAddress);
        centralWallet.depositStableCoin(msg.sender, _stableCoinAddress, _value, _balance + _value);
    }

}
