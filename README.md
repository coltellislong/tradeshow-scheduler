# tradeshow-scheduler

CLI tool to track upcoming tradeshows and their associated needs.

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Add a tradeshow
tradeshow add "CES 2026" "Las Vegas" 2026-01-07 2026-01-10 --booth A42

# List all tradeshows
tradeshow list

# List only upcoming, with needs details
tradeshow list -u -v

# Show details for a specific tradeshow
tradeshow show <id>

# Delete a tradeshow
tradeshow delete <id>

# Add a need to a tradeshow
tradeshow add-need <show_id> "Order banners" -p high -a "Alice"

# Mark a need as completed
tradeshow complete-need <show_id> <need_id>

# Remove a need
tradeshow remove-need <show_id> <need_id>
```

## Need Priorities

`low` | `medium` (default) | `high` | `critical`

## Data Storage

Data is stored in `~/.tradeshow-scheduler/data.json`.

## Running Tests

```bash
pip install pytest
pytest
```
