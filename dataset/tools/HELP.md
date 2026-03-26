# Steps to minimally compile Web3Bugs repos

This is designed for cases in which the ablation study can't run properly due to missing dependencies or failed compilations.

0. Go into a conda environment with node v20.

1. Create a temp config file at the repo root (e.g. hh.temp.config.js):

```
touch hh.temp.config.js && vi hh.temp.config.js
```

Add this:

```
/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    compilers: [
      { version: "0.8.6", settings: { optimizer: { enabled: true, runs: 1000 }, metadata: { bytecodeHash: "none" } } },
      { version: "0.7.6", settings: { optimizer: { enabled: true, runs: 800  }, metadata: { bytecodeHash: "none" } } }
    ],
    // root-level outputSelection so solc emits storage layouts into build-info
    outputSelection: {
      "*": { "*": ["abi","evm.bytecode","evm.deployedBytecode","storageLayout"] },
      "": ["ast"]
    }
  },
  paths: {
    sources: "contracts",
    artifacts: "artifacts",
    cache: "cache",
    tests: "test"
  },
  mocha: { timeout: 1_000_000 }
};
```

2. Pin hardhat v2 with ```npm i -D hardhat@2```. If that fails, 99% of the time, ```npm i -D hardhat@2 --legacy-peer-deps``` solves it.

3. Clean and compile with the temp config.

```
rm -rf artifacts cache
npx hardhat clean   --config hh.temp.config.js
npx hardhat compile --config hh.temp.config.js --force
```

4. Manual dependency installation required if compilation fails.