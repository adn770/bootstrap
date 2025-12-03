#!/usr/bin/env python3

import subprocess
import os
import sys
import shutil
import platform

# --- Global Constants for URLs ---
OH_MY_ZSH_INSTALL_URL = "https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh"
POWERLEVEL10K_REPO_URL = "https://github.com/romkatv/powerlevel10k.git"
VIM_PLUG_URL = "https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim"
# Base URL for dotfiles from adn770/bootstrap repository
DOTFILES_BASE_URL = "https://raw.githubusercontent.com/adn770/bootstrap/main"

# GitHub API for fetching latest mkcert release (fallback for Ubuntu)
MKCERT_LATEST_RELEASE_URL = "https://api.github.com/repos/FiloSottile/mkcert/releases/latest"

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
        # Only print stdout/stderr if they haven't been consumed by the loop above
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
        """Ensures a specific line is present in the file."""
        normalized_line_to_add = line_to_add.strip()

        for line in self.content:
            if normalized_line_to_add in line.strip():
                print(f"Content '{normalized_line_to_add}' already exists in {self.file_path}. Skipping.")
                return True

        if after_line_prefix:
            found_idx = -1
            for i, line in enumerate(self.content):
                if line.strip().startswith(after_line_prefix):
                    found_idx = i
                    break

            if found_idx != -1:
                self.content.insert(found_idx + 1, line_to_add + "\n" if not line_to_add.endswith('\n') else line_to_add)
            else:
                if not self.content or not self.content[-1].endswith('\n'):
                    self.content.append('\n')
                self.content.append(line_to_add + "\n" if not line_to_add.endswith('\n') else line_to_add)
        else:
            if not self.content or not self.content[-1].endswith('\n'):
                self.content.append('\n')
            self.content.append(line_to_add + "\n" if not line_to_add.endswith('\n') else line_to_add)

        return self._write_file(self.content)

    def replace_line_prefix(self, prefix, new_line):
        """Replaces a line starting with a specific prefix with a new line."""
        new_content = []
        replaced = False
        for line in self.content:
            if line.strip().startswith(prefix):
                new_content.append(new_line + "\n" if not new_line.endswith('\n') else new_line)
                replaced = True
            else:
                new_content.append(line)

        if not replaced:
            if not new_content or not new_content[-1].endswith('\n'):
                new_content.append('\n')
            new_content.append(new_line + "\n" if not new_line.endswith('\n') else new_line)

        self.content = new_content
        return self._write_file(self.content)

    def overwrite_file(self, new_content):
        """Overwrites the entire file with new content."""
        self.content = [line + "\n" if not line.endswith('\n') else line for line in new_content.splitlines()]
        print(f"Overwriting {self.file_path}.")
        return self._write_file(self.content)

class PackageManager:
    """
    Handles package installation for different Linux distributions (Arch/Ubuntu).
    """
    def __init__(self):
        self.distro = self._detect_distro()
        print(f"Detected Distribution: {self.distro.upper()}")

    def _detect_distro(self):
        """Detects the Linux distribution."""
        try:
            with open("/etc/os-release") as f:
                content = f.read().lower()
                # Check for Arch or Arch-based (including CachyOS)
                if "id=arch" in content or "id_like=arch" in content or "cachyos" in content:
                    return "arch"
                # Check for Debian/Ubuntu
                if "ubuntu" in content or "debian" in content:
                    return "ubuntu"
        except FileNotFoundError:
            pass
        return "unknown"

    def update_repositories(self):
        """Updates package repositories."""
        print("Updating package repositories...")
        if self.distro == "arch":
            run_command("sudo pacman -Sy")
        elif self.distro == "ubuntu":
            run_command("sudo apt update")
        else:
            print(f"Warning: Update not implemented for {self.distro}")

    def install(self, packages):
        """Installs a list of packages."""
        if not packages:
            return

        print(f"Installing packages: {', '.join(packages)}...")
        if self.distro == "arch":
            # --needed skips already installed packages, --noconfirm avoids yes/no prompts
            run_command(f"sudo pacman -S --needed --noconfirm {' '.join(packages)}")
        elif self.distro == "ubuntu":
            run_command(f"sudo apt install -y {' '.join(packages)}")
        else:
            print(f"Error: Installation not implemented for {self.distro}")
            sys.exit(1)

    def get_distro_specific_name(self, package):
        """Handles naming differences between distros."""
        mapping = {
            "ubuntu": {
                "base-devel": "build-essential",
                "docker": "docker.io", # ubuntu typically uses docker.io or docker-ce
                "fd": "fd-find",       # installs as fdfind binary often, handled by zoxide usually
                "mkcert_deps": "libnss3-tools"
            },
            "arch": {
                "build-essential": "base-devel",
                "python3-dev": "python", # Arch python includes headers
                "fd-find": "fd",
                "mkcert_deps": "nss",
                "ollama": "ollama" # Arch usually has it in community/extra
            }
        }

        # Check if the specific distro has a mapped name
        if self.distro in mapping and package in mapping[self.distro]:
            return mapping[self.distro][package]

        # Check if the OTHER distro has this key, meaning we are using the generic key
        # and checking if we need to swap.
        if self.distro == "arch" and package == "build-essential":
            return "base-devel"
        if self.distro == "ubuntu" and package == "base-devel":
            return "build-essential"

        return package


class DotfileDownloader:
    """
    A helper class to download dotfiles from a specified GitHub repository.
    """
    def __init__(self, base_url):
        self.base_url = base_url

    def download_dotfile(self, dotfile_name, local_path=None):
        """
        Downloads a specific dotfile from the repository to a local path.
        """
        remote_url = f"{self.base_url}/{dotfile_name}"
        target_local_path = (os.path.expanduser(local_path if local_path
                                                else f"~/{dotfile_name}"))

        print(f"Downloading {remote_url} to {target_local_path}...")
        try:
            run_command(f"curl -fLo {target_local_path} {remote_url}")
            print(f"Successfully downloaded {dotfile_name} to {target_local_path}.")
            return True
        except Exception as e:
            print(f"Error downloading {dotfile_name}: {e}")
            return False

# --- Setup Functions ---

def _setup_zsh(pm: PackageManager):
    """
    Checks for Zsh, installs it if not present, and sets it as the default shell.
    """
    print("\n--- Setting up Zsh ---")
    print("Checking for Zsh installation...")
    result = run_command("which zsh", check=False)
    if result.returncode != 0:
        print("Zsh not found. Installing Zsh...")
        pm.install(["zsh"])
        print("Zsh installed successfully.")
    else:
        print("Zsh is already installed.")

    current_shell = os.environ.get('SHELL')
    if "zsh" not in current_shell:
        print("Changing default shell to Zsh...")
        try:
            run_command(f"chsh -s $(which zsh) {os.getenv('USER')}")
            print("Default shell changed to Zsh. Please log out and log back in.")
        except Exception as e:
            print(f"Could not change shell automatically: {e}")
            print("Run: chsh -s $(which zsh)")
    else:
        print("Zsh is already your default shell.")

def _install_base_packages(pm: PackageManager):
    """
    Installs a list of essential packages.
    """
    print("\n--- Installing base packages ---")

    # Common packages
    packages = ["bat", "btop", "cmake", "curl", "fzf", "gdb", "git", "tig",
                "tmux", "vim", "zoxide", "wget"]

    # Add distro-specific build tools
    if pm.distro == "arch":
        packages.append("base-devel")
        packages.append("python") # Ensure python is there
    else:
        packages.append("build-essential")
        packages.append("python3-pip")
        packages.append("python3-venv")

    # Resolve names
    final_packages = [pm.get_distro_specific_name(p) for p in packages]
    final_packages.sort()

    pm.install(final_packages)
    print("Base packages installed successfully.")

def _install_docker(pm: PackageManager):
    """
    Installs Docker, enables service, and adds user to group.
    """
    print("\n--- Installing and Configuring Docker ---")

    if pm.distro == "arch":
        docker_pkg = pm.get_distro_specific_name("docker")
        pm.install([docker_pkg])
    elif pm.distro == "ubuntu":
        print("Detected Ubuntu/Debian. Installing Docker from official repository...")

        # 1. Install prerequisites
        pm.install(["ca-certificates", "curl", "gnupg"])

        # 2. Add Docker's official GPG key
        # Create directory for keyrings if it doesn't exist
        run_command("sudo install -m 0755 -d /etc/apt/keyrings")
        # Download and save the GPG key
        run_command("sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc")
        run_command("sudo chmod a+r /etc/apt/keyrings/docker.asc")

        # 3. Add the repository to Apt sources
        # We assume standard /etc/os-release is available
        repo_cmd = (
            'echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] '
            'https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | '
            'sudo tee /etc/apt/sources.list.d/docker.list > /dev/null'
        )
        run_command(repo_cmd)

        # 4. Update and Install
        run_command("sudo apt update")
        # Install specific docker packages for Docker Engine
        run_command("sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin")

    print("Enabling and starting Docker service...")
    # Arch needs explicit enable --now, Ubuntu usually starts it but enable ensures it persists
    run_command("sudo systemctl enable --now docker")

    print("Adding current user to 'docker' group...")
    user = os.getenv('USER')
    try:
        run_command(f"sudo usermod -aG docker {user}")
        print(f"User {user} added to docker group. You may need to re-login.")
    except Exception as e:
        print(f"Failed to add user to docker group: {e}")

def _install_mkcert(pm: PackageManager):
    """
    Installs mkcert and its dependencies, prioritizing apt on Ubuntu/Debian
    and falling back to a binary download if apt fails.
    """
    print("\n--- Installing mkcert ---")

    # Dependencies (NSS tools)
    dep_pkg = pm.get_distro_specific_name("mkcert_deps")
    pm.install([dep_pkg])

    if pm.distro == "arch":
        # Arch has mkcert in community/extra
        pm.install(["mkcert"])
    elif pm.distro == "ubuntu":
        # Ubuntu apt: Try apt install first, then fallback to binary.
        print("Detected Ubuntu/Debian. Trying apt install for mkcert first...")

        # 1. Try apt install (check=False so script doesn't exit on failure)
        apt_install_cmd = f"sudo apt install -y mkcert"
        apt_install_proc = run_command(apt_install_cmd, check=False)

        if apt_install_proc.returncode == 0:
            print("mkcert installed successfully via apt.")
        else:
            # 2. Fallback to binary download
            print("Apt installation failed or mkcert package not found. Falling back to binary download from GitHub...")
            try:
                # Using curl to get the binary URL to avoid python dependency hell inside the bootstrap
                cmd = "curl -s https://api.github.com/repos/FiloSottile/mkcert/releases/latest | grep browser_download_url | grep linux-amd64 | cut -d '\"' -f 4"
                proc = run_command(cmd, check=False)
                download_url = proc.stdout.strip()

                if download_url:
                    target_path = "/usr/local/bin/mkcert"
                    run_command(f"sudo curl -L {download_url} -o {target_path}")
                    run_command(f"sudo chmod +x {target_path}")
                    print(f"mkcert binary installed to {target_path}")
                else:
                    print("Failed to fetch mkcert download URL.")
            except Exception as e:
                print(f"Error installing mkcert binary: {e}")

    # Run mkcert installation
    print("Running mkcert -install...")
    try:
        run_command("mkcert -install", check=False)
        print("mkcert CA installed.")
    except Exception:
        print("mkcert is installed but 'mkcert -install' failed. You may need to run it manually.")

def _install_ollama(pm: PackageManager):
    """
    Installs Ollama and configures the systemd override.
    """
    print("\n--- Installing and Configuring Ollama ---")

    # 1. Install Ollama
    if pm.distro == "arch":
        # Arch usually has a package, or we can use the script.
        # Using package manager is preferred on Arch for updates.
        print("Installing Ollama via pacman...")
        pm.install(["ollama"])
    else:
        # Ubuntu/Debian or others: Use the official install script to get the latest version
        print("Installing Ollama via official install script...")
        run_command("curl -fsSL https://ollama.com/install.sh | sh")

    # 2. Configure Systemd Override
    print("Configuring systemd override for Ollama...")
    override_dir = "/etc/systemd/system/ollama.service.d"
    override_file = f"{override_dir}/override.conf"

    override_content = """[Service]
#Environment="OLLAMA_DEBUG=1"
#Environment="HSA_OVERRIDE_GFX_VERSION=11.5.1"
Environment="OLLAMA_HOST=0.0.0.0"
Environment="OLLAMA_ORIGINS=*"
"""

    try:
        # Create directory securely
        if not os.path.exists(override_dir):
            run_command(f"sudo mkdir -p {override_dir}")

        # Write content using tee to handle sudo permission
        # Using echo with pipe to sudo tee
        run_command(f"echo '{override_content}' | sudo tee {override_file} > /dev/null")
        print(f"Created {override_file}")

        # Reload systemd and restart ollama
        run_command("sudo systemctl daemon-reload")
        run_command("sudo systemctl enable --now ollama")
        run_command("sudo systemctl restart ollama")
        print("Ollama service restarted with new configuration.")

    except Exception as e:
        print(f"Error configuring Ollama systemd override: {e}")


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
        # Check if vim is accessible
        run_command("vim --version", check=False)
        run_command("vim +PlugInstall +qall", message="Running Vim PlugInstall")
        print("Vim PlugInstall completed.")
    except Exception as e:
        print(f"Error running Vim PlugInstall: {e}")
        print("Please run 'vim +PlugInstall +qall' manually inside your terminal.")

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

        ssh_rc_manager = ConfigFileManager(ssh_rc_path)
        ssh_rc_manager.overwrite_file(ssh_rc_content)
        os.chmod(ssh_rc_path, 0o600)
        print(f"Permissions for '{ssh_rc_path}' set to 0o600.")

    except Exception as e:
        print(f"Error creating/modifying '{ssh_rc_path}': {e}")

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
    Installs PowerLevel10k theme, downloads dot.p10k.zsh, and configures .zshrc.
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
    zshrc_manager.ensure_line_present("[ ! -f ~/.p10k.zsh ] || source ~/.p10k.zsh")

def main():
    if sys.version_info[0] < 3:
        print("This script requires Python 3. Please run it with python3.")
        sys.exit(1)

    print("\n--- Running full system bootstrap ---")

    # Initialize Package Manager (Auto-detects OS)
    pm = PackageManager()
    pm.update_repositories()

    _install_base_packages(pm)
    _install_docker(pm)
    _install_mkcert(pm)
    _install_ollama(pm)

    _setup_zsh(pm)
    _configure_zshenv()
    _install_oh_my_zsh()
    _install_powerlevel10k_and_set_theme()
    _configure_vimrc()
    _install_vim_plug()
    _run_vim_plug_install()
    _create_ssh_rc_file()

    print("\n--- Setup complete! ---")
    print("Please log out and log back in for group changes (docker) and shell changes to take effect.")

if __name__ == "__main__":
    main()
