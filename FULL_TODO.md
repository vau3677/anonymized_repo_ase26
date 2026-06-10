**Paper defense:** MV-SI is a DeFi/EVM-specific specialization of broader inconsistent-state-update and multi-variable correlation bugs. MV-Scan is the first scalable static triage approximation specialized for that setting. Evaluation rigor stems from detector-output labeling and an independent known-bug oracle.

- Remove “random selection” language
- add annotation reliability
- distinguish TP/oracle/PoC evidence
- add a simple toy example before Vader
- and explicitly model the paper after the successful Nyx pattern: formalize the logical/exploitability oracle first, then present the analyzer as an approximation. Nyx is a useful template because it distinguishes raw data races from exploitable front-running using an independent vulnerability definition and validation oracle, rather than treating every race as a vulnerability.

- Paper thesis: MV-SI is not a wholly new phenomenon in computer science. It is a structured DeFi/EVM specialization of inconsistent-state-update and multi-variable correlation bugs. The novelty is the EVM-specific formulation, state namespace, static triage approximation, oracle, taxonomy, and empirical validation on audited, high-stakes DeFi protocols.
  * We do not prove all MV-SI bugs. We provide a scalable static triage approximation for a hard logical-bug subclass, release a labeled output corpus, and validate the approximation with an independent strict known-bug oracle.

- The current oracle README/NEXT_STEPS language says the Web3Bugs complement came from a random subset or randomly chosen repositories. That is a reviewer trap! The oracle README currently says the complement investigated additional High/Medium Code4rena findings from a random subset of evaluated Web3Bugs repositories until reaching the 30-MV-SI-label goal.  The readiness check also lists the randomly chosen repositories and says the team randomly selected repos from the evaluated corpus. We just need to reframe the selection protocol:
  * In the paper, replace "random subset" with “repository-level complement audit":
    ```latex
    Because the TOSEM-overlap seed produced fewer than 30 MV-SI cases, we complemented it with a repository-level audit of High/Medium Code4rena findings from evaluated Web3Bugs repositories. The complement was constructed before aggregating strict B0 outcomes and was labeled using the same semantic schema as the TOSEM overlap. We included all High/Medium findings in each selected repository rather than selecting individual findings conditional on MV-Scan output.
    ```
  * In the artifact README:
    ```markdown
    ### Web3Bugs/Code4rena complement

    Because the TOSEM seed-overlap pass produced fewer than 30 MV-SI cases, we added a repository-level complement from evaluated Web3Bugs repositories with complete Code4rena reports and corresponding MV-Bench sheets. For each selected repository, we reviewed all High/Medium findings under the same semantic schema used for the TOSEM overlap. Selection and labeling were performed before computing the final strict B0 recall headline, and no individual finding was included or excluded based on whether B0 matched it.
    ```
  * Then we list the six repos as **complement repositories**, not "randomly chosen repositories." If a reviewer asks why these six, the answer is: they were evaluated MV-Bench repositories with complete Code4rena reports and sufficient High/Medium logical-bug density to raise the independent MV-SI denominator above 30. The unit of complement selection was the repository/report, and all High/Medium findings were labeled under the same schema.
  * Do not claim statistical randomness unless you can provide population, seed, sampling procedure, stopping rule, and non-response handling.


- The perception difference between having and not having reliability is large. The oracle README says the strict oracle is complete, but the annotation-reliability package is incomplete: two-pass labels, adjudication records, agreement statistics, Cohen’s kappa, zero-day confirmation, and B0 TP/FP sample audit remain unfinished.
  * At minimum, use 3 human-audited reliability slices:
    | Slice            | Required action                                          | Paper result                                   |
    | ---------------- | -------------------------------------------------------- | ---------------------------------------------- |
    | Known-bug oracle | 2 independent human labels for all 114 known-bug rows  | agreement and Cohen’s kappa and adjudicated labels |
    | Zero-days        | 2 independent confirmations for all 9 ZD candidates | agreement and PoC/vendor/evidence status         |
    | B0 label sample  | stratified sample of B0 TP/FP/ZD labels                  | agreement and kappa or raw agreement             |
  * Paper-ready text:
    ```latex
    \PP{Annotation Reliability}
    Two authors independently labeled the known-bug oracle under the MV-SI semantic schema. Disagreements were adjudicated through discussion and resolved into a final label. We separately performed two-pass confirmation for all zero-day candidates and a stratified reliability audit of B0 TP/FP labels. We report raw agreement, Cohen's kappa, and adjudication counts.
    ```

- A strong distinction between TP and oracle verification is whether there exists a PoC. Add fields to oracle and zero-day tables:
    * ```text
      poc_status:
      source_poc
      author_poc
      exploit_sketch_only
      no_poc_but_report_evidence
      not_applicable  
      
      vendor_status:
      acknowledged
      disputed
      no_response
      not_disclosed
      archived_snapshot_only
      ```
  * Then we define the label tiers:
    ```latex
    \PP{Evidence Tiers}
    A TP is a manually validated detector-output bucket that corresponds to a real semantic desynchronization under our labeling protocol. A ZD is a previously unreported TP in the evaluated project version with author PoC evidence or an independently checkable exploit sketch showing security or economic impact. Vendor acknowledgment is reported separately and is not required for the TP label.
    ```
  * Good zero-day wording:
    ```latex
    Across all ablations, \sys surfaced nine high-impact zero-day candidates validated by author review and PoC or exploit-sketch evidence; five were vendor-acknowledged at submission time.
    ```

- The strict recall table is the evaluation anchor: 114 reviewed known bugs, 31 MV-SI denominator rows, 6 strict B0 matches, strict recall 6/31 = 0.194.  The strict B0 audit gives the paper-facing table: TOSEM overlap 1/9, Web3Bugs/Code4rena complement 5/22, combined 6/31. Main paper should report only strict recall.
  * Paper-ready text:
    ```latex
    \PP{Strict Known-MVSI Recall}
    Full ecosystem recall is not measurable without manually enumerating all latent MV-SI defects in the corpus. We therefore report strict known-MVSI recall over an independent oracle. A B0 bucket strictly matches a known bug only when it comes from the same evaluated repository, represents the same violated invariant or a direct specialization, contains at least one coupled state entity or external proxy from the oracle case, identifies at least one writer, reader, or transaction step from the known trace, and reaches the same class of protocol decision. Under this conservative rule, B0 matches 6/31 known MV-SI cases.
    ```
  * A useful paper-ready table:
    ```latex
    \begin{table}[t]
    \centering
    \caption{Strict known-MVSI recall over the independent oracle.}
    \label{tab:strict-recall}
    \begin{tabular}{lrrr}
    \toprule
    Source pool & MV-SI denom. & Strict B0 matches & Strict recall \\
    \midrule
    TOSEM overlap & 9 & 1 & 11.1\% \\
    Web3Bugs/Code4rena complement & 22 & 5 & 22.7\% \\
    Combined independent oracle & 31 & 6 & 19.4\% \\
    \bottomrule
    \end{tabular}
    \end{table}
    ```
  * ```latex
    This result is conservative. The strict criterion does not count adjacent diagnostic buckets as recall matches. The result therefore quantifies the limitations of the frozen static approximation: many known MV-SI bugs require invariant evidence that is not exposed through predicate co-use, shallow multi-return summaries, supported external selectors, or the current sink-context model.
    ```

- The paper must explicitly show that TOSEM is broader and MV-SI is narrower:
    ```latex
    \begin{table}[t]
    \centering
    \caption{TOSEM-overlap relabeling under the MV-SI semantic schema.}
    \label{tab:tosem-alignment}
    \begin{tabular}{lr}
    \toprule
    Adjudicated label & Cases \\
    \midrule
    MV-SI & 9 \\
    SV-SI / same-variable & 6 \\
    ISU-other & 0 \\
    Other / not applicable & 0 \\
    \bottomrule
    \end{tabular}
    \end{table}
    ```
  * ```latex
    TOSEM studies the broader inconsistent-state-update family, while MV-SI is a stricter DeFi/EVM specialization requiring a relational invariant over at least two coupled state entities and a security- or economic-relevant sink.
    ```

- Section 2 needs a toy example before Vader: Vader is impactful but too complex as the first explanation. Add a small toy example where each variable is locally valid but the invariant fails.
  * In Background before Vader:
    ```latex
    \begin{listing}[t]
    \begin{minted}[fontsize=\scriptsize,breaklines]{solidity}
    mapping(address => uint256) balance;
    mapping(address => uint256) votingPower;

    function deposit(uint256 x) external {
        balance[msg.sender] += x;
        votingPower[msg.sender] += x;
    }

    function withdraw(uint256 x) external {
        require(balance[msg.sender] >= x);
        balance[msg.sender] -= x;
        transfer(msg.sender, x);
        // BUG: votingPower[msg.sender] is not reduced.
    }

    function vote(uint256 proposal) external {
        require(votingPower[msg.sender] > 0);
        votes[proposal] += votingPower[msg.sender];
    }
    \end{minted}
    \caption{Toy MV-SI example. Each storage operation is locally valid, but
    the relational invariant $\texttt{votingPower[u]}=\texttt{balance[u]}$
    is violated before a governance sink.}
    \label{lst:toy-mvsi}
    \end{listing}
    ```
  * ```latex
    `withdraw` correctly checks and updates `balance`, and `vote` correctly checks `votingPower`. A missing synchronization between two semantically coupled state entities before a governance decision creates this bug. We illustrate why MV-SI is a logical-bug subclass rather than a syntactic race pattern.
    ```
  * Then Vader becomes the real-world motivating example.

- The 5-criteria litmus test should appear twice: (I) Section 3: semantic definition of MV-SI and (II) Evaluation: oracle labeling protocol.
  * ```latex
    \begin{definition}[MV-SI]
    A known bug or detector finding is labeled MV-SI iff: (i) there exist $n \ge 2$ semantically coupled state entities
    $v_1,\ldots,v_n$; (ii) the coupling is justified by an independent source, such as a protocol invariant, bug report, accounting equation, documentation, code comment, team note, PoC, or vendor confirmation; (iii) an execution path updates, advances, invalidates, or consumes one constituent without synchronizing at least one required counterpart; (iv) the stale or inconsistent counterpart reaches a security- or economically relevant sink, such as a branch predicate, external call, storage write, accounting update, mint, burn, transfer, liquidation, vote, emission, reward, or access decision; and (v) the defect is not reducible to same-variable stale read, reentrancy, ordinary missing access control, or arithmetic error.
    \end{definition}
    ```
  * Then bridge to detector:
    ```latex
    This definition is semantic and evidence-based. \sys does not prove all five conditions statically. Instead, it approximates them using state access grouping, mapping-slot normalization, selected external-state wrappers, user-callable reachability, and bounded sink-context reachability.
    ```
  * The oracle schema already supports this structure with fields for semantic label, invariant, coupled entities, primary/counterpart state, external proxy state, desynchronization step, sink type, impact type, attacker model, and strict match.

- We show that heuristics are derived from the bug definition. Section 4 must explicitly map semantic criteria to static approximations:
    ```latex
    \begin{table*}[t]
    \centering
    \caption{Mapping the semantic MV-SI definition to \sys's static approximation.}
    \label{tab:semantic-to-static}
    \begin{tabular}{p{0.23\linewidth}p{0.34\linewidth}p{0.34\linewidth}}
    \toprule
    Semantic criterion & Static approximation in \sys & Known limitation \\
    \midrule
    Coupled state entities & Predicate co-use groups, shallow multi-return summaries,
    mapping-slot abstraction, selected external-state wrappers &
    Implicit economic invariants may not appear syntactically. \\
    Independent invariant evidence & Used by oracle labeling, not by detector &
    Detector can only propose candidates; manual validation supplies evidence. \\
    Partial update or consumption & Writer/read candidate tuples over state-access maps &
    Path feasibility and transaction sequencing are approximated. \\
    Security/economic sink & Bounded sink-context reachability over branches, calls, and
    write-bearing blocks &
    Not full value dependence or exploitability proof. \\
    Not reducible to SV-SI/reentrancy/access/arithmetic & Human semantic labeling &
    Detector bucket kind is not the final semantic label. \\
    \bottomrule
    \end{tabular}
    \end{table*}
    ```

**Code-faithful Section 4 fixes**

- Still not completely finished changing all references of SDG/SAG to state-annotated ICFG. The implementation file and all the references towards it should be renamed from `sdg.py` to `icfg.py`. It defines mapping-slot variables, external wrappers, per-block read/write maps, CFG successor edges, and call/return approximations.
  * ```latex
    The implementation module for the state-annotated ICFG stores CFG-node blocks, successor edges, approximated call/return edges, and per-block read/write metadata.
    ```
- The code represents mapping accesses as `(base, canonical key expression)`, with syntactic equality/hashing. 
  * ```latex
    Mapping slots are represented as $\langle base,key\rangle$, where $key$ is a canonicalized expression string. Equality is syntactic; \sys does not use an SMT solver to prove key equivalence.
    ```
- External selectors: the code uses fixed selector tables: read-like selectors include `balanceOf`, `totalSupply`, and `lastBalance`; write-like selectors include `transfer`, `transferFrom`, `mint`, `burn`, and `sync`. 
  * ```latex
    External-state wrapping is selector-table-based. We wrap selected common DeFi/ERC-20-style selectors; unsupported selectors may therefore cause false negatives.
    ```
- Alias precision: the alias registry key includes address, selector, and caller contract context, while the external wrapper itself is selector/address-based.
  * ```latex
    Wrapper creation uses caller context for attribution, but proxy equality is selector/address-based. This favors aggregation and scalability over argument-sensitive external-state precision.
    ```
- Sink gate: The code’s B0 sink test is not full value propagation. It checks branch, call, or write-bearing blocks where the tracked state is read and reachable without overwrite.
  * ```latex
    The sink-context gate is topological and overwrite-aware, and never proves that the stale value causes the downstream behavior.
    ```
- B5: The code returns false immediately when budget is zero. ```B5 disables forward sink propagation. It is not a same-node sink baseline.```
- The paper reports Type III configuration risks, but B0 filters admin-write/public-read pairs by defaultm so we use a two-mode framing:
  * ```latex
    \PP{Threat Model Modes}
    The B0 configuration targets unprivileged exploitability. It therefore suppresses admin-write/public-read pairs when the writer is heuristically classified as role-gated or owner-gated. We report B0 zero-day claims only under this unprivileged-exploit mode.

    Configuration/governance risks are analyzed separately. These cases remain security-relevant when privileged or governance actors can desynchronize protocol state, but they are not mixed into B0's unprivileged zero-day count.
    ```
  * | Mode      | Admin-write/public-read pairs | Main use  |
    | ---------------- | ------------- | ------ |
    | B0 unprivileged-exploit mode | filtered | default evaluation and zero-day count |
    | governance-risk mode | retained | Type III configuration-risk analysis / appendix / artifact |
- Many validated positives are `single_var_cross_tx`, so we should make clear that:
  * ```latex
    The emitted bucket kind is an implementation-level witness type, not the semantic oracle label. A \cc{single\_var\_cross\_tx} bucket can still correspond to an MV-SI bug when the violated invariant couples the tracked state to additional protocol state established by independent evidence. Conversely, a syntactically multi-variable bucket is not labeled MV-SI unless the semantic criteria are satisfied.
    ```

- The frozen ablation results look a bit odd, but are 100% right if we break down what is going on here. So TP was originally distinct from ZD, so when we reported TP as X and ZD as Y, we were distinguishing them in classification. But upon the first draft of our paper, we realized that TP must be counting ZD, so TP is really TP+ZD. Thus, the following table is technically correct by our benchmark, but the paper must additionally add ZD to TP when reporting TP (e.g. B0 has 335 TP of which 7 are ZD, B1 has 340 TP of which 8 are ZD):
  * | Config | Raw rows | Scored buckets |  TP | ZD |  FP | Precision |
    | ------ | -------: | -------------: | --: | -: | --: | --------: |
    | B0     |    1,592 |          1,111 | 328 |  7 | 776 |    30.15% |
    | B1     |    1,637 |          1,141 | 332 |  8 | 801 |    29.80% |
    | B2     |    1,628 |          1,149 | 324 |  7 | 818 |    28.81% |
    | B3     |    1,765 |          1,237 | 354 |  6 | 877 |    29.10% |
    | B4     |      689 |            410 | 152 |  0 | 258 |    37.07% |
    | B6     |    1,619 |          1,133 | 318 |  8 | 807 |    28.77% |
  * ```latex
    Across the nonzero-output configurations, the frozen artifact contains 8,930 raw rows. After applying the exclusion protocol, 6,181 scored buckets remain. Alarm counts refer to scored buckets.
    ```
  * ```latex
    B0 emits 1,592 raw rows and 1,111 scored buckets. Among scored B0 buckets, 335 are TP of which 7 are ZD, and 776 are FP, yielding 30.15\% precision.
    ```
  * ```latex
    B5 appears in the runtime and union-coverage summaries but has zero scored buckets because the zero-budget configuration disables forward sink propagation.
    ```

- If space allows, we add by-kind precision as it is genuinely impressive:
  * | B0 bucket kind             | Scored | Positive | Precision |
    | -------------------------- | -----: | -------: | --------: |
    | `multi_var_cross_contract` |    361 |      145 |    40.17% |
    | `single_var_cross_tx`      |    750 |      190 |    25.33% |
  * ```latex
    Within B0, cross-contract MV-SI buckets are denser than cross-transaction, SV-SI witnesses: 145/361 = 40.2\% versus 190/750 = 25.3\%. This supports the state-access namespace design while also reinforcing why detector bucket kind must remain separate from the semantic MV-SI label.
    ```
  * Vlad note: (?) It *may* potentially also be inferred from the data that the heuristics used to identify MV-SI are distinct from the heuristics required to identify SV-SI.

- FN categories should align with the actual oracle, so this is for the paper:
  * | Category    | Meaning                                                  |
    | ----------- | -------------------------------------------------------- |
    | FN0         | No same-finding candidate row produced by B0             |
    | FN1         | Same finding appears only in non-B0 ablations            |
    | FN2         | Symbolic key mismatch or key abstraction miss            |
    | FN3         | External selector not recognized by wrapper table        |
    | FN4         | Relevant path pruned as admin/init under B0 threat model |
    | FN5         | Stale value does not reach current sink-context model    |
    | FN6         | Compilation or Slither modeling limitation               |
    | FN7         | Adjacent bucket found but not a strict match             |
  * ```latex
    We miss known MV-SI cases when the true coupling is visible in the protocol logic, but not in our detector's modeled static patterns. In the strict audit, some misses have no same-finding B0 bucket, some are found only by non-B0 ablations, and some produce adjacent diagnostic buckets that do not satisfy the strict invariant/path/sink rule. These misses are expected for logical bugs whose coupling may be encoded in protocol economics, documentation, or multi-step accounting rather than directly visible in the state-annotated ICFG.
    ```
- Add a concise FP taxonomy from B0 sample audit once you complete reliability. Suggested categories are:
  * | FP category          | Description                                                |
    | -------------------- | ---------------------------------------------------------- |
    | semantic masking     | downstream guard/oracle prevents exploitability            |
    | bucket pollution     | valid and irrelevant state accesses merged into one bucket |
    | key imprecision      | syntactic key abstraction cannot prove/disprove equality   |
    | external abstraction | selector/address abstraction merges or misses remote state |
    | admin/init mismatch  | outside unprivileged attacker model or setup-only          |
    | adjacent evidence    | detector finds related state but not violated invariant    |
    | non-economic use     | stale read reaches logging/view/non-impact context         |
  * ```latex
    False positives are not dominated by one failure mode. They arise from semantic masking, bucket pollution, syntactic key limitations, argument-insensitive external-state wrappers, admin/init threat-model boundaries, adjacent-but-nonviolating state evidence, and non-economic uses that survive the sink-context gate.
    ```

- Updating related work should be a clean thing to do:
  * VLAD: I like how we already did the Related Work section because it is so dense and covers so much prior work, so we should be VERY careful about this. I think maybe we should only add exactly what we're missing and keep everything else the same.
  * ```latex
    \PP{Classic Multi-Variable Inconsistency}
    Multi-variable access correlations and inconsistent updates are a long-studied phenomenon (cite:MUVI). \sys studies EVM contracts which expose persistent keyed storage, public transaction entrypoints, gas-induced lazy synchronization, cross-contract proxy state, and economic/security sink decisions.
    ```
  * *Database and Cache Consistency* lineage must be articulated/cited carefully.
- Phrases to eliminate/replace:
  * | Current phrase  | Replace with |
    | ----- | --- |
    | “randomly selected repositories”         | “repository-level complement audit” |
    | “ground truth benchmark”                 | “labeled output corpus” |
    | “recall omitted”                         | “full recall infeasible; strict known-MVSI recall reported” |
    | “confirmed exploitable zero-days”        | “high-impact zero-day candidates validated by author review/PoC evidence; five vendor-acknowledged” |
    | “580 unique vulnerabilities”             | “580 manually validated positive output buckets” |
    | “dynamic fuzzing completely ineffective” | “generic static rules and unguided fuzzing are unlikely to expose MV-SI without a relational invariant or focused state-space guide” |
    | “semantic value propagation”             | “sink-context reachability” |
    | “same-site sink baseline”                | “zero-propagation ablation” |
    | “MV-SI is a new class”                   | “MV-SI is a DeFi/EVM-specific specialization within the broader inconsistent-state-update family” |
    
# **Attacker responses:**

1. “This is TOSEM renamed.”

```text
TOSEM studies inconsistent-state updates broadly. We relabel its overlap
under our stricter semantic schema and find both MV-SI and SV-SI cases.
MV-SI is a DeFi/EVM specialization with a specific detector, oracle,
state namespace, taxonomy, sink model, and a unique gas constraint that incentivizes this behavior.
```

2. “Your benchmark is circular.”

```text
MV-Bench is a labeled output corpus for precision and ablation behavior. Strict recall is measured on
a separate known-bug oracle that starts from TOSEM/Web3Bugs/Code4rena bugs.
```

3. “Recall is low.”

```text
Correct. B0 strictly recalls 6/31 known MV-SI cases. We report this as a conservative lower-bound measurement for a scalable static triage configuration. The miss analysis identifies concrete limitations of the current approximation.
```

4. “The sink gate is not value dependence.”

```text
Correct. The paper describes it as bounded sink-context reachability. It is not a full value-dependence proof or exploitability validation.
```

5. “Why no direct SOTA comparison?”

```text
Existing tools target different definitions. We avoid unfair head-to-head precision/recall comparison and instead provide related-work positioning, ablation, labeled-output precision, runtime context, and independent strict known-bug recall.
```

6. “Random repository selection biases the oracle.”

```text
The paper does not present the complement as statistical random sampling. It is a repository-level complement audit over evaluated repositories with complete reports, labeled under the same schema and before final strict B0 aggregation. All High/Medium findings in these additional repositories are included.
```

# Repass + New stuff

**Core thesis:** MV-Scan is a scalable static triage detector for DeFi/EVM multi-variable state desynchronization. It does not prove protocol invariants, complete path feasibility, or semantic exploitability. It approximates MV-SI by constructing a state-annotated ICFG, normalizing state accesses into a shared namespace, inferring candidate relational groups, enumerating writer/read candidates, and retaining those that survive pruning and sink-context reachability.

The current manuscript says B5 tests whether the stale read itself functions as a same-site critical sink. The code does not implement that experiment. In `value_influence_hits_sensitive_sink`, `budget == 0` returns `False` before the same-node sink check. The same structure exists in the same-var sink helper. 

The current paper text says B5 “tests whether the stale read itself functions simultaneously as a critical sink without traversing the annotated ICFG,” then interprets B5’s zero findings as proof that MV-SI is not local. 

### Fix

Do not call B5 a same-node sink baseline. Call it a **zero-propagation ablation**.

Paper-ready replacement:

```latex
\PP{Zero-Propagation Ablation (B5)}
B5 sets the traversal budget to zero and therefore disables forward
sink propagation in the frozen \sys pipeline. This configuration is
not intended to estimate the prevalence of same-node sink uses.
Rather, it isolates the contribution of positive-depth propagation:
without allowing a candidate read to reach any downstream
security or accounting context, the detector emits no scored
findings. The contrast between B5 and B0 therefore shows that
\sys's positive findings depend on positive-depth traversal over the
state-annotated ICFG, rather than on local stale-read patterns alone.
```

Replace:

> “empirically proves that annotated-ICFG traversal is mandatory”

with:

> “shows that MV-Scan’s positive findings depend on positive-depth traversal over the state-annotated ICFG.”

That wording is faithful and still strong.

---

## P0.2 — Rename “Value Sink” to “sink-context reachability”

### Reviewer attack

The paper says B0 “traces whether the corrupted value propagates into critical operations,” including indirect flow through entangled variables. 

The code is more modest. It checks whether the tracked variable is read in a branch, call, or write-bearing block reachable from the candidate read without an intervening overwrite. It does not prove unique causation, full value dependence, symbolic path feasibility, or semantic exploitability. 

### Fix

Replace every “Value Sink” label with:

> **Sink-Context Reachability**

Replace “semantic value sink filtering” with:

> **bounded sink-context reachability**

Replace “value propagates” with:

> **the same tracked state remains observable at a downstream critical context**

Paper-ready replacement:

```latex
\PP{Sink-Context Reachability}
B0 applies a lightweight sink-context gate over \sys's
state-annotated ICFG. Starting from a candidate read block, \sys
performs bounded forward traversal over the annotated successor
relation and retains the candidate when the tracked state is read
again in a security- or accounting-relevant context, such as a branch
predicate, a high-level or internal call site, or a write-bearing block
recognized by Slither's variable-write or IR-lvalue metadata. The
path must be overwrite-free with respect to the tracked state. For
mapping-slot candidates, a read of the base mapping is treated as
compatible evidence for the tracked slot, reflecting Slither's
mixed-granularity exposure of mapping accesses. This gate is a
static triage filter over observable downstream use; it is not a proof
that the stale value uniquely causes the downstream behavior.
```

Then Table 2 should say:

| Config | Heuristic                       |
| ------ | ------------------------------- |
| B3     | No sink gate                    |
| B4     | Same-variable sink-context gate |
| B0     | Sink-context reachability       |

Do not use “semantic Value Sink.” That phrase invites an implementation-faithfulness attack.

- The output corpus contains many findings whose detector bucket is `single_var_cross_tx`. A reviewer may say: “Your benchmark is supposedly MV-SI, but many positives are single-variable.”
- This is especially dangerous because the current paper says MV-Scan shifts from single-variable safety to multi-variable semantic consistency. 
- The bucket kind is an **implementation witness class**, not the final semantic label. A semantic MV-SI can be surfaced through a single tracked storage variable when the relational invariant is supplied by branch groups, multi-return summaries, oracle evidence, or manual semantic validation. The code explicitly classifies emitted buckets as `single_var_cross_tx`, `multi_var_intra_contract`, or `multi_var_cross_contract` based on bucket structure. 
  * ```latex
    \PP{Detector Bucket Kind vs. Semantic Label}
    The emitted bucket kind is an implementation-level witness type,
    not the semantic oracle label. A bucket labeled
    \cc{single\_var\_cross\_tx} may still correspond to an MV-SI bug
    when the manually validated violated invariant couples that state
    entity to additional protocol state. Conversely, a syntactically
    multi-variable bucket is not counted as MV-SI unless the independent
    semantic criteria are satisfied. We therefore separate detector
    bucket structure from oracle labels throughout the evaluation.
    ```

- Background currently defines an entangled group as `H = {v_p, v_r}` with a primary state and redundant state. That is too narrow. Your oracle schema supports `n ≥ 2` coupled state entities, external proxy state, and cases with no obvious primary/counterpart split. The current paper’s pair framing invites attacks on Vader, Aura, and multi-contract accounting examples. This might be better-ish:
  * ```latex
    \begin{definition}[Entangled State Group]
    Let $V$ be the set of protocol state entities, including concrete storage variables, mapping slots, and modeled external proxy states. An entangled state group is a set $H \subseteq V$, $|H| \ge 2$, whose members are coupled by a protocol-level relational invariant $\Phi_H$. A source-of-truth member may exist, but it is not required: many DeFi invariants couple several accounting views without a single canonical primary variable.
    \end{definition}
    ```
  * ```latex
    \begin{definition}[Multi-Variable State Inconsistency]
    An execution exhibits MV-SI with respect to $H$ when:
    (1) $H$ is justified by independent semantic evidence;
    (2) the execution updates, advances, invalidates, or consumes a
    proper subset of $H$;
    (3) at least one required counterpart in $H$ is not synchronized
    before the relevant protocol decision;
    (4) the stale or inconsistent constituent reaches a security- or
    economically relevant sink; and
    (5) the defect is not reducible to same-variable SI, reentrancy,
    missing access control, or arithmetic error.
    \end{definition}
    ```

- The intro currently says MV-SI occurs when the protocol updates a primary state variable but fails to synchronize the counterpart “within the same logical transaction.” That is not general enough. Many MV-SI bugs are cross-transaction, lazy-synchronization, checkpoint, governance-configuration, or oracle-consumption bugs. Replace “within the same logical transaction” with:
  * ```latex
    before the next security- or economically relevant protocol decision that assumes the relational invariant.
    ```
  * ```latex
    MV-SI occurs when a protocol updates, advances, invalidates, or consumes one constituent of a coupled state group without
 synchronizing the required counterpart before the next security- or economically relevant decision that assumes the relational invariant.
    ```

- The current paper says state-of-the-art tools operate under a “Variable Independence Assumption” and are structurally blind to relational invariants.  A reviewer can object immediately: symbolic tools can reason about multiple variables if given a specification; MUVI explicitly infers multi-variable correlations; TOSEM studies correlated state variables; DivertScan models flow divergence.
  * MUVI is explicitly about automatically inferring multi-variable access correlations and detecting inconsistent updates and multi-variable concurrency bugs.  TOSEM/Li et al. explicitly studies inconsistent state updates in smart contracts, including correlated state variables requiring synchronized updates. ([arXiv][1]) DivertScan introduces flow divergence and multiplex symbolic execution to determine exploitability of smart-contract state-inconsistency bugs. ([Yinqian Zhang's Homepage][2]) SAILFISH is a scalable smart-contract state-inconsistency detector for reentrancy and TOD. ([arXiv][3])
  * Replace “operate under a Variable Independence Assumption” with something like:
    ```latex
    Most existing smart-contract analyzers do not infer protocol-specific DeFi relational invariants across symbolic mapping
 slots, cross-contract proxy state, public transaction boundaries, and economic/security sinks unless such relationships are explicitly specified or encoded in a detector rule.
    ```

Replace “rendering both static pattern matching and dynamic fuzzing campaigns completely ineffective” with:
```latex
making generic static rules and unguided dynamic fuzzing unlikely to expose the defect without a relational invariant or a focused state-space guide.
```

The related work currently mentions Sailfish and DivertScan, but it does not sufficiently position MV-SI against TOSEM and MUVI. The co-author email already identified this as a main reviewer concern, so something like this would help:
  * ```latex
    \PP{Inconsistent Updates and Multi-Variable Correlations}
    Our work is closest in motivation to studies of inconsistent state
    updates and correlated-variable bugs. Li et al. systematically study
    116 inconsistent state update vulnerabilities in 352 smart-contract
    projects and show that correlated state variables often require
    synchronized updates. \sys does not claim that correlated updates
    are a new general software phenomenon. Instead, MV-SI is a
    DeFi/EVM-specific specialization within this broader family, focused
    on symbolic mapping slots, cross-contract proxy states, public
    transaction boundaries, and economic/security sinks. Similarly,
    MUVI inferred multi-variable access correlations in conventional
    software and used them to detect inconsistent updates and
    multi-variable concurrency bugs. MV-SI differs in its execution
    model, state namespace, and exploit semantics: EVM contracts expose
    public transaction entry points, persistent keyed storage, gas-induced
    lazy synchronization, and financial sink decisions that require a
    domain-specific static triage model.
    ```

This paragraph prevents the novelty attack without conceding the contribution.

- Performance comparison can be attacked as apples-to-oranges. The paper claims MV-Scan is 154× faster than DivertScan and 3,709× faster than Mythril.  If those numbers are pulled from prior papers or different environments, reviewers will object. Rename the section to something like **Reported Throughput Context**, not “Comparison with State-of-the-Art.”
  * ```latex
    These numbers are not a head-to-head effectiveness benchmark. They
    provide throughput context using reported per-contract runtimes
    from prior systems under their published settings. The comparison
    supports the design motivation for static triage, but we do not use it
    to claim superiority in detection quality.
    ```
  * Then add something like:
    ```latex
    Because existing tools target different vulnerability definitions and
    use different corpora, we avoid direct precision/recall comparison
    against them. Our quantitative evaluation is instead based on
    ablation, labeled alert precision, and strict known-bug recall.
    ```

- Replace: “Because MV-SI represents an entirely novel architectural defect class, no pre-labeled dataset exists.” with:
```latex
Because no pre-labeled benchmark exists for MV-SI under our stricter DeFi/EVM semantic schema, we separate two artifacts: a labeled detector-output corpus for precision and an independent known-bug oracle for strict MV-SI recall.
```

- The code’s multi-return summaries are shallow, as the design says: “For a read-only function f, we compute its return dependency set RetDeps(f), which contains all state variables that flow into its return values.” The code collects state variables and mapping slots visible in return nodes of functions that do not write storage. It does not implement a full backward slice through local temporaries or a complete return-value dependency analysis.
  * Replace “all state variables that flow into return values” with:
    ```latex
    state entities directly exposed in the return nodes according to Slither's return-node variables and IR-level indexed accesses.
    ```
  * Paper-ready text to avoid a false dataflow claim:
    ```latex
    For a read-only helper $f$, \sys computes a shallow return summary $\text{RetDeps}(f)$ consisting of state entities directly exposed in Slither return nodes, including concrete state variables and recognized mapping-slot accesses. When such a summary contains multiple state entities, \sys materializes a multi-return pseudo-variable to expose API-level coupling at the callsite. This is a lightweight summary rather than a complete interprocedural return-value slice.
    ```

- The design says external calls are modeled as state variables and could sound general. The code only classifies a small selector table: read-like selectors include `balanceOf`, `totalSupply`, `lastBalance`; write-like selectors include `transfer`, `transferFrom`, `mint`, `burn`, `sync`. It also maps selected local storage names to external getter selectors. Replace general language with:
  * ```latex
    \sys currently wraps a selected family of common DeFi/ERC-20-style external state interfaces, such as \cc{balanceOf}, \cc{totalSupply}, \cc{lastBalance}, \cc{transfer}, \cc{transferFrom}, \cc{mint}, \cc{burn}, and \cc{sync}. This selector-table abstraction is deliberately conservative and does not model arbitrary external contract state.
    ```
  * In Threats, we can add something like:
    ```latex
    External-state wrapping is selector-driven and argument-insensitive. It can miss invariants mediated by unsupported selectors, and it can merge distinct remote states when selector and target are insufficient to distinguish semantic state.
    ```

- MV-Scan uses a lighter interprocedural CFG annotated with reads and writes. So `sdg.py` file name should be updated everywhere it is depended on to avoid reviewer confusion. The paper and artifacts must also be consistent.
  * Use **state-annotated ICFG**. Use **state-access namespace** alternatively in sections where it doesn't sound confusing.
  * Avoid **SDG**, **SAG**, **storage dependency graph**, or **program dependence graph** as this forces us to explain the lineage/usage.

- `entry_of` is single-owner reachability, so avoid claiming complete entry-set attribution. The code tracks `entry_of[block]` as one reaching public entry. If an internal block is reachable from multiple public entries, the first reaching owner in traversal wins. Do not claim the transaction set is the complete set of all possible reaching public entries. Use something like:
  * ```latex
    \sys associates each retained block with a representative user-callable entry discovered during reachability pruning and buckets each candidate by the resulting writer/reader entry pair. This approximation is sufficient for triage but can miss alternative outer-entry witnesses for shared internal helpers.
    ```
  * In Threats:
    ```latex
    Entry attribution is approximate. Shared internal helpers may be reachable from multiple public entrypoints, but the frozen
    implementation records a representative reaching entry for each retained block. This can merge or miss alternative transaction-set witnesses and contributes to strict recall loss.
    ```

---

## O12 — Placeholder block early-return risk means do not overclaim interprocedural completeness

### Reviewer attack

`SDG.add_block` returns immediately if a block already exists. The code also creates placeholder callee entry/exit blocks during call handling. If a placeholder is created before the actual callee node is processed, the early return can skip real read/write/successor population. 

Since the code is frozen, do not describe the graph as a complete interprocedural model.

### Fix

Use:

```latex
The state-annotated ICFG is a best-effort interprocedural
approximation over Slither CFG nodes. It is designed for scalable
triage, not complete call-graph or dependence recovery.
```

Threats text:

```latex
Our interprocedural graph construction is intentionally lightweight.
It approximates call and return edges over Slither CFG nodes and may
under-approximate state metadata for some callee blocks. We therefore
interpret detected findings and strict known-bug recall as properties
of the frozen triage implementation, not as completeness results for
the semantic MV-SI class.
```

This avoids a reviewer saying the paper promised full interprocedural precision.

---

## O13 — Admin pruning is heuristic, not a privilege proof

### Reviewer attack

The paper says admin writes are benign or centralization risks. The code identifies admin-only functions via common modifier names and inline guard patterns. That is a heuristic, not a proof of authorization semantics. 

### Fix

Replace:

> “variables writable only by privileged roles”

with:

```latex
variables written from functions heuristically identified as
role-gated or owner-gated.
```

Replace:

> “cannot be desynchronized by an attacker”

with:

```latex
are outside the default unprivileged-attacker triage target.
```

Better text for B2:

```latex
B2 disables the default administrative-write suppression. In B0,
\sys suppresses writer/reader pairs where the writer belongs to a
function heuristically identified as role-gated and the reader is
user-callable. This does not prove the absence of centralization risk;
it reflects the default attacker model, which prioritizes
unprivileged exploitation.
```

- Init pruning is heuristic, not immutability proof. B1 disables creation/init-like pruning. In B0, \sys suppresses variables whose observed writes are confined to constructor- or initializer-like phases under the heuristic. This pruning improves triage density for post-deployment unprivileged bugs, but it is not a proof that every suppressed variable is semantically immutable.

## O15 — Raw rows versus scored buckets must be explicit

### Reviewer attack

`normalized_rows(8).csv` has 8,930 rows across B0/B1/B2/B3/B4/B6. Of these, 6,181 are scored rows: 4,337 FP, 1,808 TP, and 36 ZD. The rest are excluded/nonlabel/unlabeled rows. B5 has zero scored findings and appears in runtime/coverage, not normalized scored rows.

For B0, the raw row count is 1,592, but the scored bucket count is 1,111. The paper currently says “1,111 total alarms.” 

### Fix

Use:

```latex
Across all nonzero-output configurations, the frozen artifact
contains 8,930 raw rows. After applying the pre-declared exclusion
protocol, 6,181 scored buckets remain. Unless otherwise stated,
reported alarm counts refer to scored buckets.
```

For B0:

```latex
B0 emitted 1,592 raw rows, of which 1,111 were scored under our
labeling protocol. Among scored B0 buckets, 335 were positive
(328 TP and 7 ZD) and 776 were FP, yielding 30.15\% precision.
```

This will prevent an artifact-evaluation mismatch.

---

## O16 — The 23,889-contract corpus number conflicts with runtime’s 4,094 analyzed contracts

### Reviewer attack

The manuscript says the corpus has 23,889 smart contracts and 1,987,395 Solidity LOC.  The runtime summary reports 4,094 contracts analyzed for each ablation.

### Fix

You need to distinguish:

* raw Solidity files/contracts in repository corpus;
* in-scope compiled contracts;
* contracts actually analyzed after exclusion/fallback compilation.

Paper-ready text:

```latex
The 61 selected repositories contain 23,889 Solidity contract files
or declarations in the raw repository corpus, totaling 1,987,395
Solidity LOC. After compilation, scope filtering, and exclusion of
mocks/interfaces/failing targets, the frozen ablation runs analyze
4,094 in-scope compiled contracts. Runtime statistics are normalized
over this analyzed-contract denominator.
```

Use the exact denominator labels from your scripts. If `23,889` is not “contract files or declarations,” rename it precisely. Do not leave both numbers unexplained.

---

- We must make explicit that the JSON isn't necessary "stable JSON": "MV-Scan emits machine-readable JSON intended to support future dynamic exploit generation. We do not rely on JSON identifier stability for any quantitative result in this paper."

---

The paper says bounded exploration “provides the optimal architectural tradeoff.” B0 is chosen as a reference tradeoff under your objective, not proven globally optimal. We can replace “optimal” with: **reference**, **balanced under our triage objective**, or **selected operating point** depending on what sounds academically most beautiful/rigorous.
  * ```latex
    We use B0 as the optimal reference configuration because it balances scored alert volume, validated positives, zero-day yield, and precision under our triage objective. This does not imply global optimality over all possible budgets or downstream audit workflows.
    ```

- False-positive explanation must not rely only on “external oracles”. B0 false positives arise from several sources: semantic masking by downstream checks or external oracles, bucket pollution caused by coarse aggregation, unsupported argument-sensitive external state, syntactic mapping-key limitations, and cases where the static slice identifies adjacent state evidence but not the strict violated invariant.

## 7.5 Algorithm 1

Replace:

```latex
\WHILE{$Q$ is not empty \AND $steps \leq K$}
```

with:

```latex
\IF{$K = 0$}
    \RETURN \FALSE
\ENDIF
\WHILE{$Q$ is not empty \AND ($K=\infty$ \OR $steps < K$)}
```

Also replace the `ENSURE` line: "if candidate read r affects a critical sink" with "if candidate read r reaches a compatible sink-context block." Paper-ready algorithm caption:

```latex
\caption{Bounded Sink-Context Reachability}
```

Replace “Candidate value impacts a critical sink” with:

```latex
\RETURN \TRUE \COMMENT{Tracked state is re-observed at sink context}
```

## 8.6 Strict recall subsection

Use the correct table, then add:

```latex
The low strict recall should not be read as a failure of the semantic
MV-SI definition. It quantifies the limits of the frozen static
approximation. Many false negatives arise because the known
invariant is latent in protocol economics, documentation, fix
discussion, or multi-step accounting rather than syntactically
exposed through branch co-use, shallow multi-return summaries, or
supported external-state wrappers.
```