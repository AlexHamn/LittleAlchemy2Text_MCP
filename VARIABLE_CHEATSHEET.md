# Little Alchemy 2 Text MCP - Variable Cheatsheet

## 🔧 Shortened Request Parameter Names

This cheatsheet explains all the super-short variable names used in the Little Alchemy 2 Text MCP API requests to minimize typing and improve efficiency.

### 🎮 Core Game Tools

#### `start_game` Tool Parameters

| Short Name | Full Name      | Description                            | Example        |
| ---------- | -------------- | -------------------------------------- | -------------- |
| `sid`      | session_id     | Unique 6-digit game session identifier | `"123456"`     |
| `mode`     | game_mode      | Game mode (open-ended/targeted)        | `"open-ended"` |
| `rounds`   | max_rounds     | Maximum combination attempts           | `15`           |
| `type`     | reasoning_type | Reasoning approach being used          | `"logical"`    |

#### `get_game_state` Tool Parameters

| Short Name | Full Name  | Description                     | Example    |
| ---------- | ---------- | ------------------------------- | ---------- |
| `sid`      | session_id | 6-digit game session identifier | `"123456"` |

#### `make_move` Tool Parameters

| Short Name | Full Name             | Description                        | Example                             |
| ---------- | --------------------- | ---------------------------------- | ----------------------------------- |
| `sid`      | session_id            | Game session identifier            | `"123456"`                          |
| `i1`       | item1                 | First item to combine              | `"air"`                             |
| `i2`       | item2                 | Second item to combine             | `"fire"`                            |
| `r`        | reasoning_explanation | Why you're trying this combination | `"Air + fire should create energy"` |

#### `end_game` Tool Parameters

| Short Name | Full Name  | Description                            | Example    |
| ---------- | ---------- | -------------------------------------- | ---------- |
| `sid`      | session_id | 6-digit game session identifier to end | `"123456"` |

### 📊 Logging & Analysis Tools

#### `get_attempt_logs` Tool Parameters

| Short Name | Full Name  | Description             | Example                        |
| ---------- | ---------- | ----------------------- | ------------------------------ |
| `sid`      | session_id | Game session identifier | `"123456"`                     |
| `fmt`      | format     | Output format           | `"summary"`, `"json"`, `"csv"` |

#### `get_session_logs` Tool Parameters

| Short Name | Full Name  | Description                        | Example                        |
| ---------- | ---------- | ---------------------------------- | ------------------------------ |
| `sid`      | session_id | Game session identifier (optional) | `"123456"`                     |
| `fmt`      | format     | Output format                      | `"summary"`, `"json"`, `"csv"` |

## 📋 Internal Logging Variable Names

### Attempt Log Fields (per combination attempt)

| Short Name | Full Name               | Description                           |
| ---------- | ----------------------- | ------------------------------------- |
| `sid`      | session_id              | Session identifier                    |
| `att_n`    | attempt_number          | Sequential attempt number             |
| `e1`       | element1                | First element in combination          |
| `e2`       | element2                | Second element in combination         |
| `ok`       | success                 | Whether combination succeeded         |
| `res`      | result_element          | Item(s) created (if successful)       |
| `inv_b4`   | inventory_size_before   | Inventory size before attempt         |
| `reason`   | reasoning_explanation   | Player's reasoning                    |
| `novel`    | is_novel                | Whether combination was tried before  |
| `str_typ`  | streak_type             | Current streak type (success/failure) |
| `str_len`  | streak_length           | Current streak length                 |
| `t_since`  | time_since_last_success | Seconds since last success            |

### Session Log Fields (per game session)

| Short Name  | Full Name              | Description                  |
| ----------- | ---------------------- | ---------------------------- |
| `sid`       | session_id             | Session identifier           |
| `r_typ`     | reasoning_type         | Player's reasoning approach  |
| `start`     | start_time             | Session start timestamp      |
| `end`       | end_time               | Session end timestamp        |
| `tot_att`   | total_attempts         | Total combination attempts   |
| `succ_att`  | successful_attempts    | Successful combinations only |
| `elem_disc` | elements_discovered    | Total unique items found     |
| `final_inv` | final_inventory_size   | Items in final inventory     |
| `disc_rate` | discovery_rate         | Success percentage           |
| `max_succ`  | longest_success_streak | Best consecutive successes   |
| `max_fail`  | longest_failure_streak | Worst consecutive failures   |
| `plateaus`  | plateau_count          | Learning plateau periods     |

## 🚀 Quick Reference Examples

### Starting a Game

```json
{
  "tool": "start_game",
  "arguments": {
    "sid": "654321",
    "mode": "open-ended",
    "rounds": 20,
    "type": "creative"
  }
}
```

### Making a Move

```json
{
  "tool": "make_move",
  "arguments": {
    "sid": "654321",
    "i1": "air",
    "i2": "fire",
    "r": "Air feeds fire to create energy"
  }
}
```

### Getting Logs

```json
{
  "tool": "get_attempt_logs",
  "arguments": {
    "sid": "654321",
    "fmt": "csv"
  }
}
```

## 💡 Why Super Short Names?

1. **Faster Typing** - Reduce API call complexity
2. **Less Bandwidth** - Smaller JSON payloads
3. **Easier Integration** - Simpler for LLM agents
4. **Consistent Logging** - Uniform short names throughout system
5. **Research-Friendly** - Compact CSV exports for analysis

## 🔄 Backward Compatibility

The system internally converts short names to full names, so all existing functionality remains intact while providing the convenience of abbreviated parameters.

---

_Last Updated: Generated for Little Alchemy 2 Text MCP with super-short variable names_
