<a name="readme-top"></a>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#installation">Installation</a>
      <ul>
        <li><a href="#prérequis">Prérequis</a></li>
        <li><a href="#initialisation">Initialisation</a></li>
        <li><a href="#lancement">Lancement</a></li>
      </ul>
    </li>
  </ol>
</details>


<!-- INITIALISATION -->
# Installation

## Prérequis


### Ubuntu 

Version 20.04 (ou 18.04 pas testé), ne fonctionne pas avec la version 22.04.

### Packages via apt 

De nombreux packages dans cette liste sont inutiles, à trier.

```sh
sudo apt-get update && apt install \
    wget
    apt-utils \
    build-essential \
    python \
    vim \
    locate \
    curl \
    python3-pip \
    npm \    
    gfortran \
    libcurl4-openssl-dev \
    gcc \
    libpython3-dev \
    git \
    libldap2-dev \
    libsasl2-dev \
    python3-pip 
    
sudo apt install python3.8-venv    
```

### Librairies via pip

```sh
sudo python3 -m pip install --upgrade \
    pip \
    setuptools \
    setuptools_scm \
    wheel 
```

### RabbitMQ via apt

- Voir le lien suivant : https://www.rabbitmq.com/install-debian.html et suivre les indications des sections "Cloudsmith Quick Start Script" et "Add Repository Signing Keys" (le paquet rabbitmqctl n'est pas trouvable avec la commande "sudo apt-get install rabbitmqctl")

- Si problème avec rabbitmqctl : https://stackoverflow.com/questions/58689551/rabbitmq-vhost-is-down-for-user-xyz-even-after-user-has-all-access

- Problèmes courants avec rabbitMQ :

```sh
sudo rabbitmqctl status
```

### MongoDB via apt (Installation pour ubuntu 20.04 (focal))

- Installation :
```sh
curl -fsSL https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -
apt-key list
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list
sudo apt update
sudo apt install mongodb-org
```

- OU suivre les indications du liens suivants (section "Install MongoDB Community Edition") : https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/ 


- Problème courant lié à MongoDB

Voir : 
https://developpaper.com/spring-boot-mongodb/
https://askubuntu.com/questions/823288/mongodb-loads-but-breaks-returning-status-14

```sh
sudo rm /var/lib/mongodb/mongod.lock
```

- Lancement : 

```sh
sudo systemctl start mongod.service
sudo systemctl status mongod
sudo systemctl enable mongod
mongo --eval 'db.runCommand({ connectionStatus: 1 })'
```

## Initialisation

### Installation de Girder via PyEnv

1. Initialiser l'environnement du projet
    ```sh
    mkdir GirderEcosystem
    cd GirderEcosystem
    python3 -m venv PyGirderEnv
    ```

2. Activer l'environnement virtuel python
    ```sh
    source PyGirderEnv/bin/activate
    ```

3. Installer (minimale) les paquets python pour faire tourner girder
    ```sh
    pip install wheel
    pip install girder
    ```

4. Installation étendue
    ```sh
    pip install scikit-image
    pip install scikit-learn
    pip install skimage
    pip install matplolib
    pip install nibabel
    ```

### Installation des plugins officiel Girder via pip

Toujours dans l'environnement virtuel.

```sh
pip install girder-dicom-viewer
pip install girder-user-quota
pip install girder-virtual-folders
pip install girder-homepage
pip install girder-jobs
pip install girder-autojoin
pip install girder-client
pip install girder-slicer-cli-web
pip install girder-worker
```

### Installation des plugins développés dans Girder

Toujours dans l'environnement virtuel.

1. Dans un dossier Plugins à partir de la racine, cloner le dépôt
    ```sh
    mkdir Plugins
    git clone https://github.com/valeryozenne/plugin_uct
    ```
2. Se déplacer sur la branche "PFA_plugins"
    ```sh
    git checkout PFA_plugins
    ```
3. Installer chaque plugin
    ```sh
    pip install <nom_du_plugin>/
    ```

### Ressources du projet

Doivent être créées à la racine du projet (GirderEcosystem), pourront être déplacer dans un répertoire "ressources" par la suite. 

- Templates de mails

success_template.txt:
```text
Destinataire: ${PERSON_NAME}, 
Nom du job: ${JOB_NAME},
Heure de début: ${START_HOUR},
Fichier traité: ${PROCESSED_FILE},
Etat: Succès
```

canceled_template.txt:
```text
Destinataire: ${PERSON_NAME}, 
Nom du job: ${JOB_NAME},
Heure de début: ${START_HOUR},
Fichier traité: ${PROCESSED_FILE},
Etat: Annulé
```

error_template.txt:
```text
Destinataire: ${PERSON_NAME}, 
Nom du job: ${JOB_NAME},
Heure de début: ${START_HOUR},
Fichier traité: ${PROCESSED_FILE},
Etat: Erreur
```

- Fichier de configuration du server webmail

settings.txt:
```json
{
    "SMTP_ENCRYPTION": "...",
    "SMTP_HOST": "...",
    "SMTP_PASSWORD": "...",
    "SMTP_PORT": "...",
    "SMTP_USERNAME": "..."
}
```

### Images du Micro CT

Dans dossier Girder_MicroCT à partir de la racine.

## Lancement

Toujours dans l'environnement virtuel.
  
1. Build du projet
    ```sh
    girder build
    ```

2. Lancement de Girder à partir de la racine
    ```
    girder serve
    ```

3. Lancer celery dans un deuxième terminal

```
celery -A worker  girder_worker.app -l info -E 
```

## Annexes

- Dans le plugin "PyGirderEnv/lib/python3.8/site-packages/plugin_uct/init.py", modifier les lignes 201 et 222
    ```python
    201: folder_json_dictionarybase_uct='/chemin/absolu/vers/GirderEcosystem/Girder_MicroCT/'
    222: collection_id='id_de_la_collection_ou_inserer_les_json'
    ```

- Pour que le worker detecte les tâches à lancer, vous trouverez dans "PyGirderEnv/lib/python3.8/site-packages/girder_worker/docker/init.py" la fonction task_imports 

    ```python
    def task_imports(self):
        return ['girder_worker.docker.tasks']
    ```
Y ajouter les chemings vers les dossiers des tasks à détecter

```python
def task_imports(self):
    return ['girder_worker.docker.tasks','plugin_uct.Tasks']
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>
