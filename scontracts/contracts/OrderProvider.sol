// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract OrderProvider {
    // CentralWallet.sol
    address public owner;
    address payable public centralWallet;

    event AcceptNative(uint orderId, uint amount, address sender);
    event AcceptStableCoin(uint orderId, uint amount, address stableCoinAddress, address sender);

    modifier onlyOwner() {
        require(msg.sender == owner, "not owner!");
        _;
    }

    constructor (address _centralWallet, address _owner) {
        owner = _owner == address(0) ? msg.sender : _owner;
        centralWallet = payable(_centralWallet);
    }

    receive() external payable {
        payable(centralWallet).transfer(msg.value);
    }

    fallback() external payable {}

    // Owner functions

    function setNewOwner(address _newOwner) external onlyOwner {
        require(_newOwner != address(0), 'invalid address');
        owner = _newOwner;
    }

    function setNewCentralWallet(address _newCentralWallet) external onlyOwner {
        require(_newCentralWallet != address(0), 'invalid address');
        centralWallet = payable(_newCentralWallet);
    }

    function withdrawStableCoin(address _toAddress, address _stableCoinAddress) external onlyOwner {
        address toAddress = _toAddress == address(0) ? centralWallet : _stableCoinAddress;
        require(_stableCoinAddress != address(0), 'invalid address');

        IERC20 stableCoin = IERC20(_stableCoinAddress);

        stableCoin.transfer(toAddress, stableCoin.balanceOf(address(this)));
    }
    
    // Functionals

    function acceptNative(uint orderId, uint _value) external payable {
        require(msg.value == _value, 'invalid amount');

        centralWallet.transfer(_value);

        emit AcceptNative(orderId, _value, msg.sender);
    }

    function acceptStableCoin(uint orderId, uint _value, address _stableCoinAddress) external {
        IERC20 stableCoin = IERC20(_stableCoinAddress);

        require(stableCoin.balanceOf(msg.sender) >= _value, 'not enough balance');
        require(stableCoin.allownace(msg.sender, centralWallet), 'not approved');

        stableCoin.transferFrom(msg.sender, centralWallet, _value);

        emit AcceptStableCoin(orderId, _value, _stableCoinAddress, msg.sender);
    }

}
