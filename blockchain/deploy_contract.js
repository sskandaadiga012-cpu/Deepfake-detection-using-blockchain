const Web3 = require("web3");
const fs   = require("fs");
const solc = require("solc");

async function main() {
  const web3 = new Web3("http://127.0.0.1:8545");

  const isConnected = await web3.eth.net.isListening().catch(() => false);
  if (!isConnected) {
    console.error("ERROR: Cannot connect to Geth at http://127.0.0.1:8545");
    process.exit(1);
  }

  const accounts = await web3.eth.getAccounts();
  const deployer = accounts[0];
  const blockNumber = await web3.eth.getBlockNumber();
  const block = await web3.eth.getBlock("latest");

  console.log("Connected to Geth node");
  console.log("Using account :", deployer);
  console.log("Block number  :", blockNumber);
  console.log("Block gasLimit:", block.gasLimit);

  const source = fs.readFileSync("DeepfakeVerifier.sol", "utf8");
  console.log(`Read DeepfakeVerifier.sol (${source.length} chars)`);

  const input = {
    language: "Solidity",
    sources: { "DeepfakeVerifier.sol": { content: source } },
    settings: {
      optimizer: { enabled: true, runs: 200 },
      outputSelection: { "*": { "*": ["abi", "evm.bytecode"] } }
    }
  };

  console.log("Compiling contract...");
  const output = JSON.parse(solc.compile(JSON.stringify(input)));

  if (output.errors) {
    const errors = output.errors.filter(e => e.severity === "error");
    if (errors.length > 0) {
      errors.forEach(e => console.error(e.formattedMessage));
      process.exit(1);
    }
  }

  const contractOutput = output.contracts["DeepfakeVerifier.sol"]["DeepfakeVerifier"];
  const abi      = contractOutput.abi;
  const bytecode = contractOutput.evm.bytecode.object;

  console.log("Compilation successful!");
  console.log("Bytecode size:", bytecode.length / 2, "bytes");

  const gasLimit = Math.floor(block.gasLimit * 0.9);
  console.log("Using gas    :", gasLimit);
  console.log("");
  console.log("Deploying contract...");

  const instance = await new web3.eth.Contract(abi)
    .deploy({ data: "0x" + bytecode })
    .send({ from: deployer, gas: gasLimit, gasPrice: "1000000000" });

  const contractAddress = instance.options.address;

  console.log("");
  console.log("============================================");
  console.log("  Contract deployed successfully!");
  console.log("============================================");
  console.log("  Address  :", contractAddress);
  console.log("  Block    :", await web3.eth.getBlockNumber());
  console.log("============================================");
  console.log("");
  console.log("Next step:");
  console.log('  Open blockchain.py and set:');
  console.log(`  contract_address = "${contractAddress}"`);

  fs.writeFileSync("DeepfakeVerifier_abi.json",    JSON.stringify(abi, null, 2));
  fs.writeFileSync("DeepfakeVerifier_address.txt", contractAddress);
  console.log("");
  console.log("Saved: DeepfakeVerifier_abi.json");
  console.log("Saved: DeepfakeVerifier_address.txt");
}

main().catch(err => {
  console.error("Deployment failed:", err.message);
  process.exit(1);
});