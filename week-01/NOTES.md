# WEEK 1 NOTES

I set up my whole dev environment from
scratch on Windows: GitHub, Git, Python, VS Code and an SSH key. I learnt the basic git loop: `git add` picks the files, `git commit` saves a snapshot with a message, and `git push` uploads it to GitHub. I also learnt that a virtual environment (`.venv`) is a private box for a project's packages, and that it must not be committed, which is what the `.gitignore` is for.


# For the password checker, the main ideas were:
-`character_classes` goes through a password one character at a time and uses `any(...)` to say whether at least one character is lowercase uppercase a digit or a symbol.It returns the answers as a dictionary. 

# What broke
-`ssh-keygen` kept saying "passphrases do not match" because I couldn't see  what I was typing.
-I pasted a repo address without `git clone` in front, and PowerShell didn't recognise it.
-My first `pytest` run said "collected 0 items" because the test file was still empty and I hadn't saved the code into it.


# How I fixed it
I created the SSH key with a single command that sets no passphrase. I read the red error messages properly: they told me exactly what was wrong each time. For pytest I pasted the tests, saved the file and ran it again, and got 15 passed.

# Resources and LLM prompts that helped
I used Claude and asked it to explain each piece of code in one or two lines. I also used youtube to learn the basics of using GitHub, referred forums and the websites provided by you.
