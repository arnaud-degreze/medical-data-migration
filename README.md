# CSV To Mongo - Medical Data Migration

## OVERVIEW

This project implements a **Python pipepline** to load, clean, transform and migrate healthcare admission data from a CSV file to a MongoDB database.  
The main objective is to structure patients and admissions data into two separate collections, while preserving their relationships.

## FEATURES

- CSV loading with pandas.
- Data cleaning and duplicate removal
- Data validation
- Patient identification and data transformation
- Migration to MongoDB using PyMongo
- MongoDB index creation
- Unit testing with pytest
- Containerized execution with Docker Compose

## PREREQUISITES

- Git
- Docker Engine
- Docker Compose

Python and MongoDB do not need to be installed locally beforehand. Docker Compose will take care of it when running the pipeline.

## Architecture
The proposed pipeline works by following these steps:
- Loading : read the CSV file.
- Cleaning : standardize the column names, handle missing values and remove the duplicates.
- Validation : check the structure and validity of the data.
- Transform : separates patients information from admission records, and associate patients identifiers.
- Migration : insert the transformed data into MongoDB and creates the necessary indexes.

The architecture scheme can be visualized just below.

![alt text](images/folder-structure.png)

## Application

### Clone the repository

```console
git clone https://github.com/arnaud-degreze/medical-data-migration
cd <REPO_PATH>
```

### Run the migration

Start MongoDB -
```console
docker compose up -d mongodb
```
Build the Python image and lauch the migration - 
```console
docker compose run --build --rm migration
```
The default configuration will use the sample CSV file included in the /data/sample folder.

### Verify the results 

Connect to MongoDB -
```console
docker compose exec mongodb mongosh medical
```

Inspect the collections - 
```console
show collections
db.patients.countDocuments({})   # Will show how many patients we have in the collection
db.admissions.countDocuments({}) # Same but for admissions
```

In case you want to take a look at a document -
```console
db.patients.find({}).limit(1)    # Will show the first patient of the collection 
db.admissions.find({}).limit(1)  # Respectively for an admission
```


