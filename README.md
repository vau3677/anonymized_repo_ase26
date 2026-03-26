# mv-scan-research-artifacts

This repository contains the source code for the **MV-Scan** tool, the analysis rules used in the experiment, the dataset of target repositories, and the Python scripts used to orchestrate and evaluate the white-box controlled experiment.

## Repository Structure

```
mv-scan-research-artifacts/
├── dataset/             # Python script to run the ablation study
│   └── Web3Bugs/        # Dataset we run MV-Scan on
├── evaluation/          # Scripts to evaluate results with accompanying results
├── MV-Bench.xlsx        # Our full annotated benchmark with all alarms and audit notes
└── slither-si-detector/ # Source code for the MV-Scan tool is in /slither/detectors/inconsistent_state
```

## MV-Scan Tool

Our custom analysis tool uses Slither/SlitherIR to interface with smart contract code.

Slither is a Solidity & Vyper static analysis framework written in Python3. It runs a suite of vulnerability detectors, prints visual information about contract details, and provides an API to write custom analyses.

### Building & Running

From source (Slither, Hardhat v2):

```bash
git clone <this repo>
cd <this repo>/slither-si-detector
pip install -e .
npx hardhat clean && npx hardhat compile
ISD_JSON_OUT=out.json slither smart-contract/repo --detect inconsistent_state --hardhat-ignore-compile
```

Using Docker (recommended for experiment automation):

```
cd <contract_example>
```

<!-- ### Example: Hardhat v2

```
vi hardhat.config.js
```

Within hardhat.config.js, we need to allow a few things to be tracked in our output. This is because JSON artifacts include a storageLayout section detailing each state variable’s slot and offset, but it must be manually set in older versions of Slither. If you update Slither to its latest version, you may not need to do this step, but it is encouraged to use 0.9.2 (our research snapshot).

```json
module.exports = {
  solidity: {
    version: "0.8.x",
    settings: {
      outputSelection: {
        "*": { "*": ["storageLayout"] }
      }
    }
  }
};
``` -->