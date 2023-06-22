const { expect } = require("chai")
const { ethers } = require("hardhat")

describe('OrderProvider', function() {
  let account1;
  let account2;
  let orderProvider;

  beforeEach(async function() {
    [account1, account2] = await ethers.getSigners();
    const OrderProvider = await ethers.getContractFactory('OrderProvider', account1);
    orderProvider = await OrderProvider.deploy()
    await orderProvider.deployed()
  })

  it('Owner should be a sender', async function() {
    const owner = await orderProvider.owner();
  })
})