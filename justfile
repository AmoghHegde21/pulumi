# ================================
# VARIABLES
# ================================

wrapper_path := env_var("HOME") + "/tools-venv/bin/virtualenvwrapper.sh"
venv_name := "pulumi_env"

python_path := env_var("WORKON_HOME") + "/" + venv_name + "/bin/python"
venv_path := env_var("WORKON_HOME") + "/" + venv_name

python_version := "python3.13"

controller := "pulumi_controller.py"

# ================================
# ALIASES
# ================================

alias i := install
alias u := up
alias p := preview
alias d := destroy
alias r := refresh
alias c := cancel

# ================================
# DEFAULT
# ================================

default:
    just --list

# ================================
# VENV SETUP
# ================================

venv:
    #!/bin/bash
    set -e

    if [ ! -d "$WORKON_HOME/{{venv_name}}" ]
    then
        source {{wrapper_path}}
        mkvirtualenv -p {{python_version}} {{venv_name}} || echo "Ignore activation"
        echo "Virtualenv created: {{venv_name}}"
    fi

# ================================
# INSTALL
# ================================

install-deps:
    #!/bin/bash
    set -e
    {{python_path}} -m pip install --upgrade pip
    {{python_path}} -m pip install pip-tools

install-requirements:
    #!/bin/bash
    set -e
    {{python_path}} -m pip install -r requirements.txt

install: venv install-deps install-requirements
    #!/bin/bash
    echo "Install setup completed"

# ================================
# CLEAN
# ================================

clean:
    #!/bin/bash
    set -e

    if [ -d "{{venv_path}}" ]
    then
        source {{wrapper_path}}
        rmvirtualenv {{venv_name}}
    fi

    echo "Environment cleaned"

# ================================
# PULUMI COMMANDS
# ================================

up *args:
    #!/bin/bash
    set -e
    {{python_path}} {{controller}} up {{args}}

preview *args:
    #!/bin/bash
    set -e
    {{python_path}} {{controller}} preview {{args}}

destroy *args:
    #!/bin/bash
    set -e
    {{python_path}} {{controller}} destroy {{args}}

refresh *args:
    #!/bin/bash
    set -e
    {{python_path}} {{controller}} refresh {{args}}

cancel *args:
    #!/bin/bash
    set -e
    {{python_path}} {{controller}} cancel {{args}}


# ================================
# STACK HELPERS
# ================================

stack-select stack:
    #!/bin/bash
    pulumi stack select {{stack}}

stack-init stack:
    #!/bin/bash
    pulumi stack init {{stack}}

stack-rm stack:
    #!/bin/bash
    pulumi stack rm {{stack}} --yes

stacks:
    #!/bin/bash
    pulumi stack ls


