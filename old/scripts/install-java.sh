#!/bin/bash

# Function to install Java
install_java() {
  sudo apt update
  sudo apt install -y openjdk-11-jdk
}

# Function to update .bashrc for JAVA_HOME and PATH
update_bashrc() {
  JAVA_HOME_LINE="export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64"
  PATH_LINE="export PATH=\$JAVA_HOME/bin:\$PATH"

  # Add JAVA_HOME and PATH only if they are not already in .bashrc
  grep -qF -- "$JAVA_HOME_LINE" ~/.bashrc || echo "$JAVA_HOME_LINE" >> ~/.bashrc
  grep -qF -- "$PATH_LINE" ~/.bashrc || echo "$PATH_LINE" >> ~/.bashrc

  # Reload .bashrc to apply changes
  source ~/.bashrc
}

# Check if Java is installed
java -version &>/dev/null
if [ $? -ne 0 ]; then
  echo "Java is not installed. Installing..."
  install_java
else
  echo "Java is already installed."
fi

# Update .bashrc for JAVA_HOME and PATH
update_bashrc

echo "Setup completed."
