require("@nomicfoundation/hardhat-toolbox");

module.exports = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: { enabled: true, runs: 200 },
      evmVersion: "berlin"
    }
  },
  networks: {
    geth: {
      url: "http://127.0.0.1:8545",
      chainId: 2025,
      accounts: ["0x6ac342416ad3f00dfb7844312cd006ec4130d5fe3bf1366aa18cabb770d40834"],
      gas: 3000000,
      gasPrice: 1000000000
    }
  }
};