# CyberSentinel : Détection d'Anomalies de Sécurité via Big Data

![Cybersecurity](https://img.shields.io/badge/Domain-Cybersecurity-red)
![Big Data](https://img.shields.io/badge/Tech-Big_Data-blue)
![Docker](https://img.shields.io/badge/Infrastructure-Docker-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

##  Présentation du Projet
CyberSentinel est une solution de détection d'intrusions en temps réel spécialisée dans l'identification des attaques **Brute Force SSH**. Ce projet démontre comment les technologies Big Data peuvent surpasser les outils de surveillance classiques en traitant des flux massifs de logs avec une latence minimale.

L'objectif est de passer d'une analyse statique à une **défense proactive** capable d'identifier et de classifier une menace en quelques secondes.

##  Architecture Technique
Le système repose sur un pipeline de données moderne, résilient et entièrement conteneurisé :

1. **Génération/Ingestion** : Simulation de flux de logs SSH (réussites et échecs) envoyés vers **Apache Kafka**.
2. **Traitement (Stream Processing)** : **Apache Spark Streaming** consomme le flux et utilise des fenêtres glissantes (**Sliding Windows**) pour corréler les événements.
3. **Analyse & Alerte** : Identification des adresses IP suspectes dépassant un seuil critique (ex: > 10 tentatives en 30 secondes).
4. **Stockage & Indexation** : Les alertes structurées (JSON) sont indexées en temps réel dans **Elasticsearch**.
5. **Visualisation** : Un dashboard **Kibana** permet le monitoring, la géolocalisation des IPs et la classification de la sévérité.



##  Fonctionnalités Clés
- **Analyse Temps Réel** : Détection immédiate dès que l'attaque se produit.
- **Logique de Fenêtrage** : Distinction précise entre un oubli de mot de passe (basse fréquence) et une attaque automatisée (haute fréquence).
- **Classification par Sévérité** : Attribution automatique d'un niveau de risque (Medium/High) selon l'intensité de l'attaque.
- **Observabilité** : Dashboard dynamique pour une aide à la décision rapide des analystes SOC.

##  Stack Technologique
- **Langage** : Python (PySpark)
- **Streaming & Messaging** : Apache Kafka, Spark Streaming
- **Data Stack (ELK)** : Elasticsearch, Kibana
- **Infrastructure & DevOps** : Docker, Docker Compose

##  Structure du Projet
```text
CyberSentinel/
├── src/                               # Dossier technique (PoC)
│   ├── log-generator/                 # Simulateur d'attaques Python
│   ├── spark-job/                     # Script de détection PySpark
│   └── docker-compose.yml             # Orchestration de l'infrastructure
├── docs/
│   └── CyberSentinel_report.pdf       # Rapport technique complet
└── README.md
