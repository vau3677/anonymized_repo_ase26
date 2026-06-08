# Web3Bugs / Code4rena MV-Bench strict B0 audit

This file is the manual strict B0 matching audit for `oracle/web3bugs_mvbench_review_queue.csv` and the semantic-label evidence consolidated in `oracle/audits/web3bugs_semantic_label_audit.md` for IDs `59`, `104`, `60`, `72`, `123`, and `41`. Semantic labels remain sourced from Web3Bugs / Code4rena evidence; MV-Bench is used only for detector-bucket matching.

Strict B0 match rule: same evaluated repo, same or direct-specialization invariant, at least one oracle state entity or external proxy in the B0 entangled group, at least one writer/reader/transaction step from the known bug trace, and same sink class.

## Summary

| Source pool | MV-SI denominator rows | Strict B0 matches | Strict B0 false negatives | Strict recall | Notes |
| --- | ---: | ---: | ---: | ---: | --- |
| TOSEM overlap | 9 | 1 | 8 | 1/9 = 0.111 | Included here for the combined denominator; detailed TOSEM audit is in `audits/tosem_oracle_review_queue.csv` and `audits/TOSEM_manual_audit.md`. |
| Web3Bugs/Code4rena complement | 22 | 5 | 17 | 5/22 = 0.227 | Non-MV-SI rows were marked `NA-not-MVSI` and excluded from the MV-SI recall denominator. |
| Combined independent oracle | 31 | 6 | 25 | 6/31 = 0.194 | Paper-facing strict known-MVSI recall denominator. |

## Web3Bugs ID 59 / `2021-11-malt`

- MV-Bench sheet: `59src`
- MV-SI denominator rows: 8
- Strict B0 matches: 0
- Strict B0 FNs: 8

### H-05 AuctionEschapeHatch.sol#exitEarly updates state of the auction wrongly
- Label: `MV-SI` / `Type-II-asset-utility`
- Strict B0 match: `no`
- Matched bucket: `NA-no-strict-B0-match`
- FN reason: `FN7-bucket-adjacent-not-strict`
- Notes: B0 row 4 is adjacent and marked FP; it does not represent the exitEarly auction-state desynchronization.
- Candidate MV-Bench rows:
  - sheet=59src | row=4 | abl=B0 | type=FP | finding=[single_var_cross_tx] idToAuction  tx-set -> claimArbitrage(uint256), purchaseArbitrageTokens(uint256)   • write  contracts/Auction.sol:843  (Auction.('allocateArbRewards', ['uint256'], ['uint256']))   • write  contracts/Auction.sol:197  (Auction.('purchaseArbitrageTokens', ['uint256'], []))   • read  contracts/Auction.sol:640  (Auction.('_finalizeAuction', ['uint256'], []))   • read  contracts/Auction.sol:859  (Auction.('allocateArbRewards', ['uint256'], ['uint256'])) | report= | comments=Adjacent to [H-05], but not distinct or zero-day in and of itself. If this was a multi-var report with a few additional specs, this could be a new bug
  - sheet=59src | row=80 | abl=B1 | type=FP | finding=[single_var_cross_tx] idToAuction  tx-set -> claimArbitrage(uint256), purchaseArbitrageTokens(uint256)   • write  contracts/Auction.sol:198  (Auction.('purchaseArbitrageTokens', ['uint256'], []))   • read  contracts/Auction.sol:221  (Auction.('claimArbitrage', ['uint256'], [])) | report= | comments=Adjacent to [H-05], but not distinct or zero-day in and of itself. If this was a multi-var report with a few additional specs, this could be a new bug
  - sheet=59src | row=172 | abl=B2 | type=FP | finding=[single_var_cross_tx] idToAuction  tx-set -> claimArbitrage(uint256), purchaseArbitrageTokens(uint256)   • write  contracts/Auction.sol:197  (Auction.('purchaseArbitrageTokens', ['uint256'], []))   • read  contracts/Auction.sol:221  (Auction.('claimArbitrage', ['uint256'], [])) | report= | comments=Adjacent to [H-05], but not distinct or zero-day in and of itself. If this was a multi-var report with a few additional specs, this could be a new bug
  - sheet=59src | row=226 | abl=B3 | type=FP | finding=[single_var_cross_tx] idToAuction  tx-set -> claimArbitrage(uint256), purchaseArbitrageTokens(uint256)   • write  contracts/Auction.sol:192  (Auction.('purchaseArbitrageTokens', ['uint256'], []))   • read  contracts/Auction.sol:221  (Auction.('claimArbitrage', ['uint256'], [])) | report= | comments=Adjacent to [H-05], but not distinct or zero-day in and of itself. If this was a multi-var report with a few additional specs, this could be a new bug
  - sheet=59src | row=314 | abl=B6 | type=FP | finding=[single_var_cross_tx] idToAuction  tx-set -> claimArbitrage(uint256), purchaseArbitrageTokens(uint256)   • write  contracts/Auction.sol:198  (Auction.('purchaseArbitrageTokens', ['uint256'], []))   • read  contracts/Auction.sol:221  (Auction.('claimArbitrage', ['uint256'], [])) | report= | comments=Adjacent to [H-05], but not distinct or zero-day in and of itself. If this was a multi-var report with a few additional specs, this could be a new bug

### M-03 AbstractRewardMine.sol#setRewardToken is dangerous
- Label: `MV-SI` / `Type-II-asset-utility`
- Strict B0 match: `no`
- Matched bucket: `NA-no-strict-B0-match`
- FN reason: `FN0-no-same-finding-tag-row`
- Notes: No same-finding MV-Bench row was found for setRewardToken/reward mine accounting.
- Candidate MV-Bench rows: none found by same issue/comment tag.

### M-07 MovingAverage.setSampleMemory may break exchangeRate in StabilizerNode.stabilize
- Label: `MV-SI` / `Type-I-temporal-checkpoint`
- Strict B0 match: `no`
- Matched bucket: `NA-no-strict-B0-match`
- FN reason: `FN0-no-same-finding-tag-row`
- Notes: No same-finding MV-Bench row was found for sampleMemory/exchangeRate desynchronization.
- Candidate MV-Bench rows: none found by same issue/comment tag.

### M-10 AuctionParticipant.sol setReplenishingIndex mistake could freeze unclaimed tokens
- Label: `MV-SI` / `Type-II-asset-utility`
- Strict B0 match: `no`
- Matched bucket: `NA-no-strict-B0-match`
- FN reason: `FN0-no-same-finding-tag-row`
- Notes: No same-finding MV-Bench row was found for replenishingIndex/unclaimed-token freeze.
- Candidate MV-Bench rows: none found by same issue/comment tag.

### M-13 Reducing the epoch length results in leaking value from advancement incentives
- Label: `MV-SI` / `Type-I-temporal-checkpoint`
- Strict B0 match: `no`
- Matched bucket: `NA-no-strict-B0-match`
- FN reason: `FN0-no-same-finding-tag-row`
- Notes: No same-finding MV-Bench row was found for epoch-length/advancement incentive leakage.
- Candidate MV-Bench rows: none found by same issue/comment tag.

### M-18 AuctionParticipant.sol purchaseArbitrageTokens should not push duplicate auctions
- Label: `MV-SI` / `Type-II-asset-utility`
- Strict B0 match: `no`
- Matched bucket: `NA-no-strict-B0-match`
- FN reason: `FN0-no-same-finding-tag-row`
- Notes: No same-finding MV-Bench row was found for duplicate auction participation state.
- Candidate MV-Bench rows: none found by same issue/comment tag.

### M-20 Users Can Contribute To An Auction Without Directly Committing Collateral Tokens
- Label: `MV-SI` / `Type-II-asset-utility`
- Strict B0 match: `no`
- Matched bucket: `NA-no-strict-B0-match`
- FN reason: `FN1-same-finding-tag-not-in-B0`
- Notes: Same finding appears only in non-B0 ablations B1 rows 68 and 106; no strict B0 bucket.
- Candidate MV-Bench rows:
  - sheet=59src | row=68 | abl=B1 | type=TP | finding=[single_var_cross_tx] idToAuction  tx-set -> purchaseArbitrageTokens(uint256), realValueOfLPToken(uint256)   • write  contracts/Auction.sol:772  (Auction.('_resetAuctionMaxCommitments', [], []))   • write  contracts/Auction.sol:198  (Auction.('purchaseArbitrageTokens', ['uint256'], []))   • read  contracts/Auction.sol:186  (Auction.('purchaseArbitrageTokens', ['uint256'], []))   • read  contracts/Auction.sol:859  (Auction.('allocateArbRewards', ['uint256'], ['uint256'])) | report= | comments=[M-20], [L-13]
  - sheet=59src | row=106 | abl=B1 | type=TP | finding=[single_var_cross_tx] idToAuction  tx-set -> averageMaltPrice(uint256), consult(uint256)   • write  contracts/Auction.sol:643  (Auction.('_finalizeAuction', ['uint256'], []))   • read  contracts/Auction.sol:335  (Auction.('averageMaltPrice', ['uint256'], ['uint256'])) | report= | comments=[M-20]

### M-30 Malt Protocol Uses Stale Results From MaltDataLab Which Can Be Abused By Users
- Label: `MV-SI` / `Type-I-temporal-checkpoint`
- Strict B0 match: `no`
- Matched bucket: `NA-no-strict-B0-match`
- FN reason: `FN1-same-finding-tag-not-in-B0`
- Notes: Same finding appears only in non-B0 ablations B1 row 109 and B2 row 151; no strict B0 bucket.
- Candidate MV-Bench rows:
  - sheet=59src | row=109 | abl=B1 | type=TP | finding=[multi_var_cross_contract] idToAuction, unclaimedArbTokens, epochState, {epochState}, _currentEpoch, samples, cumulativeValue, blockTimestampLast, counter  tx-set -> consult(uint256)   • write  contracts/MovingAverage.sol:208  (MovingAverage.('update', ['uint256'], []))   • write  contracts/Bonding.sol:318  (Bonding.('_updateEpochState', ['uint256'], []))   • read  contracts/Bonding.sol:299  (Bonding.('_updateEpochState', ['uint256'], []))   • read  contracts/Auction.sol:640  (Auction.('_finalizeAuction', ['uint256'], [])) | report= | comments=[M-30]
  - sheet=59src | row=151 | abl=B2 | type=TP | finding=[multi_var_cross_contract] idToAuction, unclaimedArbTokens, epochState, {epochState}, _currentEpoch, samples, cumulativeValue, blockTimestampLast, counter, daoRewardCut, lpRewardCut, callerRewardCut, auctionPoolRewardCut, swingTraderRewardCut, deployedCapital, {10, deployedCapital}  tx-set -> unbond(uint256)   • write  contracts/Bonding.sol:284  (Bonding.('_updateEpochState', ['uint256'], []))   • write  contracts/MovingAverage.sol:208  (MovingAverage.('update', ['uint256'], []))   • read  contracts/MovingAverage.sol:291  (MovingAverage.('updateCumulative', ['uint256'], []))   • read  contracts/MovingAverage.sol:294  (MovingAverage.('updateCumulative', ['uint256'], [])) | report= | comments=[M-30]

## Web3Bugs ID 104 / `2022-03-joyn`

- MV-Bench sheet: `104core-contracts`
- MV-SI denominator rows: 2
- Strict B0 matches: 0
- Strict B0 FNs: 2

### M-07 Ineffective Handling of FoT or Rebasing Tokens
- Label: `MV-SI` / `Type-II-asset-utility`
- Strict B0 match: `no`
- Matched bucket: `NA-no-strict-B0-match`
- FN reason: `FN0-no-same-finding-tag-row`
- Notes: No same-finding MV-Bench row was found for Splitter nominal-share/actual-balance FoT/rebasing accounting.
- Candidate MV-Bench rows: none found by same issue/comment tag.

### M-12 CoreCollection.setRoyaltyVault doesn't check royaltyVault.royaltyAsset against payableToken, resulting in potential permanent lock of payableTokens in RoyaltyVault
- Label: `MV-SI` / `Type-III-governance-config`
- Strict B0 match: `no`
- Matched bucket: `NA-no-strict-B0-match`
- FN reason: `FN0-no-same-finding-tag-row`
- Notes: No same-finding MV-Bench row was found for payableToken/royaltyAsset configuration mismatch.
- Candidate MV-Bench rows: none found by same issue/comment tag.

## Web3Bugs ID 60 / `2021-12-perennial`

- MV-Bench sheet: `60protocol`
- MV-SI denominator rows: 1
- Strict B0 matches: 0
- Strict B0 FNs: 1

### H-02 withdrawTo Does Not Sync Before Checking A Position's Margin Requirements
- Label: `MV-SI` / `Type-I-temporal-checkpoint`
- Strict B0 match: `no`
- Matched bucket: `NA-no-strict-B0-match`
- FN reason: `FN0-no-same-finding-tag-row`
- Notes: No same-finding MV-Bench row was found for withdrawTo missing account/product settlement before maintenance checks.
- Candidate MV-Bench rows: none found by same issue/comment tag.

## Web3Bugs ID 72 / `2022-01-openleverage`

- MV-Bench sheet: `72openleverage-contracts`
- MV-SI denominator rows: 1
- Strict B0 matches: 1
- Strict B0 FNs: 0

### M-04 OpenLevV1.closeTrade with V3 DEX doesn't correctly accounts fee on transfer tokens for repayments
- Label: `MV-SI` / `Type-II-asset-utility`
- Strict B0 match: `yes`
- Matched bucket: `72:B0:row13`
- FN reason: `NA-strict-B0-match`
- Notes: B0 row 13 has same repo/finding, activeTrades/markets repayment-accounting state, closeTrade step, and accounting/loss sink.
- Candidate MV-Bench rows:
  - sheet=72openleverage-contracts | row=13 | abl=B0 | type=TP | finding=[multi_var_cross_contract] activeTrades, markets, {markets}  tx-set -> closeTrade(uint16,bool,uint256,uint256,bytes), liquidate(address,uint16,bool,uint256,uint256,bytes)   • write  contracts/OpenLevV1.sol:438  (OpenLevV1.('feesAndInsurance', ['address', 'uint256', 'address', 'uint16', 'uint256', 'uint256'], ['uint256']))   • write  contracts/OpenLevV1.sol:413  (OpenLevV1.('reduceInsurance', ['uint256', 'uint256', 'uint16', 'bool', 'address', 'uint256'], ['uint256']))   • read  contracts/OpenLevV1.sol:170  (OpenLevV1.('closeTrade', ['uint16', 'bool', 'uint256', 'uint256', 'bytes'], []))   • read  contracts/OpenLevV1.sol:318  (OpenLevV1.('liquidate', ['address', 'uint16', 'bool', 'uint256', 'uint256', 'bytes'], [])) | report=https://github.com/code-423n4/2022-01-openleverage-findings/issues/104 https://github.com/code...
  - sheet=72openleverage-contracts | row=98 | abl=B1 | type=TP | finding=[multi_var_cross_contract] activeTrades, markets, {markets}  tx-set -> closeTrade(uint16,bool,uint256,uint256,bytes), liquidate(address,uint16,bool,uint256,uint256,bytes)   • write  contracts/OpenLevV1.sol:225  (OpenLevV1.('closeTrade', ['uint16', 'bool', 'uint256', 'uint256', 'bytes'], []))   • write  contracts/OpenLevV1.sol:398  (OpenLevV1.('reduceInsurance', ['uint256', 'uint256', 'uint16', 'bool', 'address', 'uint256'], ['uint256']))   • read  contracts/OpenLevV1.sol:318  (OpenLevV1.('liquidate', ['address', 'uint16', 'bool', 'uint256', 'uint256', 'bytes'], []))   • read  contracts/OpenLevV1.sol:170  (OpenLevV1.('closeTrade', ['uint16', 'bool', 'uint256', 'uint256', 'bytes'], [])) | report=https://github.com/code-423n4/2022-01-openleverage-findings/issues/104 https://github.com/code-423n4/2022-01-openleverage-fin...
  - sheet=72openleverage-contracts | row=189 | abl=B2 | type=TP | finding=[multi_var_cross_contract] activeTrades, markets, {markets}  tx-set -> closeTrade(uint16,bool,uint256,uint256,bytes), liquidate(address,uint16,bool,uint256,uint256,bytes)   • write  contracts/OpenLevV1.sol:398  (OpenLevV1.('reduceInsurance', ['uint256', 'uint256', 'uint16', 'bool', 'address', 'uint256'], ['uint256']))   • write  contracts/OpenLevV1.sol:438  (OpenLevV1.('feesAndInsurance', ['address', 'uint256', 'address', 'uint16', 'uint256', 'uint256'], ['uint256']))   • read  contracts/OpenLevV1.sol:248  (OpenLevV1.('liquidate', ['address', 'uint16', 'bool', 'uint256', 'uint256', 'bytes'], []))   • read  contracts/OpenLevV1.sol:318  (OpenLevV1.('liquidate', ['address', 'uint16', 'bool', 'uint256', 'uint256', 'bytes'], [])) | report=https://github.com/code-423n4/2022-01-openleverage-findings/issues/104 https://gith...
  - sheet=72openleverage-contracts | row=391 | abl=B6 | type=TP | finding=[multi_var_cross_contract] activeTrades, markets, {markets}  tx-set -> closeTrade(uint16,bool,uint256,uint256,bytes), liquidate(address,uint16,bool,uint256,uint256,bytes)   • write  contracts/OpenLevV1.sol:438  (OpenLevV1.('feesAndInsurance', ['address', 'uint256', 'address', 'uint16', 'uint256', 'uint256'], ['uint256']))   • write  contracts/OpenLevV1.sol:398  (OpenLevV1.('reduceInsurance', ['uint256', 'uint256', 'uint16', 'bool', 'address', 'uint256'], ['uint256']))   • read  contracts/OpenLevV1.sol:318  (OpenLevV1.('liquidate', ['address', 'uint16', 'bool', 'uint256', 'uint256', 'bytes'], []))   • read  contracts/OpenLevV1.sol:248  (OpenLevV1.('liquidate', ['address', 'uint16', 'bool', 'uint256', 'uint256', 'bytes'], [])) | report=https://github.com/code-423n4/2022-01-openleverage-findings/issues/104 https://gith...
  - sheet=72openleverage-contracts | row=394 | abl=B6 | type=TP | finding=[single_var_cross_tx] activeTrades  tx-set -> liquidate(address,uint16,bool,uint256,uint256,bytes), marginTrade(uint16,bool,bool,uint256,uint256,uint256,bytes)   • write  contracts/OpenLevV1.sol:145  (OpenLevV1.('marginTrade', ['uint16', 'bool', 'bool', 'uint256', 'uint256', 'uint256', 'bytes'], []))   • read  contracts/OpenLevV1.sol:318  (OpenLevV1.('liquidate', ['address', 'uint16', 'bool', 'uint256', 'uint256', 'bytes'], [])) | report=https://github.com/code-423n4/2022-01-openleverage-findings/issues/104 https://github.com/code-423n4/2022-01-openleverage-findings/issues/233 | comments=[M-04], [M-05]

## Web3Bugs ID 123 / `2022-05-aura`

- MV-Bench sheet: `123`
- MV-SI denominator rows: 7
- Strict B0 matches: 1
- Strict B0 FNs: 6

### M-03 Improperly Skewed Governance Mechanism
- Label: `MV-SI` / `Type-III-governance-config`
- Strict B0 match: `no`
- Matched bucket: `NA-no-strict-B0-match`
- FN reason: `FN7-bucket-adjacent-not-strict`
- Notes: B0 row 26 captures _checkpointedVotes/getPastVotes but misses the total voting supply counterpart required by the M-03 invariant.
- Candidate MV-Bench rows:
  - sheet=123 | row=26 | abl=B0 | type=TP | finding=[multi_var_cross_contract] _checkpointedVotes, {_checkpointedVotes}  tx-set -> getPastVotes(address,uint256), mint(address,uint256)   • write  contracts/AuraLocker.sol:524  (AuraLocker.('_checkpointDelegate', ['address', 'uint256', 'uint256'], []))   • read  contracts/AuraLocker.sol:600  (AuraLocker.('getPastVotes', ['address', 'uint256'], ['uint256'])) | report=https://github.com/code-423n4/2022-05-aura-findings/issues/232 https://github.com/code-423n4/2022-05-aura-findings/issues/186 | comments=[M-03], [M-08]
  - sheet=123 | row=82 | abl=B1 | type=TP | finding=[single_var_cross_tx] epochs  tx-set -> delegate(address), totalSupplyAtEpoch(uint256)   • write  contracts/AuraLocker.sol:293  (AuraLocker.('_lock', ['address', 'uint256'], []))   • read  contracts/AuraLocker.sol:718  (AuraLocker.('totalSupplyAtEpoch', ['uint256'], ['uint256'])) | report= | comments=[M-03] governance problem in supply acounting

### M-08 Locking up AURA Token does not increase voting power of individual
- Label: `MV-SI` / `Type-III-governance-config`
- Strict B0 match: `yes`
- Matched bucket: `123:B0:row12`
- FN reason: `NA-strict-B0-match`
- Notes: B0 row 12 has userLocks and _checkpointedVotes, the _lock/checkpoint path, and governance voting-power sink.
- Candidate MV-Bench rows:
  - sheet=123 | row=12 | abl=B0 | type=TP | finding=[multi_var_cross_contract] epochs, userLocks, _checkpointedVotes, {_checkpointedVotes}  tx-set -> mint(address,uint256)   • write  contracts/AuraLocker.sol:524  (AuraLocker.('_checkpointDelegate', ['address', 'uint256', 'uint256'], []))   • write  contracts/AuraLocker.sol:293  (AuraLocker.('_lock', ['address', 'uint256'], []))   • read  contracts/AuraLocker.sol:292  (AuraLocker.('_lock', ['address', 'uint256'], []))   • read  contracts/AuraLocker.sol:281  (AuraLocker.('_lock', ['address', 'uint256'], [])) | report=https://github.com/code-423n4/2022-05-aura-findings/issues/186 | comments=[M-08]
  - sheet=123 | row=25 | abl=B0 | type=TP | finding=[single_var_cross_tx] userLocks  tx-set -> delegate(address), mint(address,uint256)   • write  contracts/AuraLocker.sol:282  (AuraLocker.('_lock', ['address', 'uint256'], []))   • read  contracts/AuraLocker.sol:469  (AuraLocker.('delegate', ['address'], [])) | report=https://github.com/code-423n4/2022-05-aura-findings/issues/186 | comments=[M-08]
  - sheet=123 | row=26 | abl=B0 | type=TP | finding=[multi_var_cross_contract] _checkpointedVotes, {_checkpointedVotes}  tx-set -> getPastVotes(address,uint256), mint(address,uint256)   • write  contracts/AuraLocker.sol:524  (AuraLocker.('_checkpointDelegate', ['address', 'uint256', 'uint256'], []))   • read  contracts/AuraLocker.sol:600  (AuraLocker.('getPastVotes', ['address', 'uint256'], ['uint256'])) | report=https://github.com/code-423n4/2022-05-aura-findings/issues/232 https://github.com/code-423n4/2022-05-aura-findings/issues/186 | comments=[M-03], [M-08]
  - sheet=123 | row=81 | abl=B1 | type=TP | finding=[multi_var_cross_contract] epochs, userLocks, _checkpointedVotes, {_checkpointedVotes}  tx-set -> delegate(address)   • write  contracts/AuraLocker.sol:546  (AuraLocker.('_checkpointDelegate', ['address', 'uint256', 'uint256'], []))   • write  contracts/AuraLocker.sol:293  (AuraLocker.('_lock', ['address', 'uint256'], []))   • read  contracts/AuraLocker.sol:281  (AuraLocker.('_lock', ['address', 'uint256'], []))   • read  contracts/AuraLocker.sol:469  (AuraLocker.('delegate', ['address'], [])) | report= | comments=[M-08] missing coupling
  - sheet=123 | row=91 | abl=B1 | type=TP | finding=[multi_var_cross_contract] _checkpointedVotes, {_checkpointedVotes}  tx-set -> delegate(address), getPastVotes(address,uint256)   • write  contracts/AuraLocker.sol:546  (AuraLocker.('_checkpointDelegate', ['address', 'uint256', 'uint256'], []))   • read  contracts/AuraLocker.sol:600  (AuraLocker.('getPastVotes', ['address', 'uint256'], ['uint256'])) | report= | comments=[M-08]
  - sheet=123 | row=322 | abl=B6 | type=TP | finding=[single_var_cross_tx] userLocks  tx-set -> delegate(address)   • write  contracts/AuraLocker.sol:282  (AuraLocker.('_lock', ['address', 'uint256'], []))   • read  contracts/AuraLocker.sol:279  (AuraLocker.('_lock', ['address', 'uint256'], []))   • read  contracts/AuraLocker.sol:469  (AuraLocker.('delegate', ['address'], [])) | report=https://github.com/code-423n4/2022-05-aura-findings/issues/186 | comments=[M-08]

### M-11 Users may lose rewards to other users if rewards are given as fee-on-transfer tokens
- Label: `MV-SI` / `Type-II-asset-utility`
- Strict B0 match: `no`
- Matched bucket: `NA-no-strict-B0-match`
- FN reason: `FN0-no-same-finding-tag-row`
- Notes: No same-finding MV-Bench row was found for ExtraRewardsDistributor nominal amount vs actual FoT received-balance accounting.
- Candidate MV-Bench rows: none found by same issue/comment tag.

### M-13 ConvexMasterChef: When _lpToken is cvx, reward calculation is incorrect
- Label: `MV-SI` / `Type-II-asset-utility`
- Strict B0 match: `no`
- Matched bucket: `NA-no-strict-B0-match`
- FN reason: `FN0-no-same-finding-tag-row`
- Notes: No same-finding MV-Bench row was found for ConvexMasterChef lpToken==cvx reward-supply corruption.
- Candidate MV-Bench rows: none found by same issue/comment tag.

### M-15 ConvexMasterChef: safeRewardTransfer can cause loss of funds
- Label: `MV-SI` / `Type-II-asset-utility`
- Strict B0 match: `no`
- Matched bucket: `NA-no-strict-B0-match`
- FN reason: `FN0-no-same-finding-tag-row`
- Notes: No same-finding MV-Bench row was found for safeRewardTransfer silent underpayment accounting.
- Candidate MV-Bench rows: none found by same issue/comment tag.

### M-21 ConvexMasterChef: When using add() and set(), it should always call massUpdatePools() to update all pools
- Label: `MV-SI` / `Type-I-temporal-checkpoint`
- Strict B0 match: `no`
- Matched bucket: `NA-no-strict-B0-match`
- FN reason: `FN0-no-same-finding-tag-row`
- Notes: No same-finding MV-Bench row was found for totalAllocPoint update without pool checkpoint synchronization.
- Candidate MV-Bench rows: none found by same issue/comment tag.

### M-22 Duplicate LP token could lead to incorrect reward distribution
- Label: `MV-SI` / `Type-II-asset-utility`
- Strict B0 match: `no`
- Matched bucket: `NA-no-strict-B0-match`
- FN reason: `FN0-no-same-finding-tag-row`
- Notes: No same-finding MV-Bench row was found for duplicate LP token pool reward accounting.
- Candidate MV-Bench rows: none found by same issue/comment tag.

## Web3Bugs ID 41 / `2021-10-defiprotocol`

- MV-Bench sheet: `41contracts`
- MV-SI denominator rows: 3
- Strict B0 matches: 3
- Strict B0 FNs: 0

### M-04 Fee on transfer tokens do not work within the protocol
- Label: `MV-SI` / `Type-II-asset-utility`
- Strict B0 match: `yes`
- Matched bucket: `41:B0:row33`
- FN reason: `NA-strict-B0-match`
- Notes: B0 row 33 has same finding, tokens/weights accounting state, pullUnderlying transfer step, and accounting sink for fee-on-transfer behavior.
- Candidate MV-Bench rows:
  - sheet=41contracts | row=30 | abl=B0 | type=TP | finding=[single_var_cross_tx] ibRatio  tx-set -> settleAuction(uint256[],address[],uint256[],address[],uint256[]), totalSupply()   • write  contracts/Basket.sol:139  (Basket.('handleFees', [], []))   • read  contracts/Basket.sol:251  (Basket.('pushUnderlying', ['uint256', 'address'], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/51 | comments=[M-08] auction settles, setting ibRatio via UpdateIBRatio(newRatio), later handleFees tweaks ibRatio again [M-07], then burns use pushUnderlying with this result, and are subject to fee-on-transfer problems via [M-04]
  - sheet=41contracts | row=32 | abl=B0 | type=TP | finding=[multi_var_cross_contract] tokens, weights  tx-set -> setNewWeights(), settleAuction(uint256[],address[],uint256[],address[],uint256[])   • write  contracts/Basket.sol:216  (Basket.('setNewWeights', [], []))   • write  contracts/Basket.sol:215  (Basket.('setNewWeights', [], []))   • read  contracts/Basket.sol:251  (Basket.('pushUnderlying', ['uint256', 'address'], []))   • read  contracts/Basket.sol:252  (Basket.('pushUnderlying', ['uint256', 'address'], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/78 https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/51 | comments=[M-04] and [M-08] combine to create a tokens/weights + ratio + supply invariant that underlies 2 independent mediums and leads to broken accounting and theft
  - sheet=41contracts | row=33 | abl=B0 | type=TP | finding=[multi_var_cross_contract] tokens, weights  tx-set -> addBounty(IERC20,uint256), setNewWeights()   • write  contracts/Basket.sol:216  (Basket.('setNewWeights', [], []))   • write  contracts/Basket.sol:215  (Basket.('setNewWeights', [], []))   • read  contracts/Basket.sol:258  (Basket.('pullUnderlying', ['uint256', 'address'], []))   • read  contracts/Basket.sol:260  (Basket.('pullUnderlying', ['uint256', 'address'], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/78 | comments=[M-04]
  - sheet=41contracts | row=61 | abl=B1 | type=TP | finding=[single_var_cross_tx] ibRatio  tx-set -> owner(), settleAuction(uint256[],address[],uint256[],address[],uint256[])   • write  contracts/Basket.sol:139  (Basket.('handleFees', [], []))   • read  contracts/Basket.sol:258  (Basket.('pullUnderlying', ['uint256', 'address'], []))   • read  contracts/Basket.sol:251  (Basket.('pushUnderlying', ['uint256', 'address'], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/78 | comments=[M-04]
  - sheet=41contracts | row=62 | abl=B1 | type=TP | finding=[multi_var_cross_contract] tokens, weights  tx-set -> setNewWeights(), settleAuction(uint256[],address[],uint256[],address[],uint256[])   • write  contracts/Basket.sol:216  (Basket.('setNewWeights', [], []))   • write  contracts/Basket.sol:215  (Basket.('setNewWeights', [], []))   • read  contracts/Basket.sol:260  (Basket.('pullUnderlying', ['uint256', 'address'], []))   • read  contracts/Basket.sol:252  (Basket.('pushUnderlying', ['uint256', 'address'], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/78 https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/51 | comments=[M-04] and [M-08] combine to create a tokens/weights + ratio + supply invariant that underlies 2 independent mediums and leads to broken accounting and theft
  - sheet=41contracts | row=85 | abl=B2 | type=TP | finding=[single_var_cross_tx] ibRatio  tx-set -> owner(), settleAuction(uint256[],address[],uint256[],address[],uint256[])   • write  contracts/Basket.sol:139  (Basket.('handleFees', [], []))   • read  contracts/Basket.sol:258  (Basket.('pullUnderlying', ['uint256', 'address'], []))   • read  contracts/Basket.sol:251  (Basket.('pushUnderlying', ['uint256', 'address'], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/78 | comments=[M-04]
  - sheet=41contracts | row=92 | abl=B2 | type=TP | finding=[multi_var_cross_contract] tokens, weights  tx-set -> setNewWeights(), settleAuction(uint256[],address[],uint256[],address[],uint256[])   • write  contracts/Basket.sol:215  (Basket.('setNewWeights', [], []))   • write  contracts/Basket.sol:216  (Basket.('setNewWeights', [], []))   • read  contracts/Basket.sol:252  (Basket.('pushUnderlying', ['uint256', 'address'], []))   • read  contracts/Basket.sol:258  (Basket.('pullUnderlying', ['uint256', 'address'], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/78 https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/51 | comments=[M-04] and [M-08] combine to create a tokens/weights + ratio + supply invariant that underlies 2 independent mediums and leads to broken accounting and theft
  - sheet=41contracts | row=122 | abl=B3 | type=TP | finding=[single_var_cross_tx] ibRatio  tx-set -> owner(), settleAuction(uint256[],address[],uint256[],address[],uint256[])   • write  contracts/Basket.sol:139  (Basket.('handleFees', [], []))   • read  contracts/Basket.sol:258  (Basket.('pullUnderlying', ['uint256', 'address'], []))   • read  contracts/Basket.sol:251  (Basket.('pushUnderlying', ['uint256', 'address'], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/78 | comments=[M-04]
  - sheet=41contracts | row=124 | abl=B3 | type=TP | finding=[multi_var_cross_contract] tokens, weights  tx-set -> setNewWeights(), settleAuction(uint256[],address[],uint256[],address[],uint256[])   • write  contracts/Basket.sol:215  (Basket.('setNewWeights', [], []))   • write  contracts/Basket.sol:216  (Basket.('setNewWeights', [], []))   • read  contracts/Basket.sol:257  (Basket.('pullUnderlying', ['uint256', 'address'], []))   • read  contracts/Basket.sol:260  (Basket.('pullUnderlying', ['uint256', 'address'], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/78 https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/51 | comments=[M-04] and [M-08] combine to create a tokens/weights + ratio + supply invariant that underlies 2 independent mediums and leads to broken accounting and theft
  - sheet=41contracts | row=159 | abl=B6 | type=TP | finding=[single_var_cross_tx] ibRatio  tx-set -> settleAuction(uint256[],address[],uint256[],address[],uint256[]), totalSupply()   • write  contracts/Basket.sol:139  (Basket.('handleFees', [], []))   • read  contracts/Basket.sol:251  (Basket.('pushUnderlying', ['uint256', 'address'], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/51 | comments=[M-08] auction settles, setting ibRatio via UpdateIBRatio(newRatio), later handleFees tweaks ibRatio again [M-07], then burns use pushUnderlying with this result, and are subject to fee-on-transfer problems via [M-04]
  - sheet=41contracts | row=163 | abl=B6 | type=TP | finding=[multi_var_cross_contract] tokens, weights  tx-set -> setNewWeights(), settleAuction(uint256[],address[],uint256[],address[],uint256[])   • write  contracts/Basket.sol:215  (Basket.('setNewWeights', [], []))   • write  contracts/Basket.sol:216  (Basket.('setNewWeights', [], []))   • read  contracts/Basket.sol:252  (Basket.('pushUnderlying', ['uint256', 'address'], []))   • read  contracts/Basket.sol:250  (Basket.('pushUnderlying', ['uint256', 'address'], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/78 https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/51 | comments=[M-04] and [M-08] combine to create a tokens/weights + ratio + supply invariant that underlies 2 independent mediums and leads to broken accounting and theft

### M-07 Basket becomes unusable if everybody burns their shares
- Label: `MV-SI` / `Type-I-temporal-checkpoint`
- Strict B0 match: `yes`
- Matched bucket: `41:B0:row31`
- FN reason: `NA-strict-B0-match`
- Notes: B0 row 31 has ibRatio/lastFee, handleFees writes/reads, totalSupply read, and the basket fee-accounting sink.
- Candidate MV-Bench rows:
  - sheet=41contracts | row=24 | abl=B0 | type=TP | finding=[single_var_cross_tx] ibRatio  tx-set -> totalSupply(), updateIBRatio(uint256)   • write  contracts/Basket.sol:235  (Basket.('updateIBRatio', ['uint256'], ['uint256']))   • read  contracts/Basket.sol:138  (Basket.('handleFees', [], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/49 | comments=[M-07]
  - sheet=41contracts | row=28 | abl=B0 | type=TP | finding=[single_var_cross_tx] ibRatio  tx-set -> auctionBurn(uint256), totalSupply()   • write  contracts/Basket.sol:139  (Basket.('handleFees', [], []))   • write  contracts/Basket.sol:118  (Basket.('auctionBurn', ['uint256'], []))   • read  contracts/Basket.sol:117  (Basket.('auctionBurn', ['uint256'], []))   • read  contracts/Basket.sol:138  (Basket.('handleFees', [], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/84 https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/49 | comments=[M-06], [M-07]
  - sheet=41contracts | row=30 | abl=B0 | type=TP | finding=[single_var_cross_tx] ibRatio  tx-set -> settleAuction(uint256[],address[],uint256[],address[],uint256[]), totalSupply()   • write  contracts/Basket.sol:139  (Basket.('handleFees', [], []))   • read  contracts/Basket.sol:251  (Basket.('pushUnderlying', ['uint256', 'address'], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/51 | comments=[M-08] auction settles, setting ibRatio via UpdateIBRatio(newRatio), later handleFees tweaks ibRatio again [M-07], then burns use pushUnderlying with this result, and are subject to fee-on-transfer problems via [M-04]
  - sheet=41contracts | row=31 | abl=B0 | type=TP | finding=[multi_var_cross_contract] ibRatio, lastFee  tx-set -> totalSupply()   • write  contracts/Basket.sol:136  (Basket.('handleFees', [], []))   • write  contracts/Basket.sol:139  (Basket.('handleFees', [], []))   • read  contracts/Basket.sol:130  (Basket.('handleFees', [], []))   • read  contracts/Basket.sol:138  (Basket.('handleFees', [], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/49 | comments=[M-07]
  - sheet=41contracts | row=55 | abl=B1 | type=TP | finding=[single_var_cross_tx] ibRatio  tx-set -> auctionBurn(uint256), owner()   • write  contracts/Basket.sol:139  (Basket.('handleFees', [], []))   • write  contracts/Basket.sol:118  (Basket.('auctionBurn', ['uint256'], []))   • read  contracts/Basket.sol:138  (Basket.('handleFees', [], []))   • read  contracts/Basket.sol:117  (Basket.('auctionBurn', ['uint256'], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/49 | comments=[M-07]
  - sheet=41contracts | row=60 | abl=B1 | type=TP | finding=[single_var_cross_tx] ibRatio  tx-set -> owner()   • write  contracts/Basket.sol:139  (Basket.('handleFees', [], []))   • read  contracts/Basket.sol:138  (Basket.('handleFees', [], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/49 | comments=[M-07]
  - sheet=41contracts | row=84 | abl=B2 | type=TP | finding=[single_var_cross_tx] ibRatio  tx-set -> owner()   • write  contracts/Basket.sol:139  (Basket.('handleFees', [], []))   • read  contracts/Basket.sol:138  (Basket.('handleFees', [], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/49 | comments=[M-07]
  - sheet=41contracts | row=86 | abl=B2 | type=TP | finding=[single_var_cross_tx] ibRatio  tx-set -> auctionBurn(uint256), owner()   • write  contracts/Basket.sol:118  (Basket.('auctionBurn', ['uint256'], []))   • write  contracts/Basket.sol:139  (Basket.('handleFees', [], []))   • read  contracts/Basket.sol:138  (Basket.('handleFees', [], []))   • read  contracts/Basket.sol:117  (Basket.('auctionBurn', ['uint256'], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/49 | comments=[M-07]
  - sheet=41contracts | row=115 | abl=B3 | type=TP | finding=[single_var_cross_tx] ibRatio  tx-set -> auctionBurn(uint256), owner()   • write  contracts/Basket.sol:118  (Basket.('auctionBurn', ['uint256'], []))   • write  contracts/Basket.sol:139  (Basket.('handleFees', [], []))   • read  contracts/Basket.sol:141  (Basket.('handleFees', [], []))   • read  contracts/Basket.sol:117  (Basket.('auctionBurn', ['uint256'], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/49 | comments=[M-07]
  - sheet=41contracts | row=121 | abl=B3 | type=TP | finding=[single_var_cross_tx] ibRatio  tx-set -> owner()   • write  contracts/Basket.sol:139  (Basket.('handleFees', [], []))   • read  contracts/Basket.sol:141  (Basket.('handleFees', [], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/49 | comments=[M-07]
  - sheet=41contracts | row=152 | abl=B6 | type=TP | finding=[single_var_cross_tx] ibRatio  tx-set -> totalSupply(), updateIBRatio(uint256)   • write  contracts/Basket.sol:235  (Basket.('updateIBRatio', ['uint256'], ['uint256']))   • read  contracts/Basket.sol:138  (Basket.('handleFees', [], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/49 | comments=[M-07]
  - sheet=41contracts | row=156 | abl=B6 | type=TP | finding=[multi_var_cross_contract] ibRatio, lastFee  tx-set -> totalSupply()   • write  contracts/Basket.sol:136  (Basket.('handleFees', [], []))   • write  contracts/Basket.sol:139  (Basket.('handleFees', [], []))   • read  contracts/Basket.sol:130  (Basket.('handleFees', [], []))   • read  contracts/Basket.sol:138  (Basket.('handleFees', [], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/49 | comments=[M-07]
  - sheet=41contracts | row=157 | abl=B6 | type=TP | finding=[single_var_cross_tx] ibRatio  tx-set -> bondForRebalance(), totalSupply()   • write  contracts/Basket.sol:139  (Basket.('handleFees', [], []))   • read  contracts/Basket.sol:258  (Basket.('pullUnderlying', ['uint256', 'address'], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/49 | comments=[M-07]
  - sheet=41contracts | row=158 | abl=B6 | type=TP | finding=[single_var_cross_tx] ibRatio  tx-set -> auctionBurn(uint256), totalSupply()   • write  contracts/Basket.sol:118  (Basket.('auctionBurn', ['uint256'], []))   • write  contracts/Basket.sol:139  (Basket.('handleFees', [], []))   • read  contracts/Basket.sol:117  (Basket.('auctionBurn', ['uint256'], []))   • read  contracts/Basket.sol:138  (Basket.('handleFees', [], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/84 https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/49 | comments=[M-06], [M-07]
  - sheet=41contracts | row=159 | abl=B6 | type=TP | finding=[single_var_cross_tx] ibRatio  tx-set -> settleAuction(uint256[],address[],uint256[],address[],uint256[]), totalSupply()   • write  contracts/Basket.sol:139  (Basket.('handleFees', [], []))   • read  contracts/Basket.sol:251  (Basket.('pushUnderlying', ['uint256', 'address'], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/51 | comments=[M-08] auction settles, setting ibRatio via UpdateIBRatio(newRatio), later handleFees tweaks ibRatio again [M-07], then burns use pushUnderlying with this result, and are subject to fee-on-transfer problems via [M-04]

### M-08 Auction bonder can steal user funds if bond block is high enough
- Label: `MV-SI` / `Type-I-temporal-checkpoint`
- Strict B0 match: `yes`
- Matched bucket: `41:B0:row23`
- FN reason: `NA-strict-B0-match`
- Notes: B0 row 23 has ibRatio, updateIBRatio/settleAuction/pushUnderlying steps, and same temporal auction settlement accounting sink.
- Candidate MV-Bench rows:
  - sheet=41contracts | row=20 | abl=B0 | type=FP | finding=[single_var_cross_tx] licenseFee  tx-set -> changeLicenseFee(uint256), totalSupply()   • write  contracts/Basket.sol:171  (Basket.('changeLicenseFee', ['uint256'], []))   • read  contracts/Basket.sol:131  (Basket.('handleFees', [], [])) | report= | comments=Points to [M-01], [M-08-M-11], but NOT SI per se
  - sheet=41contracts | row=23 | abl=B0 | type=TP | finding=[single_var_cross_tx] ibRatio  tx-set -> settleAuction(uint256[],address[],uint256[],address[],uint256[]), updateIBRatio(uint256)   • write  contracts/Basket.sol:235  (Basket.('updateIBRatio', ['uint256'], ['uint256']))   • read  contracts/Basket.sol:251  (Basket.('pushUnderlying', ['uint256', 'address'], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/51 | comments=[M-08]
  - sheet=41contracts | row=30 | abl=B0 | type=TP | finding=[single_var_cross_tx] ibRatio  tx-set -> settleAuction(uint256[],address[],uint256[],address[],uint256[]), totalSupply()   • write  contracts/Basket.sol:139  (Basket.('handleFees', [], []))   • read  contracts/Basket.sol:251  (Basket.('pushUnderlying', ['uint256', 'address'], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/51 | comments=[M-08] auction settles, setting ibRatio via UpdateIBRatio(newRatio), later handleFees tweaks ibRatio again [M-07], then burns use pushUnderlying with this result, and are subject to fee-on-transfer problems via [M-04]
  - sheet=41contracts | row=32 | abl=B0 | type=TP | finding=[multi_var_cross_contract] tokens, weights  tx-set -> setNewWeights(), settleAuction(uint256[],address[],uint256[],address[],uint256[])   • write  contracts/Basket.sol:216  (Basket.('setNewWeights', [], []))   • write  contracts/Basket.sol:215  (Basket.('setNewWeights', [], []))   • read  contracts/Basket.sol:251  (Basket.('pushUnderlying', ['uint256', 'address'], []))   • read  contracts/Basket.sol:252  (Basket.('pushUnderlying', ['uint256', 'address'], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/78 https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/51 | comments=[M-04] and [M-08] combine to create a tokens/weights + ratio + supply invariant that underlies 2 independent mediums and leads to broken accounting and theft
  - sheet=41contracts | row=53 | abl=B1 | type=FP | finding=[single_var_cross_tx] licenseFee  tx-set -> changeLicenseFee(uint256), totalSupply()   • write  contracts/Basket.sol:171  (Basket.('changeLicenseFee', ['uint256'], []))   • read  contracts/Basket.sol:131  (Basket.('handleFees', [], [])) | report= | comments=Points to [M-01], [M-08-M-11], but NOT SI per se
  - sheet=41contracts | row=59 | abl=B1 | type=TP | finding=[single_var_cross_tx] ibRatio  tx-set -> settleAuction(uint256[],address[],uint256[],address[],uint256[]), updateIBRatio(uint256)   • write  contracts/Basket.sol:235  (Basket.('updateIBRatio', ['uint256'], ['uint256']))   • read  contracts/Basket.sol:258  (Basket.('pullUnderlying', ['uint256', 'address'], []))   • read  contracts/Basket.sol:251  (Basket.('pushUnderlying', ['uint256', 'address'], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/51 | comments=[M-08]
  - sheet=41contracts | row=62 | abl=B1 | type=TP | finding=[multi_var_cross_contract] tokens, weights  tx-set -> setNewWeights(), settleAuction(uint256[],address[],uint256[],address[],uint256[])   • write  contracts/Basket.sol:216  (Basket.('setNewWeights', [], []))   • write  contracts/Basket.sol:215  (Basket.('setNewWeights', [], []))   • read  contracts/Basket.sol:260  (Basket.('pullUnderlying', ['uint256', 'address'], []))   • read  contracts/Basket.sol:252  (Basket.('pushUnderlying', ['uint256', 'address'], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/78 https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/51 | comments=[M-04] and [M-08] combine to create a tokens/weights + ratio + supply invariant that underlies 2 independent mediums and leads to broken accounting and theft
  - sheet=41contracts | row=82 | abl=B2 | type=FP | finding=[single_var_cross_tx] licenseFee  tx-set -> changeLicenseFee(uint256), totalSupply()   • write  contracts/Basket.sol:171  (Basket.('changeLicenseFee', ['uint256'], []))   • read  contracts/Basket.sol:131  (Basket.('handleFees', [], [])) | report= | comments=Points to [M-01], [M-08-M-11], but NOT SI per se
  - sheet=41contracts | row=90 | abl=B2 | type=TP | finding=[single_var_cross_tx] ibRatio  tx-set -> settleAuction(uint256[],address[],uint256[],address[],uint256[]), updateIBRatio(uint256)   • write  contracts/Basket.sol:235  (Basket.('updateIBRatio', ['uint256'], ['uint256']))   • read  contracts/Basket.sol:258  (Basket.('pullUnderlying', ['uint256', 'address'], []))   • read  contracts/Basket.sol:251  (Basket.('pushUnderlying', ['uint256', 'address'], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/51 | comments=[M-08]
  - sheet=41contracts | row=92 | abl=B2 | type=TP | finding=[multi_var_cross_contract] tokens, weights  tx-set -> setNewWeights(), settleAuction(uint256[],address[],uint256[],address[],uint256[])   • write  contracts/Basket.sol:215  (Basket.('setNewWeights', [], []))   • write  contracts/Basket.sol:216  (Basket.('setNewWeights', [], []))   • read  contracts/Basket.sol:252  (Basket.('pushUnderlying', ['uint256', 'address'], []))   • read  contracts/Basket.sol:258  (Basket.('pullUnderlying', ['uint256', 'address'], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/78 https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/51 | comments=[M-04] and [M-08] combine to create a tokens/weights + ratio + supply invariant that underlies 2 independent mediums and leads to broken accounting and theft
  - sheet=41contracts | row=113 | abl=B3 | type=FP | finding=[single_var_cross_tx] licenseFee  tx-set -> changeLicenseFee(uint256), totalSupply()   • write  contracts/Basket.sol:171  (Basket.('changeLicenseFee', ['uint256'], []))   • read  contracts/Basket.sol:131  (Basket.('handleFees', [], [])) | report= | comments=Points to [M-01], [M-08-M-11], but NOT SI per se
  - sheet=41contracts | row=119 | abl=B3 | type=TP | finding=[single_var_cross_tx] ibRatio  tx-set -> settleAuction(uint256[],address[],uint256[],address[],uint256[]), updateIBRatio(uint256)   • write  contracts/Basket.sol:235  (Basket.('updateIBRatio', ['uint256'], ['uint256']))   • read  contracts/Basket.sol:258  (Basket.('pullUnderlying', ['uint256', 'address'], []))   • read  contracts/Basket.sol:251  (Basket.('pushUnderlying', ['uint256', 'address'], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/51 | comments=[M-08]
  - sheet=41contracts | row=124 | abl=B3 | type=TP | finding=[multi_var_cross_contract] tokens, weights  tx-set -> setNewWeights(), settleAuction(uint256[],address[],uint256[],address[],uint256[])   • write  contracts/Basket.sol:215  (Basket.('setNewWeights', [], []))   • write  contracts/Basket.sol:216  (Basket.('setNewWeights', [], []))   • read  contracts/Basket.sol:257  (Basket.('pullUnderlying', ['uint256', 'address'], []))   • read  contracts/Basket.sol:260  (Basket.('pullUnderlying', ['uint256', 'address'], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/78 https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/51 | comments=[M-04] and [M-08] combine to create a tokens/weights + ratio + supply invariant that underlies 2 independent mediums and leads to broken accounting and theft
  - sheet=41contracts | row=127 | abl=B4 | type=TP | finding=[single_var_cross_tx] bondBlock  tx-set -> bondForRebalance(), settleAuction(uint256[],address[],uint256[],address[],uint256[])   • write  contracts/Auction.sol:61  (Auction.('bondForRebalance', [], []))   • read  contracts/Auction.sol:81  (Auction.('settleAuction', ['uint256[]', 'address[]', 'uint256[]', 'address[]', 'uint256[]'], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/51 | comments=[M-08]
  - sheet=41contracts | row=150 | abl=B6 | type=FP | finding=[single_var_cross_tx] licenseFee  tx-set -> changeLicenseFee(uint256), totalSupply()   • write  contracts/Basket.sol:171  (Basket.('changeLicenseFee', ['uint256'], []))   • read  contracts/Basket.sol:131  (Basket.('handleFees', [], [])) | report= | comments=Points to [M-01], [M-08-M-11], but NOT SI per se
  - sheet=41contracts | row=155 | abl=B6 | type=TP | finding=[single_var_cross_tx] ibRatio  tx-set -> settleAuction(uint256[],address[],uint256[],address[],uint256[]), updateIBRatio(uint256)   • write  contracts/Basket.sol:235  (Basket.('updateIBRatio', ['uint256'], ['uint256']))   • read  contracts/Basket.sol:251  (Basket.('pushUnderlying', ['uint256', 'address'], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/51 | comments=[M-08]
  - sheet=41contracts | row=159 | abl=B6 | type=TP | finding=[single_var_cross_tx] ibRatio  tx-set -> settleAuction(uint256[],address[],uint256[],address[],uint256[]), totalSupply()   • write  contracts/Basket.sol:139  (Basket.('handleFees', [], []))   • read  contracts/Basket.sol:251  (Basket.('pushUnderlying', ['uint256', 'address'], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/51 | comments=[M-08] auction settles, setting ibRatio via UpdateIBRatio(newRatio), later handleFees tweaks ibRatio again [M-07], then burns use pushUnderlying with this result, and are subject to fee-on-transfer problems via [M-04]
  - sheet=41contracts | row=163 | abl=B6 | type=TP | finding=[multi_var_cross_contract] tokens, weights  tx-set -> setNewWeights(), settleAuction(uint256[],address[],uint256[],address[],uint256[])   • write  contracts/Basket.sol:215  (Basket.('setNewWeights', [], []))   • write  contracts/Basket.sol:216  (Basket.('setNewWeights', [], []))   • read  contracts/Basket.sol:252  (Basket.('pushUnderlying', ['uint256', 'address'], []))   • read  contracts/Basket.sol:250  (Basket.('pushUnderlying', ['uint256', 'address'], [])) | report=https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/78 https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/51 | comments=[M-04] and [M-08] combine to create a tokens/weights + ratio + supply invariant that underlies 2 independent mediums and leads to broken accounting and theft
