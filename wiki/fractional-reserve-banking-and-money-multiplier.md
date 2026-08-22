---
type: Concept
title: Fractional-reserve banking, the money multiplier, and bank capital
description: Mankiw Ch.16 — how 100-percent-reserve vs fractional-reserve banking creates money, the 1/R money multiplier, T-account mechanics, and leverage, capital requirements, and the 2008–2009 credit crunch.
tags: [banks, money-supply, fractional-reserve, reserve-ratio, reserves, money-multiplier, t-account, bank-capital, leverage, leverage-ratio, capital-requirement, financial-crisis, credit-crunch]
status: stable
created: 2026-08-22
generated: { by: llm-wiki-agent/1, at: 2026-08-22T15:20:00Z }
sources:
  - id: mankiw-16-1
    resource: ../raw/PrinciplesofMacroeconomics_8thEdition_GregoryMankiw/049-money-and-prices-in-the-long-run.md
    title: "Money and Prices in the Long Run — The Monetary System (Mankiw 8th Ed. Ch.16, Part 49)"
---

# Fractional-reserve banking, the money multiplier, and bank capital

Money holdings include currency and demand deposits; because deposits live in banks, bank behavior influences demand deposits and therefore the money supply, complicating the Fed's indirect control[^mankiw-16-1]. Under fractional-reserve banking each dollar of reserves can generate many dollars of money via the money multiplier `1/R`, but leverage makes banks fragile — a lesson of the 2008–2009 crisis when capital shortfalls produced a credit crunch[^mankiw-16-1].

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
- Detailed Fed tools for controlling reserves and reserve ratio (open-market operations vs Fed lending, reserve requirements, interest on reserves) and monetary-control problems (depositor/banker behavior, bank runs, 1929–1933 28% money-supply fall) belong to 050 (16-4a–c) and are not compiled here per idempotency; 049 truncated mid-16-4.

[^mankiw-16-1]: Mankiw, *Principles of Macroeconomics* 8th ed., Ch.16 — The Monetary System (raw/PrinciplesofMacroeconomics_8thEdition_GregoryMankiw/049-money-and-prices-in-the-long-run.md).
