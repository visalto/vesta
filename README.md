<p style="font-size: 40px; font-weight: bold">VESTA</p>
<p style="font-size: 16px; margin-top:-30px; margin-left:4px">Made by Visalto</p>
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
setup process (assuming docker engine is configured) of base can be achieved
in minutes

Finally we want to say THANK YOU to entire open source community and making this 
project open sourced is very important for us because without the community vesta 
would not exist! Thank you and please contribute to the Vesta project #todo: add open source contribution guidelines
