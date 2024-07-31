sudo apt-get update; sudo apt-get install make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
curl https://pyenv.run | bash

#!/bin/bash

# File to append to
BASHRC="$HOME/.bashrc"

# Lines to append
NEW_LINES="# pyenv
export PATH=\"\$HOME/.pyenv/bin:\$PATH\"
eval \"\$(pyenv init --path)\"
eval \"\$(pyenv virtualenv-init -)\""
echo $NEW_LINES
# Check if NEW_LINES are already present
if ! grep -q "# pyenv" "$BASHRC"; then
  echo "$NEW_LINES" >> "$BASHRC"
  echo "Lines appended to .bashrc."
else
  echo "Lines are already in .bashrc."
fi
