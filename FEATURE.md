# FEATURE.md -- Contextual Information, Warnings and Split Applications

Features and contextual advisory notes that RB209 describes but that the tool
does not yet surface (or surfaces only partially) in its outputs.  This
document catalogues them by category so they can be incorporated into the
recommendation engine and CLI output.

---

## 1. Nitrogen Application Timing and Split Dressings

RB209 gives detailed guidance on **when** and **how** to apply nitrogen, not
just how much.  The tool currently outputs a single total N figure with no
timing or splitting advice.

### 1.1 Winter Wheat / Triticale (Section 4, Table 4.17 footnotes)

| Total N required | Timing guidance |
|------------------|-----------------|
| Any rate | Apply in one or two dressings during early stem extension |
| > 120 kg N/ha remaining | Half at start of stem extension (not before April); half at least two weeks later (not after early May) |

- For **milling wheat**, extra N for protein should be applied during stem
  extension (GS32-GS39).  Late foliar urea at GS73 can boost protein further
  but not yield.

### 1.2 Winter Barley (Section 4, Table 4.18 footnotes)

| Total N required | Split guidance |
|------------------|---------------|
| < 100 kg N/ha | Single dressing at GS30-31 |
| 100-200 kg N/ha | Two splits: half at late tillering (mid-Feb/early Mar), half at GS30-31 |
| >= 200 kg N/ha | Three splits: 40% late tillering, 40% GS30-31, 20% GS32 |

- Reduce by 25 kg N/ha if the lodging risk is high.

### 1.3 Spring Wheat (Section 4, Table 4.21 footnotes)

| Scenario | Timing |
|----------|--------|
| Drilled before March | N at early stem extension, not before early April or after early May |
| > 70 kg N/ha on non-light soils | First 40 kg N/ha in seedbed; remainder by stem extension |
| > 70 kg N/ha on light sand soils | First 40 kg N/ha at three-leaf stage (not before March); remainder by stem extension |
| Late-drilled | All in seedbed, except on light sands split as above |

### 1.4 Spring Barley (Section 4, Table 4.22)

| Total N required | Split guidance |
|------------------|---------------|
| < 100 kg N/ha | Single dressing by early stem extension, not before late March |
| >= 100 kg N/ha | 40 kg N/ha mid-Feb/early Mar during tillering; remainder split if > 100 kg N/ha remains |

### 1.5 Winter Oilseed Rape (Section 4)

- Autumn N not usually required (already noted in `CROP_INFO`).
- Spring N: recommendations are for spring application only.
- Large canopies (GAI > 2) should have canopy N deducted from recommendation.

### 1.6 Winter Rye (Section 4, Table 4.20)

- Reduce by 25 kg N/ha if lodging risk is high.

### 1.7 Potatoes (Section 5, p. 23)

| Scenario | Timing |
|----------|--------|
| Light sand / shallow soils | Apply ~2/3 N in seedbed; remainder shortly after emergence |
| Other soils | Apply all N in seedbed |
| All | Aim to apply all N by tuber initiation (~3 weeks after 50% emergence) |

- Rain-fed, determinate crops: may reduce N by 15-20 kg N/ha vs irrigated.
- If previous crops had excessive canopy / delayed skin-set problems, reduce N
  towards lower end of range.

### 1.8 Grass Silage (Section 3, Table 3.8 footnotes)

| Situation | Guidance |
|-----------|----------|
| 1st cut > 80 kg N/ha | Split: 40 kg N/ha mid-Feb to early Mar; remainder late Mar to early Apr, at least 6 weeks before cutting |
| 2nd+ cut applications | Apply as soon as possible after the previous cut |
| High SNS | Apply 30 kg N/ha less across the season |
| Low SNS | Apply 30 kg N/ha more across the season |
| Previous growth restricted by drought | Reduce or omit 3rd/4th cut N |
| Following early spring grazing | Reduce 1st-cut recommendation by 25 kg N/ha |

### 1.9 Grazed Grass (Section 3, Table 3.9)

- Monthly split schedule from Jan/Feb through Aug (Table 3.9 gives per-rotation
  rates by target DM yield).
- N after August is usually unproductive (soil organic N mineralisation covers
  demand at that time).
- Check NVZ rules for timing restrictions.
- For drought-affected growth, reduce or omit Jul/Aug applications.

### 1.10 Grass Hay (Section 3, Table 3.10)

- Rates vary by SNS (low/moderate/high): 100 / 70 / 40 kg N/ha per cut.
- Single application per cut.

---

## 2. Regulatory Restrictions and NVZ Warnings

RB209 repeatedly flags regulatory constraints.  The tool does not currently
warn about these.

### 2.1 Nitrate Vulnerable Zones (NVZs)

- **Closed periods** exist for N applications in NVZs (dates vary by crop type
  and material).
- **N max limits** apply in NVZs.  Several recommendation table values (e.g.
  wheat on shallow soils at SNS 0: 280 kg N/ha) exceed the NVZ N-max limit.
  The RB209 tables flag these with footnote "a".
- The N-max limit is calculated for the whole farm area of a crop type, not per
  field.
- NVZ rules apply in England and Scotland; similar rules in Wales.

### 2.2 Farming Rules for Water (England)

- Cover nutrient use generally but particularly N and phosphate.
- Top-dressing to soil surface should be avoided where there is a high risk of
  run-off into neighbouring watercourses.

### 2.3 Application Restrictions (all regions)

- Do **not** apply inorganic fertilisers or organic manures when soils are:
  snow-covered, frozen hard, waterlogged, deeply cracked, or on steeply sloping
  ground adjacent to watercourses.

---

## 3. Split Applications -- Non-Nitrogen

### 3.1 Lime (already partially implemented)

- Maximum single application: **7.5 t CaCO3/ha**.
- The tool already warns when the total exceeds this and advises split
  dressings over successive years.
- **Not yet surfaced:** RB209 advises applying lime well before sensitive crops
  (e.g. potatoes -- avoid liming immediately before potatoes as it increases
  common scab risk).

### 3.2 Potash for Potatoes (Section 5, p. 9)

- When > 300 kg K2O/ha required: apply **half in late autumn/winter** and
  **half in spring**.
- On light sandy soils: all potash after primary cultivation, no sooner than
  late winter.
- Large amounts of potash can reduce tuber dry matter content (consider SOP
  instead of MOP).

### 3.3 Potash for Grass Silage (Section 3, Table 3.3)

- Spring application for 1st cut limited to 80-90 kg K2O/ha to minimise luxury
  uptake.
- Balance of recommended rate applied previous autumn.
- Extra potash after last cut needed at K Index 2- or below:
  - 1-2 cut systems: +60 kg K2O/ha after last cut or by autumn
  - 3-cut systems: +30 kg K2O/ha after cutting
  - 4-cut systems: no extra needed

### 3.4 Phosphate for Cereals (Section 4, p. 21)

- At P Index 0 and 1: apply annually and work into seedbed.
- At P Index 2: can apply when convenient during the year.
- Do not combine-drill more than **150 kg/ha of N + K2O** on sandy soils (risk
  of seedling damage).

### 3.5 Potash for Grazed Grass (Section 3, Table 3.4)

- Where there is a known risk of **hypomagnesaemia** (grass staggers),
  application of potash in spring should be avoided.
- Potash may be applied in one application in June/July, or in several small
  applications during the season.

---

## 4. Crop-Specific Warnings and Contextual Notes

### 4.1 Sugar Beet

- **Excess N reduces sugar content.** Already noted in `CROP_INFO` but could
  also appear as a warning when the N recommendation is high.
- Sensitive to soil acidity -- sample well before the crop.

### 4.2 Potatoes

- **Avoid liming immediately before potatoes** unless soil pH is very low --
  increases common scab risk and manganese deficiency risk.
- Only significant trace element deficiency in potatoes is **manganese (Mn)**,
  which can occur on peaty/organic/sandy soils at high pH or if over-limed.
- **Excess N** in potatoes can:
  - Decrease yield (especially shorter-season indeterminate varieties)
  - Increase haulm size, preventing effective fungicide penetration
  - Delay natural senescence, creating desiccation difficulties
  - Delay skin set
  - Affect target dry matter concentrations
- N requirements vary by **variety determinacy group** (1-4) and **growing
  season length** (<60, 60-90, 90-120, >120 days).  The tool currently uses
  simplified single values; RB209 gives ranges by group/season.

### 4.3 Milling Wheat

- Extra N (+40 kg N/ha vs feed) already implemented.
- Grain protein at economic optimum: ~12% (2.1% N) for bread-making, ~11%
  (1.9% N) for feed.
- If grain protein consistently above/below target, adjust N by 25 kg N/ha per
  0.5% difference.

### 4.4 Malting Barley

- Lower N rates to maintain grain nitrogen spec (1.8% grain N target).
- Already partially noted in `CROP_INFO`.

### 4.5 Winter Oilseed Rape

- Large canopies (GAI > 2) can contain > 100 kg N/ha by spring.  RB209 allows
  deducting all crop N from the recommendation when using the SMN method.
- Canopy assessment by GAI or crop height affects the effective N rate.

### 4.6 Peas and Field Beans

- N-fixing: no fertiliser N required (already implemented -- always returns 0).
- They leave **high N residues** for the following crop (SNS effect).

### 4.7 Grass/Clover Swards

- Any mineral N application **inhibits N fixation** in clover nodules.
- Risk of grass shading out clover if N applied.
- During clover establishment: **no nitrogen** should be applied.
- Red clover and lucerne: no N requirement apart from establishment on low-SNS
  soils (up to 50 kg N/ha).

### 4.8 Forage Maize

- N recommendations in the tool are straightforward, but RB209 cautions that
  forage maize is sensitive to cold soils and late drilling -- N uptake may be
  poor in these conditions.

---

## 5. Organic Material Application Context

### 5.1 Timing Seasons (already partially implemented)

The tool supports `--timing` with seasons and `--incorporated` flag for
available-N calculation.  Additional context from RB209 Section 2:

| Season | Calendar months |
|--------|----------------|
| Autumn | August-October |
| Winter | November-January |
| Spring | February-April |
| Summer | Grassland use only |

- **Summer + incorporated** is N/A for all materials in RB209.
- Composts and paper crumble have no timing factors (flat coefficient only) --
  the tool already rejects `--timing` for these.

### 5.2 Incorporation Windows

| Material type | Incorporation deadline | RB209 Table |
|---------------|----------------------|-------------|
| FYM (cattle, pig, sheep, horse) | Within 24 hours | Table 2.3 |
| Poultry litter / layer manure | Within 24 hours | Table 2.6 |
| Cattle slurry | Within 6 hours | Table 2.9 |
| Pig slurry | Within 6 hours | Table 2.12 |
| Biosolids cake | Within 24 hours | Table 2.15 |

- Prompt incorporation increases retained N, especially for slurries in
  spring (e.g. pig slurry spring incorporated: 60% available N vs 25% surface
  applied).

### 5.3 Contextual Warnings for Organic Applications

- Apply manures **in spring if possible** and incorporate rapidly into the soil.
- Ammonia emissions are substantially reduced by injection, trailing-shoe and
  trailing-hose vs splash-plate/broadcast.
- Organic N applied **after harvest of previous crop** should be deducted from
  the fertiliser N recommendation -- not from the SNS calculation.
- Organic N applied **before SMN sampling** is already accounted for in the
  measured value and should **not** be deducted separately.

---

## 6. Soil and Environmental Warnings

### 6.1 Very Acidic Soils (pH < 5.0)

- Already implemented: warning note added to lime output.
- **Additional context:** soil at this pH may induce trace element deficiencies
  (Mn, Cu) and severely limit crop growth.

### 6.2 Over-liming

- Avoid liming grassland fields above pH 7 as this can induce deficiencies of
  copper, cobalt and selenium affecting livestock.
- Manganese deficiency more likely on any soil with pH > 7.5; sandy soils with
  pH > 6.5; organic/peaty/marshland soil with pH > 6.0.

### 6.3 Organic / Peat Soils

- SNS tables for organic soils show "Consult a FACTS Qualified Adviser" for
  SNS indices 3-6.
- Peat soils: "Consult a FACTS Qualified Adviser" for SNS 4-6.
- Table 4.6 (grass ley SNS) does **not** cover organic soils (already
  enforced in engine).
- The SMN Measurement Method is **not** recommended for peat soils.

### 6.4 Hypomagnesaemia (Grass Staggers)

- At Mg Index 0 on grassland: apply 50-100 kg MgO/ha every 3-4 years.
- Maintain herbage Mg > 0.20% DM and K:Mg ratio < 20:1.
- Avoid applying potash in spring where there is a known risk.

### 6.5 Sodium Deficiency in Grassland

- Minimum dietary Na for livestock: 0.15% DM.
- If Na < 0.15% or K:Na > 20:1, mineral supplements or Na-containing
  fertiliser may be needed.

---

## 7. Yield Adjustment Guidance

RB209 provides guidance on adjusting recommendations based on expected yield,
which the tool does not currently support.

### 7.1 Winter Wheat

- Adjust by +/- 10 kg N/ha per 0.5 t/ha difference from the 8 t/ha baseline,
  up to a maximum of 13 t/ha.

### 7.2 Potash for Potatoes

- Adjust K2O at target Index by 5.8 kg K2O per tonne difference from 50 t/ha
  expected yield.

### 7.3 Phosphate and Potash for Cereals

- Adjust by offtake per tonne using Table 4.12 values (e.g. winter wheat
  grain + straw: 7.0 kg P2O5/t, 10.5 kg K2O/t).

### 7.4 Winter Oats

- N adjusts by 20 kg N/ha per 1 t/ha change in expected yield (Table 4.19).

### 7.5 Grass

- Recommendations are by target DM yield class, which already implicitly
  adjusts for productivity.

---

## 8. Economic Adjustment (Break-Even Ratio)

- Wheat and barley N recommendations are based on a break-even ratio of **5.0**
  (cost of fertiliser N in GBP/kg N divided by grain value in GBP/kg).
- Tables 4.25 and 4.26 provide adjustments for different ratios.
- Not currently implemented; could be offered as an optional `--ber` parameter.

---

## 9. SNS Adjustments Not Yet Surfaced

### 9.1 Manure History Adjustment

- Where regular organic manure applications have been made to previous crops,
  increase the SNS Index by 1-2 levels depending on type, rate and frequency.

### 9.2 Vegetable Rotation Persistence

- On medium/deep silty/deep clayey soils, N residues from vegetable rotations
  can persist for several years, especially in drier areas.  May need upward
  SNS adjustment.

### 9.3 Cover Crops

- If a cover crop was sown in autumn and grew well over winter, the SNS Index
  should be increased.

### 9.4 Previous Crop Failure

- If the previous crop failed (drought, disease), nitrogen residues may be
  higher than normal -- increase the SNS Index.

---

## 10. Summary: Features Not Yet Implemented

| Feature | RB209 Source | Priority | Complexity |
|---------|-------------|----------|------------|
| N timing / split dressing advice per crop | S3 pp.14-15, S4 pp.26-31, S5 p.23 | High | Medium |
| NVZ N-max warnings | S4 Table 4.17/4.18 footnotes | High | Low |
| Potash split for potatoes (>300 kg K2O/ha) | S5 p.9 | Medium | Low |
| Potash split for grass silage | S3 Table 3.3 footnotes | Medium | Low |
| Avoid liming before potatoes warning | S5 p.11 | Medium | Low |
| Yield adjustment for N/P/K | S4 p.26, S5 p.8 | Medium | Medium |
| Potato variety group / season length N ranges | S5 Table 5.10 | Medium | High |
| Economic break-even ratio adjustment | S4 Tables 4.25-4.26 | Low | Medium |
| Manure history SNS adjustment note | S4 p.11 | Low | Low |
| Hypomagnesaemia warning for grassland K | S3 p.10 | Low | Low |
| Over-liming trace element warning | S1 p.14, S3 p.18 | Low | Low |
| Clover sward N-fixation inhibition warning | S3 p.16 | Low | Low |
| Organic application condition restrictions | S1 p.6 | Low | Low |
| Seedbed N+K2O combine-drill limit (150 kg/ha) | S4 p.21 | Low | Low |
