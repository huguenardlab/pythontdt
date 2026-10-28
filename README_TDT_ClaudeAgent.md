**WSL, Claude agentic, python, tdt**


**Here's how to get Claude Code set up and running on a specific desktop:**

## 1. Prerequisites

- **Node.js 18+ installed (Claude Code is distributed via npm). Check with `node --version`.**

- **A terminal (Terminal on macOS/Linux, or PowerShell/Windows Terminal on Windows — WSL is often recommended on Windows).**

## 2. Install

```
**bash**

**Copy code**

**`npm install -g @anthropic-ai/claude-code`**
```

**Don't use `sudo` with npm — if you hit permission errors, it's better to fix your npm permissions or use a Node version manager (like `nvm`) rather than installing as root.**

## 3. Navigate to your project

```
**bash**

**Copy code**

**`cd /path/to/your/project`**
```

## 4. Launch and authenticate

```
**bash**

**Copy code**

**`claude`**
```

**The first time you run it, it will prompt you to authenticate. You'll typically have options like:**

- **Log in with your Claude account (Pro/Max subscription) — opens a browser to sign in.**

- **Anthropic Console / API key — if you're billing through the developer console.**

**Since you mentioned you have an account, just pick the matching login method and complete the browser sign-in. That ties this desktop to your account.**

## 5. Verify

**Once authenticated, you can confirm things are working:**

```
**bash**

**Copy code**

**`claude --version`**
```

**And check your config / auth status by running `claude` and using the `/status` or `/login` commands inside the session.**


**A couple of questions so I can tailor the rest:**

- **Which OS are you on (macOS, Windows, Linux)?**

- **Are you authenticating via a Claude subscription (Pro/Max) or an API key from the console? The flow differs slightly.**

**Let me know and I can walk you through any sticking points.**

![](data:image/svg+xml;utf8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%20100%20100%22%3E%3Cmetadata%20xmlns%3Ardf%3D%22http%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%22%20xmlns%3Axsi%3D%22http%3A%2F%2Fwww.w3.org%2F2001%2FXMLSchema-instance%22%20xmlns%3Adc%3D%22http%3A%2F%2Fpurl.org%2Fdc%2Felements%2F1.1%2F%22%20xmlns%3Adcterms%3D%22http%3A%2F%2Fpurl.org%2Fdc%2Fterms%2F%22%3E%3Crdf%3ARDF%3E%3Crdf%3ADescription%3E%3Cdc%3Atitle%3EInitials%3C%2Fdc%3Atitle%3E%3Cdc%3Acreator%3EDiceBear%3C%2Fdc%3Acreator%3E%3Cdc%3Asource%20xsi%3Atype%3D%22dcterms%3AURI%22%3Ehttps%3A%2F%2Fgithub.com%2Fdicebear%2Fdicebear%3C%2Fdc%3Asource%3E%3Cdcterms%3Alicense%20xsi%3Atype%3D%22dcterms%3AURI%22%3Ehttps%3A%2F%2Fcreativecommons.org%2Fpublicdomain%2Fzero%2F1.0%2F%3C%2Fdcterms%3Alicense%3E%3Cdc%3Arights%3E„Initials”%20(https%3A%2F%2Fgithub.com%2Fdicebear%2Fdicebear)%20by%20„DiceBear”%2C%20licensed%20under%20„CC0%201.0”%20(https%3A%2F%2Fcreativecommons.org%2Fpublicdomain%2Fzero%2F1.0%2F)%3C%2Fdc%3Arights%3E%3C%2Frdf%3ADescription%3E%3C%2Frdf%3ARDF%3E%3C%2Fmetadata%3E%3Cmask%20id%3D%22viewboxMask%22%3E%3Crect%20width%3D%22100%22%20height%3D%22100%22%20rx%3D%220%22%20ry%3D%220%22%20x%3D%220%22%20y%3D%220%22%20fill%3D%22%23fff%22%20%2F%3E%3C%2Fmask%3E%3Cg%20mask%3D%22url(%23viewboxMask)%22%3E%3Crect%20fill%3D%22%238e24aa%22%20width%3D%22100%22%20height%3D%22100%22%20x%3D%220%22%20y%3D%220%22%20%2F%3E%3Ctext%20x%3D%2250%25%22%20y%3D%2250%25%22%20font-family%3D%22Verdana%22%20font-size%3D%2236%22%20font-weight%3D%22400%22%20fill%3D%22%23ffffff%22%20text-anchor%3D%22middle%22%20dy%3D%2212.816%22%3EJH%3C%2Ftext%3E%3C%2Fg%3E%3C%2Fsvg%3E "avatar")

**windows. is npm already installed?**

**Not by default — Windows does not come with npm (or Node.js) pre-installed. You have to install Node.js, which includes npm.**

## Check if it's already there

**Open PowerShell or Windows Terminal and run:**

```
**powershell**

**Copy code**

**`node --version`**

**`npm --version`**
```

- **If you get version numbers back (e.g., `v20.11.0` and `10.2.4`), you're good to go.**

- **If you get an error like *"'node' is not recognized..."*, you need to install it.**

## Installing Node.js (if needed)

**Option A — Official installer (simplest):**

1. **Go to [nodejs.org](https://nodejs.org/).**

2. **Download the LTS version (recommended for stability).**

3. **Run the installer, accept defaults (make sure "Add to PATH" stays checked).**

4. **Close and reopen your terminal, then re-run `node --version` to confirm.**

**Option B — winget (if you prefer command line):**

```
**powershell**

**Copy code**

**`winget install OpenJS.NodeJS.LTS`**
```

**Then restart your terminal.**


## ⚠️ One important note for Windows + Claude Code

**Anthropic has historically recommended running Claude Code under WSL (Windows Subsystem for Linux) rather than native Windows, because some features behave better in a Linux environment. Native Windows support has improved, but if you run into issues, WSL is the fallback.**

**If you want, I can walk you through either:**

- **Native Windows setup (install Node, then `npm install -g @anthropic-ai/claude-code`), or**

- **WSL setup (more reliable, slightly more initial effort).**

**Which would you prefer?**



**Here's the full WSL setup, step by step.**

**Step 1 — Install WSL**

**Open PowerShell as Administrator (right-click Start → "Terminal (Admin)" or "Windows PowerShell (Admin)"), then run:**

**powershell**


**Copy code**

**wsl --install**

**This single command will:**

- **Enable the required Windows features**

- **Install WSL 2**

- **Download and install Ubuntu (the default distro)**

**If you want a different distro, run wsl --list --online to see options, then wsl --install -d \<DistroName\>. Ubuntu is a solid default — I'd stick with it unless you have a reason not to.**

**Step 2 — Reboot**

**When it finishes, restart your computer. This is required for the Windows features to fully enable.**

**Step 3 — Create your Linux user**

**After rebooting, Ubuntu will launch automatically (or find "Ubuntu" in the Start menu). On first launch it will:**

- **Take a minute to finish setting up**

- **Prompt you to create a username and password**

**This password is for your Linux environment (used for sudo). It's separate from your Windows login. The screen won't show characters as you type the password — that's normal.**

**Step 4 — Update the system**

**In the Ubuntu terminal:**

**bash**


**Copy code**

**sudo apt update && sudo apt upgrade -y**

**Enter your Linux password when prompted.**

**Step 5 — Install Node.js (via nvm — recommended)**

**Rather than apt's often-outdated Node, use nvm so you get a current version and avoid permission issues:**

**bash**


**Copy code**

**curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash**

**Then close and reopen the Ubuntu terminal (or run source ~/.bashrc), and install the LTS Node:**

**bash**


**Copy code**

**nvm install --lts**

**Verify:**

**bash**


**Copy code**

**node --version npm --version**

**Step 6 — Install Claude Code**

**bash**


**Copy code**

**npm install -g @anthropic-ai/claude-code**

**Note: with nvm, no sudo needed — that's one of the big reasons to use it.**

**Step 7 — Set up your project**

**Important tip: keep your code inside the Linux filesystem (e.g., ~/projects/...), not on /mnt/c/.... Working in the Windows-mounted drive is much slower and can cause file-watching issues.**

**bash**


**Copy code**

**mkdir -p ~/projects cd ~/projects \# then cd into or clone your project here**

**Step 8 — Launch and authenticate**

**bash**


**Copy code**

**claude**

**It'll prompt you to log in — a browser will open on Windows, you sign in with your Claude account, and you're connected.**


**Quick tips**

- **Opening WSL later: just type wsl in PowerShell, or open "Ubuntu" from the Start menu.**

- **VS Code users: install the "WSL" extension — then code . from inside WSL opens VS Code connected to your Linux environment seamlessly.**

**Want me to cover the VS Code integration, or help with anything once you reach the authentication step?**









**and how to best implement python in wsl**






**Good question — Python needs the same "don't use the system one directly" discipline as Node. Here's the best-practice setup.**

**Step 1 — Know what's already there**

**Ubuntu ships with a system Python 3, but don't build your projects on it directly. It's used by the OS itself, and messing with it (or installing packages globally) can break system tools. Treat it as off-limits for your own work.**

**Check what you have:**

**bash**


**Copy code**

**python3 --version**

**Step 2 — Install essentials**

**bash**


**Copy code**

**sudo apt update sudo apt install -y python3-pip python3-venv**

- **python3-pip → the package installer**

- **python3-venv → lets you create isolated virtual environments**

**Step 3 — Choose your approach**

**Option A — Virtual environments (simplest, great default)**

**For each project, create an isolated environment so dependencies never collide:**

**bash**


**Copy code**

**cd ~/projects/myproject python3 -m venv .venv source .venv/bin/activate**

**Your prompt now shows (.venv). Install packages freely here:**

**bash**


**Copy code**

**pip install requests pandas \# example**

**Deactivate when done:**

**bash**


**Copy code**

**deactivate**

**This is the single most important habit: one venv per project. It keeps things clean and reproducible.**

**Option B — pyenv (best if you need multiple Python versions)**

**If you'll juggle different Python versions across projects, pyenv is the gold standard:**

**bash**


**Copy code**

**curl https://pyenv.run | bash**

**Then add it to your shell by appending to ~/.bashrc:**

**bash**


**Copy code**

**export PYENV\_ROOT="$HSME/.pyenv" command -v pyenv \>/dev/null || export PATH="$PYENV\_ROOT/bin:$PATH" eval "$(pyenv init - bash)"**

**⚠️ Correction on that first line — it should be $HOME, not a typo:**

**bash**


**Copy code**

**export PYENV\_ROOT="$HOME/.pyenv" export PATH="$PYENV\_ROOT/bin:$PATH" eval "$(pyenv init - bash)"**

**Reopen the terminal, then:**

**bash**


**Copy code**

**pyenv install 3.12.4 \# install a specific version pyenv global 3.12.4 \# set default**

**You still make venvs per project on top of this.**

**Option C — uv (modern, fast, increasingly popular)**

**uv is a newer all-in-one tool (installer, venv manager, resolver) that's extremely fast and handles Python versions *and* packages:**

***bash**


***Copy code**

***curl -LsSf https://astral.sh/uv/install.sh | sh**

***Then in a project:**

***bash**


***Copy code**

***uv venv \# creates .venv source .venv/bin/activate uv pip install requests**

***It can even install Python versions for you (uv python install 3.12). If you're starting fresh, this is a great modern choice.**

***My recommendation**

- ***Just getting going / want simplicity: Option A (venv) — zero extra tools.**

- ***Need multiple Python versions: pyenv, or uv (which does that *and* is faster).**

- ***If you like trying modern tooling, uv is my top pick right now — it replaces pip, venv, and pyenv in one tool.**

***A few tips**

- ***Keep projects in the Linux filesystem (~/projects/...), same as before — not /mnt/c/....**

- ***VS Code + WSL extension auto-detects your venvs; just select the interpreter (.venv/bin/python) via the command palette.**

- ***Since you like a modular code structure, venvs pair perfectly with that — each project stays self-contained with its own dependencies and logical file layout.**

***Want me to show a clean starter project layout (with a venv, a src/ structure, and a requirements.txt or pyproject.toml)?**









***the code will have to use a windows layer to access a TDT device**






***Ah, this changes the calculus significantly. TDT (Tucker-Davis Technologies) hardware and their drivers/SDK are Windows-native — they talk to the device through Windows drivers (ActiveX/COM, the TDTbin/Synapse APIs, etc.). This is exactly the kind of scenario where WSL becomes a liability rather than a help.**

***The core problem**

- ***WSL (even WSL 2) cannot directly access most physical hardware that relies on Windows kernel drivers. USB/PCIe device access, COM/ActiveX automation, and TDT's driver stack live on the Windows side.**

- ***TDT's Python interface (e.g., tdt package, SynapseAPI, or ActiveX via win32com) expects to run on native Windows Python, talking to Windows-installed TDT drivers and software (Synapse/OpenEx).**

- ***Trying to bridge WSL → Windows hardware is possible in narrow cases but fragile, and for driver-level device control it generally won't work.**

***So, the recommendation flips**

***For this project, run Python natively on Windows, not in WSL. Here's the clean way to do that:**

***Step 1 — Install native Windows Python**

- ***Get it from [python.org](https://python.org/) (download the Windows installer), or use winget:**

***powershell**


***Copy code**

***winget install Python.Python.3.12**

- ***During install (python.org installer), check "Add Python to PATH."**

***Step 2 — Verify in PowerShell**

***powershell**


***Copy code**

***python --version pip --version**

***Step 3 — Use a virtual environment (same good habit, Windows flavor)**

***powershell**


***Copy code**

***cd C:\\projects\\myproject python -m venv .venv .\\.venv\\Scripts\\Activate.ps1**

***If you get an execution-policy error activating the venv, run once:**

***Set-ExecutionPolicy -Scope CurrentUser RemoteSigned**

***Step 4 — Install TDT + dependencies**

***powershell**


***Copy code**

***pip install tdt pywin32**

- ***tdt → TDT's official Python package**

- ***pywin32 → for COM/ActiveX automation if you use SynapseAPI or legacy ActiveX controls**

- ***Make sure TDT's drivers and Synapse/OpenEx are installed on the machine too.**

***What about Claude Code then?**

***This is the key point — you can run Claude Code in either place, but to keep things sane:**

- ***Simplest: run Claude Code on native Windows too, so it operates in the same environment where the code actually runs and can be tested against the device. Your earlier Node/npm install on native Windows covers this.**

- ***Alternative: keep Claude Code in WSL for the general dev experience, but understand it can't run/test the TDT-dependent code — only the hardware-independent parts. You'd test the device code separately on Windows. This split is doable but adds friction.**

***Given the hardware dependency, I'd lean toward doing the whole thing natively on Windows for this project — Claude Code, Python, and the TDT code all in one place.**

***A clean architecture tip (fits your modular preference)**

***Isolate the hardware layer so you *can* develop/test logic anywhere:**

***python**


***Copy code**

***project/ src/ device/ \# TDT-specific code (Windows + hardware required) tdt\_client.py core/ \# hardware-independent logic (testable anywhere) processing.py analysis.py interfaces/ device\_api.py \# abstract interface; real + mock implementations tests/ test\_core.py \# run anywhere, incl. WSL/CI test\_device.py \# run only on Windows w/ hardware**

***With a mock implementation of the device interface, Claude Code can help you build and test the core/ logic freely, while the real device/ layer only runs on the Windows machine with the TDT hardware attached.**


***Want me to:**

1. ***Help you scaffold that modular project structure, or**

2. ***Walk through the native Windows Claude Code + Python setup end to end, or**

3. ***Sketch the device interface + mock so you can develop against hardware you don't always have plugged in?**









