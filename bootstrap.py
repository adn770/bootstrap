#!/usr/bin/env python3

import subprocess
import os
import sys
import time # Added for sleep

def run_command(command, message=None, check=True):
    """
    Runs a shell command, prints output, and handles errors.
    """
    if message:
        print(f"\n--- {message} ---")
    try:
        process = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if process.stdout:
            print(process.stdout)
        if process.stderr:
            print(process.stderr)
        return process
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Command not found: {command.split()[0]}")
        sys.exit(1)

def action_base():
    """
    Sets up Zsh as the default shell and installs base packages including Vim-Plug.
    """
    print("\n--- Running 'base' action: Setting up Zsh and installing base packages ---")

    # Check and install zsh
    print("Checking for Zsh installation...")
    result = run_command("which zsh", check=False)
    if result.returncode != 0:
        print("Zsh not found. Installing Zsh...")
        run_command("sudo apt update")
        run_command("sudo apt install -y zsh")
        print("Zsh installed successfully.")
    else:
        print("Zsh is already installed.")

    # Change default shell to zsh if not already
    current_shell = os.environ.get('SHELL')
    if current_shell != "/usr/bin/zsh" and current_shell != "/bin/zsh":
        print("Changing default shell to Zsh...")
        run_command(f"chsh -s $(which zsh) {os.getenv('USER')}")
        print("Default shell changed to Zsh. Please log out and log back in for changes to take effect.")
    else:
        print("Zsh is already your default shell.")

    # Install desired packages
    packages = ["vim", "git", "fzf", "btop", "tmux", "cmake", "bat", "zoxide", "curl"] # Added curl for vim-plug
    print(f"Installing base packages: {', '.join(packages)}...")
    run_command("sudo apt update")
    run_command(f"sudo apt install -y {' '.join(packages)}")
    print("Base packages installed successfully.")

    # Install Vim-Plug
    print("\n--- Installing Vim-Plug ---")
    vim_autoload_dir = os.path.expanduser("~/.vim/autoload")
    vim_plug_path = os.path.join(vim_autoload_dir, "plug.vim")

    if not os.path.exists(vim_plug_path):
        print(f"Creating directory: {vim_autoload_dir}")
        run_command(f"mkdir -p {vim_autoload_dir}")
        print(f"Downloading Vim-Plug to {vim_plug_path}...")
        run_command(f"curl -fLo {vim_plug_path} --create-dirs https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim")
        print("Vim-Plug installed successfully.")
        print("\n--- IMPORTANT: Remember to add the Vim-Plug configuration to your ~/.vimrc and run :PlugInstall in Vim. ---")
        print("  Example .vimrc configuration:")
        print("  call plug#begin('~/.vim/plugged')")
        print("  Plug 'tpope/vim-fugitive'")
        print("  Plug 'airblade/vim-gitgutter'")
        print("  call plug#end()")
        time.sleep(2) # Pause briefly to ensure the message is seen
    else:
        print("Vim-Plug is already installed.")


def action_ohmyzsh():
    """
    Installs Oh My Zsh and PowerLevel10k, and sets the theme.
    """
    print("\n--- Running 'ohmyzsh' action: Installing Oh My Zsh and PowerLevel10k ---")

    ohmyzsh_dir = os.path.expanduser("~/.oh-my-zsh")
    if not os.path.exists(ohmyzsh_dir):
        print("Installing Oh My Zsh...")
        # The Oh My Zsh installer might try to change the shell and create .zshrc if it doesn't exist.
        # We use --unattended to prevent it from prompting to change shell.
        run_command('sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended',
                    message="Running Oh My Zsh installer (unattended)", check=False)
        print("Oh My Zsh installed successfully.")
    else:
        print("Oh My Zsh is already installed.")

    p10k_dir = os.path.expanduser("~/.oh-my-zsh/custom/themes/powerlevel10k")
    if not os.path.exists(p10k_dir):
        print("Installing PowerLevel10k...")
        run_command("git clone --depth=1 https://github.com/romkatv/powerlevel10k.git " + p10k_dir)
        print("PowerLevel10k cloned successfully.")
    else:
        print("PowerLevel10k is already installed.")

    # Automatically set ZSH_THEME to powerlevel10k/powerlevel10k in .zshrc
    zshrc_path = os.path.expanduser("~/.zshrc")
    if os.path.exists(zshrc_path):
        print(f"Updating ZSH_THEME in {zshrc_path}...")
        try:
            with open(zshrc_path, 'r') as f:
                lines = f.readlines()

            new_lines = []
            theme_set = False
            for line in lines:
                if line.strip().startswith("ZSH_THEME="):
                    if not theme_set: # Only modify the first occurrence
                        new_lines.append('ZSH_THEME="powerlevel10k/powerlevel10k"\n')
                        theme_set = True
                        print(f"  - Changed 'ZSH_THEME' line.")
                    else:
                        new_lines.append(line) # Keep subsequent ZSH_THEME lines as they are (unlikely but safe)
                else:
                    new_lines.append(line)

            if not theme_set:
                # If ZSH_THEME was not found, add it to the end of the file
                new_lines.append('\nZSH_THEME="powerlevel10k/powerlevel10k"\n')
                print(f"  - Added 'ZSH_THEME' line to {zshrc_path}.")

            with open(zshrc_path, 'w') as f:
                f.writelines(new_lines)
            print("ZSH_THEME set to 'powerlevel10k/powerlevel10k' in ~/.zshrc.")

        except Exception as e:
            print(f"Error modifying {zshrc_path}: {e}")
            print("Please manually set ZSH_THEME=\"powerlevel10k/powerlevel10k\" in your ~/.zshrc file.")
    else:
        print(f"Warning: {zshrc_path} not found. Cannot set PowerLevel10k theme automatically.")
        print("Please ensure Oh My Zsh creates .zshrc or create it manually, then set ZSH_THEME=\"powerlevel10k/powerlevel10k\".")


def print_usage():
    print("Usage: ./bootstrap.py [action1] [action2] ...")
    print("Available actions:")
    print("  base      - Sets up Zsh, changes default shell, and installs essential packages (including Vim-Plug).")
    print("  ohmyzsh   - Installs Oh My Zsh and PowerLevel10k theme.")
    sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print_usage()

    actions = {
        "base": action_base,
        "ohmyzsh": action_ohmyzsh,
    }

    selected_actions = sys.argv[1:]

    for action_name in selected_actions:
        if action_name in actions:
            actions[action_name]()
        else:
            print(f"Error: Unknown action '{action_name}'")
            print_usage()

    print("\n--- Setup complete! ---")
    print("Remember to log out and log back in for shell changes and theme to take full effect.")
    print("For PowerLevel10k, configure it by running `p10k configure` after opening a new Zsh session.")

if __name__ == "__main__":
    # Ensure the script is run with python3
    if sys.version_info[0] < 3:
        print("This script requires Python 3. Please run it with python3.")
        sys.exit(1)

    # Make sure the script is executable
    if not os.access(__file__, os.X_OK):
        print(f"Warning: Script '{__file__}' is not executable. Run 'chmod +x {__file__}'")

    main()
