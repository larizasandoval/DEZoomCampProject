## Scientific Production in Honduras Data Pipeline
---

### Problem Statement
---
Honduras is a small Central American country with a growing intellectual development distributed across its universities and research centers. However, this generated knowledge faces a barrier of dispersion. There is a critical disconnect between the generation of science and its monitoring. Lacking an infrastructure to centralize, standardize, and analyze these publications, the country suffers from statistical invisibility regarding articles published in scientific journals.

This project aims to build a data pipeline and transform it into actionable insights, visualizing key metrics such as: 
* **The volume of publications per year** and
*  **their distribution by participating institucion**

### Data source
The dataset comes from the [Crossref](https://www.crossref.org/) database, which is the world's largest registry of [DOIs (Digital Object Identifiers)](https://es.wikipedia.org/wiki/Identificador_de_objeto_digital). 


Crossref provides a [REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/).  So about the dataset: 
- Nature: Semi-structured data (JSON).
- Extraction Filter: Scientific articles where at least one author's **affiliation** is some of the following academic institutions:
    * Universidad Nacional Autonoma de Honduras (UNAH)
    * Universidad Pedagógica Nacional Francisco Morazán (UPNFM)
    * Escuela Agrícola Panamerica del Zamorano 
    * Universidad Tecnológica Centroamericana (UNITEC)

Fields of interest:
* DOI: The article's unique identifier (our Primary Key).

* Title: Article title (can be in English or Spanish).

* Published-Print / Published-Online: Publication dates.

* Author (Nested JSON): A nested list containing the authors' names and, their affiliations, among others
### Architecture  & Tech Stack

![Arquitecture adn Tech diagram](assets/infrastructure_diagram.png)

| Layer         |      Tool     |  Role |
| ------------- | :-----------: | :----: |
| Infrastructure (IaC)	| Terraform | Cloud Provisioning: Automatically define and create Buckets, Datasets, and Permissions (IAM) in GCP. |
| Ingestion   | Python  | API Extraction consuming the Crossref API
|  Orchestration    |  Kestra    | Workflow Manager. Executes the Python script,   and load the data into the bucket and create a raw table in the bigquery dataset |
| Storage (Load) | Google Cloud Storage | Data Lake Object repository where the original .json files are stored as a backup |
| Datawarehouse | Google BigQuery  |  Analytics Storage. Engine where the data resides. Supports JSON processing and bulk SQL queries. |
|Transformation | dbt  | Data Modeling Cleans, normalizes, and unifies tables, generete final factable for consumption   |
|Visualization| Shiny for python | BI / Dashboarding Interactive web interface that displays insightful charts

### Directory Project Structure
```
DEZoomCampProject
├── 1-infra-terraform                           #Cloud infrastructure
│   ├── main.tf
│   └── variables.tf
├── 2-orchestration-kestra                      
│   ├── flow.yml                                #Kestra flow to extract and load data into the bucket and create the raw data table
│   ├── script_source.py                        #Python script for extraction from api ifself
├── 3-tranform-dbt                              #dbt transformation
│   └── science_production
│       ├── dbt_project.yml
│       ├── models
│       │   ├── marts
│       │   │   └── ftc_science_production.sql  #Final tables with all articles
│       │   └── staging
│       │       ├── source.yml                  #BigQuery raw data table
│       │       ├── stg_afiliations.sql         #Table with desired affiliation 
│       │       └── stg_works.sql               #Table with articles from desired affiliation
├── 4-visualization-shiny
│   └── dashboard
│       ├── app.py                              #Main python file for shiny application
│       ├── requirements.txt                    #Requirement for python and shiny
│       ├── shared.py                           #File path management for the shiny application
│       └── styles.css                          #Visual styles for applicacion
```

### Dashboard

The dashboard was developed using [**Shiny for Python**](https://shiny.posit.co/py/), a fantastic and fast tool!

First, a connection was established to the data source using a Service Account to communicate with BigQuery. The `fct_science_production` table was queried, where the data is clean and normalized.

You can see a live demo here: [Scientific Production in Honduras](https://shiny.posit.co/py/)

We can see the following metrics:
* Number of articles whose authors are affiliated with the academic institutions of interest.
* Number of journals in which these articles are published.
* Articles distributed by institution.
* Number of articles published per year.

![Arquitecture adn Tech diagram](assets/Dashboard_capture.png)