# Street-Ready
Software for my portfolio
Hello, I am Nick Britto. I am learning how to code by building a real project every week for 12 months.

My goal: My goal is to develop a software which will help me creating my portfolio.

# Weekly Log

| Week | Topic | Link | Status |
|------|-------|------|--------|
| 01 | Git, Python, pytest: password strength checker | [week-01](week-01/) | Done |
| 02 | Bash: file tidy and backup tool | [week-02](week-02/) | In progress |

# How to run Week 01

```powershell
git clone git@github.com:NickB28/Street-Ready.git
cd Street-Ready
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python week-01/pwcheck.py
pytest
```