

Mode d'emploi 
========================

## Commandes à lancer une fois pour initialiser ElasticSearch et l'image docker des scripts :

```sh
cd src
docker build -t mappings:0.0.1 mappings
docker run -d -p 127.0.0.1:9411:9200 mappings:0.0.1
docker build -t poseidon:0.0.1 .
```

## Commandes à ré-excécuter pour mettre à jour l'index Elastic Search avec la donnée source dans data/scenarios.csv, et lancer le script :  
#### (Adapt to local path)

```sh
docker run -ti --network=host -v $PWD/data:/data poseidon:0.0.1
```
