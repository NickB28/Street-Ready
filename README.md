# Street-Ready
Software for my portfolio

Hello, I am Nick Britto. I am learning how to code by building a real project every week for 12 months.

My goal is to build software that helps me create a strong portfolio.

# Weekly Log

| Week | Topic | Link | Status |
|------|-------|------|--------|
| 01 | Git, Python, pytest: password strength checker | [week-01](week-01/) | Done |
| 02 | Bash: file tidy and backup tool | [week-02](week-02/) | Done |
| 03 | Python: sgdfx CLI for MAS SGD/USD rates, with CI | - | In progress |

## How to run Week 01

Windows PowerShell:

```powershell
git clone https://github.com/NickB28/Street-Ready.git
cd Street-Ready
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python week-01/pwcheck.py
pytest
```

macOS / Linux:

```bash
git clone https://github.com/NickB28/Street-Ready.git
cd Street-Ready
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 week-01/pwcheck.py
pytest
```

## How to run Week 02

See [week-02/README.md](week-02/README.md) for install steps, commands and tests.