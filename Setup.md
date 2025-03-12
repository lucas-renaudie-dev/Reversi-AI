You might have tried setting up the project and run into issues like conflicting library versions or incompatible Python versions. If you're facing challenges, follow this guide to set up your environment step by step.

Tip: Use Conda for managing isolated environments—it simplifies handling dependencies and Python versions. If you don’t have Conda installed, refer to the Miniconda installation guide.

1. Start by cloning the project repository from GitHub: <br>
`git clone https://github.com/dmeger/COMP424-Fall2024.git`

2. Create a new Conda environment for the project with python 3.9: <br>
`conda create -n <environment-name> python=3.9` <br>
Replace `<environment-name>` with a name of your choice, e.g. comp424. 

3. Activate your Conda environment: <br>
`conda activate <environment_name>` <br>
After this you should see the environment name appear at the beginning of your terminal prompt. This indicates that your environment is active in the current terminal session. 

4. From the COMP424-Fall2024 directory, install project dependencies: <br> 
`pip install -r requirements.txt`

5. Run the following command to test the setup: <br>
`python simulator.py --player_1 random_agent --player_2 random_agent`

6. You can deactivate your environment by conda deactivate.
To reactivate the environment in a new session, follow Step 3.

If you are still encountering errors, try downgrading numpy to a version older than 2, such as 1.26.4 (the version needs to be between 1.22 and 2): <br>
`pip3 install --upgrade numpy==1.26.1`
