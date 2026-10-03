"""Generators for the three computation-heavy decision families (temporal_numeric, multi_hop, long_policy).

Nothing here is taken from a benchmark: every scenario is assembled from random parameters and its gold label is
COMPUTED (dates with `datetime`, money with explicit rates, policy outcomes by walking the generated rules), so a
label can only be wrong if the generator is wrong — `selftest()` re-derives each answer a second way.

Each item is a dict: {"state", "instructions", "options": {label: rubric}, "gold", "family", "surface"} where
`surface` is the tempting wrong answer that the state's narrative pushes (a colleague's note, a customer's claim).
"""
import calendar
import random
from datetime import date, datetime, timedelta

NAMES = ["Halvorsen", "Okafor", "Lindqvist", "Marchetti", "Tanaka", "Abernathy", "Kowalczyk", "Desrosiers", "Nakamura", "Oyelaran"]
ORGS = ["Brightwater", "Calloway", "Dunmore", "Eastlake", "Fenwick", "Greyfield", "Hollis", "Ironbridge", "Juniper", "Kestrel"]


def add_months(d, n):
    y, m = d.year + (d.month - 1 + n) // 12, (d.month - 1 + n) % 12 + 1
    return d.replace(year=y, month=m, day=min(d.day, calendar.monthrange(y, m)[1]))


def fmt_dt(dt, off):
    return f"{dt:%d %B %Y, %H:%M} (UTC{off:+d})"


def rand_date(rng, y0=2023, y1=2028):
    """Skewed towards month ends and leap-year Februaries, where the month-end rule and day counts actually bite."""
    y, m = rng.randint(y0, y1), rng.randint(1, 12)
    if rng.random() < 0.4:
        y, m = rng.choice([2024, 2028, y]), rng.choice([1, 2, 2, 3, 8, 10, 12])
        return date(y, m, min(rng.choice([28, 29, 30, 31]), calendar.monthrange(y, m)[1]))
    return date(y, m, rng.randint(1, calendar.monthrange(y, m)[1]))


YESNO = lambda yes, no: {"yes": yes, "no": no}  # noqa: E731


# ------------------------------------------------------------------------------------------ temporal / numeric
def t_window(rng):
    """Coverage ends at 23:59 policy time, N months after purchase (month-end rule); the report carries another zone."""
    p = rand_date(rng)
    n = rng.choice([3, 6, 12, 18, 24, 36])
    pol_off, rep_off = rng.choice([-5, 0, 1, 2]), rng.choice([-8, -3, 3, 5, 8, 9])
    end_local = datetime.combine(add_months(p, n), datetime.min.time()) + timedelta(hours=23, minutes=59)
    end_utc = end_local - timedelta(hours=pol_off)
    delta = timedelta(minutes=rng.choice([-150, -40, -10, 15, 45, 170])) if rng.random() < 0.7 else timedelta(days=rng.randint(-20, 20))
    rep_utc = end_utc + delta
    inside = rep_utc <= end_utc
    rep_local = rep_utc + timedelta(hours=rep_off)
    who = rng.choice(NAMES)
    note = ("The agent's note says the report came in a day too late." if inside else
            "The customer insists the report was filed before the plan ran out.")
    state = (f"Service plan {rng.randint(100000, 999999)} for {who}. Purchased on {p:%d %B %Y}. The plan runs for {n} months: it "
             f"ends at 23:59 on the day with the same day-number {n} months after purchase, or on the last day of that "
             f"month if the month has no such day. All plan times are in UTC{pol_off:+d}.\n"
             f"Fault reported: {fmt_dt(rep_local, rep_off)}.\n{note}")
    return dict(state=state, instructions="Was the fault reported before the plan ended?",
                options=YESNO("The report was made at or before the end of the plan.", "The report was made after the plan had ended."),
                gold="yes" if inside else "no", surface="no" if inside else "yes", family="temporal_numeric",
                check=("window", p, n, pol_off, rep_local, rep_off))


def t_business(rng):
    start = rand_date(rng)
    k = rng.randint(3, 12)
    hol = sorted({start + timedelta(days=rng.randint(1, 16)) for _ in range(rng.randint(0, 2))})
    d, left = start, k
    while left:
        d += timedelta(days=1)
        if d.weekday() < 5 and d not in hol:
            left -= 1
    sent = d + timedelta(days=rng.choice([-2, -1, 0, 0, 1, 2, 3]))
    ok = sent <= d
    hs = ", ".join(f"{h:%d %B %Y}" for h in hol) or "none"
    state = (f"Complaint received on {start:%A, %d %B %Y}. Rule: a written reply must be sent within {k} business days of "
             f"receipt; the day of receipt does not count, Saturdays and Sundays are not business days, and neither are "
             f"these public holidays: {hs}.\nReply sent on {sent:%A, %d %B %Y}.\n"
             f"A colleague counted {k} calendar days and says the reply was {'late' if ok else 'on time'}.")
    return dict(state=state, instructions="Was the reply sent within the deadline?",
                options=YESNO("The reply was sent on or before the last permitted business day.", "The reply was sent after the deadline."),
                gold="yes" if ok else "no", surface="no" if ok else "yes", family="temporal_numeric",
                check=("business", start, k, tuple(hol), sent))


def t_latefee(rng):
    due = rand_date(rng)
    days = rng.choice([-3, 0, 1, 4, 5, 6, 9, 15, 16, 22, 40])
    paid = due + timedelta(days=days)
    gold = "no_fee" if days <= 0 else "fee_2_percent" if days <= 5 else "fee_5_percent" if days <= 15 else "fee_8_percent_and_suspension"
    opts = {"no_fee": "Paid on or before the due date", "fee_2_percent": "Paid 1 to 5 days late",
            "fee_5_percent": "Paid 6 to 15 days late", "fee_8_percent_and_suspension": "Paid more than 15 days late"}
    state = (f"Invoice due {due:%d %B %Y}. Payment received {paid:%d %B %Y}. Late fees: none if paid by the due date; 2% if "
             f"1 to 5 days late; 5% if 6 to 15 days late; 8% plus account suspension beyond 15 days.\n"
             f"The account manager wrote: 'only about a week, take the small fee'.")
    return dict(state=state, instructions="Which late-fee outcome applies to this payment?", options=opts, gold=gold,
                surface="fee_2_percent" if gold != "fee_2_percent" else "fee_5_percent", family="temporal_numeric",
                check=("latefee", due, paid))


def t_count(rng):
    rows, late = [], 0
    for i in range(rng.randint(5, 8)):
        promised = rand_date(rng)
        d = rng.choice([-2, -1, 0, 0, 1, 2, 5])
        late += d > 0
        rows.append(f"  order {rng.randint(1000, 9999)}: promised {promised:%d %b %Y}, delivered {promised + timedelta(days=d):%d %b %Y}")
    lv = min(late, 3)
    opts = {"0": "No late deliveries", "1": "Exactly one late delivery", "2": "Exactly two late deliveries", "3": "Three or more late deliveries"}
    state = "Delivery log for the quarter (a delivery is late if it arrives after the promised date):\n" + "\n".join(rows)
    return dict(state=state, instructions="How many deliveries in this log were late? (0 = none, 1, 2, 3 = three or more)",
                options=opts, gold=str(lv), surface=str(lv - 1 if lv else 1), family="temporal_numeric", check=("count", late))


TEMPORAL = [t_window, t_business, t_latefee, t_count]


# ------------------------------------------------------------------------------------------ multi hop
SKINS = [("wire transfer", "beneficiary", "treasury"), ("equipment order", "supplier", "procurement"),
         ("grant disbursement", "recipient organisation", "programme office"), ("credit-limit increase", "customer", "credit desk"),
         ("consulting engagement", "contractor", "engagement review")]
TIERS = ["tier1_team_lead", "tier2_department_head", "tier3_finance_director", "tier4_board_committee"]


def multi_hop(rng):
    thing, party, desk = rng.choice(SKINS)
    org = rng.choice(ORGS)
    legal, alias = f"{org} {rng.choice(['Holdings', 'Group', 'Partners'])} {rng.choice(['AG', 'Ltd', 'BV'])}", f"{org} {rng.choice(['Trading', 'Services', 'Logistics'])}"
    decoy = f"{org} {rng.choice(['International', 'Capital'])} Inc"
    base_risk = rng.choice(["standard", "elevated"])
    country, watch = rng.choice(["Norland", "Veskia", "Aruvia", "Tollmark"]), rng.sample(["Norland", "Veskia", "Aruvia", "Tollmark", "Ostrava"], 2)
    use_override, use_fx, use_agg = rng.random() < 0.6, rng.random() < 0.7, rng.random() < 0.6
    risk = "elevated" if (base_risk == "elevated" or (use_override and country in watch)) else "standard"
    cur, rate, inverse = rng.choice(["KRN", "DLM", "ZAF"]), round(rng.uniform(1.4, 9.5), 2), rng.random() < 0.5
    amount = rng.randint(8, 400) * 1000
    usd = (amount / rate if inverse else amount * rate) if use_fx else amount
    prior = []
    if use_agg:
        for _ in range(rng.randint(1, 3)):
            days_ago, amt = rng.choice([5, 12, 25, 29, 31, 45, 70]), rng.randint(5, 120) * 1000
            prior.append((days_ago, amt))
    window = 30
    total = usd + sum(a for d, a in prior if d <= window)
    lims = [25_000, 100_000, 400_000]
    idx = sum(total > x for x in lims)
    if risk == "elevated":
        idx = min(idx + 1, 3)
    gold = TIERS[idx]
    naive = TIERS[min(sum((amount if not use_fx else amount) > x for x in lims), 3)]
    lines = [f"REQUEST: {thing} of {amount:,} {cur if use_fx else 'USD'} to {alias} ({country}).",
             f"MASTER DATA ({party}s): '{legal}' — also trades as '{alias}' — base risk class: {base_risk}. "
             f"'{decoy}' is a different legal entity with base risk class: {'standard' if base_risk == 'elevated' else 'elevated'}."]
    if use_override:
        lines.append(f"COUNTRY RULE: any {party} located in {', '.join(watch)} is treated as elevated risk, whatever the master data says.")
    if use_fx:
        lines.append(f"RATES: all thresholds are in USD. Today's rate: " + (f"1 USD = {rate} {cur}." if inverse else f"1 {cur} = {rate} USD."))
    if use_agg:
        lines.append(f"AGGREGATION: approved {thing}s to the same {party} in the last {window} days count towards the total. History (USD): "
                     + "; ".join(f"{a:,} approved {d} days ago" for d, a in prior) + ".")
    lines.append(f"THRESHOLDS (total in USD): up to 25,000 {TIERS[0]}; up to 100,000 {TIERS[1]}; up to 400,000 {TIERS[2]}; above that {TIERS[3]}. "
                 f"Elevated-risk {party}s go one tier higher (never above {TIERS[3]}).")
    lines.append(f"The {desk} analyst suggests {naive} based on the headline amount.")
    body = [lines[0]] + rng.sample(lines[1:-1], len(lines) - 2) + [lines[-1]]
    return dict(state="\n".join(body), instructions=f"Which approval tier must this {thing} be routed to?",
                options={t: t.split("_", 1)[1].replace("_", " ") + " approves" for t in TIERS}, gold=gold,
                surface=naive if naive != gold else TIERS[(idx + 1) % 4], family="multi_hop",
                check=("hop", usd, tuple(prior), risk))


# ------------------------------------------------------------------------------------------ long policy
BOILER = ["GENERAL CONDITIONS. This agreement is governed by the laws of the jurisdiction named in the schedule. Headings are for convenience only and do not affect interpretation.",
          "NOTICES. Any notice under this agreement must be in writing and is deemed received on the second business day after posting or, if sent electronically, on the day of transmission.",
          "ASSIGNMENT. Neither party may assign its rights under this agreement without the prior written consent of the other, such consent not to be unreasonably withheld.",
          "FRAUD. If a claim is in any respect fraudulent, all benefit under this agreement is forfeited and the provider may recover sums already paid.",
          "OTHER COVER. If the loss is also covered elsewhere, the provider pays only its rateable share.",
          "DISPUTES. The parties will first attempt to resolve any dispute through the provider's internal complaints procedure before referring it to an external body.",
          "RECORDS. The customer must keep receipts, reports and correspondence relating to a claim for at least twenty-four months.",
          "SUBROGATION. After payment the provider may pursue any third party responsible for the loss in the customer's name.",
          "SANCTIONS. No benefit is payable where payment would breach trade or economic sanctions applicable to the provider.",
          "CHANGES TO THE PLAN. The provider may vary these terms on thirty days' written notice; a variation does not affect a loss that occurred before it took effect.",
          "CANCELLATION. The customer may cancel within fourteen days of the cover start date for a full refund provided no claim has been made; afterwards a pro-rata refund applies less an administration charge.",
          "PREMIUM. Cover is conditional on payment of the premium when due. If an instalment is more than twenty-one days overdue the provider may suspend cover until it is paid.",
          "DUTY OF CARE. The customer must take reasonable steps to prevent loss and to stop a loss from getting worse; the provider may reduce a payment to the extent a failure to do so increased the loss.",
          "REPAIR NETWORK. Repairs are carried out by the provider's approved repairers. Work done elsewhere without prior approval is reimbursed only up to the amount the approved repairer would have charged.",
          "DATA PROTECTION. Personal data is processed to administer the plan and handle claims, and may be shared with repairers, assessors and fraud-prevention agencies.",
          "INTERPRETATION. Words in the singular include the plural. A reference to a section is a reference to a section of this document as amended by any endorsement shown in the schedule.",
          "CURRENCY. All amounts in this document are stated in the currency shown in the schedule and claims are settled in that currency.",
          "EVIDENCE. The provider may ask for proof of ownership, proof of purchase and any report that is reasonably needed to assess the claim, at the customer's expense.",
          "SALVAGE. Where an item is replaced, the damaged item becomes the property of the provider.",
          "TERRITORY. Cover applies within the territory named in the schedule and for up to sixty days in any plan year elsewhere.",
          "THIRD PARTIES. A person who is not a party to this agreement has no right to enforce any of its terms."]
DEFS = {"Accident": "a sudden, unexpected and unintended event that happens at an identifiable time and place",
        "Approved repairer": "a repairer appointed by the provider and named on the provider's current list",
        "Assessed loss": "the reasonable cost of repair or, if lower, of replacement with an item of like kind and quality, as determined by the provider's assessor",
        "Business day": "any day other than a Saturday, a Sunday or a public holiday in the territory",
        "Concealed loss": "a loss that a reasonable person in the customer's position could not have discovered at the time it occurred",
        "Cover start date": "the date shown as such in the schedule, from which the waiting period is counted",
        "Deductible": "the first part of each and every claim, which the customer bears",
        "Endorsement": "a written change to these terms issued by the provider and listed in the schedule",
        "Family member": "the customer's spouse, civil partner, parent, child or sibling living at the same address",
        "Loss": "physical loss of or damage to the item described in the schedule",
        "Plan year": "each consecutive period of twelve months beginning on the cover start date",
        "Pre-existing condition": "any fault, damage or condition that existed, or whose symptoms were apparent, before the cover start date",
        "Schedule": "the document headed 'Schedule' that names the customer, the item and the limits that apply",
        "Territory": "the country shown in the schedule together with any country the customer visits for no more than sixty days in a plan year",
        "Unattended": "out of the customer's sight or beyond the distance at which the customer could prevent interference",
        "Wear and tear": "gradual deterioration through ordinary use, including scratching, denting and fading that does not affect function"}
PROCEDURE = ["Tell the provider about the loss using the claims line or the online form.",
             "Give the plan number, the date and cause of the loss, and where the item is now.",
             "Do not dispose of a damaged item, and do not authorise repairs, until the provider has inspected it or has agreed in writing.",
             "Send any document the provider asks for within fourteen days of the request.",
             "The provider acknowledges a complete claim within five business days and aims to decide it within twenty.",
             "If the claim is accepted the provider arranges repair, replacement or payment at its option.",
             "If the claim is declined the provider gives its reasons in writing and explains how to complain."]
DOMAINS = [("travel protection plan", "trip", ["illness of the traveller", "cancelled flight", "lost baggage"]),
           ("equipment breakdown cover", "machine", ["electrical burnout", "mechanical fracture", "operator error"]),
           ("pet health plan", "animal", ["accidental injury", "sudden illness", "dental disease"]),
           ("device protection plan", "device", ["accidental damage", "liquid damage", "theft"])]


def long_policy(rng):
    plan, obj, perils = rng.choice(DOMAINS)
    covered = rng.sample(perils, 2)
    peril = rng.choice(perils)
    start = rand_date(rng, 2024, 2026)
    wait = rng.choice([14, 30])
    loss_day = rng.choice([wait - 5, wait - 1, wait, wait + 20, 200])
    loss = start + timedelta(days=loss_day)
    report_days = rng.choice([3, 20, 29, 31, 60])
    report_limit = 30
    concealed = rng.random() < 0.5          # exception that restores cover for a late report
    # the endorsement raises the limit for plans starting on/after a date that falls just before or just after this one
    end_date = start + timedelta(days=rng.choice([-60, -1, 0, 1, 45]))
    old_sub, new_sub = rng.choice([1000, 2500]), rng.choice([4000, 6000])
    applies_new = start >= end_date
    sub = new_sub if applies_new else old_sub
    ded = rng.choice([100, 250, 500])
    amount = rng.choice([600, 1800, 3200, 5200, 9000])
    if peril not in covered:
        gold = "deny_not_a_covered_cause"
    elif loss_day < wait:
        gold = "deny_waiting_period"
    elif report_days > report_limit and not concealed:
        gold = "deny_late_notification"
    else:
        gold = f"pay_up_to_sublimit_{sub}" if amount - ded > sub else "pay_claim_less_deductible"
    opts = {"deny_not_a_covered_cause": "The cause of loss is not one the plan covers", "deny_waiting_period": "The loss happened inside the waiting period",
            "deny_late_notification": "The loss was reported too late and no exception applies",
            f"pay_up_to_sublimit_{old_sub}": f"Payable, capped at the {old_sub} sublimit", f"pay_up_to_sublimit_{new_sub}": f"Payable, capped at the {new_sub} sublimit",
            "pay_claim_less_deductible": "Payable in full less the deductible"}
    wrong = [k for k in opts if k != gold]
    surface = rng.choice(wrong)
    sections = [
        f"SCHEDULE. {plan.title()} no. {rng.randint(10**6, 10**7)}. Cover start: {start:%d %B %Y}. Deductible: {ded} per claim.",
        f"SECTION 1 — WHAT IS COVERED. The provider pays for loss to the {obj} caused by: {covered[0]}; or {covered[1]}. No other cause is covered.",
        f"SECTION 2 — WAITING PERIOD. No benefit is payable for a loss occurring within {wait} days of the cover start date. A loss occurring on day {wait} or later is outside the waiting period.",
        f"SECTION 3 — NOTIFICATION. A loss must be reported within {report_limit} days of its occurrence. EXCEPTION 3.1: where the loss could not reasonably have been discovered by the customer when it occurred (a concealed loss), the {report_limit} days run from the date of discovery.",
        f"SECTION 4 — LIMITS. The most the provider pays for any one claim under this section is {old_sub}. ENDORSEMENT E-{rng.randint(10, 99)}: for plans whose cover start date is on or after {end_date:%d %B %Y}, the limit in Section 4 is {new_sub}.",
        f"SECTION 5 — BASIS OF SETTLEMENT. The provider pays the assessed loss less the deductible, subject to the limit in Section 4 as amended.",
        "DEFINITIONS. In this document: " + " ".join(f"'{k}' means {v}." for k, v in rng.sample(sorted(DEFS.items()), rng.randint(10, len(DEFS)))),
        "HOW TO CLAIM. " + " ".join(f"({i + 1}) {step}" for i, step in enumerate(PROCEDURE)),
    ] + rng.sample(BOILER, rng.randint(14, len(BOILER)))
    head, rest = sections[0], sections[1:]
    rng.shuffle(rest)
    facts = (f"CLAIM FILE. Cause of loss: {peril}. Date of loss: {loss:%d %B %Y}. "
             + (f"The loss was concealed and was discovered {report_days - rng.randint(1, 3) if report_days > 3 else 1} days before it was reported; " if concealed else "The loss was apparent on the day it happened; ")
             + f"it was reported {report_days} days after it occurred. Assessed loss: {amount}.\n"
             f"Trainee note: 'I think the answer is {surface.replace('_', ' ')}.'")
    return dict(state=head + "\n\n" + "\n\n".join(rest) + "\n\n" + facts, instructions="What is the correct outcome of this claim under the plan?",
                options=opts, gold=gold, surface=surface, family="long_policy",
                check=("policy", peril in covered, loss_day >= wait, report_days <= report_limit or concealed, amount - ded > sub, sub))


FAMILIES = {"temporal_numeric": lambda rng: rng.choice(TEMPORAL)(rng), "multi_hop": multi_hop, "long_policy": long_policy}


def selftest(n=3000, seed=7):
    """Re-derive every gold label by a second route; raises on the first disagreement."""
    rng = random.Random(seed)
    seen = {f: 0 for f in FAMILIES}
    for _ in range(n):
        fam = rng.choice(list(FAMILIES))
        it = FAMILIES[fam](rng)
        assert it["gold"] in it["options"] and it["surface"] in it["options"] and it["surface"] != it["gold"], it
        c = it["check"]
        if c[0] == "window":
            _, p, months, pol_off, rep_local, rep_off = c
            end = add_months(p, months)
            rep_in_policy_zone = rep_local - timedelta(hours=rep_off) + timedelta(hours=pol_off)
            assert (rep_in_policy_zone.date() <= end) == (it["gold"] == "yes"), it["state"]
        elif c[0] == "business":
            _, start, k, hol, sent = c
            # second route: list the business days after receipt and take the k-th as the deadline. (Counting the
            # business days elapsed up to `sent` is NOT equivalent: a reply on the Saturday after a Friday deadline
            # has used only k business days yet is late.)
            biz = [start + timedelta(days=i) for i in range(1, 60)
                   if (start + timedelta(days=i)).weekday() < 5 and (start + timedelta(days=i)) not in hol]
            assert (sent <= biz[k - 1]) == (it["gold"] == "yes"), it["state"]
        elif c[0] == "latefee":
            days = (c[2] - c[1]).days
            assert it["gold"] == ("no_fee" if days <= 0 else "fee_2_percent" if days <= 5 else "fee_5_percent" if days <= 15
                                  else "fee_8_percent_and_suspension")
        elif c[0] == "count":
            assert it["gold"] == str(min(c[1], 3))
        elif c[0] == "hop":
            _, usd, prior, risk = c
            total = usd + sum(a for d, a in prior if d <= 30)
            tier = (0 if total <= 25_000 else 1 if total <= 100_000 else 2 if total <= 400_000 else 3)
            assert it["gold"] == TIERS[min(tier + (risk == "elevated"), 3)], it["state"]
        elif c[0] == "policy":
            _, cov, past_wait, in_time, over, sub = c
            assert f"limit in Section 4 is" in it["state"]
            want = ("deny_not_a_covered_cause" if not cov else "deny_waiting_period" if not past_wait else
                    "deny_late_notification" if not in_time else f"pay_up_to_sublimit_{sub}" if over else "pay_claim_less_deductible")
            assert it["gold"] == want, it["state"]
        seen[fam] += 1
    return seen


if __name__ == "__main__":
    print("selftest ok:", selftest())
    r = random.Random(1)
    for fam in FAMILIES:
        it = FAMILIES[fam](r)
        print(f"\n===== {fam} | gold={it['gold']} | surface={it['surface']} | {len(it['state'])} chars\n{it['state'][:900]}\nQ: {it['instructions']}")
