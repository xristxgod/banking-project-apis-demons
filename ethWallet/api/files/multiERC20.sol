pragma solidity >=0.7.0 <0.9.0;


import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v4.0.0/contracts/token/ERC20/ERC20.sol";


contract MultiERC20 {
    function sum(uint256[] memory amounts) private pure returns (uint256 retVal) {
        uint256 totalAmnt = 0;
        for (uint i=0; i < amounts.length; i++) {
            totalAmnt += amounts[i];
        }
        return totalAmnt;
    }

    function multisend(
        address _tokenAddr,
        address[] memory dests,
        uint256[] memory values
    ) payable public {
        require(dests.length == values.length, "The length of two array should be the same");
        ERC20 token = ERC20(_tokenAddr);

        uint256 totalAmnt = sum(values);
        require(token.balanceOf(msg.sender) >= totalAmnt, "Not enought token on balance");

        // Transact ERC20
        for (uint i=0; i < dests.length; i++) {
           token.transferFrom(msg.sender, dests[i], values[i]);
        }
    }
}
