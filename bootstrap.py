#!/usr/bin/env python3

import subprocess
import os
import sys
import time

# --- Global Constants for URLs ---
OH_MY_ZSH_INSTALL_URL = "https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh"
POWERLEVEL10K_REPO_URL = "https://github.com/romkatv/powerlevel10k.git"
VIM_PLUG_URL = "https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim"
# Base URL for dotfiles from adn770/bootstrap repository
DOTFILES_BASE_URL = "https://raw.githubusercontent.com/adn770/bootstrap/main"


def run_command(command, message=None, check=True):
    """
    Runs a shell command, prints output in real-time, and handles errors.
    """
    if message:
        print(f"\n--- {message} ---")
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True)

        # Print stdout in real-time
        for line in process.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()

        # Print stderr in real-time
        for line in process.stderr:
            sys.stderr.write(line)
            sys.stderr.flush()

        process.wait()  # Wait for the command to complete

        if check and process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command,
                                                output=process.stdout.read(),
                                                stderr=process.stderr.read())
        return process
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Command not found: {command.split()[0]}")
        sys.exit(1)

class ConfigFileManager:
    """
    A helper class for reading, writing, and safely modifying configuration files.
    """
    def __init__(self, file_path):
        self.file_path = os.path.expanduser(file_path)
        self.content = self._read_file()

    def _read_file(self):
        """Reads the content of the file."""
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                return f.readlines()
        return []

    def _write_file(self, content):
        """Writes the given content to the file."""
        try:
            with open(self.file_path, 'w') as f:
                f.writelines(content)
            print(f"Successfully updated {self.file_path}.")
            return True
        except Exception as e:
            print(f"Error writing to {self.file_path}: {e}")
            return False

    def ensure_line_present(self, line_to_add, after_line_prefix=None):
        """Ensures a specific line is present in the file, optionally after a
        prefix.
        """
        normalized_line_to_add = line_to_add.strip()

        # Check if the line (or a line containing it) already exists
        for line in self.content:
            if normalized_line_to_add in line.strip():
                print(f"Content '{normalized_line_to_add}' already exists in "
                      f"{self.file_path}. Skipping.")
                return True

        if after_line_prefix:
            found_idx = -1
            for i, line in enumerate(self.content):
                if line.strip().startswith(after_line_prefix):
                    found_idx = i
                    break

            if found_idx != -1:
                # Insert the new line right after the found line
                self.content.insert(found_idx + 1, line_to_add + "\n"
                                    if not line_to_add.endswith('\n')
                                    else line_to_add)
                print(f"Added '{normalized_line_to_add}' after "
                      f"'{after_line_prefix}' in {self.file_path}.")
            else:
                # If prefix not found, just append to the end
                if not self.content or not self.content[-1].endswith('\n'):
                    self.content.append('\n')
                self.content.append(line_to_add + "\n"
                                    if not line_to_add.endswith('\n')
                                    else line_to_add)
                print(f"Added '{normalized_line_to_add}' to {self.file_path} "
                      f"(prefix '{after_line_prefix}' not found).")
        else:
            # Append if no specific placement is needed and it's not already there
            if not self.content or not self.content[-1].endswith('\n'):
                self.content.append('\n')
            self.content.append(line_to_add + "\n"
                                if not line_to_add.endswith('\n')
                                else line_to_add)
            print(f"Added '{normalized_line_to_add}' to {self.file_path}.")

        return self._write_file(self.content)

    def replace_line_prefix(self, prefix, new_line):
        """Replaces a line starting with a specific prefix with a new line."""
        new_content = []
        replaced = False
        for line in self.content:
            if line.strip().startswith(prefix):
                new_content.append(new_line + "\n"
                                   if not new_line.endswith('\n')
                                   else new_line)
                replaced = True
                print(f"Replaced line starting with '{prefix}' in "
                      f"{self.file_path}.")
            else:
                new_content.append(line)

        if not replaced:
            # If prefix not found, add the new line at the end
            if not new_content or not new_content[-1].endswith('\n'):
                new_content.append('\n')
            new_content.append(new_line + "\n"
                               if not new_line.endswith('\n')
                               else new_line)
            print(f"Added '{new_line}' to {self.file_path} (prefix '{prefix}' "
                  "not found).")

        self.content = new_content
        return self._write_file(self.content)

    def overwrite_file(self, new_content):
        """Overwrites the entire file with new content."""
        self.content = [line + "\n" if not line.endswith('\n') else line
                        for line in new_content.splitlines()]
        print(f"Overwriting {self.file_path}.")
        return self._write_file(self.content)

class DotfileDownloader:
    """
    A helper class to download dotfiles from a specified GitHub repository.
    """
    def __init__(self, base_url):
        self.base_url = base_url

    def download_dotfile(self, dotfile_name, local_path=None):
        """
        Downloads a specific dotfile from the repository to a local path.
        If local_path is None, it defaults to ~/.dotfile_name.
        """
        remote_url = f"{self.base_url}/{dotfile_name}"
        target_local_path = (os.path.expanduser(local_path if local_path
                                                else f"~/{dotfile_name}"))

        print(f"Downloading {remote_url} to {target_local_path}...")
        try:
            run_command(f"curl -fLo {target_local_path} {remote_url}")
            print(f"Successfully downloaded {dotfile_name} to "
                  f"{target_local_path}.")
            return True
        except Exception as e:
            print(f"Error downloading {dotfile_name}: {e}")
            print(f"Please manually check or download {remote_url}.")
            return False

def _setup_zsh():
    """
    Checks for Zsh, installs it if not present, and sets it as the default
    shell.
    """
    print("\n--- Setting up Zsh ---")
    print("Checking for Zsh installation...")
    result = run_command("which zsh", check=False)
    if result.returncode != 0:
        print("Zsh not found. Installing Zsh...")
        run_command("sudo apt update")
        run_command("sudo apt install -y zsh")
        print("Zsh installed successfully.")
    else:
        print("Zsh is already installed.")

    current_shell = os.environ.get('SHELL')
    if current_shell != "/usr/bin/zsh" and current_shell != "/bin/zsh":
        print("Changing default shell to Zsh...")
        run_command(f"chsh -s $(which zsh) {os.getenv('USER')}")
        print("Default shell changed to Zsh. Please log out and log back in "
              "for changes to take effect.")
    else:
        print("Zsh is already your default shell.")

def _install_base_packages():
    """
    Installs a list of essential packages using apt.
    """
    print("\n--- Installing base packages ---")
    packages = ["bat", "btop", "cmake", "curl", "fzf", "gdb", "git", "tig",
                "tmux", "vim", "zoxide"]
    packages.sort()
    print(f"Installing base packages: {', '.join(packages)}...")
    run_command("sudo apt update")
    run_command(f"sudo apt install -y {' '.join(packages)}")
    print("Base packages installed successfully.")


def _configure_vimrc():
    """
    Downloads the latest dot.vimrc from GitHub and updates/creates ~/.vimrc.
    """
    print("\n--- Configuring ~/.vimrc from GitHub ---")
    dotfile_downloader = DotfileDownloader(DOTFILES_BASE_URL)
    dotfile_downloader.download_dotfile("dot.vimrc", "~/.vimrc")


def _install_vim_plug():
    """
    Installs Vim-Plug for Vim.
    """
    print("\n--- Installing Vim-Plug ---")
    vim_autoload_dir = os.path.expanduser("~/.vim/autoload")
    vim_plug_path = os.path.join(vim_autoload_dir, "plug.vim")

    if not os.path.exists(vim_plug_path):
        print(f"Downloading Vim-Plug to {vim_plug_path}...")
        run_command(f"curl -fLo {vim_plug_path} --create-dirs {VIM_PLUG_URL}")
        print("Vim-Plug installed successfully.")
    else:
        print("Vim-Plug is already installed.")


def _run_vim_plug_install():
    """
    Runs Vim to install plugins using PlugInstall and then quits.
    """
    print("\n--- Running Vim PlugInstall ---")
    try:
        run_command("vim +PlugInstall +qall", message="Running Vim PlugInstall")
        print("Vim PlugInstall completed.")
    except Exception as e:
        print(f"Error running Vim PlugInstall: {e}")
        print("Please run 'vim +PlugInstall +qall' manually inside your "
              "terminal.")

def _create_ssh_rc_file():
    """
    Creates or updates the ~/.ssh/rc file for SSH Agent Forwarding Fix.
    """
    print("\n--- Creating ~/.ssh/rc file for SSH Agent Forwarding Fix ---")
    ssh_dir = os.path.expanduser("~/.ssh")
    ssh_rc_path = os.path.join(ssh_dir, "rc")
    ssh_rc_content = """#!/bin/bash

# Fix SSH auth socket location so agent forwarding works with tmux
if test "$SSH_AUTH_SOCK" ; then
  ln -sf $SSH_AUTH_SOCK ~/.ssh/ssh_auth_sock
fi"""

    try:
        if not os.path.exists(ssh_dir):
            print(f"Creating directory: {ssh_dir}")
            os.makedirs(ssh_dir, mode=0o700, exist_ok=True)
            print(f"Set permissions for {ssh_dir} to 0o700.")

        ssh_rc_manager = ConfigFileManager(ssh_rc_path)
        ssh_rc_manager.overwrite_file(ssh_rc_content)
        os.chmod(ssh_rc_path, 0o600)
        print(f"Permissions for '{ssh_rc_path}' set to 0o600.")

    except Exception as e:
        print(f"Error creating/modifying '{ssh_rc_path}': {e}")
        print("Please create the file manually if needed.")

def _configure_zshenv():
    """
    Adds custom PATH settings and a tmux+ssh helper function to ~/.zshenv.
    """
    print("\n--- Configuring ~/.zshenv ---")
    zshenv_path = os.path.expanduser("~/.zshenv")
    zshenv_content_to_add = """
# set PATH so it includes user's private bin if it exists
if [ -d "$HOME/bin" ] ; then
    PATH="$HOME/bin:$PATH"
fi

# set PATH so it includes user's private bin if it exists
if [ -d "$HOME/.local/bin" ] ; then
    PATH="$HOME/.local/bin:$PATH"
fi

# tmux+ssh helper function with iterm integration
function tmssh () {
  local IP="$1"
  if [[ -z "$IP" ]]; then
    me="${FUNCNAME[0]}${funcstack[1]}"
    IP="192.168.100.100"
    echo "usage: $me [ssh-args] hostname"
  fi

  ssh "$IP" -t 'tmux -CC new -A -s tmssh'
}
"""
    zshenv_manager = ConfigFileManager(zshenv_path)
    zshenv_manager.ensure_line_present(zshenv_content_to_add.strip())


def _install_oh_my_zsh():
    """
    Installs Oh My Zsh if it's not already present.
    """
    print("\n--- Installing Oh My Zsh ---")
    ohmyzsh_dir = os.path.expanduser("~/.oh-my-zsh")
    if not os.path.exists(ohmyzsh_dir):
        print("Oh My Zsh not found. Installing...")
        run_command(f'sh -c "$(curl -fsSL {OH_MY_ZSH_INSTALL_URL})" "" --unattended',
                    message="Running Oh My Zsh installer (unattended)",
                    check=False)
        print("Oh My Zsh installed successfully.")
    else:
        print("Oh My Zsh is already installed.")

def _install_powerlevel10k_and_set_theme():
    """
    Installs PowerLevel10k theme, downloads dot.p10k.zsh, and configures
    .zshrc.
    """
    print("\n--- Installing PowerLevel10k theme and setting it in ~/.zshrc ---")
    p10k_dir = os.path.expanduser("~/.oh-my-zsh/custom/themes/powerlevel10k")
    if not os.path.exists(p10k_dir):
        print("PowerLevel10k not found. Cloning repository...")
        run_command(f"git clone --depth=1 {POWERLEVEL10K_REPO_URL} " + p10k_dir)
        print("PowerLevel10k cloned successfully.")
    else:
        print("PowerLevel10k is already installed.")

    # Download dot.p10k.zsh using the new DotfileDownloader
    dotfile_downloader = DotfileDownloader(DOTFILES_BASE_URL)
    dotfile_downloader.download_dotfile("dot.p10k.zsh", "~/.p10k.zsh")

    zshrc_manager = ConfigFileManager("~/.zshrc")
    zshrc_manager.replace_line_prefix("ZSH_THEME=",
                                      'ZSH_THEME="powerlevel10k/powerlevel10k"')
    zshrc_manager.ensure_line_present("[ ! -f ~/.p10k.zsh ] || source "
                                      "~/.p10k.zsh")


def main():
    if sys.version_info[0] < 3:
        print("This script requires Python 3. Please run it with python3.")
        sys.exit(1)

    if not os.access(__file__, os.X_OK):
        print(f"Warning: Script '{__file__}' is not executable. Run 'chmod +x "
              f"{__file__}'")

    print("\n--- Running full system bootstrap ---")
    _setup_zsh()
    _install_base_packages()
    _configure_zshenv()
    _install_oh_my_zsh()
    _install_powerlevel10k_and_set_theme()
    _configure_vimrc()
    _install_vim_plug()
    _run_vim_plug_install()
    _create_ssh_rc_file()
    print("\n--- Setup complete! ---")

if __name__ == "__main__":
    main()

