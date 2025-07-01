#!/usr/bin/env python3
"""
FaceAuth Shell Completion Scripts
Provides auto-completion for bash and zsh shells.
"""

import click
import os
from pathlib import Path


def generate_bash_completion():
    """Generate bash completion script."""
    return '''#!/bin/bash
# FaceAuth bash completion script

_faceauth_completion() {
    local cur prev commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Main commands
    commands="enroll-face verify-face encrypt-file decrypt-file list-users delete-user auth-metrics crypto-info file-info system-check config-show config-set config-reset config-init version"
    
    # Complete main commands
    if [[ ${COMP_CWORD} == 1 ]]; then
        COMPREPLY=($(compgen -W "${commands}" -- ${cur}))
        return 0
    fi
    
    # Complete options based on command
    case "${prev}" in
        enroll-face|verify-face)
            # Complete with existing users if available
            if [[ -d ~/.faceauth/data ]]; then
                local users=$(ls ~/.faceauth/data 2>/dev/null | grep -v '\\.' | head -20)
                COMPREPLY=($(compgen -W "${users}" -- ${cur}))
            fi
            ;;
        encrypt-file|decrypt-file|file-info)
            # Complete with file names
            COMPREPLY=($(compgen -f -- ${cur}))
            ;;
        --output|-o)
            # Complete with file names for output
            COMPREPLY=($(compgen -f -- ${cur}))
            ;;
        --storage-dir|-s)
            # Complete with directories
            COMPREPLY=($(compgen -d -- ${cur}))
            ;;
        --timeout|-t|--auth-timeout)
            # Suggest common timeout values
            COMPREPLY=($(compgen -W "5 10 15 30 60" -- ${cur}))
            ;;
        --kdf-method|-k)
            # Complete with KDF methods
            COMPREPLY=($(compgen -W "argon2 pbkdf2 scrypt multi" -- ${cur}))
            ;;
        config-set)
            # Complete with config sections
            if [[ ${COMP_CWORD} == 3 ]]; then
                COMPREPLY=($(compgen -W "general authentication encryption enrollment" -- ${cur}))
            fi
            ;;
    esac
    
    # Complete common options
    if [[ ${cur} == -* ]]; then
        local opts="--help --verbose --quiet --timeout --storage-dir --output --overwrite --master-key --auth-timeout --kdf-method"
        COMPREPLY=($(compgen -W "${opts}" -- ${cur}))
    fi
}

complete -F _faceauth_completion faceauth
complete -F _faceauth_completion python main.py
'''


def generate_zsh_completion():
    """Generate zsh completion script."""
    return '''#compdef faceauth

# FaceAuth zsh completion script

_faceauth() {
    local context state line
    
    _arguments -C \\
        '1:commands:_faceauth_commands' \\
        '*::arg:->args' \\
        && return 0
    
    case $state in
        args)
            case $words[1] in
                enroll-face|verify-face)
                    _arguments \\
                        '--timeout[Authentication timeout]:timeout:(5 10 15 30 60)' \\
                        '--storage-dir[Storage directory]:directory:_directories' \\
                        '--master-key[Master key]:key:' \\
                        '--quiet[Quiet mode]' \\
                        '--verbose[Verbose mode]' \\
                        '--help[Show help]' \\
                        '1:user_id:_faceauth_users'
                    ;;
                encrypt-file|decrypt-file|file-info)
                    _arguments \\
                        '--output[Output file]:file:_files' \\
                        '--timeout[Authentication timeout]:timeout:(5 10 15 30 60)' \\
                        '--storage-dir[Storage directory]:directory:_directories' \\
                        '--master-key[Master key]:key:' \\
                        '--quiet[Quiet mode]' \\
                        '--verbose[Verbose mode]' \\
                        '--overwrite[Overwrite existing files]' \\
                        '--kdf-method[Key derivation method]:method:(argon2 pbkdf2 scrypt multi)' \\
                        '--help[Show help]' \\
                        '1:file:_files'
                    ;;
                delete-user|list-users)
                    _arguments \\
                        '--storage-dir[Storage directory]:directory:_directories' \\
                        '--master-key[Master key]:key:' \\
                        '--quiet[Quiet mode]' \\
                        '--verbose[Verbose mode]' \\
                        '--help[Show help]' \\
                        '1:user_id:_faceauth_users'
                    ;;
                config-set)
                    _arguments \\
                        '1:section:(general authentication encryption enrollment)' \\
                        '2:key:' \\
                        '3:value:'
                    ;;
            esac
            ;;
    esac
}

_faceauth_commands() {
    local commands
    commands=(
        'enroll-face:Enroll a new user face'
        'verify-face:Verify user identity'
        'encrypt-file:Encrypt a file'
        'decrypt-file:Decrypt a file'
        'list-users:List enrolled users'
        'delete-user:Delete user enrollment'
        'auth-metrics:Show authentication metrics'
        'crypto-info:Show crypto information'
        'file-info:Show file information'
        'system-check:Check system requirements'
        'config-show:Show configuration'
        'config-set:Set configuration value'
        'config-reset:Reset configuration'
        'config-init:Initialize configuration'
        'version:Show version'
    )
    _describe 'commands' commands
}

_faceauth_users() {
    local users_dir="$HOME/.faceauth/data"
    if [[ -d "$users_dir" ]]; then
        local users=(${(f)"$(ls $users_dir 2>/dev/null | grep -v '\\.')"})
        _describe 'users' users
    fi
}

_faceauth
'''


@click.group()
def completion_commands():
    """Shell completion management commands."""
    pass


@completion_commands.command('install-completion')
@click.option('--shell', type=click.Choice(['bash', 'zsh', 'auto']), default='auto',
              help='Shell type (auto-detect if not specified)')
@click.option('--path', help='Custom installation path')
def install_completion(shell: str, path: str):
    """Install shell completion scripts."""
    
    if shell == 'auto':
        # Auto-detect shell
        shell_path = os.environ.get('SHELL', '')
        if 'zsh' in shell_path:
            shell = 'zsh'
        elif 'bash' in shell_path:
            shell = 'bash'
        else:
            click.echo("❌ Could not auto-detect shell. Please specify --shell option.", err=True)
            return
    
    home = Path.home()
    
    if shell == 'bash':
        if path:
            completion_file = Path(path)
        else:
            # Try common bash completion directories
            completion_dirs = [
                home / '.bash_completion.d',
                Path('/usr/local/etc/bash_completion.d'),
                Path('/etc/bash_completion.d')
            ]
            
            completion_dir = None
            for dir_path in completion_dirs:
                if dir_path.exists() or dir_path.parent.exists():
                    completion_dir = dir_path
                    break
            
            if not completion_dir:
                completion_dir = home / '.bash_completion.d'
                completion_dir.mkdir(exist_ok=True)
            
            completion_file = completion_dir / 'faceauth'
        
        # Write bash completion script
        completion_file.write_text(generate_bash_completion())
        
        click.echo(f"✅ Bash completion installed to: {completion_file}")
        click.echo("To activate, add this to your ~/.bashrc:")
        click.echo(f"source {completion_file}")
        
    elif shell == 'zsh':
        if path:
            completion_file = Path(path)
        else:
            # Check for zsh completion directory
            zsh_dir = home / '.zsh'
            if not zsh_dir.exists():
                zsh_dir.mkdir()
            
            completion_file = zsh_dir / '_faceauth'
        
        # Write zsh completion script
        completion_file.write_text(generate_zsh_completion())
        
        click.echo(f"✅ Zsh completion installed to: {completion_file}")
        click.echo("To activate, add this to your ~/.zshrc:")
        click.echo(f"fpath=(~/.zsh $fpath)")
        click.echo("autoload -U compinit && compinit")


@completion_commands.command('generate-completion')
@click.option('--shell', type=click.Choice(['bash', 'zsh']), required=True,
              help='Shell type')
def generate_completion(shell: str):
    """Generate completion script for specified shell."""
    
    if shell == 'bash':
        click.echo(generate_bash_completion())
    elif shell == 'zsh':
        click.echo(generate_zsh_completion())


if __name__ == '__main__':
    completion_commands()
