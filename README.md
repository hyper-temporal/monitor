# Cyber Observability Tool

Real-time network monitoring for macOS. Capture packets, identify processes.

## Quick Start

```bash
# Terminal 1: Backend (packet capture with sudo)
sudo python backend/backend_daemon.py --interface any

# Terminal 2: Frontend (GUI, normal user)
python frontend/frontend_app.py
```

## Features

- 🔍 **Real-time packet capture** - See all network traffic
- 📍 **IP identification** - Know what services you're connecting to
- 🔴 **Suspicious detection** - Automatically highlights unusual activity
- 📊 **Analytics** - Group connections by IP, see activity patterns
- 💾 **Export** - JSON, CSV, SQL dumps with one click

## Project Structure

```
.
├── backend/backend_daemon.py          # Start here (with sudo)
├── frontend/            # Start here (normal user)
├── backend/                   # Core logic
│   ├── capture.py             # tcpdump parser
│   ├── storage.py             # SQLite database
│   ├── process.py             # Process enrichment (lsof)
│   ├── ip_intel.py            # IP identification
│   ├── analytics.py           # Aggregation
│   ├── api.py                 # IPC interface
│   ├── config.py              # Configuration
│   └── logger.py              # Logging
├── frontend/                  # PyQt5 GUI
│   └── main.py                # Display, search, export
├── tests/                     # Unit tests
├── tools/                     # Utilities and scripts
├── docs/                      # Detailed documentation
├── .env                       # Configuration
└── pyproject.toml             # Dependencies
```

## Documentation

- **`QUICKSTART.md`** - Get running in 5 minutes
- **`DETECTION_GUIDE.md`** - How to spot suspicious activity
- **`ANALYTICS_GUIDE.md`** - Using the analytics dashboard
- **`DATA_MANAGEMENT.md`** - Export, backup, clear data
- **`SPLIT_PROCESS_ARCHITECTURE.md`** - How it works under the hood

See `docs/` directory for all guides.

## Tools

```bash
# Export database
python tools/export_data.py --format json --output backup.json
python tools/export_data.py --stats

# Discover environment
python tools/discover.py

# Old all-in-one version (for reference)
sudo python tools/demo.py --interface any
```

## Configuration

Edit `.env`:

```bash
CAPTURE_INTERFACE=any              # Network interface
CAPTURE_PACKET_COUNT=0             # 0 = unlimited
DB_PATH=/tmp/cyb.db                # Database location
LOG_LEVEL=INFO                     # Logging verbosity
```

## Security

- **Backend** runs with `sudo` (packet capture only)
- **Frontend** runs as normal user (no privileges)
- **Database** is world-writable (accessible by both)
- **No network** exposure (local SQLite only)
- **No logs** written to disk (stdout only)

## Requirements

- Python 3.8+
- PyQt5 (`pip install PyQt5`)
- macOS (uses tcpdump, lsof)
- Network admin privileges (for tcpdump)

## License

Personal use.
