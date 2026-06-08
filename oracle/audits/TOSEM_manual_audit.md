# Full Recall/Oracle Audit

| Summary | Details |
| --- | --- |
| Findings audited | `15` |
| Labels covered | `MV-SI`, `SV-SI` |
| Oracle rows | `oracle/audits/tosem_oracle_review_queue.csv` |
| Focus | TOSEM -> MV-Bench strict B0 correspondence |

## 1. 2021-07-wildcredit#h-02

Label: `MV-SI`

Sources:
- Code4rena report: https://code4rena.com/reports/2021-07-wildcredit#h-02-lendingpairliquidateaccount-does-not-accrue-and-update-cumulativeinterestrate
- Finding issue: https://github.com/code-423n4/2021-07-wildcredit-findings/issues/122
- Local code: `dataset/Web3Bugs/contracts/18/contracts/LendingPair.sol`

```solidity
function accrue() public {
  if (lastBlockAccrued < block.number) {
    _accrueInterest(tokenA);
    _accrueInterest(tokenB);
    lastBlockAccrued = block.number;
  }
}

function accrueAccount(address _account) public {
  _distributeReward(_account);
  accrue();
  _accrueAccountInterest(_account);

  if (_account != feeRecipient()) {
    _accrueAccountInterest(feeRecipient());
  }
}

function accountHealth(address _account) public view returns(uint) {

  if (debtOf[tokenA][_account] == 0 && debtOf[tokenB][_account] == 0) {
    return controller.LIQ_MIN_HEALTH();
  }

  uint totalAccountSupply  = _supplyCredit(_account, tokenA, tokenA)  + _supplyCredit(_account, tokenB, tokenA);
  uint totalAccountBorrrow = _borrowBalance(_account, tokenA, tokenA) + _borrowBalance(_account, tokenB, tokenA);

  return totalAccountSupply * 1e18 / totalAccountBorrrow;
}

function liquidateAccount(
  address _account,
  address _repayToken,
  uint    _repayAmount,
  uint    _minSupplyOutput
) external {

  // Input validation and adjustments

  _validateToken(_repayToken);
  address supplyToken = _repayToken == tokenA ? tokenB : tokenA;

  // Check account is underwater after interest

  _accrueAccountInterest(_account);
  _accrueAccountInterest(feeRecipient());
  uint health = accountHealth(_account);
  require(health < controller.LIQ_MIN_HEALTH(), "LendingPair: account health > LIQ_MIN_HEALTH");

  // Calculate balance adjustments

  _repayAmount = Math.min(_repayAmount, debtOf[_repayToken][_account]);

  uint supplyDebt   = _convertTokenValues(_repayToken, supplyToken, _repayAmount);
  uint callerFee    = supplyDebt * controller.liqFeeCaller(_repayToken) / 100e18;
  uint systemFee    = supplyDebt * controller.liqFeeSystem(_repayToken) / 100e18;
  uint supplyBurn   = supplyDebt + callerFee + systemFee;
  uint supplyOutput = supplyDebt + callerFee;

  require(supplyOutput >= _minSupplyOutput, "LendingPair: supplyOutput >= _minSupplyOutput");

  // Adjust balances

  _burnSupply(supplyToken, _account, supplyBurn);
  _mintSupply(supplyToken, feeRecipient(), systemFee);
  _burnDebt(_repayToken, _account, _repayAmount);

  // Settle token transfers

  _safeTransferFrom(_repayToken, msg.sender, _repayAmount);
  _safeTransfer(IERC20(supplyToken), msg.sender, supplyOutput);

  emit Liquidation(_account, _repayToken, supplyToken, _repayAmount, supplyOutput);
}

function _accrueAccountInterest(address _account) internal {
  uint lpBalanceA = lpToken[tokenA].balanceOf(_account);
  uint lpBalanceB = lpToken[tokenB].balanceOf(_account);

  _accrueAccountSupply(tokenA, lpBalanceA, _account);
  _accrueAccountSupply(tokenB, lpBalanceB, _account);
  _accrueAccountDebt(tokenA, _account);
  _accrueAccountDebt(tokenB, _account);

  accountInterestSnapshot[tokenA][_account] = cumulativeInterestRate[tokenA];
  accountInterestSnapshot[tokenB][_account] = cumulativeInterestRate[tokenB];
}

function _accrueAccountDebt(address _token, address _account) internal {
  if (debtOf[_token][_account] > 0) {
    uint newDebt = _pendingBorrowInterest(_token, _account);
    _mintDebt(_token, _account, newDebt);
  }
}

function _accrueInterest(address _token) internal {
  uint blocksElapsed = block.number - lastBlockAccrued;
  uint newInterest = _borrowRatePerBlock(_token) * blocksElapsed;
  cumulativeInterestRate[_token] += newInterest;
}

function _newInterest(uint _balance, address _token, address _account) internal view returns(uint) {
  return _balance * (cumulativeInterestRate[_token] - accountInterestSnapshot[_token][_account]) / 100e18;
}
```

Audit notes:

- `liquidateAccount()` calls `_accrueAccountInterest()` and then `accountHealth()` without calling `accrue()` first.
- `accrue()` advances `cumulativeInterestRate` using `lastBlockAccrued`.
- `_accrueAccountInterest()` snapshots the stale `cumulativeInterestRate`, so liquidation debt and health can sometimes be computed from a stale global interest state.
- This is a confirmed `MV-SI` finding whose violations depend on several state variables including `lastBlockAccrued`, `cumulativeInterestRate`, `accountInterestSnapshot`, and `debtOf`.

MV-Scan/MV-Bench correspondence:

- `MV-Bench.xlsx` sheet `18`, row `2`, ablation `B0`, type `TP`.
- Finding: `[single_var_cross_tx] lastBlockAccrued tx-set -> accrue()`.
- Evidence link(s): https://github.com/code-423n4/2021-07-wildcredit-findings/issues/122
- Relationship: diagnostic adjacent True Positive, but not a strict oracle match. The row surfaces the stale global accrual checkpoint (`lastBlockAccrued`/`accrue()`), but it does not directly include the specific `liquidateAccount()` desynchronization and liquidation sink.

## 2. 2021-07-pooltogether#h-03

Label: `MV-SI`

Sources:
- Code4rena report: https://code4rena.com/reports/2021-07-pooltogether#h-03-setyieldsource-leads-to-temporary-wrong-results
- Finding issue: https://github.com/code-423n4/2021-07-pooltogether-findings/issues/4
- Local code: `dataset/Web3Bugs/contracts/24/in_scope/SwappableYieldSource.sol`

```solidity
/// @notice Calculates the number of shares that should be minted or burned when a user deposit or withdraw.
/// @param tokens Amount of tokens.
/// @return Number of shares.
function _tokenToShares(uint256 tokens) internal returns (uint256) {
  uint256 shares;
  uint256 _totalSupply = totalSupply();

  if (_totalSupply == 0) {
    shares = tokens;
  } else {
    // rate = tokens / shares
    // shares = tokens * (totalShares / swappableYieldSourceTotalSupply)
    uint256 exchangeMantissa =
      FixedPoint.calculateMantissa(_totalSupply, yieldSource.balanceOfToken(address(this)));
    shares = FixedPoint.multiplyUintByMantissa(tokens, exchangeMantissa);
  }

  return shares;
}

/// @notice Calculates the number of tokens a user has in the yield source.
/// @param shares Amount of shares.
/// @return Number of tokens.
function _sharesToToken(uint256 shares) internal returns (uint256) {
  uint256 tokens;
  uint256 _totalSupply = totalSupply();

  if (_totalSupply == 0) {
    tokens = shares;
  } else {
    // tokens = shares * (yieldSourceTotalSupply / totalShares)
    uint256 exchangeMantissa =
      FixedPoint.calculateMantissa(yieldSource.balanceOfToken(address(this)), _totalSupply);
    tokens = FixedPoint.multiplyUintByMantissa(shares, exchangeMantissa);
  }

  return tokens;
}

/// @notice Supplies tokens to the current yield source.  Allows assets to be supplied on other user's behalf using the `to` param.
/// @dev Asset tokens are supplied to the yield source, then deposited into the underlying yield source (eg: Aave, Compound, etc...).
/// @dev Shares from the yield source are minted to the swappable yield source address (this contract).
/// @dev Shares from the swappable yield source are minted to the `to` address.
/// @param amount Amount of `depositToken()` to be supplied.
/// @param to User whose balance will receive the tokens.
function supplyTokenTo(uint256 amount, address to) external override nonReentrant {
  IERC20Upgradeable _depositToken = IERC20Upgradeable(yieldSource.depositToken());

  _depositToken.safeTransferFrom(msg.sender, address(this), amount);
  yieldSource.supplyTokenTo(amount, address(this));

  _mintShares(amount, to);
}

/// @notice Redeems tokens from the current yield source.
/// @dev Shares of the swappable yield source address (this contract) are burnt from the yield source.
/// @dev Shares of the `msg.sender` address are burnt from the swappable yield source.
/// @param amount Amount of `depositToken()` to withdraw.
/// @return Actual amount of tokens that were redeemed.
function redeemToken(uint256 amount) external override nonReentrant returns (uint256) {
  IERC20Upgradeable _depositToken = IERC20Upgradeable(yieldSource.depositToken());

  _burnShares(amount);

  uint256 redeemableBalance = yieldSource.redeemToken(amount);
  _depositToken.safeTransferFrom(address(this), msg.sender, redeemableBalance);

  return redeemableBalance;
}

/// @notice Determine if passed yield source is different from current yield source.
/// @param _yieldSource Yield source address to check.
function _requireDifferentYieldSource(IYieldSource _yieldSource) internal view {
  require(address(_yieldSource) != address(yieldSource), "SwappableYieldSource/same-yield-source");
}

/// @notice Set new yield source.
/// @dev After setting the new yield source, we need to approve it to spend maxUint256 amount of depositToken (eg: DAI).
/// @param _newYieldSource New yield source address to set.
function _setYieldSource(IYieldSource _newYieldSource) internal {
  _requireDifferentYieldSource(_newYieldSource);
  require(_newYieldSource.depositToken() == yieldSource.depositToken(), "SwappableYieldSource/different-deposit-token");

  yieldSource = _newYieldSource;
  IERC20Upgradeable(_newYieldSource.depositToken()).safeApprove(address(_newYieldSource), type(uint256).max);

  emit SwappableYieldSourceSet(_newYieldSource);
}

/// @notice Set new yield source.
/// @dev This function is only callable by the owner or asset manager.
/// @param _newYieldSource New yield source address to set.
/// @return true if operation is successful.
function setYieldSource(IYieldSource _newYieldSource) external onlyOwnerOrAssetManager returns (bool) {
  _setYieldSource(_newYieldSource);
  return true;
}

/// @notice Transfer funds from specified yield source to current yield source.
/// @dev We check that the `currentBalance` transferred is at least equal or superior to the `amount` requested.
/// @dev `currentBalance` can be superior to `amount` if yield has been accruing between redeeming and checking for a mathematical error.
/// @param _yieldSource Yield source address to transfer funds from.
/// @param _amount Amount of funds to transfer from passed yield source to current yield source.
function _transferFunds(IYieldSource _yieldSource, uint256 _amount) internal {
  IYieldSource _currentYieldSource = yieldSource;

  _yieldSource.redeemToken(_amount);
  uint256 currentBalance = IERC20Upgradeable(_yieldSource.depositToken()).balanceOf(address(this));

  require(_amount <= currentBalance, "SwappableYieldSource/transfer-amount-different");

  _currentYieldSource.supplyTokenTo(currentBalance, address(this));

  emit FundsTransferred(_yieldSource, _amount);
}

/// @notice Transfer funds from specified yield source to current yield source.
/// @dev We only verify it is a different yield source in the public function cause we already check for it in `_setYieldSource` function.
/// @param _yieldSource Yield source address to transfer funds from.
/// @param amount Amount of funds to transfer from passed yield source.
/// @return true if operation is successful.
function transferFunds(IYieldSource _yieldSource, uint256 amount) external onlyOwnerOrAssetManager returns (bool) {
  _requireDifferentYieldSource(_yieldSource);
  _transferFunds(_yieldSource, amount);
  return true;
}

/// @notice Swap current yield source for new yield source.
/// @dev This function is only callable by the owner or asset manager.
/// @dev We set a new yield source and then transfer funds from the now previous yield source to the new current yield source.
/// @param _newYieldSource New yield source address to set and transfer funds to.
/// @return true if operation is successful.
function swapYieldSource(IYieldSource _newYieldSource) external onlyOwnerOrAssetManager returns (bool) {
  IYieldSource _currentYieldSource = yieldSource;
  uint256 balance = _currentYieldSource.balanceOfToken(address(this));

  _setYieldSource(_newYieldSource);
  _transferFunds(_currentYieldSource, balance);

  return true;
}
```

Audit notes:

- `setYieldSource()` updates the active yield-source pointer without transferring any of the old balances.
- `swapYieldSource()` snapshots the old source balance, updates the pointer, then migrates funds through `_transferFunds()`.
- The invariant is violated when the `yieldSource` pointer, the underlying balance held in that source, and the ERC20 share supply must remain synchronized before `supplyTokenTo()`, `redeemToken()`, and `balanceOfToken()` use share/token conversion math.

MV-Scan/MV-Bench correspondence:

- This is a False Negative.
- Workbook status: `24swappable-yield-source` and `24pooltogether-mstable` contain only headers and no MV-Bench findings.
- Relationship: False Negative is appropriate for this oracle bug when calculating MV-SI recall.

## 3. 2021-09-defiprotocol#h-02

Label: `MV-SI`

Sources:
- Code4rena report: https://code4rena.com/reports/2021-09-defiprotocol#h-02-basketsolauctionburn-a-failed-auction-will-freeze-part-of-the-funds
- Finding issue: https://github.com/code-423n4/2021-09-defiprotocol-findings/issues/134
- Local code: `dataset/Web3Bugs/contracts/36/contracts/contracts/Basket.sol`

```solidity
function burn(uint256 amount) public override {
    require(auction.auctionOngoing() == false);
    require(amount > 0);
    require(balanceOf(msg.sender) >= amount);

    handleFees();

    pushUnderlying(amount, msg.sender);
    _burn(msg.sender, amount);

    emit Burned(msg.sender, amount);
}

function auctionBurn(uint256 amount) onlyAuction external override {
    handleFees();

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

function updateIBRatio(uint256 newRatio) onlyAuction external override returns (uint256) {
    ibRatio = newRatio;

    emit NewIBRatio(ibRatio);

    return ibRatio;
}

function pushUnderlying(uint256 amount, address to) private {
    for (uint256 i = 0; i < weights.length; i++) {
        uint256 tokenAmount = amount * weights[i] * ibRatio / BASE / BASE;
        IERC20(tokens[i]).safeTransfer(to, tokenAmount);
    }
}
```

Audit notes:

- `auctionBurn()` lowers `totalSupply()` without the `ibRatio` repair that is performed inside `handleFees()` after fee-driven supply changes.
- Downstream redemptions use a stale claim ratio and the underlying token claims are underaccounted.

MV-Scan/MV-Bench correspondence:

- `MV-Bench.xlsx` sheet `36contracts`, row `91`, ablation `B3`, type `TP`.
- Finding: `[single_var_cross_tx] ibRatio tx-set -> updateIBRatio(uint256)`.
- Evidence link: https://github.com/code-423n4/2021-09-defiprotocol-findings/issues/134.
- Relationship: direct diagnostic True Positive, but it is outside B0 and in B3. The row targets stale `ibRatio` and links `H-02`, but it is not a strict B0 recall match.

## 4. 2021-12-mellow#h-04

Label: `MV-SI`

Sources:
- Code4rena report: https://code4rena.com/reports/2021-12-mellow#h-04-aavevault-does-not-update-tvl-on-depositwithdraw
- Finding issue: https://github.com/code-423n4/2021-12-mellow-findings/issues/41
- Local code: `dataset/Web3Bugs/contracts/58/mellow-vaults/contracts/AaveVault.sol` and `dataset/Web3Bugs/contracts/58/mellow-vaults/contracts/LpIssuer.sol`.

```solidity
uint256[] internal _tvls;

function tvl() public view override returns (uint256[] memory tokenAmounts) {
    return _tvls;
}

function updateTvls() public {
    for (uint256 i = 0; i < _tvls.length; i++) {
        _tvls[i] = IERC20(_aTokens[i]).balanceOf(address(this));
    }
}

function _push(uint256[] memory tokenAmounts, bytes memory options)
    internal
    override
    returns (uint256[] memory actualTokenAmounts)
{
    address[] memory tokens = _vaultTokens;
    uint256 referralCode = 0;
    if (options.length > 0) {
        referralCode = abi.decode(options, (uint256));
    }

    for (uint256 i = 0; i < _aTokens.length; i++) {
        if (tokenAmounts[i] == 0) {
            continue;
        }
        address token = tokens[i];
        _allowTokenIfNecessary(token);
        _lendingPool().deposit(tokens[i], tokenAmounts[i], address(this), uint16(referralCode));
    }
    updateTvls();
    actualTokenAmounts = tokenAmounts;
}

function deposit(uint256[] calldata tokenAmounts, bytes memory options) external nonReentrant {
    IVaultRegistry registry = _vaultGovernance.internalParams().registry;
    uint256 thisNft = _nft;
    require(thisNft > 0, ExceptionsLibrary.INITIALIZATION);
    require(_subvaultNft > 0, ExceptionsLibrary.INITIALIZE_SUB_VAULT);
    require(registry.ownerOf(thisNft) == address(this), ExceptionsLibrary.INITIALIZE_OWNER);
    IVault subvault = _subvault();
    uint256[] memory existentials_ = _existentials;
    uint256[] memory tvl = subvault.tvl(); //pre-money
    uint256 supply = totalSupply();
    uint256 balanceFactor = CommonLibrary.PRICE_DENOMINATOR;
    if (supply > 0) {
        balanceFactor = _getLpAmount(tvl, tokenAmounts, existentials_, CommonLibrary.PRICE_DENOMINATOR);
    }

    require(balanceFactor > 0, "BF");
    uint256[] memory balancedAmounts = new uint256[](tokenAmounts.length);

    for (uint256 i = 0; i < _vaultTokens.length; i++) {
        balancedAmounts[i] = _getBalancedAmount(tvl[i], tokenAmounts[i], existentials_[i], balanceFactor, supply);
        _allowTokenIfNecessary(_vaultTokens[i], address(subvault));
        IERC20(_vaultTokens[i]).safeTransferFrom(msg.sender, address(this), balancedAmounts[i]);
    }

    uint256[] memory actualTokenAmounts = subvault.transferAndPush(
        address(this),
        _vaultTokens,
        balancedAmounts,
        options
    );
    uint256 amountToMint = _getLpAmount(tvl, actualTokenAmounts, existentials_, supply);

    _chargeFees(thisNft, tvl, supply, actualTokenAmounts, amountToMint, false);
    _mint(msg.sender, amountToMint);
}
```

Audit notes:

- `LpIssuer.deposit()` snapshots `subvault.tvl()` before a transfer.
- `AaveVault._push()` only refreshes `_tvls` after depositing into Aave.
- Share minting may use stale cached TVL rather than the current rebasing `aToken` balances.

MV-Scan/MV-Bench correspondence:

- `MV-Bench.xlsx` sheet `58mellow-vaults`, row `20`, ablation `B0`, type `--`.
- Finding: `[single_var_cross_tx] _vaultTokens tx-set -> setVaultTokens(address[]), tvl()`.
- Comments: `Tests not counted`.
- Relationship: False Negative; only a superficial TVL-related same-repo row identified part of this finding. It is test-code/non-counted and does not match the Aave rebasing `_tvls` stale-cache deposit/withdraw bug. No True Positive can be claimed for H-04.

## 5. 2021-12-vader#h-10

Label: `SV-SI`

Sources:
- Code4rena report: https://code4rena.com/reports/2021-12-vader#h-10-previousprices-is-never-updated-upon-syncing-token-price
- Finding issue: https://github.com/code-423n4/2021-12-vader-findings/issues/103
- Local code: `dataset/Web3Bugs/contracts/70/contracts/lbt/LiquidityBasedTWAP.sol`

```solidity
function syncVaderPrice()
    public
    override
    returns (
        uint256[] memory pastLiquidityWeights,
        uint256 pastTotalLiquidityWeight
    )
{
    uint256 _totalLiquidityWeight;
    uint256 totalPairs = vaderPairs.length;
    pastLiquidityWeights = new uint256[](totalPairs);
    pastTotalLiquidityWeight = totalLiquidityWeight[uint256(Paths.VADER)];

    for (uint256 i; i < totalPairs; ++i) {
        IUniswapV2Pair pair = vaderPairs[i];
        ExchangePair storage pairData = twapData[address(pair)];
        uint256 timeElapsed = block.timestamp - pairData.lastMeasurement;

        if (timeElapsed < pairData.updatePeriod) continue;

        uint256 pastLiquidityEvaluation = pairData.pastLiquidityEvaluation;
        uint256 currentLiquidityEvaluation = _updateVaderPrice(
            pair,
            pairData,
            timeElapsed
        );

        pastLiquidityWeights[i] = pastLiquidityEvaluation;
        pairData.pastLiquidityEvaluation = currentLiquidityEvaluation;
        _totalLiquidityWeight += currentLiquidityEvaluation;
    }

    totalLiquidityWeight[uint256(Paths.VADER)] = _totalLiquidityWeight;
}

function _updateVaderPrice(
    IUniswapV2Pair pair,
    ExchangePair storage pairData,
    uint256 timeElapsed
) internal returns (uint256 currentLiquidityEvaluation) {
    pairData.nativeTokenPriceCumulative = nativeTokenPriceCumulative;
    pairData.lastMeasurement = currentMeasurement;

    currentLiquidityEvaluation =
        (reserveNative * previousPrices[uint256(Paths.VADER)]) +
        (reserveForeign * getChainlinkPrice(pairData.foreignAsset));
}

function setupVader(
    IUniswapV2Pair pair,
    IAggregatorV3 oracle,
    uint256 updatePeriod,
    uint256 vaderPrice
) external onlyOwner {
    require(previousPrices[uint256(Paths.VADER)] == 0, "LBTWAP::setupVader: Already Initialized");
    previousPrices[uint256(Paths.VADER)] = vaderPrice;
    _addVaderPair(pair, oracle, updatePeriod);
}
```

Audit notes:

- The stale state is the cached `previousPrices[path]` value.
- `syncVaderPrice()` and `syncUSDVPrice()` update TWAP/liquidity bookkeeping but don't assign a fresh value back into `previousPrices`.
- This involves one variable, so we identify it as `SV-SI` -- even though the sink also uses reserves and Chainlink prices.

MV-Scan/MV-Bench correspondence:

- `MV-Bench.xlsx` sheet `70`, row `2`, ablation `B0`, type `TP`.
- Finding: `[multi_var_cross_contract] twapData, maxUpdateWindow tx-set -> getChainlinkPrice(address)`.
- Evidence link: https://github.com/code-423n4/2021-12-vader-findings/issues/160.
- Comments: MV-Bench notes this interacts with `[H-11], [H-03], [H-05], [H-10]`.
- Relationship: not a strict oracle match for H-10. The B0 row is a diagnostic same-contract overlap for the `twapData`/`maxUpdateWindow` oracle-window bucket and only mentions H-10 in comments; it does not include the stale `previousPrices[path]` state entity, the `syncVaderPrice()`/`syncUSDVPrice()` missing assignment, or the H-10 liquidity-evaluation sink. Since H-10 is labeled `SV-SI`, it is excluded from known-MVSI strict recall.

## 6. 2022-02-concur#h-01

Label: `MV-SI`

Sources:
- Code4rena report: https://code4rena.com/reports/2022-02-concur#h-01-wrong-reward-token-calculation-in-masterchef-contract
- Finding issue: https://github.com/code-423n4/2022-02-concur-findings/issues/219
- Source code: https://github.com/code-423n4/2022-02-concur/blob/main/contracts/MasterChef.sol#L86
- Local code: `dataset/Web3Bugs/contracts/83/contracts/MasterChef.sol`

```solidity
function add(address _token, uint _allocationPoints, uint16 _depositFee, uint _startBlock) public onlyOwner {
    require(_token != address(0), "zero address");
    uint lastRewardBlock = block.number > _startBlock ? block.number : _startBlock;
    totalAllocPoint = totalAllocPoint.add(_allocationPoints);
    require(pid[_token] == 0, "already registered");
    poolInfo.push(PoolInfo({
        depositToken: IERC20(_token),
        allocPoint: _allocationPoints,
        lastRewardBlock: lastRewardBlock,
        accConcurPerShare: 0,
        depositFeeBP: _depositFee
    }));
    pid[_token] = poolInfo.length - 1;
}

function massUpdatePools() public {
    uint length = poolInfo.length;
    for (uint _pid = 0; _pid < length; ++_pid) {
        updatePool(_pid);
    }
}

function updatePool(uint _pid) public {
    PoolInfo storage pool = poolInfo[_pid];
    uint multiplier = getMultiplier(pool.lastRewardBlock, block.number);
    uint concurReward = multiplier.mul(concurPerBlock).mul(pool.allocPoint).div(totalAllocPoint);
    pool.accConcurPerShare = pool.accConcurPerShare.add(concurReward.mul(_concurShareMultiplier).div(lpSupply));
    pool.lastRewardBlock = block.number;
}
```

Audit notes:

- `add()` changes `totalAllocPoint` before existing pools checkpoint their old allocation slope.

MV-Scan/MV-Bench correspondence:

- `MV-Bench.xlsx` sheet `83`, row `9`, ablation `B0`, type `TP`.
- Finding: `[single_var_cross_tx] poolInfo tx-set -> massUpdatePools(), updatePool(uint256)`.
- Comments: `[H-01] missing updates when adding pools, and multiple updatePool reward-accounting issues`.
- Relationship: diagnostic same-finding-tag overlap, but not a strict B0 oracle match. The B0 bucket catches the broad pool reward-accounting surface, but it does not include the `add()` path where `totalAllocPoint` changes before existing pools are checkpointed, so it fails the same-desynchronization-step requirement for strict recall.

## 7. 2022-04-backd#h-02

Label: `MV-SI`

Sources:
- Code4rena report: https://code4rena.com/reports/2022-04-backd#h-02-function-lockfunds-in-topupactionlibrary-can-cause-serious-fund-lose-fee-and-capped-bypass-its-not-calling-stakervaultincreaseactionlockedbalance-when-transfers-stakes
- Finding issue: https://github.com/code-423n4/2022-04-backd-findings/issues/60
- Local code: `dataset/Web3Bugs/contracts/112/backd/contracts/actions/topup/TopUpAction.sol` and `dataset/Web3Bugs/contracts/112/backd/contracts/StakerVault.sol`.

```solidity
function lockFunds(
    address stakerVaultAddress,
    address payer,
    address token,
    uint256 lockAmount,
    uint256 depositAmount
) external {
    uint256 amountLeft = lockAmount;
    IStakerVault stakerVault = IStakerVault(stakerVaultAddress);

    if (depositAmount > 0) {
        depositAmount = depositAmount > amountLeft ? amountLeft : depositAmount;
        IERC20(token).safeTransferFrom(payer, address(this), depositAmount);
        IERC20(token).safeApprove(stakerVaultAddress, depositAmount);
        stakerVault.stake(depositAmount);
        stakerVault.increaseActionLockedBalance(payer, depositAmount);
        amountLeft -= depositAmount;
    }

    if (amountLeft > 0) {
        uint256 balance = stakerVault.balanceOf(payer);
        uint256 allowance = stakerVault.allowance(payer, address(this));
        uint256 availableFunds = balance < allowance ? balance : allowance;
        if (availableFunds >= amountLeft) {
            stakerVault.transferFrom(payer, address(this), amountLeft);
            amountLeft = 0;
        }
    }

    require(amountLeft == 0, Error.INSUFFICIENT_UPDATE_BALANCE);
}

function transferFrom(
    address src,
    address dst,
    uint256 amount
) external override notPaused returns (bool) {
    uint256 srcTokens = balances[src];
    require(srcTokens >= amount, Error.INSUFFICIENT_BALANCE);

    uint256 srcTokensNew = srcTokens - amount;
    uint256 dstTokensNew = balances[dst] + amount;

    balances[src] = srcTokensNew;
    balances[dst] = dstTokensNew;

    emit Transfer(src, dst, amount);
    return true;
}

function increaseActionLockedBalance(address account, uint256 amount)
    external
    override
    returns (bool)
{
    require(controller.addressProvider().isAction(msg.sender), Error.UNAUTHORIZED_ACCESS);
    actionLockedBalances[account] += amount;
    return true;
}
```

Audit notes:

- The branch that transfers staked funds moves `balances[src]` through `StakerVault.transferFrom()`.
- It never calls `increaseActionLockedBalance()`, so `balances[account]` and `actionLockedBalances[account]` diverge.

MV-Scan/MV-Bench correspondence:

- `MV-Bench.xlsx` sheet `112backd`, row `199`, ablation `B3`, type `TP`.
- Finding: `[multi_var_cross_contract] {actionLockedBalances, balances} tx-set -> increaseActionLockedBalance(address,uint256), transferFrom(address,address,uint256)`.
- Comments: `[H-02] Direct match from our original build motivation -- this is a confirmed multi-variable invariant matching ground truth from during our initial build of MV-Scan`.
- Relationship: direct diagnostic True Positive outside B0. It matches the `balances`/`actionLockedBalances` invariant, but it is not a B0 row and therefore does not count toward strict B0 recall.

## 8. 2022-12-tigris#h-01

Label: `MV-SI`

Sources:
- Code4rena report: https://code4rena.com/reports/2022-12-tigris#h-01-locksol-assets-deposited-with-lockextendlock-function-are-lost
- Finding issue: https://github.com/code-423n4/2022-12-tigris-findings/issues/23
- Source code: https://github.com/code-423n4/2022-12-tigris/blob/496e1974ee3838be8759e7b4096dbee1b8795593/contracts/Lock.sol#L61-L105
- Local code: `dataset/Web3Bugs/contracts/192/contracts/Lock.sol`

```solidity
mapping(address => uint) public totalLocked;

function lock(address _asset, uint _amount, uint _period) public {
    IERC20(_asset).transferFrom(msg.sender, address(this), _amount);
    totalLocked[_asset] += _amount;
    bondNFT.createLock(_asset, _amount, _period, msg.sender);
}

function extendLock(uint _id, uint _amount, uint _period) public {
    address _asset = claim(_id);
    IERC20(_asset).transferFrom(msg.sender, address(this), _amount);
    bondNFT.extendLock(_id, _asset, _amount, _period, msg.sender);
}

function release(uint _id) public {
    (uint amount, uint lockAmount, address asset, address _owner) = bondNFT.release(_id, msg.sender);
    totalLocked[asset] -= lockAmount;
    IERC20(asset).transfer(_owner, amount);
}
```

Audit notes:

- `extendLock()` increases per-bond amount.
- It does not increase `totalLocked[asset]`.
- `release()` later decrements the aggregate.

MV-Scan/MV-Bench correspondence:

- `MV-Bench.xlsx` sheet `192`, row `3`, ablation `B0`, type `FP`.
- Finding: `[single_var_cross_tx] _idToBond tx-set -> extendLock(uint256,address,uint256,uint256,address), isExpired(uint256)`.
- Related True Positive row: sheet `192`, row `4`, ablation `B0`, type `TP`, `[multi_var_cross_contract] _idToBond, bondPaid tx-set -> extendLock(...), idToBond(uint256)`, linked to https://github.com/code-423n4/2022-12-tigris-findings/issues/170 (`[H-05]`).
- Relationship: no True Positive for H-01. MV-Scan sees `extendLock()`, but not the internal `Lock.totalLocked[asset]` aggregate missing update that causes release underflow.

## 9. 2021-05-visorfinance#h-02

Label: `SV-SI`

Sources:
- Code4rena report: https://code4rena.com/reports/2021-05-visorfinance#h-02-nft-transfer-approvals-are-not-removed-and-cannot-be-revoked-thus-leading-to-loss-of-nft-tokens
- Finding issue: https://github.com/code-423n4/2021-05-visorfinance-findings/issues/34
- Local code: `dataset/Web3Bugs/contracts/10/contracts/contracts/visor/Visor.sol`

```solidity
function approveTransferERC721(
  address delegate,
  address nftContract,
  uint256 tokenId
) external onlyOwner {
  nftApprovals[keccak256(abi.encodePacked(delegate, nftContract, tokenId))] = true;
}

function transferERC721(
    address to,
    address nftContract,
    uint256 tokenId
) external {
    if(msg.sender != _getOwner()) {
      require( nftApprovals[keccak256(abi.encodePacked(msg.sender, nftContract, tokenId))], "NFT not approved for transfer");
    }

    _removeNft(nftContract, tokenId);
    IERC721(nftContract).safeTransferFrom(address(this), to, tokenId);
}
```

Audit notes:

- Stale authorization, but not a relational-accounting invariant.

MV-Scan/MV-Bench correspondence:

- Closest row: `MV-Bench.xlsx` sheet `10contracts`, row `7`, ablation `B0`, type `TP`.
- Finding: `[multi_var_cross_contract] _locks, {_locks}, {_lockSet, _locks} tx-set -> getBalanceLocked(address), lock(address,uint256,bytes)`.
- Evidence link: https://github.com/code-423n4/2021-05-visorfinance-findings/issues/61.
- Relationship: False Negative. This is an unrelated same-repo True Positive. It concerns lock accounting, not stale ERC721 transfer approvals, so it should not be claimed as a True Positive for H-02.

## 10. 2021-05-visorfinance#h-03

Label: `SV-SI`

Sources:
- Code4rena report: https://code4rena.com/reports/2021-05-visorfinance#h-03-approval-for-nft-transfers-is-not-removed-after-transfer
- Finding issue: https://github.com/code-423n4/2021-05-visorfinance-findings/issues/48
- Local code: `dataset/Web3Bugs/contracts/10/contracts/contracts/visor/Visor.sol`

```solidity
function transferERC721(
    address to,
    address nftContract,
    uint256 tokenId
) external {
    if(msg.sender != _getOwner()) {
      require( nftApprovals[keccak256(abi.encodePacked(msg.sender, nftContract, tokenId))], "NFT not approved for transfer");
    }

    _removeNft(nftContract, tokenId);
    IERC721(nftContract).safeTransferFrom(address(this), to, tokenId);
}
```

Audit notes:

- This is the same stale approval variable after a transfer, and it is kept as `SV-SI`.

MV-Scan/MV-Bench correspondence:

- Closest row: `MV-Bench.xlsx` sheet `10contracts`, row `7`, ablation `B0`, type `TP`.
- Finding: `[multi_var_cross_contract] _locks, {_locks}, {_lockSet, _locks} tx-set -> getBalanceLocked(address), lock(address,uint256,bytes)`.
- Evidence link: https://github.com/code-423n4/2021-05-visorfinance-findings/issues/61.
- Relationship: False Negative. It does not cover `transferERC721()` failing to clear token-specific NFT approval, so it should not be claimed as a True Positive for H-03.

## 11. 2021-11-unlock#h-03

Label: `SV-SI`

Sources:
- Code4rena report: https://code4rena.com/reports/2021-11-unlock#h-03-mixintransfersoltransferfrom-wrong-implementation-can-potentially-allows-attackers-to-reverse-transfer-and-cause-fund-loss-to-the-users
- Finding issue: https://github.com/code-423n4/2021-11-unlock-findings/issues/182
- Local code: `dataset/Web3Bugs/contracts/54/smart-contracts/contracts/mixins/MixinTransfer.sol` and `dataset/Web3Bugs/contracts/54/smart-contracts/contracts/mixins/MixinKeys.sol`

```solidity
function transferFrom(
  address _from,
  address _recipient,
  uint _tokenId
) public onlyIfAlive hasValidKey(_from) onlyKeyManagerOrApproved(_tokenId) {
  Key storage fromKey = keyByOwner[_from];
  Key storage toKey = keyByOwner[_recipient];

  uint previousExpiration = toKey.expirationTimestamp;

if (toKey.tokenId == 0) {
  toKey.tokenId = _tokenId;
  _recordOwner(_recipient, _tokenId);
  // Clear any previous approvals
  _clearApproval(_tokenId);
}

if (previousExpiration <= block.timestamp) {
  toKey.expirationTimestamp = fromKey.expirationTimestamp;
  toKey.tokenId = _tokenId;

  // Reset the key Manager to the key owner
  _setKeyManagerOf(_tokenId, address(0));

  _recordOwner(_recipient, _tokenId);
}
```

Audit notes:

- In the `toKey.tokenId == 0` branch, ownership is recorded but key manager reset is not applied.
- Stale key-manager authority leads to this bug.

MV-Scan/MV-Bench correspondence:

- `MV-Bench.xlsx` sheet `54smart-contracts`, row `4`, ablation `B0`, type `FP`.
- Finding: `[single_var_cross_tx] locks tx-set -> createLock(bytes), recordKeyPurchase(uint256,address)`.
- Relationship: classified as False Negative. There is an unrelated same-repo False Positive. MV-Bench has no row for stale `keyManagerOf[tokenId]` after `transferFrom()`, so no True Positive can be claimed for H-03.

## 12. 2021-11-unlock#h-04

Label: `SV-SI`

Sources:
- Code4rena report: https://code4rena.com/reports/2021-11-unlock#h-04-approvals-not-cleared-after-key-transfer
- Finding issue: https://github.com/code-423n4/2021-11-unlock-findings/issues/160
- Local code: `dataset/Web3Bugs/contracts/54/smart-contracts/contracts/mixins/MixinTransfer.sol` and `dataset/Web3Bugs/contracts/54/smart-contracts/contracts/mixins/MixinKeys.sol`

```solidity
if (previousExpiration <= block.timestamp) {
  toKey.expirationTimestamp = fromKey.expirationTimestamp;
  toKey.tokenId = _tokenId;

  // Does not clear approval if keyManagerOf[_tokenId] was already address(0)
  _setKeyManagerOf(_tokenId, address(0));

  _recordOwner(_recipient, _tokenId);
}

function _setKeyManagerOf(uint _tokenId, address _keyManager) internal {
  if (keyManagerOf[_tokenId] != _keyManager) {
    keyManagerOf[_tokenId] = _keyManager;
    _clearApproval(_tokenId);
    emit KeyManagerChanged(_tokenId, address(0));
  }
}

function _clearApproval(
  uint256 _tokenId
) internal
{
  if (approved[_tokenId] != address(0)) {
    approved[_tokenId] = address(0);
  }
}
```

Audit notes:

- `_clearApproval()` is guarded by a key-manager change.
- A stale single-token approval can stay live.

MV-Scan/MV-Bench correspondence:

- `MV-Bench.xlsx` sheet `54smart-contracts`, row `4`, ablation `B0`, type `FP`.
- Finding: `[single_var_cross_tx] locks tx-set -> createLock(bytes), recordKeyPurchase(uint256,address)`.
- Relationship: False Negative. There is an unrelated same-repo False Positive. MV-Bench has no row for stale `approved[tokenId]`/`_clearApproval()` after key transfer.

## 13. 2022-07-ens#h-02

Label: `MV-SI`

Sources:
- Code4rena report: https://code4rena.com/reports/2022-07-ens#h-02-the-expiry-of-the-parent-node-can-be-smaller-than-the-one-of-a-child-node-violating-the-guarantee-policy
- Finding issue: https://github.com/code-423n4/2022-07-ens-findings/issues/187
- ENS expiry docs: https://docs.ens.domains/wrapper/expiry/
- Local code: `dataset/Web3Bugs/contracts/145/contracts/wrapper/NameWrapper.sol`

```solidity
function unwrap(
    bytes32 parentNode,
    bytes32 labelhash,
    address newController
) public override onlyTokenOwner(_makeNode(parentNode, labelhash)) {
    if (parentNode == ETH_NODE) {
        revert IncompatibleParent();
    }
    _unwrap(_makeNode(parentNode, labelhash), newController);
}

function _unwrap(bytes32 node, address newOwner) private {
    // Burn token and fuse data
    _burn(uint256(node));
    ens.setOwner(node, newOwner);

    emit NameUnwrapped(node, newOwner);
}

function setSubnodeOwner(
    bytes32 parentNode,
    string calldata label,
    address newOwner,
    uint32 fuses,
    uint64 expiry
) public onlyTokenOwner(parentNode) returns (bytes32 node) {
    bytes32 labelhash = keccak256(bytes(label));
    node = _makeNode(parentNode, labelhash);
    (, , expiry) = _getDataAndNormaliseExpiry(parentNode, node, expiry);

    if (ens.owner(node) != address(this)) {
        ens.setSubnodeOwner(parentNode, labelhash, address(this));
        _addLabelAndWrap(parentNode, node, label, newOwner, fuses, expiry);
    } else {
        _transferAndBurnFuses(node, newOwner, fuses, expiry);
    }
}

function _getDataAndNormaliseExpiry(
    bytes32 parentNode,
    bytes32 node,
    uint64 expiry
)
    internal
    view
    returns (address owner, uint32 fuses, uint64)
{
    uint64 oldExpiry;
    (owner, fuses, oldExpiry) = getData(uint256(node));
    (, , uint64 maxExpiry) = getData(uint256(parentNode));

    expiry = _normaliseExpiry(expiry, oldExpiry, maxExpiry);
    return (owner, fuses, expiry);
}

function _normaliseExpiry(
    uint64 expiry,
    uint64 oldExpiry,
    uint64 maxExpiry
) internal pure returns (uint64) {
    if (expiry > maxExpiry) {
        expiry = maxExpiry;
    }
    if (expiry < oldExpiry) {
        expiry = oldExpiry;
    }
    return expiry;
}
```

Audit notes:

- Parent and child expiry form a hierarchy invariant.
- Unwrapping drops parent expiry state while child state remains.

MV-Scan/MV-Bench correspondence:

- `MV-Bench.xlsx` sheet `145`, row `3`, ablation `B0`, type `FP`.
- Finding: `[multi_var_cross_contract] expiries, {GRACE_PERIOD, TMP_1342, expiries} tx-set -> available(uint256), renew(uint256,uint256)`.
- Relationship: False Negative. It is about registrar expiry availability/renewal, not `NameWrapper` parent/child wrapped-node expiry after unwrap/rewrap, so no TP can be claimed for H-02.

## 14. 2022-01-behodler#h-04

Label: `MV-SI`

Sources:
- Code4rena report: https://code4rena.com/reports/2022-01-behodler#h-04-logic-error-in-burnflashgovernanceasset-can-cause-locked-assets-to-be-stolen
- Finding issue: https://github.com/code-423n4/2022-01-behodler-findings/issues/305
- Local code: `dataset/Web3Bugs/contracts/78/contracts/DAO/FlashGovernanceArbiter.sol`

```solidity
function assertGovernanceApproved(
  address sender,
  address target,
  bool emergency
) public {
  if (
    IERC20(flashGovernanceConfig.asset).transferFrom(sender, address(this), flashGovernanceConfig.amount) &&
    pendingFlashDecision[target][sender].unlockTime < block.timestamp
  ) {
    pendingFlashDecision[target][sender] = flashGovernanceConfig;
    pendingFlashDecision[target][sender].unlockTime += block.timestamp;
  } else {
    revert("LIMBO: governance decision rejected.");
  }
}

function burnFlashGovernanceAsset(
    address targetContract,
    address user,
    address asset,
    uint256 amount
) public virtual onlySuccessfulProposal {
    if (pendingFlashDecision[targetContract][user].assetBurnable) {
      Burnable(asset).burn(amount);
    }

    pendingFlashDecision[targetContract][user] = flashGovernanceConfig;
}

function withdrawGovernanceAsset(address targetContract, address asset) public virtual {
    require(
      pendingFlashDecision[targetContract][msg.sender].asset == asset &&
        pendingFlashDecision[targetContract][msg.sender].amount > 0 &&
        pendingFlashDecision[targetContract][msg.sender].unlockTime < block.timestamp,
      "Limbo: Flashgovernance decision pending."
    );
    IERC20(pendingFlashDecision[targetContract][msg.sender].asset).transfer(
      msg.sender,
      pendingFlashDecision[targetContract][msg.sender].amount
    );
    delete pendingFlashDecision[targetContract][msg.sender];
}
```

Audit notes:

- A user-specific pending decision record is reset to default/withdrawable config rather than getting deleted.
- It then reaches a transfer sink.

MV-Scan/MV-Bench correspondence:

- `MV-Bench.xlsx` sheet `78`, row `6`, ablation `B0`, type `TP`.
- Finding: `[multi_var_cross_contract] pendingFlashDecision, {flashGovernanceConfig, pendingFlashDecision} tx-set -> burnFlashGovernanceAsset(address,address,address,uint256), withdrawGovernanceAsset(address,address)`.
- Comments: `[H-04]`.
- Relationship: True Positive. Same repo, state group, burn/reset desynchronization, and withdrawal transfer sink.

## 15. 2021-08-yield#h-02

Label: `SV-SI`

Sources:
- Code4rena report: https://code4rena.com/reports/2021-08-yield#h-02-erc20rewards-returns-wrong-rewards-if-no-tokens-initially-exist
- Finding issue: https://github.com/code-423n4/2021-08-yield-findings/issues/28
- Fix commit referenced by report: https://github.com/yieldprotocol/yield-utils-v2/commit/d2ad343f40d375baf492131d9b1c7e288b5825d6
- Local code: `dataset/Web3Bugs/contracts/25/contracts/utils/token/ERC20Rewards.sol`

```solidity
function _updateRewardsPerToken() internal returns (uint128) {
    RewardsPerToken memory rewardsPerToken_ = rewardsPerToken;
    RewardsPeriod memory rewardsPeriod_ = rewardsPeriod;

    // We skip the calculations if we can
    if (_totalSupply == 0 || block.timestamp.u32() < rewardsPeriod_.start) return 0;
    if (rewardsPerToken_.lastUpdated >= rewardsPeriod_.end) return rewardsPerToken_.accumulated;

    // Find out the unaccounted period
    uint32 end = earliest(block.timestamp.u32(), rewardsPeriod_.end);
    uint256 timeSinceLastUpdated = end - rewardsPerToken_.lastUpdated;

    rewardsPerToken_.accumulated =
        (rewardsPerToken_.accumulated + 1e18 * timeSinceLastUpdated * rewardsPerToken_.rate / _totalSupply).u128();
    rewardsPerToken_.lastUpdated = end;
    rewardsPerToken = rewardsPerToken_;
}
```

Audit notes:

- The stale value is the single reward checkpoint `rewardsPerToken_.lastUpdated`, so it is `SV-SI`.

MV-Scan/MV-Bench correspondence:

- `MV-Bench.xlsx` sheet `25`, row `6`, ablation `B0`, type `ZD`.
- Finding: `[single_var_cross_tx] auctions tx-set -> auction(bytes12), payAll(bytes12,uint128)`.
- Comments: `payAll doesn't delete the auction entry, so a fully-repaid vault remains permanently auctioned and cannot be re-auctioned.`
- Relationship: unrelated same-repo zero-day. MV-Bench has no row for `ERC20Rewards._updateRewardsPerToken()` failing to advance `rewardsPerToken_.lastUpdated` when `totalSupply == 0`, so no True Positive can be claimed for H-02.
