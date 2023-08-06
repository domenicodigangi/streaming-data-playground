
# Get the folder name as input
read -p "Enter the project name: " proj_name

cd /workspaces/streaming-anomaly-detection/microservices/${proj_name}
source "venv_${proj_name}"/bin/activate

uvicorn src.${proj_name}.app.main:app --host 0.0.0.0 --port 8000
