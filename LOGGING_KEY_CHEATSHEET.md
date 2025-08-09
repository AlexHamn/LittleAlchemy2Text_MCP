# Logging Key Cheatsheet

This document maps the original (long) logging key names to their new shortened versions for character savings.

## 📋 Attempt Log Keys

| Original Key              | New Key   | Description                            | Chars Saved |
| ------------------------- | --------- | -------------------------------------- | ----------- |
| `Session_ID`              | `sid`     | Unique game session identifier         | 7           |
| `Attempt_Number`          | `att_n`   | Sequential attempt number (1, 2, 3...) | 9           |
| `Element_1`               | `e1`      | First element in combination           | 7           |
| `Element_2`               | `e2`      | Second element in combination          | 7           |
| `Success`                 | `ok`      | Whether the combination succeeded      | 5           |
| `Result_Element`          | `res`     | Created element(s) if successful       | 11          |
| `Inventory_Size_Before`   | `inv_b4`  | Number of items before this attempt    | 14          |
| `Reasoning_Explanation`   | `reason`  | Player's reasoning for the attempt     | 14          |
| `Is_Novel_Combination`    | `novel`   | First time trying this combination     | 13          |
| `Current_Streak_Type`     | `str_typ` | Current streak type                    | 11          |
| `Current_Streak_Length`   | `str_len` | Length of current streak               | 13          |
| `Time_Since_Last_Success` | `t_since` | Seconds since last successful attempt  | 14          |

**Total savings per attempt log entry: ~130+ characters**

## 🎯 Session Log Keys

| Original Key             | New Key       | Description                              | Chars Saved |
| ------------------------ | ------------- | ---------------------------------------- | ----------- |
| `Session_ID`             | `sid`         | Unique identifier for each session       | 7           |
| `Reasoning_Type`         | `r_typ`       | Cognitive approach categorization        | 9           |
| `Start_Time`             | `start`       | Session start timestamp                  | 5           |
| `End_Time`               | `end`         | Session end timestamp                    | 5           |
| `Start_Timestamp`        | `start_ts`    | Session start timestamp (Unix)           | 8           |
| `End_Timestamp`          | `end_ts`      | Session end timestamp (Unix)             | 9           |
| `Total_Attempts`         | `tot_att`     | All combination attempts made            | 7           |
| `Successful_Attempts`    | `succ_att`    | Number of successful combinations        | 11          |
| `Elements_Discovered`    | `elem_disc`   | Total unique items found                 | 9           |
| `Final_Inventory_Size`   | `final_inv`   | Items remaining at session end           | 11          |
| `Discovery_Rate`         | `disc_rate`   | Success percentage (successful/total)    | 5           |
| `Longest_Success_Streak` | `max_succ`    | Maximum consecutive successes            | 13          |
| `Longest_Failure_Streak` | `max_fail`    | Maximum consecutive failures             | 13          |
| `Plateau_Count`          | `plateaus`    | Periods of 5+ attempts without discovery | 5           |
| `Last_Discovery_Time`    | `last_disc_t` | Timestamp of last successful discovery   | 9           |

**Total savings per session log entry: ~126+ characters**

## 🔧 Internal Keys (Unchanged)

These keys remain the same as they are internal and don't affect log size significantly:

| Key          | Description                         |
| ------------ | ----------------------------------- |
| `_timestamp` | Internal timestamp for calculations |
| `_datetime`  | Human-readable timestamp            |

## 💡 Quick Reference

### Most Common Patterns:

- **Boolean success**: `Success` → `ok`
- **Elements**: `Element_1/Element_2` → `e1/e2`
- **Counts/Numbers**: `*_Number/*_Count` → `*_n/*s` (abbreviated)
- **Sizes**: `*_Size` → `*` (removed suffix)
- **Times**: `*_Time` → `*` or `*_t` (shortened)
- **Streaks**: `*_Streak` → `max_*` (more descriptive)

### Memory Aids:

- `ok` = success (shorter than "Success")
- `e1`/`e2` = element 1/2
- `att_n` = attempt number
- `inv_b4` = inventory before
- `str_typ`/`str_len` = streak type/length
- `t_since` = time since (last success)

## 📈 Impact Summary

- **Per attempt log**: ~130 characters saved
- **Per session log**: ~126 characters saved
- **Typical 50-attempt game**: ~6,500+ characters saved
- **CSV headers**: Significant reduction in repeated header overhead

---

_Last updated: After key shortening implementation_
_Version: 1.0_
