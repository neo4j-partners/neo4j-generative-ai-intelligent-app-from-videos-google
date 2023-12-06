VENV=py38
conda create -y -q -p $HOME/conda_env/$VENV python=3.8 ipykernel
source /opt/conda/bin/activate ~/conda_env/$VENV
python -m ipykernel install --user --name $VENV
conda install -y -c conda-forge ipywidgets