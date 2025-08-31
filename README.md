<p align="center">
  <a href="https://github.com/jotaesee/keybin">
    <img src="/img/logo.png?raw=true" width="300" alt="keybin Logo"/>
  </a>
</p>

# Keybin

<p align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.9+-darkblue.svg)](https://www.python.org/downloads/)
[![Made with Typer](https://img.shields.io/badge/Made%20with-Typer-purple)](https://typer.tiangolo.com)
[![Built-with-mate-y-facturas](https://img.shields.io/badge/Built%20with-Mate%20y%20Facturas-blue)](https://www.youtube.com/watch?v=OqSQo2aifAA&list=RDOqSQo2aifAA&start_radio=1)
[![Tweet](https://img.shields.io/badge/X-share-black.svg)](https://twitter.com/intent/tweet?text=Manage%20your%20passwords%20from%20the%20terminal%20with%20keybin,%20an%20open-source%20project.&url=https://github.com/jotaesee/keybin)

</p>

Your secure, local and private password manager. Right in your terminal.

<p align="center">
  <img src="/img/demo.gif?raw=true" alt="keybin Demo"/>
</p>

Built to be **secure** and **efficient** 🔑.

If you like the project, support me with a `star` and a `follow` on GitHub.

---

# Table of Contents

- [Keybin](#keybin)
- [Table of Contents](#table-of-contents)
- [Features](#features)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [Detailed Usage](#detailed-usage)
  - [Main Commands](#main-commands)
  - [Profile Management (`profile`)](#profile-management-profile)
  - [Log Management (`log`)](#log-management-log)
- [License](#license)

# Features

- **👥 Profile Management:** Create multiple, independent profiles (e.g., for personal and work use) protected by a master password. Your data stays completely separate and secure.
- **📊 Status and session check:** See which profile is currently active, how much time you've got left in session, log count and the current profile's security level.
- **🛡️ Security First:** No passwords stored, not even hashed. Your masterkey is used to securely encrypt and decrypt a unique encryption key for each profile, ensuring only you can access your data.
- **🎲 Secure Password Generator:** Create strong passwords, customizable in length and symbol usage.
- **🗄️ Robust Log Management:** Safely add, find, and manage your sensitive data. Every operation is atomic, writing to a portable JSON file to prevent data corruption.
- **🔍 Intelligent Search:** Search by exact fields and a powerful **fuzzy search** to find what you need even if you make a typo.
- **🏷️ Tag-based Organization:** Add tags to your logs to filter and organize them your way.
- **✨ Modern Interface:** Built with Typer and Rich for a clean and pleasant user experience.
- **🌐 Cross-Platform:** Works on Linux, Windows, and MacOS, storing data in standard user directories for each OS.

## Installation

You need **Python 3.9+** and `pip` installed on your system.

### Option A: Install from PyPI (Recommended)

The easiest way to install `keybin` is directly from the Python Package Index (PyPI).

For command-line tools like this, it is highly recommended to use `pipx` to install them in an isolated environment. This avoids dependency conflicts with other Python projects.

1.  **Install pipx** (if you don't have it already):

    ```bash
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath
    ```

    _(You may need to restart your terminal after this step)_

2.  **Install keybin using pipx:**

    ```bash
    pipx install keybin
    ```

    If you prefer to use `pip`, you can install it directly:

    ```bash
    pip install keybin
    ```

3.  **Verify the installation:**
    After installation, you can verify that keybin is working correctly.
    ```bash
    keybin --version
    ```

### Option B: Install from Source (For Developers)

If you want to contribute to the project or use the latest development version, you can install it from the source code.

1.  **Clone the repository**:

    ```bash
    git clone https://github.com/jotaesee/keybin.git

    cd keybin

    ```

2.  **(Recommended) Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install in editable mode:**
    This will install the package, but any changes you make to the source code will be immediately effective.
    ```bash
    pip install -e .
    ```

# Getting Started

Getting started with `keybin` is fast and intuitive. Here's a typical workflow for a first-time user to set up their secure vault.

### 1. Create Your First Profile

First, you'll need to create a profile. Think of a profile as your personal encrypted vault. You'll protect it with a strong master password. You only set a profile once, but you can have multiple profiles.
You could also use the default one, but remember, profiles with no masterkey are not encrypted!

```bash
# We'll use "profile add" to create a profile named "myprofile" with a master password
keybin profile add --user myprofile --key "your-very-strong-master-password"

```

**_Security Tip: You can create profiles without a masterkey, but a profile not secured does not encrypt it's logs._**

### 2. Log In to Your Profile

To start using a profile, you need to log into it. If the profile's secured, you'll need to provide your masterkey to login.

```bash
# If the selected profile is encrypted, keybin will prompt for your masterkey.
keybin login myprofile

```

**_Tip: You can check your current session status at any time with keybin status._**

### 3. Add Your First Password Log

Once you're logged in, you can add your first entry. For the most user-friendly experience, simply run the add command, and keybin will guide you.

```bash
# This will prompt you for all the necessary info (service, user, password, etc.).
keybin log add
```

You could also just use flags for a faster experience:

```bash
# --autopass will auto generate a new secure password.
keybin log add -s "GitHub" -u "jotaesee" --autopass -t dev -t personal
```

Pro Tip: Leave fields empty using --no-prompts or -n, this flag will skip missing info, and log it as you say.

### 4. Check your logs

Now, let's verify that your log was saved correctly. Use the find command to search your vault.

```bash
# A fuzzy search for "git" will find the "GitHub" log we just created.
keybin log find git
```

You could pair this fuzzy search with filters like email, service, tags and username, or direcly search a log by it's id.
You can also see all logs in the current profile by running keybin log find all.

### 5. Log Out of Your Profile

When you're finished, it's good practice to log out. This locks your vault, ensuring your data is secure until you log in again.

```bash
# The logout command ends the session, so secured commands are not accesible.
keybin logout
```

Pro-Tip: If you are already logged into a profile and want to change to another one without logging out first, you can use the "keybin profile switch <other_profile>" command.

# Detailed Usage

This section provides a detailed breakdown of all available commands and their options.

Most data-related commands (like adding or finding logs) require an active, logged-in session. You can check your current session with `keybin status`.

---

## Main Commands

These are the top-level commands available directly under `keybin`.

### `login`

Logs into a profile to start a secure session. This unlocks the vault, allowing you to use session-secured commands.

**Usage:**

```bash
keybin login <USER> [KEY]
```

**Arguments:**

    USER: The name of the profile you want to log into.

    KEY (Optional): The masterkey for the profile. If the profile is encrypted and the key is not provided, you will be prompted to enter it securely.

**Example:**

```bash
# Log into the 'personal' profile. It will prompt for the password.
keybin login personal
```

### `logout`

Logs out of the current profile, ending the secure session and locking the vault.

**Usage:**

```bash
keybin logout
```

### `status`

Displays a summary of the current session, including the active profile, its encryption status, the path to its data file, the number of saved logs, and the time remaining in the current session.

**Usage:**

```bash
keybin status
```

### `genpass`

Generates a new, secure password. Also available via the alias gp.

**Usage:**

```bash
keybin genpass [OPTIONS]
```

**Options:**

    -l, --length <INTEGER>: The desired length for the new password (default: 16).

    --no-symbols / --symbols: Include or exclude symbols in the generated password (default: include symbols).

    -c, --copy: If set, copies the new password directly to the clipboard.

**Example:**

```bash
# Generate a 24-character password and copy it to the clipboard
keybin genpass -l 24 -c
```

## Profile Management (profile)

Commands for creating, viewing, and managing your user profiles.

### `profile add`

Creates a new profile. If options are not provided, it will guide you through an interactive setup.

**Usage:**

```bash
keybin profile add [OPTIONS]
```

**Options:**

    -u, --user <TEXT>: The name for the new profile.

    -k, --key <TEXT>: The masterkey to encrypt the profile's data (recommended).

    -p, --path <TEXT>: A custom file path to store the profile's data.

**Example:**

```bash
# Create a new encrypted profile named "work"
keybin profile add --user work --key "my-secret-work-password"
```

### `profile list`

Displays a table with all your existing profiles, their data paths, and whether they are encrypted.

**Usage:**

```bash
keybin profile list
```

### `profile switch`

Switches from one logged-in profile to another without needing to log out first. Requires an active session.

**Usage:**

```bash
keybin profile switch <USER> [KEY]
```

**Arguments:**

    USER: The name of the profile you want to switch to.

    KEY (Optional): The masterkey for the target profile. You will be prompted if it's required.

### `profile delete`

Permanently deletes a profile and all of its associated data.

**Usage:**

```bash
keybin profile delete <PROFILE>
```

    Warning: This action is irreversible. For encrypted profiles, you will be prompted for the masterkey to confirm the deletion.

## Log Management (log)

Commands for adding, finding, and deleting logs (entries) within the currently active profile. These commands require a logged-in session.

### `log add`

Adds a new password log to the active vault. You can provide info via flags or let the command prompt you for any missing fields.

**Usage:**

```bash
keybin log add [OPTIONS]
```

**Options:**

    -s, --service <TEXT>: The name of the service (e.g., Google, GitHub).

    -u, --user <TEXT>: Your username for the service.

    -e, --email <TEXT>: Your email for the service.

    -p, --password <TEXT>: The password to save.

    -t, --tags <TEXT>: Add one or more tags for organization (e.g., -t work -t dev).

    -a, --autopass: Automatically generates a secure password for this log.

    -n, --no-prompts: Skips interactive prompts for missing information.

### `log find`

Searches for logs in the active vault. Running keybin log find <TERM> will perform a fuzzy search.

**Usage:**

```bash
keybin log find [SEARCH] [OPTIONS]
```

**Options:**

    -i, --id <INTEGER>: Search for a log by its exact ID.

    -s, --service <TEXT>: Filter by exact service name.

    -u, --user <TEXT>: Filter by exact username.

    -e, --email <TEXT>: Filter by exact email.

    -t, --tags <TEXT>: Filter for logs that contain all specified tags.

**Examples:**

```bash
# Fuzzy search for any logs related to "google"
keybin log find google

# Find all logs with the "work" tag for the "GitHub" service
keybin log find --service "GitHub" -t work
```

### `log delete`

Deletes a specific log from the vault using its ID.

**Usage:**

```bash
keybin log delete <ID> [OPTIONS]
```

**_Tip: Not sure what the ID is? Run keybin log find all to see a list of all your logs._**

**Options:**

    -n, --no-prompt: If set, deletes the log without asking for confirmation.

**Example:**

```bash
# Delete the log with ID 15 after showing a confirmation prompt
keybin log delete 15
```

# License

[MIT](https://choosealicense.com/licenses/mit/)
