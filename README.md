# 🔑 Keybin

**Password Generator & Manager CLI**  
A mini-LastPass style command-line tool.

Keybin allows you to:

- 🔐 Generate secure and customizable passwords.
- 🗄 Store them encrypted with a master key.
- 👤 Manage multiple user profiles and password logs.
- 🛡️ Encrypt your password logs. ##TODO
- 📤 Import and export logs. ##TODO
- ⚡ Auto-login and cloud/local sync. ##TODO
- 📋 Copy passwords to the clipboard using `pyperclip`.

## Features

### General Commands
- `keybin genpass` — Generate a new password.
- `keybin genlog` — Save a password log.
- `keybin find` — Search logs by service, username, or tags.
- `keybin find all` — Return all logs for the current profile.

### Profile Management
- `keybin profile whoami` — Show the active profile.
- `keybin profile new` — Add a new profile.
- `keybin profile switch` — Switch between profiles.
- `keybin profile list` — List all available profiles.

### Planned / Upcoming Features
- `keybin profile delete` — Delete a profile.
- `keybin export` — Export logs in a specific format.
- `keybin import` — Import logs from a file.
- `keybin sync` — Sync logs with the cloud or a local directory.

This is a work in progress CLI tool. More detailed usage instructions and command options will be added soon.

## Example Usage

```bash
# Generate a new password
keybin genpass

# Save a password log
keybin genlog

# Search logs
keybin find --service Gmail

# Manage profiles
keybin profile new
keybin profile switch
keybin profile whoami


