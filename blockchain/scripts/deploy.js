const hre = require("hardhat");
const fs  = require("fs");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying with account:", deployer.address);

  const Factory = await hre.ethers.getContractFactory("DeepfakeVerifier");
  const contract = await Factory.deploy();
  await contract.waitForDeployment();

  const address = await contract.getAddress();
  console.log("DeepfakeVerifier deployed to:", address);

  const artifact = await hre.artifacts.readArtifact("DeepfakeVerifier");
  fs.writeFileSync("DeepfakeVerifier_abi.json", JSON.stringify(artifact.abi, null, 2));
  fs.writeFileSync("DeepfakeVerifier_address.txt", address);
  console.log("Saved ABI and address.");
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});