# MSPR6.3 et 6.4
Installer le front
Dans le dossier front 
1 - ouvrir le terminal
2- lancer la commande npm install

Pour lancer le front
 npm run dev

## Les dépendances python du projet ##
pip install -r pandemie_api/requirements.txt -r ETL/requirements.txt  -r IA/requirements.txt

## Lancement du serveur ## 
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

 
## ETL ##
python -m venv venv
..\venv\Scripts\Activate.ps1


## Training du model ##
python training.py 1 -l 14 -o ./saved_models/

# Pour les variables d'environnemnts
pip install python-dotenv

##  Lancement des script python
python etl_suivi_pandemie.py --input_file data/covid.csv --virus_id 1 --nom_maladie "covid-19" --description "ajout du data-sets sur le covid-19"
python etl_suivi_pandemie3.py --input_file data/variole.csv --virus_id 2 --nom_maladie "variole du singe" --description "ajout du data-sets sur la variole du singe"
python test_model.py 1 33   


## IA ##
python -m venv venv
pip install numpy
pip install scikit-learn
pip install pandas sqlalchemy mysql-connector-python statsmodels scikit-learn matplotlib
pip install python-dotenv
pip install xgboost
pip install fastapi
