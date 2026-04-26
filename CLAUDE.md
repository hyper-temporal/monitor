# Cyber Observability Tool — Project Guidelines

## Project Overview
Personal network observability tool: monitor & control outbound traffic from your PC.
- **Backend**: Python, tcpdump/libpcap, SQLite
- **Frontend**: PyQt (direct IPC, no network)
- **Scope**: Single machine, security-first

---

## Architecture

```
Backend (Python)
├── Network Capture: tcpdump/libpcap parser
├── Process Enrichment: PID → executable, user
├── Analysis: DNS resolution, port info, rules
├── Storage: SQLite
└── IPC Interface: Direct Python API (no HTTP)
    ↓
PyQt Frontend (same process or subprocess)
├── Display live connections
├── Query history
└── Send control signals (block/allow)
```

---

## Code Organization

```
cyb/
├── backend/
│   ├── capture.py        # tcpdump parser
│   ├── process.py        # PID → executable, user (lsof enrichment)
│   ├── storage.py        # SQLite CRUD & schema
│   ├── rules.py          # Rule matching engine
│   ├── api.py            # IPC interface (backend public API)
│   ├── config.py         # Configuration management (.env)
│   ├── logger.py         # Logging setup
│   ├── export.py         # Data export (JSON, CSV, SQL dump)
│   ├── analytics.py      # Connection analysis & aggregation
│   ├── ip_intel.py       # IP intelligence (service mapping)
│   └── backend_daemon.py # Entry point (packet capture + enrichment)
├── frontend/
│   ├── main.py           # PyQt app (real-time display + rule creation)
│   └── frontend_app.py   # Entry point (GUI launcher)
├── tests/
│   ├── test_capture.py   # Parser tests
│   ├── test_rules.py     # Rule matching tests
│   ├── test_storage.py   # Storage CRUD tests
│   └── test_tcpdump.py   # Test/explore tcpdump behavior
├── requirements.txt
├── CLAUDE.md
└── README.md
```

---

## Design Principles

### **KISS** (Keep It Simple, Stupid)
- No abstraction layers you don't need yet
- No framework boilerplate
- Direct, readable code over clever patterns
- When in doubt, the simpler solution wins

### **DRY** (Don't Repeat Yourself)
- **Single source of truth for test data**: Use `fixtures.py`, not hardcoded values
- **Configuration**: Use `config.yaml` for runtime settings, `fixtures.py` for test constants
- **No copy-paste**: Extract common logic into reusable functions
- **Schema management**: Single definition in `storage.py`

### **SOC** (Separation of Concerns)
- **capture.py**: Only parse tcpdump/libpcap (no assumptions about structure)
- **process.py**: Only map PIDs to metadata
- **storage.py**: Only query/store (schema lives here)
- **rules.py**: Only evaluate rules (agnostic to storage)
- **config.py**: Load/access configuration
- **fixtures.py**: Test data constants
- **api.py**: IPC interface (backend public surface)
- **ui/**: Only render (PyQt)

### **SOLID Principles**

**S - Single Responsibility**: Each class/function does one thing
- Example: `RuleEngine` evaluates rules; `Storage` persists them

**O - Open/Closed**: Open for extension, closed for modification
- Parser accepts configurable `field_map` instead of hardcoded paths

**L - Liskov Substitution**: Subtypes are substitutable
- Future rule types can extend `Rule` protocol

**I - Interface Segregation**: Depend on specific interfaces, not fat ones
- Don't force capture.py to depend on storage internals

**D - Dependency Inversion**: Depend on abstractions, not implementations
- Parser accepts `field_map` dict, not hardcoded JSON structure

### **Data-Driven, Not Hardcoded**
- **No magic values in code**: IPs, ports, executables → `fixtures.py`
- **No assumptions about format**: Field paths in tcpdump JSON → `field_map` parameter
- **Configuration externalized**: Runtime settings → `config.yaml`
- **Tests self-contained**: Use fixtures, not external files

### **Security First**
- No network sockets (direct IPC only)
- Minimal dependencies
- All data stays local (SQLite)
- Clear separation: capture → enrich → display

### **IPC Over HTTP**
- Use `queue.Queue` or `multiprocessing.Queue` for backend → frontend
- Callbacks for frontend → backend (signal/slot pattern in PyQt)
- No serialization overhead, no network exposure

---

## Data Model (Minimal)

```python
# Connection: a single network flow
{
    "id": "uuid",
    "timestamp": "2026-04-25T12:34:56Z",
    "src_ip": "192.168.1.100",
    "dst_ip": "8.8.8.8",
    "dst_port": 53,
    "protocol": "UDP",
    "pid": 1234,
    "exe": "/usr/bin/chrome",
    "user": "cami",
    "status": "allowed|blocked|pending"
}

# Rule: block/allow based on destination
{
    "id": "uuid",
    "action": "allow|block",
    "dst_ip": "8.8.8.8" | null,
    "dst_port": 443 | null,
    "exe": "/usr/bin/chrome" | null,
    "created": "2026-04-25T12:34:56Z"
}
```

---

## Development Workflow

1. **Start with capture**: Parse tcpdump output, write tests
2. **Add enrichment**: Map PIDs to executables
3. **Add storage**: SQLite schema, simple queries
5. **Build UI**: PyQt displays data, sends control signals
6. **Iterate**: Test edge cases, refine rules

---

## Dependencies (Minimal)

```
pyqt5>=5.15.0
pyshark>=0.6  # or parse tcpdump JSON directly
sqlite3       # stdlib
dataclasses   # stdlib (Python 3.7+)
pytest>=7.0   # dev only
```

---

## Testing Strategy

- **Unit tests**: Pure functions (rules, parsing, enrichment)
- **Integration tests**: Capture + storage together
- **No UI tests** unless you have time
- Use pytest, avoid mocking internals

---

## Priority Checklist

- [ ] tcpdump/libpcap parsing with sample data
- [ ] Process enrichment (PID → exe)
- [ ] SQLite schema & basic queries
- [ ] Rule matching logic
- [ ] PyQt UI scaffold
- [ ] Real-time display
- [ ] Control signals (block/allow)

