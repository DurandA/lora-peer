var router = artifacts.require("./LoraRouter");

module.exports = function(deployer) {
  deployer.deploy(router);
};
