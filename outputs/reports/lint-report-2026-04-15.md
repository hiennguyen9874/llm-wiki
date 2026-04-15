---
title: "Wiki Lint Report — 2026-04-15"
created: 2026-04-15
last_updated: 2026-04-15
source_count: 0
status: completed
page_type: report
tags: [maintenance, lint, review]
domain: knowledge-management
---

# Wiki Lint Report — 2026-04-15

Automated lint scan of `wiki/` layer. Run: monthly review pass.

## Summary

| Metric | Count |
|--------|-------|
| Total wiki pages | 26 |
| Source pages | 6 |
| Topic/concept pages | 3 |
| Entity pages | 5 |
| Organization pages | 3 |
| Person pages | 5 |
| Bases | 2 |
| Canvases | 2 |
| Broken wikilinks | **0** ✅ |
| Pages with Evidence/claims structure | **0** ⚠️ |
| Pages missing lifecycle fields | 3 |

---

## 🔴 Errors

### None detected

No hard errors (broken links, missing frontmatter blocks, invalid metadata) were found.

---

## 🟡 Warnings

### 1. Missing Lifecycle Metadata on System Pages
**Severity:** Medium  
**Pages:** `home.md`, `index.md`, `log.md`

These three system pages are missing recommended lifecycle fields:
- `retention_class` (recommended values: `foundational` for index, `durable` for log, `transient` for home)
- `confidence_score`
- `visibility` (recommend `shared` for index, `private` for log)

**Suggested fix (safe — auto-fixable):**
```yaml
# For index.md
retention_class: foundational
visibility: shared

# For log.md  
retention_class: durable
visibility: private

# For home.md
retention_class: transient
visibility: shared
```

### 2. No Evidence/Claims Structure on Any Page
**Severity:** Medium  
**Pages:** All 26 wiki pages

Zero pages currently use the lightweight `## Evidence / claims` structure recommended in `llm-wiki-core`. This makes it harder to:
- Track claim-level confidence
- Resolve contradictions between sources
- Audit provenance of specific assertions

**High-value pages that should add Evidence/claims sections:**
1. `kinh-te-vi-mo-viet-nam-q2-2026.md` — central synthesis page with multiple source inputs
2. `gia-xang-dau-va-tac-dong-kinh-te.md` — contains important claim-level contradictions (oil peak debate)
3. `entity-46-ngan-hang-thuong-mai.md` — key claims about banking sector liquidity
4. `concept-tien-gui-kho-bac-nha-nuoc.md` — central mechanism for interest rate policy
5. `person-thai-pham.md` — contains contradictory oil price predictions vs. ĐTDT 13/4

### 3. Source Pages Not Integrated into Topic Pages
**Severity:** Low-Medium  
**Pages affected:** Some source pages may be under-linked from the main synthesis

The macro synthesis page (`kinh-te-vi-mo-viet-nam-q2-2026.md`) has 41 wikilinks — good integration. However, several source pages are primarily cited by the index rather than being deeply woven into concept/topic pages:

- `source-ban-tron-dau-tu-q2-2026.md` — cited mainly by index and oil page
- `source-thai-pham-12-4-2026.md` — linked from macro page but oil contradiction not tracked
- `source-luong-huynh-9-4-2026.md` — investment strategy claims not cross-linked to specific stock entity pages

### 4. Unresolved Contradiction on Oil Price
**Severity:** Medium  
**Pages:** `gia-xang-dau-va-tac-dong-kinh-te.md`, `source-thai-pham-12-4-2026.md`, `source-dtdt-13-4-2026.md`

**Contradiction:** 
- **Thái Phạm (12/4/2026):** "Dầu đã tạo đỉnh ngắn hạn"
- **ĐTDT 13/4/2026:** Brent $102.80, WTI $104.88 — dầu bật mạnh, vượt $100

This contradiction is noted in the canvas but not formally tracked in the wiki pages with claim-level metadata.

---

## 🔵 Info

### 1. Good Wikilink Health
**Status:** ✅ Healthy

All wikilinks resolve to existing pages. No broken internal links detected.

Notable working links:
- `source-quang-dung-10-4-2026` → 37 outgoing references (highest)
- `Ngân-hàng-Nhà-nước` → 21 incoming references
- `kinh-te-vi-mo-viet-nam-q2-2026` → 19 incoming references

### 2. Well-Structured Source Pages
All 6 source pages have:
- ✅ Required frontmatter (`title`, `created`, `last_updated`, `source_count`, `status`, `page_type`, `importance`)
- ✅ Source attribution with `source_file` pointing to raw/
- ✅ `source_type` (video, transcript, etc.)
- ✅ Good internal linking to related wiki pages

### 3. Good Coverage of Key Concepts
Strong concept pages exist for:
- `concept-tien-gui-kho-bac-nha-nuoc` — 13 wikilinks
- `concept-thong-tu-22-2019` — 10 wikilinks
- `concept-nghi-quyet-42` — 7 wikilinks

### 4. Bases and Canvases Status
**Bases:**
- `inbox.base` — References `raw/inbox/` folder (currently empty)
- `review.base` — Well-configured with status filters for `draft`, `needs_update`, `claim_status`

**Canvases:**
- `home.canvas` — Basic workflow overview, links to `raw/README.md` (missing file)
- `kinh-te-vi-mo-q2-2026.canvas` — Rich visual synthesis with 40 nodes, well-connected

### 5. No Duplicate Pages Detected
QMD semantic search found no significant duplicate or near-duplicate content.

### 6. No Orphan Pages
All 26 wiki pages have at least one incoming link from the index or other wiki pages.

### 7. Retention Check
**Status:** N/A — no `retention_class` fields populated yet.

Most pages are effectively "new" (created 2026-04-14/15). Recommend:
- Set `retention_class: durable` for topic/synthesis pages
- Set `retention_class: episodic` for source pages
- Set `first_seen: 2026-04-14` (or actual date) and `last_confirmed: 2026-04-14`

---

## ✅ Auto-Fixes Applied

None — all detected issues require human judgment or structural changes.

**Safe fixes that could be applied without review:**
1. Add `retention_class`, `visibility`, `confidence_score` to `home.md`, `index.md`, `log.md`
2. Add a callout noting the oil price contradiction in `gia-xang-dau-va-tac-dong-kinh-te.md`

---

## 📋 Recommended Actions

### High Priority
1. **Add Evidence/claims structure** to `kinh-te-vi-mo-viet-nam-q2-2026.md` — this is the central synthesis and should track claim provenance
2. **Add formal contradiction tracking** for the oil price dispute (Thái Phạm vs. ĐTDT 13/4)
3. **Populate retention metadata** on all pages — especially `first_seen`, `last_confirmed`, `retention_class`

### Medium Priority
4. **Cross-link stock picks** from `source-luong-huynh-9-4-2026` to entity pages for those stocks (or create entity pages for FPT, MWG, STB, HHV, etc.)
5. **Add `wiki/canvases/kinh-te-vi-mo-q2-2026.canvas` to Obsidian** — the canvas has richer structure than the markdown page in places
6. **Review `source-ban-tron-dau-tu-q2-2026`** — this source predates the other sources and may need `superseded_by` links

### Low Priority
7. **Create `raw/README.md`** — `home.canvas` references it but it doesn't exist
8. **Add aliases** to entity pages for better search (e.g., `BIDV` → `entity-bidv`)
9. **Review `importance` on source pages** — all sources marked `high` importance; consider differentiation

---

## 🔍 Knowledge Gaps (3)

### 1. Banking Sector Capital Adequacy Details
The `concept-thong-tu-22-2019` page exists but lacks detailed breakdowns of CAR ratios, LDR calculations, and historical compliance data. No dedicated entity pages for key private banks (Techcombank, VPBank, ACB, MB) despite frequent citations.

### 2. International Geopolitical Context
Pages reference `Iran`, `Mỹ`, `Nga`, `Saudi-Arabia`, `Fed` as entities but have no dedicated pages. The oil transmission model needs explicit geopolitical risk pages.

### 3. Investment Sector Analyst Coverage
Stock-picking strategies cite specific tickers (FPT, MWG, STB, HHV, VHC, ACB) but there are no entity pages for these companies. The investment theme lacks a dedicated synthesis page.

---

## 📚 Next Sources to Ingest (3)

### 1. Vietnam GDP and IIP Official Data (Q1/2026)
**Rationale:** Multiple sources cite GDP 7.83% and IIP 6.9% for Q1/2026, but no official government statistical release is captured. The official source would resolve discrepancies and provide confidence for macro claims.

### 2. NHNN Press Releases on Interest Rate Policy
**Rationale:** The 46-bank interest rate consensus (9/4/2026) is cited but not linked to official NHNN documentation. An official press release would strengthen the liquidity crisis narrative.

### 3. FTSE Russell Vietnam Market Update
**Rationale:** Sources mention FTSE Russell nâng hạng (21/9 deadline) but no dedicated source page exists. Official FTSE documentation would clarify the nâng hạng criteria and implications.

---

## 📦 Consolidation Candidates (3)

### 1. Oil Price Transmission Model
**Files:** `gia-xang-dau-va-tac-dong-kinh-te.md`, `source-thai-pham-12-4-2026.md` (partial), `source-dtdt-13-4-2026.md` (partial)

**Issue:** The two-channel model (gasoline→CPI, diesel→PPI) is documented in `gia-xang-dau-va-tac-dong-kinh-te.md` but oil price forecasts and geopolitical scenarios are scattered across source pages.

**Recommendation:** Create a dedicated `concept-gia-dau-the-gioi.md` page that integrates:
- The transmission model (from gia-xang-dau-va-tac-dong-kinh-te)
- Price forecasts from all sources
- Geopolitical scenarios
- Formal contradiction tracking

### 2. Banking Sector Overview
**Files:** `entity-46-ngan-hang-thuong-mai.md`, `concept-tien-gui-kho-bac-nha-nuoc.md`, `organization-ngan-hang-nha-nuoc.md`, individual bank pages

**Issue:** Banking sector content is fragmented across 9+ pages. Cross-references exist but a dedicated `topic-ngan-hang-viet-nam.md` page would consolidate:
- Banking system structure (46 banks)
- Policy mechanisms (Tiền gửi Kho bạc, Thông tư 22/2019, Nghị quyết 42)
- Central bank role
- State bank specifics

### 3. Investment Strategy Synthesis
**Files:** `source-quang-dung-10-4-2026.md`, `source-luong-huynh-9-4-2026.md`, `source-thai-pham-12-4-2026.md` (partial), `source-dtdt-13-4-2026.md` (investment section)

**Issue:** Investment recommendations are spread across multiple source pages with overlapping themes (market outlook, stock picks, risk management) but no consolidated synthesis.

**Recommendation:** Create `topic-chien-luoc-dau-tu-viet-nam-q2-2026.md` to synthesize:
- Market outlook (wave scenarios)
- Sector priorities
- Stock-specific recommendations
- Contradictions between analysts

---

## 📝 Log Entry

```markdown
## [2026-04-15] lint | Full wiki lint pass
- Ran QMD + file analysis across wiki/ (26 pages, 2 bases, 2 canvases)
- Found 0 broken wikilinks ✅
- Found 0 pages with Evidence/claims structure ⚠️
- Found 3 system pages missing lifecycle metadata
- Found 1 unresolved contradiction (oil price: Thái Phạm vs ĐTDT 13/4)
- Suggested 3 gaps, 3 next sources, 3 consolidation targets
- Saved report to outputs/reports/lint-report-2026-04-15.md
```

---

*Report generated: 2026-04-15*  
*Skills activated: llm-wiki-core, llm-wiki-maintenance, qmd, obsidian-markdown*  
*Tool: pi coding agent*
