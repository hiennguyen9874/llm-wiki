---
type: Concept
title: Fractional-reserve banking, the money multiplier, and bank capital
description: Mankiw Ch.16 — how 100-percent-reserve vs fractional-reserve banking creates money, the 1/R money multiplier, T-account mechanics, and leverage, capital requirements, and the 2008–2009 credit crunch.
tags: [banks, money-supply, fractional-reserve, reserve-ratio, reserves, money-multiplier, t-account, bank-capital, leverage, leverage-ratio, capital-requirement, financial-crisis, credit-crunch]
status: stable
created: 2026-08-22
generated: { by: llm-wiki-agent/1, at: 2026-08-22T11:55:37Z }
sources:
  - id: krugman-ch14-077
    resource: ../raw/Macroeconomics_Krugman/077-chapter-14-money-banking-and-the-federal-reserve-system-economics-in-a.md
    title: "Chapter 14 Money, Banking, and the Federal Reserve System — ECONOMICS >> in Action (Krugman/Wells)"
  - id: krugman-ch14-078
    resource: ../raw/Macroeconomics_Krugman/078-chapter-14-money-banking-and-the-federal-reserve-system-how-banks-crea.md
    title: "Chapter 14 Money, Banking, and the Federal Reserve System — How Banks Create Money (Krugman/Wells)"
  - id: mankiw-16-1
    resource: ../raw/PrinciplesofMacroeconomics_8thEdition_GregoryMankiw/049-money-and-prices-in-the-long-run.md
    title: "Money and Prices in the Long Run — The Monetary System (Mankiw 8th Ed. Ch.16, Part 49)"
  - id: krugman-ch14-081
    resource: ../raw/Macroeconomics_Krugman/081-chapter-14-money-banking-and-the-federal-reserve-system-problems.md
    title: "Chapter 14 Money, Banking, and the Federal Reserve System — Problems (Krugman/Wells)"
---

# Fractional-reserve banking, the money multiplier, and bank capital

Money holdings include currency and demand deposits; because deposits live in banks, bank behavior influences demand deposits and therefore the money supply, complicating the Fed's indirect control[^mankiw-16-1]. Under fractional-reserve banking each dollar of reserves can generate many dollars of money via the money multiplier `1/R`, but leverage makes banks fragile — a lesson of the 2008–2009 crisis when capital shortfalls produced a credit crunch[^mankiw-16-1].

## Banking as liquidity transformation

Banks finance borrowers' illiquid assets (such as mortgages and business loans) with depositors' liquid, on-demand claims. They can do this because withdrawals normally do not occur all at once, but must retain **bank reserves** — vault currency plus their deposits at the Federal Reserve — to meet ordinary withdrawals[^krugman-ch14-077]. A **T-account** makes this balance-sheet position visible by listing assets on the left and liabilities on the right[^krugman-ch14-077].

## 100-percent-reserve benchmark

- Without banks, if currency is $100, money supply = $100[^mankiw-16-1].
- Suppose **First National Bank** accepts deposits but makes no loans — a **depository institution** holding all deposits as **reserves** (deposits received but not loaned)[^mankiw-16-1]. This is **100-percent-reserve banking**[^mankiw-16-1].
- T-account if the entire $100 is deposited: Assets Reserves $100 = Liabilities Deposits $100[^mankiw-16-1]. Assets and liabilities balance as a **balance sheet**[^mankiw-16-1].
- Money supply unchanged: $100 currency → $100 demand deposits, no currency outstanding; banks do not influence supply when they hold all deposits in reserve[^mankiw-16-1].

## Fractional-reserve banking and money creation

- Leaving idle vault cash is wasteful; banks can earn interest by lending some reserves. With stable deposit-withdrawal flows they need hold only a **fraction** — **fractional-reserve banking**[^mankiw-16-1].
- **Reserve ratio** ($R$) = fraction of total deposits held as reserves, influenced by regulation and bank policy; the Fed sets a minimum — the **reserve requirement** — and banks may hold **excess reserves** above it for safety[^mankiw-16-1].
- Example: $R = 1/10$ (10%). First National: Liabilities Deposits $100; Assets Reserves $10 + Loans $90[^mankiw-16-1]. Liabilities unchanged (still owe depositors $100); loans are borrower liabilities but bank assets to be repaid[^mankiw-16-1].
- Money supply now $100 deposits + $90 currency held by borrowers = **$190** — banking system creates money[^mankiw-16-1].
- This is not wealth creation: borrowers gain currency and purchasing power but also take on equal debts; economy is more liquid (more medium of exchange) but not wealthier[^mankiw-16-1].

## The money multiplier

- Creation does not stop: borrower spends $90, seller deposits $90 in Second National Bank — with $R=10%$, Second National holds $9 reserves, loans $81, creating $81 more money[^mankiw-16-1]. That $81 deposited in Third National Bank → $8.10 reserves, $72.90 loans[^mankiw-16-1], and so on.
- Infinite sequence sum: $100 original reserves generates **$1,000** of money in this example; **money multiplier** = amount banking system generates per dollar of reserves = **10**[^mankiw-16-1].
- General formula: if $R$ is reserve ratio for all banks, multiplier = $1/R$; each dollar of reserves generates $1/R$ dollars of money[^mankiw-16-1]. Intuition: if $R=1/10$, $1,000 deposits require $100 reserves; turned around, $100 reserves supports $1,000 deposits[^mankiw-16-1].
- Implications: $R=1/20$ → multiplier 20 ($20 per $1 reserves); $R=1/4$ → multiplier 4; higher ratio → less lent out → smaller multiplier; under 100% reserves $R=1$ → multiplier 1, no creation[^mankiw-16-1].
- Mankiw notes this simple formula will become more complex when 16-4 introduces additional Fed tools; the chapter's 16-3 presentation is the simplified case.

## Monetary base and the practical money multiplier

A currency deposit initially only changes money's form: currency in circulation falls by the deposited amount while checkable deposits rise equally. Money expands when the bank lends excess reserves, placing currency back into circulation while the original deposit remains spendable[^krugman-ch14-078]. Repeated lending requires loan proceeds to return to the banking system; cash that borrowers retain is a leakage that reduces the multiplier[^krugman-ch14-078].

- In the simplified checkable-deposits-only model, a $1,000 increase in excess reserves generates $1,000 + $1,000(1-rr) + $1,000(1-rr)^2 + ... = $1,000/rr$ in deposits. At $rr=0.1$, that is $10,000; equivalently, each reserve dollar supports $1/rr$ in deposits[^krugman-ch14-078]. This is the same idealized logic as the $1/R$ multiplier above.
- The **monetary base** is currency in circulation plus bank reserves; the Fed controls this total but not its allocation between the two. The money supply instead includes currency and checkable/near-checkable deposits, not bank reserves[^krugman-ch14-078]. Thus currency belongs to both aggregates, reserves only to the base, and deposits only to the money supply.
- In practice the **money multiplier** is money supply divided by the monetary base, not mechanically $1/rr$. The source reports approximately 1.6 before the 2008 crisis, 0.7 afterward, and 1.01 in March 2020 — dated observations, not current measurements[^krugman-ch14-078]. Currency held by the public and banks' voluntary excess reserves both lower it relative to the simplified benchmark.
- The source attributes the post-2008 fall below one to the Fed's base expansion and banks' choice to hold deposits at the Fed rather than make safe, profitable loans; currency was 40% of the base at the beginning of 2009 and 47% in 2019[^krugman-ch14-078].

### Derived reserve-ratio checks

These calculations apply the problem source's assumptions (banks hold the stated reserve ratio, no excess reserves unless stated, and loan proceeds return as deposits where specified); they are synthesis, not supplied answer text.[^krugman-ch14-081]

- A $500 currency deposit initially changes only M1's composition. If all loan proceeds are redeposited, it ultimately raises M1 by **$4,500** at a 10% reserve ratio and by **$9,500** at 5%: the final deposit totals are $500/rr, while the original $500 currency was already in M1. Conversely, a $400 withdrawal into currency lowers M1 by **$3,600** at 10% and **$1,600** at 20%.
- Cash leakage reduces the multiplier. If rr = 20% and the public retains half of every loan as currency, each successive deposit is 40% of the preceding one. A $500 initial cash deposit produces total deposits of $833.33, public currency from loans of $333.33, and M1 of $1,166.67 — a $666.67 increase from the initial $500. With no leakage, the corresponding final M1 would be $2,500 (a $2,000 increase).
- In the source's Eastlandia data, M1 = $150 million currency held by the public + $500 million checkable deposits = **$650 million**. The monetary base = public currency + $100 million vault cash + $200 million central-bank deposits = **$450 million**. Banks hold $300 million reserves against a $50 million requirement, so $250 million excess reserves could support a **$2.5 billion** increase in checkable deposits at rr = 10%.

## Bank capital, leverage, and the 2008–2009 crisis

- More realistic balance sheet: banks obtain resources not only from deposits but also by **issuing equity and debt**; resources from equity issuance are **bank capital** (owners' equity); they allocate among reserves, loans, and financial securities (stocks and bonds) based on risk/return and regulations[^mankiw-16-1].
- Example — More Realistic National Bank: Assets Reserves $200 + Loans $700 + Securities $100 = $1,000; Liabilities and Owners' Equity Deposits $800 + Debt $150 + Capital $50 = $1,000[^mankiw-16-1]. By accounting, assets minus liabilities = owners' equity, so left and right always sum equally[^mankiw-16-1].
- **Leverage** is use of borrowed money to supplement existing funds for investment; central to banking because borrowing and lending are its heart[^mankiw-16-1].
- **Leverage ratio** = total assets / bank capital = $1,000 / $50 = **20** in example; for each $1 of owner capital, $20 of assets, $19 financed by deposits/debt[^mankiw-16-1].
- Leverage amplifies like a physical lever: 5% rise in asset value $1,000→$1,050 with $950 still owed → capital $50→$100 (+100%) ; 5% fall $1,000→$950 → capital $50→$0 (-100%) ; larger fall makes bank **insolvent** (assets < liabilities, cannot pay depositors/debt holders in full)[^mankiw-16-1].
- Regulators require a minimum **capital requirement** to ensure ability to pay depositors without resorting to government deposit insurance; required amount depends on asset riskiness — safe government bonds need less capital than risky dubious-credit loans[^mankiw-16-1].
- 2008–2009: banks incurred sizable losses on mortgages and mortgage-backed securities, found themselves with too little capital to meet requirements, **reduced lending** — a **credit crunch** — contributing to severe downturn (Chapter 20). The Treasury with the Fed injected many billions to **recapitalize** the system, temporarily making the taxpayer part owner of many banks; by late 2009 lending normalized[^mankiw-16-1].

## Fed's indirect control preview

- Because banks create money fractionally, Fed's control is indirect — it must consider how actions work through the banking system[^mankiw-16-1]. Tools group into those influencing quantity of reserves and those influencing reserve ratio and thus multiplier (14-4 introduction; details in next part)[^mankiw-16-1].

## Relationships

- Depends on: [Kinds of money and measurement — commodity vs fiat and M1/M2](kinds-of-money-and-measurement-m1-m2.md) — what deposits are counted in money
- Depends on: [Federal Reserve System and monetary policy — Fed organization, FOMC, and open-market operations](federal-reserve-system-and-monetary-policy.md) — reserve ratio regulation and multiplier context for policy; Fed as lender of last resort
- Uses: [Saving, Investment, and the Financial System — Financial Institutions, National Saving Identities, and the Market for Loanable Funds](saving-investment-and-the-financial-system.md) — banks as financial intermediaries; loan vs security allocation
- See also: [Future of macroeconomics — why macro isolated itself and three missing perspectives](future-of-macroeconomics-banking-behavioral-and-complexity-critique.md) — banking frontier missing from pre-crisis models
- See also: [Three functions of money as medium, store, and unit of account](functions-of-money-medium-store-unit.md) — why creating medium of exchange matters

## Coverage limits

- T-account illustrations and multiplier arithmetic transcribed from OCR; reserve ratio 10% example yields $1,000 from $100.
- Images 000319–000321 (money cartoon, T-accounts, bank-run film stills) not inspected.
- Krugman/Wells source 078 is complete and contains no credentials, PII, or disclosure markings. All five referenced images were inspected: Figures 14-4 and 14-5 support the T-account and aggregate distinctions; Figure 14-6 supports the district map; the bank cartoon and Lehman Brothers photograph add no material claims beyond their captions.
- Krugman/Wells source 081 is complete and contains no credentials, PII, or disclosure markings. Its reserve-ratio scenarios were compiled as explicitly labeled derivations; its housing-starts chart is not used for a causal claim.
- Detailed Fed tools for controlling reserves and reserve ratio (open-market operations vs Fed lending, reserve requirements, interest on reserves) and monetary-control problems (depositor/banker behavior, bank runs, 1929–1933 28% money-supply fall) belong to 050 (16-4a–c) and are not compiled here per idempotency; 049 truncated mid-16-4.

[^krugman-ch14-077]: Krugman and Wells, *Macroeconomics*, 6th ed., Ch. 14, “Money, Banking, and the Federal Reserve System — Economics in Action” (raw/Macroeconomics_Krugman/077-chapter-14-money-banking-and-the-federal-reserve-system-economics-in-a.md).
[^krugman-ch14-078]: Krugman and Wells, *Macroeconomics*, 6th ed., Ch. 14, “Money, Banking, and the Federal Reserve System — How Banks Create Money” (raw/Macroeconomics_Krugman/078-chapter-14-money-banking-and-the-federal-reserve-system-how-banks-crea.md; Figures 14-4 and 14-5 visually inspected).
[^mankiw-16-1]: Mankiw, *Principles of Macroeconomics* 8th ed., Ch.16 — The Monetary System (raw/PrinciplesofMacroeconomics_8thEdition_GregoryMankiw/049-money-and-prices-in-the-long-run.md).
[^krugman-ch14-081]: Krugman and Wells, *Macroeconomics*, 6th ed., Ch. 14, “Money, Banking, and the Federal Reserve System — Problems” (raw/Macroeconomics_Krugman/081-chapter-14-money-banking-and-the-federal-reserve-system-problems.md; calculations are synthesis from its stated assumptions and inputs).
