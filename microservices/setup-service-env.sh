
# Get the folder name as input
read -p "Enter the project name: " proj_name

cd ${proj_name}
python -m venv "venv_${proj_name}"
source "venv_${proj_name}"/bin/activate
pip install -r requirements.txt