# Web3Bugs / Code4rena Semantic Label Audit

This file consolidates the six Web3Bugs / Code4rena semantic-label audit notes for evaluated repositories `59`, `104`, `60`, `72`, `123`, and `41`. The canonical row-level Web3Bugs complement oracle and MV-Bench matching data is `oracle/web3bugs_mvbench_review_queue.csv`.

## src - 2021-11-malt MV/SV-SI Audit

| Summary | Details |
| --- | --- |
| MV-SI rows | `H-05`, `M-03`, `M-07`, `M-10`, `M-13`, `M-18`, `M-20`, `M-30` |
| SV-SI rows | `M-23`, `M-24` |
| Oracle rows | `oracle/web3bugs_mvbench_review_queue.csv` (`oracle_id` prefix `WEB3BUGS-59-`) |

## 1. H-05 AuctionEschapeHatch.sol#exitEarly updates state of the auction wrongly

Label: `MV-SI`

Oracle row: `WEB3BUGS-59-H-05`

Sources:
- Code4rena report: https://code4rena.com/reports/2021-11-malt#h-05-auctioneschapehatchsolexitearly-updates-state-of-the-auction-wrongly
- Finding issue: https://github.com/code-423n4/2021-11-malt-findings/issues/268
- Local Web3Bugs report: `dataset/Web3Bugs/reports/59.md`
- Local code: `dataset/Web3Bugs/contracts/59/src/contracts/AuctionEscapeHatch.sol`

Relevant code:

```solidity
function exitEarly(uint256 _auctionId, uint256 amount, uint256 minOut) external notSameBlock {
  uint256 maltQuantity = _calculateMaltRequiredForExit(_auctionId, amount);
  malt.mint(address(dexHandler), maltQuantity);
  uint256 amountOut = dexHandler.sellMalt();

  AuctionExits storage auctionExits = auctionEarlyExits[_auctionId];
  auctionExits.exitedEarly = auctionExits.exitedEarly + amount;
  auctionExits.earlyExitReturn = auctionExits.earlyExitReturn + amountOut;
  auctionExits.maltUsed = auctionExits.maltUsed + maltQuantity;
  auctionExits.accountExits[msg.sender].exitedEarly =
    auctionExits.accountExits[msg.sender].exitedEarly + amount;
  auctionExits.accountExits[msg.sender].earlyExitReturn =
    auctionExits.accountExits[msg.sender].earlyExitReturn + amountOut;
  auctionExits.accountExits[msg.sender].maltUsed =
    auctionExits.accountExits[msg.sender].maltUsed + maltQuantity;

  auction.amendAccountParticipation(msg.sender, _auctionId, amount, maltQuantity);
  collateralToken.safeTransfer(msg.sender, amountOut);
}
```

Strict MV/SV rationale:
- Coupled state entities: auction user commitment, `userMaltPurchased`, early-exit amount, and aggregate early-exit accounting.
- Independent evidence: the report states that `amount` represents exited commitment but the path subtracts penalty-adjusted `maltQuantity` from purchased Malt, skewing the commitment-to-Malt ratio.
- Desynchronization step: `exitEarly` advances early-exit state and amends auction participation with mismatched units.
- Sink: later auction redemption / profit calculation.
- Classification: strict `MV-SI`.

Strict B0 match status in oracle row: `no`, `NA-no-strict-B0-match`.

## 2. M-03 AbstractRewardMine.sol#setRewardToken is dangerous

Label: `MV-SI`

Oracle row: `WEB3BUGS-59-M-03`

Sources:
- Code4rena report: https://code4rena.com/reports/2021-11-malt#m-03-abstractrewardminesolsetrewardtoken-is-dangerous
- Finding issue: https://github.com/code-423n4/2021-11-malt-findings/issues/285
- Local code: `dataset/Web3Bugs/contracts/59/src/contracts/AbstractRewardMine.sol`

Relevant code:

```solidity
function withdrawForAccount(address account, uint256 amount, address to)
  external
  onlyRole(REWARD_MANAGER_ROLE, "Must have reward manager privs")
  returns (uint256)
{
  uint256 rewardEarned = earned(account);
  if (rewardEarned < amount) {
    amount = rewardEarned;
  }
  _handleWithdrawForAccount(account, amount, to);
  return amount;
}

function setRewardToken(address _token)
  public
  onlyRole(ADMIN_ROLE, "Must have admin privs")
{
  rewardToken = ERC20(_token);
}
```

Strict MV/SV rationale:
- Coupled state entities: reward-token identity, accrued reward accounting, and reward-mine balances.
- Independent evidence: the report identifies changing `rewardToken` after accounting has accrued as dangerous because reward debt/accounting is token-denominated.
- Desynchronization step: `setRewardToken` changes the asset identity without migrating or resetting accrued balances.
- Sink: reward withdrawal/accounting.
- Classification: strict `MV-SI`.

Strict B0 match status in oracle row: `no`, `NA-no-strict-B0-match`.

## 3. M-07 MovingAverage.setSampleMemory may break exchangeRate in StabilizerNode.stabilize

Label: `MV-SI`

Oracle row: `WEB3BUGS-59-M-07`

Sources:
- Code4rena report: https://code4rena.com/reports/2021-11-malt#m-07-movingaveragesetsamplememory-may-broke-movingaverage-making-the-value-of-exchangerate-in-stabilizernodestabilize-being-extremely-wrong
- Finding issue: https://github.com/code-423n4/2021-11-malt-findings/issues/313
- Local code: `dataset/Web3Bugs/contracts/59/src/contracts/MovingAverage.sol`
- Local code: `dataset/Web3Bugs/contracts/59/src/contracts/MaltDataLab.sol`

Relevant code:

```solidity
function setSampleMemory(uint256 _sampleMemory)
  external
  onlyRole(ADMIN_ROLE, "Must have admin privs")
{
  require(_sampleMemory > 0, "Cannot have sample memroy of 0");

  if (_sampleMemory > sampleMemory) {
    for (uint i = sampleMemory; i < _sampleMemory; i++) {
      samples.push();
    }
    counter = counter % _sampleMemory;
  } else {
    activeSamples = _sampleMemory;
    // TODO handle when list is smaller
  }

  sampleMemory = _sampleMemory;
}

function reserveRatioAverage(uint256 _lookback) public view returns (uint256) {
  return reserveRatioMA.getValueWithLookback(_lookback);
}
```

Strict MV/SV rationale:
- Coupled state entities: moving-average sample memory, sample counter, active sample count, and downstream reserve/exchange-rate averages.
- Independent evidence: the report shows `setSampleMemory` can make `getValueWithLookback` return zero or revert, corrupting `StabilizerNode.stabilize`.
- Desynchronization step: `sampleMemory` changes without fully realigning the sample ring/counter/active samples.
- Sink: exchange-rate / reserve-ratio accounting used by stabilization.
- Classification: strict `MV-SI`.

Strict B0 match status in oracle row: `no`, `NA-no-strict-B0-match`.

## 4. M-10 AuctionParticipant.sol setReplenishingIndex mistake could freeze unclaimed tokens

Label: `MV-SI`

Oracle row: `WEB3BUGS-59-M-10`

Sources:
- Code4rena report: https://code4rena.com/reports/2021-11-malt#m-10-auctionparticipantsol-setreplenishingindex-mistake-could-freeze-unclaimed-tokens
- Finding issue: https://github.com/code-423n4/2021-11-malt-findings/issues/88
- Local code: `dataset/Web3Bugs/contracts/59/src/contracts/AuctionParticipant.sol`

Relevant code:

```solidity
function claim() external {
  if (auctionIds.length == 0 || replenishingIndex >= auctionIds.length) {
    return;
  }

  uint256 auctionId = auctionIds[replenishingIndex];
  uint256 replenishingId = auction.replenishingAuctionId();
  if (auctionId > replenishingId) {
    return;
  }
  uint256 claimableTokens = auction.userClaimableArbTokens(address(this), auctionId);
  ...
}

function setReplenishingIndex(uint256 _index)
  public
  onlyRole(ADMIN_ROLE, "Must have admin privs")
{
  require(_index > replenishingIndex, "Cannot replenishingIndex to old value");
  replenishingIndex = _index;
}
```

Strict MV/SV rationale:
- Coupled state entities: `auctionIds`, `replenishingIndex`, and unclaimed auction reward balances.
- Independent evidence: the report states that setting `replenishingIndex` too high permanently locks unclaimed tokens for earlier auction IDs.
- Desynchronization step: admin can advance the cursor beyond claimable auctions and cannot move it back.
- Sink: reward claim loop and token recovery.
- Classification: strict `MV-SI`.

Strict B0 match status in oracle row: `no`, `NA-no-strict-B0-match`.

## 5. M-13 Reducing the epoch length results in leaking value from advancement incentives

Label: `MV-SI`

Oracle row: `WEB3BUGS-59-M-13`

Sources:
- Code4rena report: https://code4rena.com/reports/2021-11-malt#m-13-reducing-the-epoch-length-results-in-leaking-value-from-advancement-incentives
- Finding issue: https://github.com/code-423n4/2021-11-malt-findings/issues/4
- Local code: `dataset/Web3Bugs/contracts/59/src/contracts/DAO.sol`

Relevant code:

```solidity
function advance() external {
  require(block.timestamp >= getEpochStartTime(epoch + 1), "Cannot advance epoch until start of new epoch");
  incrementEpoch();
  malt.mint(msg.sender, advanceIncentive * 1e18);
}

function getEpochStartTime(uint256 _epoch) public view returns (uint256) {
  return genesisTime.add(epochLength.mul(_epoch));
}

function setEpochLength(uint256 _length)
  public
  onlyRole(ADMIN_ROLE, "Must have admin role")
{
  require(_length > 0, "Cannot have zero length epochs");
  _setEpochLength(_length);
}
```

Strict MV/SV rationale:
- Coupled state entities: `genesisTime`, `epoch`, `epochLength`, and advance incentive payout schedule.
- Independent evidence: the report says reducing `epochLength` makes the DAO believe many epochs can be advanced and incentives paid repeatedly.
- Desynchronization step: epoch length changes without checkpointing the last epoch-length update time or preserving already-paid schedule state.
- Sink: incentive minting in `advance`.
- Classification: strict `MV-SI`.

Strict B0 match status in oracle row: `no`, `NA-no-strict-B0-match`.

## 6. M-18 AuctionParticipant.sol purchaseArbitrageTokens should not push duplicate auctions

Label: `MV-SI`

Oracle row: `WEB3BUGS-59-M-18`

Sources:
- Code4rena report: https://code4rena.com/reports/2021-11-malt#m-18-auctionparticipantsol-purchasearbitragetokens-should-not-push-duplicate-auctions
- Finding issue: https://github.com/code-423n4/2021-11-malt-findings/issues/87
- Local code: `dataset/Web3Bugs/contracts/59/src/contracts/AuctionParticipant.sol`

Relevant code:

```solidity
function purchaseArbitrageTokens(uint256 maxAmount)
  external
  onlyRole(IMPLIED_COLLATERAL_SERVICE_ROLE, "Must have implied collateral service privs")
  returns (uint256 remaining)
{
  uint256 balance = usableBalance();
  if (maxAmount < balance) {
    balance = maxAmount;
  }

  uint256 currentAuction = auction.currentAuctionId();
  if (!auction.auctionActive(currentAuction)) {
    return maxAmount;
  }

  auctionIds.push(currentAuction);
  auctionRewardToken.approve(address(auction), balance);
  auction.purchaseArbitrageTokens(balance);
  return maxAmount - balance;
}
```

Strict MV/SV rationale:
- Coupled state entities: current auction ID, `auctionIds` tracking list, `replenishingIndex`, and claimable auction reward balances.
- Independent evidence: the report explains that repeated purchases for the same auction push duplicate IDs, confusing claim/replenishment.
- Desynchronization step: `auctionIds.push(currentAuction)` always appends without checking whether the current auction was already tracked.
- Sink: claim/replenishment accounting and reward recovery.
- Classification: strict `MV-SI`.

Strict B0 match status in oracle row: `no`, `NA-no-strict-B0-match`.

## 7. M-20 Users Can Contribute To An Auction Without Directly Committing Collateral Tokens

Label: `MV-SI`

Oracle row: `WEB3BUGS-59-M-20`

Sources:
- Code4rena report: https://code4rena.com/reports/2021-11-malt#m-20-users-can-contribute-to-an-auction-without-directly-committing-collateral-tokens
- Finding issue: https://github.com/code-423n4/2021-11-malt-findings/issues/188
- Local code: `dataset/Web3Bugs/contracts/59/src/contracts/Auction.sol`

Relevant code:

```solidity
function purchaseArbitrageTokens(uint256 amount) external notSameBlock {
  require(auctionActive(currentAuctionId), "No auction running");

  uint256 realCommitment = _capCommitment(currentAuctionId, amount);

  collateralToken.safeTransferFrom(msg.sender, address(liquidityExtension), realCommitment);

  uint256 purchased = liquidityExtension.purchaseAndBurn(realCommitment);
  AuctionData storage auction = idToAuction[currentAuctionId];

  auction.commitments = auction.commitments.add(realCommitment);
  auction.accountCommitments[msg.sender].commitment =
    auction.accountCommitments[msg.sender].commitment.add(realCommitment);
  auction.accountCommitments[msg.sender].maltPurchased =
    auction.accountCommitments[msg.sender].maltPurchased.add(purchased);
  auction.maltPurchased = auction.maltPurchased.add(purchased);
}
```

Strict MV/SV rationale:
- Coupled state entities: actual collateral contributed to `LiquidityExtension`, auction `commitments`, and per-account purchased/commitment accounting.
- Independent evidence: the report says users can directly send collateral to `LiquidityExtension` and call `purchaseArbitrageTokens(0)`, bypassing direct commitment accounting.
- Desynchronization step: purchase/burn can consume existing extension balance while auction accounting records zero or capped nominal commitment.
- Sink: auction commitment cap and accounting updates.
- Classification: strict `MV-SI`.

Strict B0 match status in oracle row: `no`, `NA-no-strict-B0-match`.

## 8. M-23 addLiquidity Does Not Reset Approval If Not All Tokens Were Added To Liquidity Pool

Label: `SV-SI`

Oracle row: `WEB3BUGS-59-M-23`

Sources:
- Code4rena report: https://code4rena.com/reports/2021-11-malt#m-23-addliquidity-does-not-reset-approval-if-not-all-tokens-were-added-to-liquidity-pool
- Finding issue: https://github.com/code-423n4/2021-11-malt-findings/issues/228
- Local code: `dataset/Web3Bugs/contracts/59/src/contracts/DexHandlers/UniswapHandler.sol`

Relevant code:

```solidity
function addLiquidity() external returns (
  uint256 maltUsed,
  uint256 rewardUsed,
  uint256 liquidityCreated
) {
  uint256 maltBalance = malt.balanceOf(address(this));
  uint256 rewardBalance = rewardToken.balanceOf(address(this));

  rewardToken.approve(address(router), rewardBalance);
  malt.approve(address(router), maltBalance);

  (maltUsed, rewardUsed, liquidityCreated) = router.addLiquidity(...);

  if (maltUsed < maltBalance) {
    malt.safeTransfer(msg.sender, maltBalance.sub(maltUsed));
  }
  if (rewardUsed < rewardBalance) {
    rewardToken.safeTransfer(msg.sender, rewardBalance.sub(rewardUsed));
  }
}
```

Strict MV/SV rationale:
- State entity: stale ERC20 allowance left on the router after partial liquidity use.
- Independent evidence: the report states dust approval amounts can accrue and recommends resetting approval when not all tokens are used.
- Desynchronization step: unused approval remains after unused tokens are transferred out.
- Sink: ERC20 allowance / external router spend authority.
- Classification: `SV-SI`, because this is same-variable stale allowance state, not a multi-entity protocol invariant.

Strict B0 match status in oracle row: `no`, `NA-no-strict-B0-match`.

## 9. M-24 _distributeRewards Does Not Reset Approval If Not All Tokens Were Allocated

Label: `SV-SI`

Oracle row: `WEB3BUGS-59-M-24`

Sources:
- Code4rena report: https://code4rena.com/reports/2021-11-malt#m-24-_distributerewards-does-not-reset-approval-if-not-all-tokens-were-allocated
- Finding issue: https://github.com/code-423n4/2021-11-malt-findings/issues/229
- Local code: `dataset/Web3Bugs/contracts/59/src/contracts/StabilizerNode.sol`

Relevant code:

```solidity
function _distributeRewards(uint256 rewarded) internal {
  if (rewarded == 0) {
    return;
  }
  rewardToken.approve(address(auction), rewarded);
  rewarded = auction.allocateArbRewards(rewarded);

  if (rewarded == 0) {
    return;
  }

  uint256 callerCut = rewarded.mul(callerRewardCut).div(1000);
  ...
}
```

Strict MV/SV rationale:
- State entity: stale ERC20 approval from `StabilizerNode` to `auction`.
- Independent evidence: the report says `allocateArbRewards` may not use the full approved amount, causing dust approval to accrue.
- Desynchronization step: approval is set to `rewarded` before the external call and is not reset to the amount actually consumed.
- Sink: ERC20 allowance / external auction spend authority.
- Classification: `SV-SI`, because this is same-variable stale allowance state.

Strict B0 match status in oracle row: `no`, `NA-no-strict-B0-match`.

## 10. M-30 Malt Protocol Uses Stale Results From MaltDataLab Which Can Be Abused By Users

Label: `MV-SI`

Oracle row: `WEB3BUGS-59-M-30`

Sources:
- Code4rena report: https://code4rena.com/reports/2021-11-malt#m-30-malt-protocol-uses-stale-results-from-maltdatalab-which-can-be-abused-by-users
- Finding issue: https://github.com/code-423n4/2021-11-malt-findings/issues/373
- Local code: `dataset/Web3Bugs/contracts/59/src/contracts/MaltDataLab.sol`
- Local code: `dataset/Web3Bugs/contracts/59/src/contracts/Auction.sol`

Relevant code:

```solidity
function reserveRatioAverage(uint256 _lookback) public view returns (uint256) {
  return reserveRatioMA.getValueWithLookback(_lookback);
}

function smoothedReserves() public view returns (uint256 maltReserves, uint256 collateralReserves) {
  maltReserves = poolMaltReserveMA.getValueWithLookback(reserveLookback);
  uint256 price = smoothedMaltPrice();
  return (maltReserves, maltReserves.mul(price).div(priceTarget));
}
```

The auction path consumes the moving-average reserve ratio:

```solidity
uint256 rRatio = maltDataLab.reserveRatioAverage(reserveRatioLookback);
```

Strict MV/SV rationale:
- Coupled state entities: live pool/reserve state, moving-average samples in `MaltDataLab`, and auction/stabilization decisions that consume the samples.
- Independent evidence: the report states that stale `MaltDataLab` results can be abused by users.
- Desynchronization step: protocol decisions consume stale moving-average state instead of synchronizing to current market/reserve conditions.
- Sink: auction/stabilization accounting and economic decision logic.
- Classification: strict `MV-SI`.

Strict B0 match status in oracle row: `no`, `NA-no-strict-B0-match`.

## core-contracts - 2022-03-joyn MV/SV-SI Audit

| Summary | Details |
| --- | --- |
| MV-SI rows | `M-07`, `M-12` |
| SV-SI rows | `H-07` |
| Oracle rows | `oracle/web3bugs_mvbench_review_queue.csv` (`oracle_id` prefix `WEB3BUGS-104-`) |

## 1. H-07 Duplicate NFTs Can Be Minted if payableToken Has a Callback Attached to it

Label: `SV-SI`

Oracle row: `WEB3BUGS-104-H-07`

Sources:
- Code4rena report: https://code4rena.com/reports/2022-03-joyn#h-07-duplicate-nfts-can-be-minted-if-payabletoken-has-a-callback-attached-to-it
- Finding issue: https://github.com/code-423n4/2022-03-joyn-findings/issues/121
- Local Web3Bugs report: `dataset/Web3Bugs/reports/104.md`
- Local code: `dataset/Web3Bugs/contracts/104/core-contracts/contracts/CoreCollection.sol`
- Local code: `dataset/Web3Bugs/contracts/104/core-contracts/contracts/ERC721Payable.sol`

Ground-truth evidence:
- The report says payment happens before minting, so a callback-bearing `payableToken` can reenter before `totalSupply()` is updated.
- It states the attacker can bypass `totalSupply() + amount <= maxSupply` and mint duplicate token IDs when the ID generation wraps.

Relevant code:

```solidity
function mintToken(
    address to,
    bool isClaim,
    uint256 claimableAmount,
    uint256 amount,
    bytes32[] calldata merkleProof
) external onlyInitialized {
    require(amount > 0, "CoreCollection: Amount should be greater than 0");
    require(totalSupply() + amount <= maxSupply, "CoreCollection: Over Max Supply");

    if (isClaim) {
        _claim(msg.sender, amount);
    } else {
        require(isForSale, "CoreCollection: Not for sale");
        if (mintFee > 0) {
            _handlePayment(mintFee * amount);
        }
    }

    batchMint(to, amount, isClaim);
}

function _handlePayment(uint256 _amount) internal {
    address recipient = royaltyVaultInitialized() ? royaltyVault : address(this);
    payableToken.transferFrom(msg.sender, recipient, _amount);
}
```

Token ID generation depends on the still-stale supply:

```solidity
function mint(address _to) private returns (uint256 tokenId) {
    if (startingIndex == 0) {
        setStartingIndex();
    }
    tokenId = ((startingIndex + totalSupply()) % maxSupply) + 1;
    _mint(_to, tokenId);
}
```

Strict MV/SV rationale:
- State entity: `totalSupply()` / ERC721 mint state during the mint transaction.
- Independent evidence: the report explicitly identifies stale `totalSupply()` during reentrancy.
- Desynchronization step: `_handlePayment` performs an external token call before `batchMint` updates supply.
- Sink: max-supply branch and token ID generation.
- Classification: `SV-SI`, because this is a reentrant stale single-state value (`totalSupply()`), not a multi-entity invariant.

Strict B0 match status in oracle row: `no`, `NA-no-strict-B0-match`.

## 2. M-07 Ineffective Handling of FoT or Rebasing Tokens

Label: `MV-SI`

Oracle row: `WEB3BUGS-104-M-07`

Sources:
- Code4rena report: https://code4rena.com/reports/2022-03-joyn#m-07-ineffective-handling-of-fot-or-rebasing-tokens
- Finding issue: https://github.com/code-423n4/2022-03-joyn-findings/issues/43
- Local Web3Bugs report: `dataset/Web3Bugs/reports/104.md`
- Local code: `dataset/Web3Bugs/contracts/104/royalty-vault/contracts/RoyaltyVault.sol`
- Local code: `dataset/Web3Bugs/contracts/104/splits/contracts/Splitter.sol`

Ground-truth evidence:
- The report says fee-on-transfer and rebasing tokens are not accounted for by `RoyaltyVault` or `Splitter`.
- It states that for fee-on-transfer tokens there may be insufficient funds for the last claimant because recorded split amounts exceed actual received funds.
- The recommended mitigation measures before/after balances, proving that recorded window amounts must track actual received balances.

Relevant code:

```solidity
function sendToSplitter() external override {
    uint256 balanceOfVault = getVaultBalance();
    uint256 platformShare = (balanceOfVault * platformFee) / 10000;
    uint256 splitterShare = balanceOfVault - platformShare;

    require(IERC20(royaltyAsset).transfer(splitterProxy, splitterShare) == true);
    require(ISplitter(splitterProxy).incrementWindow(splitterShare) == true);
    require(IERC20(royaltyAsset).transfer(platformFeeRecipient, platformShare) == true);
}

function incrementWindow(uint256 royaltyAmount) public returns (bool) {
    uint256 wethBalance = IERC20(splitAsset).balanceOf(address(this));
    require(wethBalance >= royaltyAmount, "Insufficient funds");
    require(royaltyAmount > 0, "No additional funds for window");
    balanceForWindow.push(royaltyAmount);
    currentWindow += 1;
    return true;
}
```

Strict MV/SV rationale:
- Coupled state entities: actual Splitter token balance and recorded `balanceForWindow` / window royalty amount.
- Independent coupling evidence: the report and recommended balance-delta mitigation tie recorded accounting to actual token receipt.
- Desynchronization step: `sendToSplitter` passes nominal `splitterShare` into `incrementWindow` rather than the actual balance delta received by the splitter.
- Sink: reward/window accounting and user claims.
- Classification: strict `MV-SI`, because actual funds and recorded per-window royalty accounting diverge.

Strict B0 match status in oracle row: `no`, `NA-no-strict-B0-match`.

## 3. M-12 CoreCollection.setRoyaltyVault doesn't check royaltyVault.royaltyAsset against payableToken

Label: `MV-SI`

Oracle row: `WEB3BUGS-104-M-12`

Sources:
- Code4rena report: https://code4rena.com/reports/2022-03-joyn#m-12-corecollectionsetroyaltyvault-doesnt-check-royaltyvaultroyaltyasset-against-payabletoken-resulting-in-potential-permanent-lock-of-payabletokens-in-royaltyvault
- Finding issue: https://github.com/code-423n4/2022-03-joyn-findings/issues/73
- Local Web3Bugs report: `dataset/Web3Bugs/reports/104.md`
- Local code: `dataset/Web3Bugs/contracts/104/core-contracts/contracts/CoreCollection.sol`
- Local code: `dataset/Web3Bugs/contracts/104/core-contracts/contracts/ERC721Payable.sol`
- Local code: `dataset/Web3Bugs/contracts/104/royalty-vault/contracts/VaultStorage.sol`

Ground-truth evidence:
- The report says each `RoyaltyVault` can only handle its configured `royaltyAsset`.
- It states that if a `CoreCollection` with `payableToken` is paired to an incompatible vault, minting fees transferred to the vault become permanently stuck.
- The recommended mitigation is to require `payableToken == royaltyVault.royaltyAsset()`.

Relevant code:

```solidity
function setRoyaltyVault(address _royaltyVault)
    external
    onlyVaultUninitialized
{
    require(
        msg.sender == splitFactory || msg.sender == owner(),
        "CoreCollection: Only Split Factory or owner can initialize vault."
    );
    royaltyVault = _royaltyVault;
}

function _handlePayment(uint256 _amount) internal {
    address recipient = royaltyVaultInitialized() ? royaltyVault : address(this);
    payableToken.transferFrom(msg.sender, recipient, _amount);
}
```

The vault stores a single asset identity:

```solidity
address public royaltyAsset;
```

Strict MV/SV rationale:
- Coupled state entities: `CoreCollection.payableToken` and `RoyaltyVault.royaltyAsset`.
- Independent coupling evidence: the report states the invariant and recommends an equality check.
- Desynchronization step: `setRoyaltyVault` stores an arbitrary vault without checking that the vault asset matches the collection payment token.
- Sink: payment transfer to vault and later royalty splitting/withdrawal logic.
- Classification: strict `MV-SI`, because cross-contract configuration state must agree for funds to remain usable.

Strict B0 match status in oracle row: `no`, `NA-no-strict-B0-match`.

## protocol - 2021-12-perennial MV/SV-SI Audit

| Summary | Details |
| --- | --- |
| MV-SI rows | `H-02` |
| SV-SI rows | `M-03` |
| Oracle rows | `oracle/web3bugs_mvbench_review_queue.csv` (`oracle_id` prefix `WEB3BUGS-60-`) |

## 1. H-02 withdrawTo Does Not Sync Before Checking A Position's Margin Requirements

Label: `MV-SI`

Oracle row: `WEB3BUGS-60-H-02`

Sources:
- Code4rena report: https://code4rena.com/reports/2021-12-perennial#h-02-withdrawto-does-not-sync-before-checking-a-positions-margin-requirements
- Finding issue: https://github.com/code-423n4/2021-12-perennial-findings/issues/74
- Local Web3Bugs report: `dataset/Web3Bugs/reports/60.md`
- Local code: `dataset/Web3Bugs/contracts/60/protocol/contracts/collateral/Collateral.sol`
- Local code: `dataset/Web3Bugs/contracts/60/protocol/contracts/product/Product.sol`

Ground-truth evidence:
- The report states that `withdrawTo` checks margin requirements without first settling/syncing the account to the latest oracle/product state.
- The recommended mitigation is to add `settleForAccount(msg.sender)` before the withdrawal margin check.

Relevant code:

```solidity
function withdrawTo(address account, IProduct product, UFixed18 amount)
notPaused
collateralInvariant(msg.sender, product)
maintenanceInvariant(msg.sender, product)
external {
    _products[product].debitAccount(msg.sender, amount);
    token.push(account, amount);
}

modifier maintenanceInvariant(address account, IProduct product) {
    _;

    UFixed18 maintenance = product.maintenance(account);
    UFixed18 maintenanceNext = product.maintenanceNext(account);

    if (UFixed18Lib.max(maintenance, maintenanceNext).gt(collateral(account, product)))
        revert CollateralInsufficientCollateralError();
}
```

The product has an explicit account settlement path, but `withdrawTo` does not invoke it:

```solidity
function settleAccountInternal(address account) internal {
    uint256 oracleVersionPreSettle = _positions[account].pre.oracleVersionToSettle(provider);
    uint256 oracleVersionCurrent = provider.currentVersion();

    accumulated = accumulated.add(
        _accumulators[account].syncTo(_accumulator, _positions[account], oracleVersionPreSettle).sum()
    );
    accumulated = accumulated.sub(
        Fixed18Lib.from(_positions[account].settle(provider, oracleVersionPreSettle))
    );
    if (oracleVersionPreSettle != oracleVersionCurrent) {
        accumulated = accumulated.add(
            _accumulators[account].syncTo(_accumulator, _positions[account], oracleVersionCurrent).sum()
        );
        _positions[account].settle(provider, oracleVersionCurrent);
    }
}
```

Strict MV/SV rationale:
- Coupled state entities: collateral balance, account position/maintenance requirement, and oracle-version/account-settlement state.
- Independent coupling evidence: the report explicitly says withdrawal safety must use the up-to-date oracle price and account settlement state.
- Desynchronization step: `withdrawTo` debits collateral and only then checks maintenance using stale product/account state, without synchronizing the account first.
- Sink: collateral withdrawal and maintenance branch predicate.
- Classification: strict `MV-SI`, because collateral, position, and oracle-settlement state are a concrete accounting invariant.

Strict B0 match status in oracle row: `no`, `NA-no-strict-B0-match`.

## 2. M-03 Chainlink's latestRoundData might return stale or incorrect results

Label: `SV-SI`

Oracle row: `WEB3BUGS-60-M-03`

Sources:
- Code4rena report: https://code4rena.com/reports/2021-12-perennial#m-03-chainlinks-latestrounddata-might-return-stale-or-incorrect-results
- Finding issue: https://github.com/code-423n4/2021-12-perennial-findings/issues/24
- Local Web3Bugs report: `dataset/Web3Bugs/reports/60.md`
- Local code: `dataset/Web3Bugs/contracts/60/protocol/contracts/oracle/ChainlinkOracle.sol`

Ground-truth evidence:
- The report says `latestRoundData` is used without checking whether the Chainlink answer is stale.
- The judge agreed that production use should verify freshness and rational bounds.

Relevant code:

```solidity
function sync() public {
    (, int256 feedPrice, , uint256 timestamp, ) = feed.latestRoundData();
    Fixed18 price = Fixed18Lib.ratio(feedPrice, SafeCast.toInt256(_decimalOffset));

    if (priceAtVersion.length == 0 || timestamp > timestampAtVersion[currentVersion()] + minDelay) {
        priceAtVersion.push(price);
        timestampAtVersion.push(timestamp);

        emit Version(currentVersion(), timestamp, price);
    }
}
```

Strict MV/SV rationale:
- State entity: external Chainlink oracle answer/freshness state consumed into local oracle versions.
- Independent evidence: the report identifies missing stale-data validation for `latestRoundData`.
- Desynchronization step: `sync` accepts `feedPrice`/`timestamp` without validating `roundId`, `answeredInRound`, or freshness.
- Sink: oracle price storage and later margin/accounting decisions.
- Classification: `SV-SI`, because this is a single stale oracle read/freshness problem rather than a multi-entity protocol accounting desynchronization.

Strict B0 match status in oracle row: `no`, `NA-no-strict-B0-match`.

## openleverage-contracts - 2022-01-openleverage MV/SV-SI Audit

| Summary | Details |
| --- | --- |
| MV-SI rows | `M-04` |
| SV-SI rows | `None` |
| Oracle rows | `oracle/web3bugs_mvbench_review_queue.csv` (`oracle_id` prefix `WEB3BUGS-72-`) |

## 1. M-04 OpenLevV1.closeTrade with V3 DEX doesn't correctly accounts fee on transfer tokens for repayments

Label: `MV-SI`

Oracle row: `WEB3BUGS-72-M-04`

Sources:
- Code4rena report: https://code4rena.com/reports/2022-01-openleverage#m-04-openlevv1closetrade-with-v3-dex-doesnt-correctly-accounts-fee-on-transfer-tokens-for-repayments
- Finding issue: https://github.com/code-423n4/2022-01-openleverage-findings/issues/104
- Local Web3Bugs report: `dataset/Web3Bugs/reports/72.md`
- Local code: `dataset/Web3Bugs/contracts/72/openleverage-contracts/contracts/OpenLevV1.sol`
- Local code: `dataset/Web3Bugs/contracts/72/openleverage-contracts/contracts/dex/eth/UniV3Dex.sol`

Ground-truth evidence:
- The report states that the amount received by `OpenLevV1` can be less than the V3 DEX returned amount, but the returned amount is used for position debt repayment accounting.
- It identifies repayment-accounting deficit and fund-freeze cases when the actual received amount is lower.

Relevant code:

```solidity
if (trade.depositToken != longToken) {
    closeTradeVars.receiveAmount = flashSell(
        marketId,
        address(marketVars.buyToken),
        address(marketVars.sellToken),
        closeTradeVars.closeAmountAfterFees,
        minOrMaxAmount,
        dexData
    );
    require(closeTradeVars.receiveAmount >= closeTradeVars.repayAmount, "ISR");

    closeTradeVars.sellAmount = closeTradeVars.closeAmountAfterFees;
    marketVars.buyPool.repayBorrowBehalf(msg.sender, closeTradeVars.repayAmount);

    closeTradeVars.depositReturn = closeTradeVars.receiveAmount.sub(closeTradeVars.repayAmount);
}
```

The V3 sell path returns the DEX-indicated swap result:

```solidity
function flashSell(
    uint16 marketId,
    address buyToken,
    address sellToken,
    uint sellAmount,
    uint minBuyAmount,
    bytes memory data
) internal returns (uint buyAmount) {
    if (sellAmount > 0) {
        DexAggregatorInterface dexAggregator = addressConfig.dexAggregator;
        IERC20(sellToken).safeApprove(address(dexAggregator), sellAmount);
        buyAmount = dexAggregator.sell(
            buyToken, sellToken,
            taxes[marketId][buyToken][2],
            taxes[marketId][sellToken][1],
            sellAmount, minBuyAmount, data
        );
    }
}
```

Strict MV/SV rationale:
- Coupled state entities: actual received token balance / contract funds and internal repayment/debt accounting.
- Independent coupling evidence: the report directly states that actual funds can be less than the DEX-indicated result while the DEX result is consumed for repayment accounting.
- Desynchronization step: `closeTrade` uses `receiveAmount` from `flashSell` instead of measuring the actual token balance delta before repaying debt and computing return funds.
- Sink: debt repayment accounting, transfer/return calculation, and protocol deficit/fund-freeze path.
- Classification: strict `MV-SI`, because the defect is actual-balance versus internal-debt-accounting divergence.

Strict B0 match status in oracle row: `yes`, `72:B0:row13`.

## 123 - 2022-05-aura MV/SV-SI Audit

| Summary | Details |
| --- | --- |
| MV-SI rows | `M-03`, `M-08`, `M-11`, `M-13`, `M-15`, `M-21`, `M-22` |
| SV-SI rows | `H-01`, `M-02`, `M-17` |
| Oracle rows | `oracle/web3bugs_mvbench_review_queue.csv` (`oracle_id` prefix `WEB3BUGS-123-`) |

## 1. H-01 User can forfeit other user rewards

Label: `SV-SI`

Oracle row: `WEB3BUGS-123-H-01`

Sources:
- Code4rena report: https://code4rena.com/reports/2022-05-aura#h-01-user-can-forfeit-other-user-rewards
- Finding issue: https://github.com/code-423n4/2022-05-aura-findings/issues/50
- Local Web3Bugs report: `dataset/Web3Bugs/reports/123.md`
- Local code: `dataset/Web3Bugs/contracts/123/contracts/ExtraRewardsDistributor.sol`

Relevant code:

```solidity
mapping(address => mapping(address => uint256)) public userClaims;

function getReward(address _account, address _token, uint256 _startIndex) public {
    _getReward(_account, _token, _startIndex);
}

function _getReward(address _account, address _token, uint256 _startIndex) public {
    (uint256 claimableTokens, uint256 index) =
        _allClaimableRewards(_account, _token, _startIndex);

    if (claimableTokens > 0) {
        userClaims[_token][_account] = index;
        IERC20(_token).safeTransfer(_account, claimableTokens);
    }
}

function _allClaimableRewards(
    address _account,
    address _token,
    uint256 _startIndex
) internal view returns (uint256, uint256) {
    uint256 epochIndex = userClaims[_token][_account];
    epochIndex = _startIndex > epochIndex ? _startIndex : epochIndex;
    ...
}
```

Strict MV/SV rationale:
- State entity: `userClaims[_token][_account]` claim cursor.
- Independent evidence: the report shows a third party can call `getReward` with `_startIndex` for another account and advance the claim cursor, skipping rewards.
- Desynchronization step: caller-controlled `_startIndex` advances another user's cursor.
- Sink: reward claim/update and token transfer.
- Classification: `SV-SI`, because this is one corrupted cursor, not a multi-entity invariant.

Strict B0 match status in oracle row: `no`, `NA-no-strict-B0-match`.

## 2. M-02 CrvDepositorWrapper.sol relies on oracle that isn't frequently updated

Label: `SV-SI`

Oracle row: `WEB3BUGS-123-M-02`

Sources:
- Code4rena report: https://code4rena.com/reports/2022-05-aura#m-02-crvdepositorwrappersol-relies-on-oracle-that-isnt-frequently-updated
- Finding issue: https://github.com/code-423n4/2022-05-aura-findings/issues/115
- Local code: `dataset/Web3Bugs/contracts/123/contracts/CrvDepositorWrapper.sol`
- Local code: `dataset/Web3Bugs/contracts/123/contracts/AuraStakingProxy.sol`

Relevant code:

```solidity
function getMinOut(uint256 _amount, uint256 _outputBps) external view returns (uint256) {
    return _getMinOut(_amount, _outputBps);
}
```

The staking proxy consumes that oracle-derived minimum output:

```solidity
uint256 crvBal = IERC20(crv).balanceOf(address(this));
if (crvBal > 0) {
    uint256 minOut = ICrvDepositorWrapper(crvDepositorWrapper).getMinOut(crvBal, outputBps);
    ICrvDepositorWrapper(crvDepositorWrapper).deposit(crvBal, minOut, true, address(0));
}
```

Strict MV/SV rationale:
- State entity: external Balancer TWAP/oracle price used for `minOut`.
- Independent evidence: the report states the oracle can go over an hour without updating, causing stale slippage/min-output behavior.
- Desynchronization step: deposit/distribution consumes stale oracle output.
- Sink: slippage branch / deposit execution.
- Classification: `SV-SI`, because the issue is a stale oracle read rather than a persistent multi-state protocol invariant.

Strict B0 match status in oracle row: `no`, `NA-no-strict-B0-match`.

## 3. M-03 Improperly Skewed Governance Mechanism

Label: `MV-SI`

Oracle row: `WEB3BUGS-123-M-03`

Sources:
- Code4rena report: https://code4rena.com/reports/2022-05-aura#m-03-improperly-skewed-governance-mechanism
- Finding issue: https://github.com/code-423n4/2022-05-aura-findings/issues/232
- Local code: `dataset/Web3Bugs/contracts/123/contracts/AuraLocker.sol`

Relevant code:

```solidity
function getPastVotes(address account, uint256 timestamp) public view returns (uint256 votes) {
    uint256 epoch = timestamp.div(rewardsDuration).mul(rewardsDuration);
    DelegateeCheckpoint memory ckpt = _checkpointsLookup(_checkpointedVotes[account], epoch);
    votes = ckpt.votes;
    if (votes == 0 || ckpt.epochStart + lockDuration <= epoch) {
        return 0;
    }
    while (epoch > ckpt.epochStart) {
        votes -= delegateeUnlocks[account][epoch];
        epoch -= rewardsDuration;
    }
}

function getPastTotalSupply(uint256 timestamp) external view returns (uint256) {
    require(timestamp < block.timestamp, "ERC20Votes: block not yet mined");
    return totalSupplyAtEpoch(findEpochId(timestamp));
}
```

Strict MV/SV rationale:
- Coupled state entities: total locked/voting supply and individual delegated voting checkpoints.
- Independent evidence: the report states total supply tracks all locked balances while individual voting power tracks delegated balances, skewing governance thresholds.
- Desynchronization step: total supply and individual voting power are computed from different accounting populations.
- Sink: governance quorum / threshold decisions.
- Classification: strict `MV-SI`.

Strict B0 match status in oracle row: `no`, `NA-no-strict-B0-match`.

## 4. M-08 Locking up AURA Token does not increase voting power of individual

Label: `MV-SI`

Oracle row: `WEB3BUGS-123-M-08`

Sources:
- Code4rena report: https://code4rena.com/reports/2022-05-aura#m-08-locking-up-aura-token-does-not-increase-voting-power-of-individual
- Finding issue: https://github.com/code-423n4/2022-05-aura-findings/issues/186
- Local code: `dataset/Web3Bugs/contracts/123/contracts/AuraLocker.sol`

Relevant code:

```solidity
function _lock(address _account, uint256 _amount) internal {
    Balances storage bal = balances[_account];
    _checkpointEpoch();

    uint112 lockAmount = _amount.to112();
    bal.locked = bal.locked.add(lockAmount);
    lockedSupply = lockedSupply.add(_amount);

    ...
    address delegatee = delegates(_account);
    if (delegatee != address(0)) {
        delegateeUnlocks[delegatee][unlockTime] += lockAmount;
        _checkpointDelegate(delegatee, lockAmount, 0);
    }

    Epoch storage e = epochs[epochs.length - 1];
    e.supply = e.supply.add(lockAmount);
}
```

Strict MV/SV rationale:
- Coupled state entities: locked AURA/vlAURA balance, total locked supply, and delegated voting checkpoint state.
- Independent evidence: the report and docs say vlAURA is voting power, but users receive zero votes unless they delegate.
- Desynchronization step: `_lock` updates balance and supply, but skips vote checkpointing when `delegatee == address(0)`.
- Sink: `getVotes` / governance and gauge voting.
- Classification: strict `MV-SI`.

Strict B0 match status in oracle row: `yes`, `123:B0:row12`.

## 5. M-11 Users may lose rewards to other users if rewards are given as fee-on-transfer tokens

Label: `MV-SI`

Oracle row: `WEB3BUGS-123-M-11`

Sources:
- Code4rena report: https://code4rena.com/reports/2022-05-aura#m-11-users-may-lose-rewards-to-other-users-if-rewards-are-given-as-fee-on-transfer-tokens
- Finding issue: https://github.com/code-423n4/2022-05-aura-findings/issues/176
- Local code: `dataset/Web3Bugs/contracts/123/contracts/AuraLocker.sol`

Relevant code:

```solidity
function notifyRewardAmount(address _rewardsToken, uint256 _reward) external {
    require(rewardDistributors[_rewardsToken][msg.sender], "Must be rewardsDistributor");
    require(_reward > 0, "No reward");

    _notifyReward(_rewardsToken, _reward);

    IERC20(_rewardsToken).safeTransferFrom(msg.sender, address(this), _reward);
}

function _notifyReward(address _rewardsToken, uint256 _reward) internal updateReward(address(0)) {
    RewardData storage rdata = rewardData[_rewardsToken];
    ...
    rdata.rewardRate = _reward.add(leftover).div(rewardsDuration).to96();
}
```

Strict MV/SV rationale:
- Coupled state entities: recorded reward amount/rate and actual reward-token balance received.
- Independent evidence: the report says fee-on-transfer rewards make users receive less than accounting promises and recommends using actual balance received.
- Desynchronization step: accounting is updated using `_reward` before measuring the actual transfer delta.
- Sink: reward-rate accounting and user reward claims.
- Classification: strict `MV-SI`.

Strict B0 match status in oracle row: `no`, `NA-no-strict-B0-match`.

## 6. M-13 ConvexMasterChef: When _lpToken is cvx, reward calculation is incorrect

Label: `MV-SI`

Oracle row: `WEB3BUGS-123-M-13`

Sources:
- Code4rena report: https://code4rena.com/reports/2022-05-aura#m-13-convexmasterchef-when-_lptoken-is-cvx-reward-calculation-is-incorrect
- Finding issue: https://github.com/code-423n4/2022-05-aura-findings/issues/151
- Local code: `dataset/Web3Bugs/contracts/123/convex-platform/contracts/contracts/ConvexMasterChef.sol`

Relevant code:

```solidity
struct PoolInfo {
    IERC20 lpToken;
    uint256 allocPoint;
    uint256 lastRewardBlock;
    uint256 accCvxPerShare;
    IRewarder rewarder;
}

IERC20 public immutable cvx;

function updatePool(uint256 _pid) public {
    PoolInfo storage pool = poolInfo[_pid];
    uint256 lpSupply = pool.lpToken.balanceOf(address(this));
    ...
    uint256 cvxReward = multiplier.mul(rewardPerBlock).mul(pool.allocPoint).div(totalAllocPoint);
    pool.accCvxPerShare = pool.accCvxPerShare.add(cvxReward.mul(1e12).div(lpSupply));
}
```

Strict MV/SV rationale:
- Coupled state entities: pool LP token identity, reward token identity (`cvx`), and balance-derived LP supply.
- Independent evidence: the report states reward calculation is corrupted when `_lpToken` is `cvx`.
- Desynchronization step: the reward token balance can also be interpreted as LP supply when the LP token equals `cvx`.
- Sink: reward-per-share accounting.
- Classification: strict `MV-SI`.

Strict B0 match status in oracle row: `no`, `NA-no-strict-B0-match`.

## 7. M-15 ConvexMasterChef: safeRewardTransfer can cause loss of funds

Label: `MV-SI`

Oracle row: `WEB3BUGS-123-M-15`

Sources:
- Code4rena report: https://code4rena.com/reports/2022-05-aura#m-15-convexmasterchef-saferewardtransfer-can-cause-loss-of-funds
- Finding issue: https://github.com/code-423n4/2022-05-aura-findings/issues/272
- Local code: `dataset/Web3Bugs/contracts/123/convex-platform/contracts/contracts/ConvexMasterChef.sol`

Relevant code:

```solidity
function claim(uint256 _pid, address _account) external {
    PoolInfo storage pool = poolInfo[_pid];
    UserInfo storage user = userInfo[_pid][_account];

    updatePool(_pid);
    uint256 pending = user.amount.mul(pool.accCvxPerShare).div(1e12).sub(user.rewardDebt);
    safeRewardTransfer(_account, pending);
    user.rewardDebt = user.amount.mul(pool.accCvxPerShare).div(1e12);
}

function safeRewardTransfer(address _to, uint256 _amount) internal {
    uint256 cvxBal = cvx.balanceOf(address(this));
    if (_amount > cvxBal) {
        cvx.safeTransfer(_to, cvxBal);
    } else {
        cvx.safeTransfer(_to, _amount);
    }
}
```

Strict MV/SV rationale:
- Coupled state entities: pending reward accounting / `rewardDebt` and actual CVX token balance.
- Independent evidence: the report says if the contract is undersupplied, users receive fewer tokens and the missing amount is not reflected in accounting.
- Desynchronization step: `safeRewardTransfer` underpays based on actual balance, then caller updates `rewardDebt` as if full `pending` was paid.
- Sink: reward claim accounting and token transfer.
- Classification: strict `MV-SI`.

Strict B0 match status in oracle row: `no`, `NA-no-strict-B0-match`.

## 8. M-17 ConvexMasterChef deposit and withdraw can be reentered

Label: `SV-SI`

Oracle row: `WEB3BUGS-123-M-17`

Sources:
- Code4rena report: https://code4rena.com/reports/2022-05-aura#m-17-convexmasterchefs-deposit-and-withdraw-can-be-reentered-drawing-all-reward-funds-from-the-contract-if-reward-token-allows-for-transfer-flow-control
- Finding issue: https://github.com/code-423n4/2022-05-aura-findings/issues/313
- Local code: `dataset/Web3Bugs/contracts/123/convex-platform/contracts/contracts/ConvexMasterChef.sol`

Relevant code:

```solidity
function deposit(uint256 _pid, uint256 _amount) public {
    PoolInfo storage pool = poolInfo[_pid];
    UserInfo storage user = userInfo[_pid][msg.sender];
    updatePool(_pid);
    if (user.amount > 0) {
        uint256 pending = user.amount.mul(pool.accCvxPerShare).div(1e12).sub(user.rewardDebt);
        safeRewardTransfer(msg.sender, pending);
    }
    pool.lpToken.safeTransferFrom(address(msg.sender), address(this), _amount);
    user.amount = user.amount.add(_amount);
    user.rewardDebt = user.amount.mul(pool.accCvxPerShare).div(1e12);
}

function withdraw(uint256 _pid, uint256 _amount) public {
    ...
    safeRewardTransfer(msg.sender, pending);
    user.amount = user.amount.sub(_amount);
    user.rewardDebt = user.amount.mul(pool.accCvxPerShare).div(1e12);
    pool.lpToken.safeTransfer(address(msg.sender), _amount);
}
```

Strict MV/SV rationale:
- State entity: stale `user.amount` / `rewardDebt` during reentrant reward transfer.
- Independent evidence: the report identifies reentry before reward-accounting updates.
- Desynchronization step: external reward transfer happens before user accounting is updated.
- Sink: repeated reward transfer.
- Classification: `SV-SI`, because criterion 5 excludes reentrancy from strict MV-SI.

Strict B0 match status in oracle row: `no`, `NA-no-strict-B0-match`.

## 9. M-21 ConvexMasterChef: add()/set() should always call massUpdatePools()

Label: `MV-SI`

Oracle row: `WEB3BUGS-123-M-21`

Sources:
- Code4rena report: https://code4rena.com/reports/2022-05-aura#m-21-convexmasterchef-when-using-add-and-set-it-should-always-call-massupdatepools-to-update-all-pools
- Finding issue: https://github.com/code-423n4/2022-05-aura-findings/issues/147
- Local code: `dataset/Web3Bugs/contracts/123/convex-platform/contracts/contracts/ConvexMasterChef.sol`

Relevant code:

```solidity
function add(uint256 _allocPoint, IERC20 _lpToken, IRewarder _rewarder, bool _withUpdate) public onlyOwner {
    if (_withUpdate) {
        massUpdatePools();
    }
    totalAllocPoint = totalAllocPoint.add(_allocPoint);
    poolInfo.push(PoolInfo({ lpToken: _lpToken, allocPoint: _allocPoint, ... }));
}

function set(uint256 _pid, uint256 _allocPoint, IRewarder _rewarder, bool _withUpdate, bool _updateRewarder) public onlyOwner {
    if (_withUpdate) {
        massUpdatePools();
    }
    totalAllocPoint = totalAllocPoint.sub(poolInfo[_pid].allocPoint).add(_allocPoint);
    poolInfo[_pid].allocPoint = _allocPoint;
}

function updatePool(uint256 _pid) public {
    uint256 cvxReward = multiplier.mul(rewardPerBlock).mul(pool.allocPoint).div(totalAllocPoint);
    pool.accCvxPerShare = pool.accCvxPerShare.add(cvxReward.mul(1e12).div(lpSupply));
}
```

Strict MV/SV rationale:
- Coupled state entities: global `totalAllocPoint`, per-pool `allocPoint`, and per-pool reward checkpoints.
- Independent evidence: the report states changing allocation without updating pools corrupts rewards.
- Desynchronization step: owner can mutate allocation denominator with `_withUpdate == false`.
- Sink: reward-per-share accounting.
- Classification: strict `MV-SI`.

Strict B0 match status in oracle row: `no`, `NA-no-strict-B0-match`.

## 10. M-22 Duplicate LP token could lead to incorrect reward distribution

Label: `MV-SI`

Oracle row: `WEB3BUGS-123-M-22`

Sources:
- Code4rena report: https://code4rena.com/reports/2022-05-aura#m-22-duplicate-lp-token-could-lead-to-incorrect-reward-distribution
- Finding issue: https://github.com/code-423n4/2022-05-aura-findings/issues/124
- Local code: `dataset/Web3Bugs/contracts/123/convex-platform/contracts/contracts/ConvexMasterChef.sol`

Relevant code:

```solidity
function add(uint256 _allocPoint, IERC20 _lpToken, IRewarder _rewarder, bool _withUpdate) public onlyOwner {
    if (_withUpdate) {
        massUpdatePools();
    }
    totalAllocPoint = totalAllocPoint.add(_allocPoint);
    poolInfo.push(
        PoolInfo({
            lpToken: _lpToken,
            allocPoint: _allocPoint,
            lastRewardBlock: lastRewardBlock,
            accCvxPerShare: 0,
            rewarder: _rewarder
        })
    );
}

function updatePool(uint256 _pid) public {
    PoolInfo storage pool = poolInfo[_pid];
    uint256 lpSupply = pool.lpToken.balanceOf(address(this));
    ...
    pool.accCvxPerShare = pool.accCvxPerShare.add(cvxReward.mul(1e12).div(lpSupply));
}
```

Strict MV/SV rationale:
- Coupled state entities: pool identity/LP token uniqueness and per-pool reward accounting.
- Independent evidence: the report states duplicate LP token pools lead to incorrect reward distribution.
- Desynchronization step: `add` does not prevent the same LP token from being assigned to multiple pool IDs, while `lpSupply` is read from the shared contract balance.
- Sink: reward-per-share accounting and claims.
- Classification: strict `MV-SI`.

Strict B0 match status in oracle row: `no`, `NA-no-strict-B0-match`.

## contracts - 2021-10-defiprotocol MV/SV-SI Audit

| Summary | Details |
| --- | --- |
| MV-SI rows | `M-04`, `M-07`, `M-08` |
| SV-SI rows | `M-05` |
| Other H/M rows | `H-01`, `M-01`, `M-02`, `M-03`, `M-06` |
| Oracle rows | `oracle/web3bugs_mvbench_review_queue.csv` (`oracle_id` prefix `WEB3BUGS-41-`) |

## 1. M-04 Fee on transfer tokens do not work within the protocol

Label: `MV-SI`

Oracle row: `WEB3BUGS-41-M-04`

Sources:
- Code4rena report: https://code4rena.com/reports/2021-10-defiprotocol#m-04-fee-on-transfer-tokens-do-not-work-within-the-protocol
- Finding issue: https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/78
- Local Web3Bugs report: `dataset/Web3Bugs/reports/41.md`
- Local code: `dataset/Web3Bugs/contracts/41/contracts/contracts/Basket.sol`

Ground-truth evidence:
- The report states that fee-on-transfer tokens transfer less than expected, causing the protocol to request incorrect amounts.
- The judge comment states that with a fee-on-transfer token, protocol accounting breaks.
- The recommended mitigation is to use stored token balances rather than nominal transfer amounts for amount calculation.

Relevant code:

```solidity
function mintTo(uint256 amount, address to) public nonReentrant override {
    require(auction.auctionOngoing() == false);
    require(amount > 0);

    handleFees();

    pullUnderlying(amount, msg.sender);

    _mint(to, amount);

    emit Minted(to, amount);
}

function pullUnderlying(uint256 amount, address from) private {
    for (uint256 i = 0; i < weights.length; i++) {
        uint256 tokenAmount = amount * weights[i] * ibRatio / BASE / BASE;
        require(tokenAmount > 0);
        IERC20(tokens[i]).safeTransferFrom(from, address(this), tokenAmount);
    }
}
```

Strict MV/SV rationale:
- Coupled state entities: actual ERC20 token balances held by the basket and protocol-requested/accounted token amounts derived from `amount * weights[i] * ibRatio`.
- Independent coupling evidence: the report and judge comment explicitly say accounting breaks because fee-on-transfer tokens transfer less than the nominal requested amount.
- Desynchronization step: `pullUnderlying` requests `tokenAmount` with `safeTransferFrom` but does not synchronize accounting against the actual before/after balance delta.
- Sink: mint/accounting path; the basket mints shares as if the nominal underlying amount arrived.
- Classification: strict `MV-SI`, because this is a persistent actual-balance versus accounted-amount invariant, not merely a token compatibility inconvenience.

Strict B0 match status in oracle row: `yes`, `41:B0:row33`.

## 2. M-05 createBasket re-entrancy

Label: `SV-SI`

Oracle row: `WEB3BUGS-41-M-05`

Sources:
- Code4rena report: https://code4rena.com/reports/2021-10-defiprotocol#m-05-createbasket-re-entrancy
- Finding issue: https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/85
- Local Web3Bugs report: `dataset/Web3Bugs/reports/41.md`
- Local code: `dataset/Web3Bugs/contracts/41/contracts/contracts/Factory.sol`

Ground-truth evidence:
- The report says `createBasket` should be `nonReentrant` because it interacts with arbitrary ERC20-like tokens in a loop and those tokens may contain callback hooks.
- The judge agreed that the function can interact with any ERC20-like token and is vulnerable to reentrancy.

Relevant code:

```solidity
function createBasket(uint256 idNumber) external override returns (IBasket) {
    Proposal memory bProposal = _proposals[idNumber];
    require(bProposal.basket == address(0));

    IAuction newAuction = IAuction(Clones.clone(address(auctionImpl)));
    IBasket newBasket = IBasket(Clones.clone(address(basketImpl)));

    _proposals[idNumber].basket = address(newBasket);

    newAuction.initialize(address(newBasket), address(this));
    newBasket.initialize(bProposal, newAuction);

    for (uint256 i = 0; i < bProposal.weights.length; i++) {
        IERC20 token = IERC20(bProposal.tokens[i]);
        token.safeTransferFrom(msg.sender, address(this), bProposal.weights[i]);
        token.safeApprove(address(newBasket), bProposal.weights[i]);
    }

    newBasket.mintTo(BASE, msg.sender);

    emit BasketCreated(address(newBasket));

    return newBasket;
}
```

Strict MV/SV rationale:
- State entity: the `createBasket` execution/state-ordering sequence, especially partially initialized proposal/basket state around `_proposals[idNumber].basket`, cloned contracts, token transfers, approvals, and final `mintTo`.
- Independent evidence: the Code4rena finding identifies token callbacks during `createBasket` as the reentrancy source and recommends `nonReentrant`.
- Desynchronization/stale step: an external token callback can reenter while creation is partially complete.
- Sink: external call/control-flow sink during basket creation.
- Classification: `SV-SI`, not `MV-SI`, because the issue is reducible to reentrancy/control-flow stale execution state. Criterion 5 excludes reentrancy from strict MV-SI.

Strict B0 match status in oracle row: `no`, `NA-no-strict-B0-match`.

## 3. M-07 Basket becomes unusable if everybody burns their shares

Label: `MV-SI`

Oracle row: `WEB3BUGS-41-M-07`

Sources:
- Code4rena report: https://code4rena.com/reports/2021-10-defiprotocol#m-07-basket-becomes-unusable-if-everybody-burns-their-shares
- Finding issue: https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/49
- Local Web3Bugs report: `dataset/Web3Bugs/reports/41.md`
- Local code: `dataset/Web3Bugs/contracts/41/contracts/contracts/Basket.sol`

Ground-truth evidence:
- The report states that `handleFees` computes a new `ibRatio` by dividing by `totalSupply`, which can be zero.
- The impact is that after everyone burns, the next mint reverts in `handleFees`, making the basket unusable.
- The recommended mitigation is to special-case zero `totalSupply`, either returning or resetting `ibRatio` to `BASE`.

Relevant code:

```solidity
function burn(uint256 amount) public nonReentrant override {
    require(auction.auctionOngoing() == false);
    require(amount > 0);

    handleFees();

    pushUnderlying(amount, msg.sender);
    _burn(msg.sender, amount);
    
    emit Burned(msg.sender, amount);
}

function handleFees() private {
    if (lastFee == 0) {
        lastFee = block.timestamp;
    } else {
        uint256 startSupply = totalSupply();

        uint256 timeDiff = (block.timestamp - lastFee);
        uint256 feePct = timeDiff * licenseFee / ONE_YEAR;
        uint256 fee = startSupply * feePct / (BASE - feePct);

        _mint(publisher, fee * (BASE - factory.ownerSplit()) / BASE);
        _mint(Ownable(address(factory)).owner(), fee * factory.ownerSplit() / BASE);
        lastFee = block.timestamp;

        uint256 newIbRatio = ibRatio * startSupply / totalSupply();
        ibRatio = newIbRatio;

        emit NewIBRatio(ibRatio);
    }
}
```

Strict MV/SV rationale:
- Coupled state entities: `totalSupply`, `ibRatio`, and fee/accounting state (`lastFee`, fee minting, and fee-derived supply changes).
- Independent coupling evidence: the Web3Bugs/Code4rena report explicitly couples zero `totalSupply` with `ibRatio`/fee handling and recommends resetting or bypassing `ibRatio` at zero supply.
- Desynchronization step: all users can burn their shares, reducing `totalSupply` to zero without synchronizing `ibRatio` and fee handling for the empty-basket state.
- Sink: next mint/burn fee-accounting path reaches division by `totalSupply()` and reverts.
- Classification: strict `MV-SI`, because the empty-supply state and `ibRatio`/fee-accounting state are semantically coupled and become invalid for later accounting.

Strict B0 match status in oracle row: `yes`, `41:B0:row31`.

## 4. M-08 Auction bonder can steal user funds if bond block is high enough

Label: `MV-SI`

Oracle row: `WEB3BUGS-41-M-08`

Sources:
- Code4rena report: https://code4rena.com/reports/2021-10-defiprotocol#m-08-auction-bonder-can-steal-user-funds-if-bond-block-is-high-enough
- Finding issue: https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/51
- Local Web3Bugs report: `dataset/Web3Bugs/reports/41.md`
- Local code: `dataset/Web3Bugs/contracts/41/contracts/contracts/Auction.sol`
- Local code: `dataset/Web3Bugs/contracts/41/contracts/contracts/Basket.sol`

Ground-truth evidence:
- The report explains that as `bondBlock` advances, `newRatio` decreases and can become lower than the current `ibRatio`, or near zero.
- The proof of concept identifies the settlement calculation and the `tokensNeeded` balance check as the vulnerable sink.
- The sponsor agreed there can be issues if `ibRatio` drops too low or to zero and planned a minimum `ibRatio` mitigation.

Relevant code:

```solidity
function bondForRebalance() public override {
    require(auctionOngoing);
    require(!hasBonded);

    bondBlock = block.number;

    IERC20 basketToken = IERC20(address(basket));
    bondAmount = basketToken.totalSupply() / factory.bondPercentDiv();
    basketToken.safeTransferFrom(msg.sender, address(this), bondAmount);
    hasBonded = true;
    auctionBonder = msg.sender;

    emit Bonded(msg.sender, bondAmount);
}

function settleAuction(
    uint256[] memory bountyIDs,
    address[] memory inputTokens,
    uint256[] memory inputWeights,
    address[] memory outputTokens,
    uint256[] memory outputWeights
) public nonReentrant override {
    require(auctionOngoing);
    require(hasBonded);
    require(bondBlock + ONE_DAY > block.number);
    require(msg.sender == auctionBonder);
    require(inputTokens.length == inputWeights.length);
    require(outputTokens.length == outputWeights.length);

    for (uint256 i = 0; i < inputTokens.length; i++) {
        IERC20(inputTokens[i]).safeTransferFrom(msg.sender, address(basket), inputWeights[i]);
    }

    for (uint256 i = 0; i < outputTokens.length; i++) {
        IERC20(outputTokens[i]).safeTransferFrom(address(basket), msg.sender, outputWeights[i]);
    }

    uint256 a = factory.auctionMultiplier() * basket.ibRatio();
    uint256 b = (bondBlock - auctionStart) * BASE / factory.auctionDecrement();
    uint256 newRatio = a - b;

    (address[] memory pendingTokens, uint256[] memory pendingWeights) = basket.getPendingWeights();
    IERC20 basketAsERC20 = IERC20(address(basket));

    for (uint256 i = 0; i < pendingWeights.length; i++) {
        uint256 tokensNeeded = basketAsERC20.totalSupply() * pendingWeights[i] * newRatio / BASE / BASE;
        require(IERC20(pendingTokens[i]).balanceOf(address(basket)) >= tokensNeeded);
    }

    basket.setNewWeights();
    basket.updateIBRatio(newRatio);
    auctionOngoing = false;
    hasBonded = false;

    basketAsERC20.safeTransfer(msg.sender, bondAmount);
    withdrawBounty(bountyIDs);
}
```

The settlement ratio is then committed in `Basket`:

```solidity
function updateIBRatio(uint256 newRatio) onlyAuction external override returns (uint256) {
    ibRatio = newRatio;

    emit NewIBRatio(ibRatio);

    return ibRatio;
}
```

Strict MV/SV rationale:
- Coupled state entities: auction-time-derived `newRatio`, basket `ibRatio`, basket `totalSupply`, pending weights, and actual underlying token balances.
- Independent coupling evidence: the report ties `newRatio` to required underlying balances and later mint/burn/withdraw accounting; the sponsor/judge discussion confirms the need for a minimum `ibRatio`.
- Desynchronization step: `newRatio` decays as `bondBlock - auctionStart` grows, but `settleAuction` does not synchronize or bound it against the current basket `ibRatio` or minimum safe ratio before consuming it.
- Sink: settlement transfers output tokens, verifies only the reduced `tokensNeeded`, then writes the stale/unsafe `newRatio` into basket `ibRatio`.
- Classification: strict `MV-SI`, because the temporal auction ratio and basket accounting/balance invariant can diverge, allowing user-fund extraction.

Strict B0 match status in oracle row: `yes`, `41:B0:row23`.
