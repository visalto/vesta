# Vesta 

Vesta is open source data engineering platform with pre included batteries 
such as

1) Deploying and Executing pipelines (engine based on Airflow w/ Celery Executors technology)
2) code/dev environment(based on codercom/code-server docker image)
3) Web platform for performing ad hoc analysis and interacting with the rest of the components (Django)
     - User and permission management 
     - Workspace management 
     - Pipeline status monitoring and deployment
     - Platform API 
4) Git version management server (Gitea)
5) Custom CI/CD internal engine (FastAPI)
6) Dataset Storage (parquet datasets stored in container that can be mapped to desired disk location, on vm or attached)
7) Data / repo lineage (OpenLineage framework -> Marquez Docker)


**Note:** Platform is designed such that each instance of Vesta can be customized with additional docker
services. Fork the repo and adjust deployment #todo: Add some framework for adding batteries 

### Product mission
Visalto team (creators of Vesta) have a strong belief that in order for organizations and teams 
to scale effectively, continue to be innovative and mitigate the risk of incurring technical 
debt during pipeline, or any data related automation development, must have some common agreement
on how the artifacts they produce will be organized.
Most common ways datasets are used today can be put in 2 categories:
1) Reporting & Analysis
2) System / process feed (Datasets that are consumed by other processes to determine actions)

In the area of reporting and analytics there are many reoccurring requests as well as
requests that are just slightly different in requirements than the previous one, 
which means that **re-usability of datasets and existing work becomes important to 
provide prompt answers** but also to not get bugged down with doing same thing over
and over again just slightly different 

Goal for Vesta is to provide a true end-to-end data engineering platform that is open-sourced,
delivers boost of productivity and creativity for engineers and the
setup process (assuming docker engine is configured) of out of the box platform can be achieved
in minutes

Finally, we want to say THANK YOU to entire open source community and making this 
project open sourced is very important for us because without the community Vesta 
would not exist! Thank you and please contribute to the Vesta project #todo: add open source contribution guidelines

# Deployment and Setup
To get started with your own vesta instance first 
clone vesta git repostiry 
```
git clone https://github.com/visalto/vesta.git
```

Then open terminal and make sure you are in just cloned vesta repo
```sh 
git submodule update --remote --recursive --init && git submodule foreach --recursive git checkout <BRANCH_NAME>
```
todo: Add link to default vesta instance as well as any customized versions of it

I will add something more here when it is time 

# Contact 
I will add something more here when it is time 

# References 
I will add something more here when it is time 

# Notes during mac deployment 
1) scripts have to be executable otherwsie build failed 
     - Wonder if that has to be done by script or something else because git may not persist that 
2) marquez does not support arm64 (sillicon chip) -> maybe build my own? 
3) 10001 is a public facing port per mac mini pro m2