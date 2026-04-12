[Readme](README.md) | [Scenario](SCENARIO.md) | [License](LICENSE.md)

# Scénario de _Robot Recovery_

## Contexte:

Alors que la planète a dépérie à cause de l’humanité et la pollution que celle-ci a généré, l’humanité a déserté la planète Terre. Le joueur incarne un humain qui était en stase dans une station spatiale en orbite autour de la Terre, la but de cette station est de s’occuper de nettoyer la Terre alors que le reste de l’humanité est parti colonisé une autre planète.

La compagnie s’occupant de l’exploitation de la planète Terre s’appelant “Cyclope Industries”, a développer des robots ayant une IA faites pour exploiter les ressources de la planète Terre. Or, ceux-ci ne se sont pas arrêtés lors du départ de l’humanité de la Terre. Ce faisant, la situation sur la planète Terre ne s’arrange pas. Mais après une réunion d’urgence de cette institution, et l’intervention de l’ingénieure Mélanie Cavill, ceux-ci réalisent qu’ils pourraient reprogrammer les robots à distance pour qu’ils nettoient la Terre et participe à son “rétablissement”. Les organisations inter-gouvernementales décident alors de vous réveiller afin que vous preniez le contrôle de ces robots. Mélanie Cavill est nommé comme étant votre référente, elle vous aidera dans votre mission et vous soutiendra lors des moments difficiles.

## Explication narrative du gameplay:

L’accès aux robots se fait par l’utilisation d’une antenne encore fonctionnelle, mais malheureusement n’est pas assez vaste pour vous permettre de contrôler la totalité des robots, ce faisant, le héros devra parfois être amener à construire/convertir des antennes ou à les réparer. Egalement, il existe des robots parfaitement autonome qui doivent être détruit car ils ne sont pas reprogrammables, cependant, nous utilisons les pièces présentes sur eux afin d’améliorer les robots et fabriquer des infrastructures permettant de dépolluer les océans, purifier l’air, soutenir la flore locale (enrichissement des sols, hydratation des sols, etc…).


## Scénario détaillé:

### Niveau 0: "Le réveil"

### Niveau 1: "Tutoriel détaillé"

### Niveau 2: "La forêt"

### Niveau 3: "Le désert"

### Niveau 4: "Le boss final"


## Déroulé du jeu

Menu 

[PLAY] 

CHAPITRE 1 : 

Premier biome : Plaine verdoyante

- Cinematique  : Explication du scénario
- Cinématique :  Réveil et communication avec l’ingénieure / Explication de l’objectif
- Base: La Map n’est que disponible
- Niveau : Tutoriel
- Base: Tutoriel - Amélioration avec les modules
- Niveau :
- NIveau :
- Niveau :
- Niveau :
- Boss :
- Cinématique : Déblocage de l’Antenne

CHAPITRE 2 :

Second biome :  Désert 

- Niveau :
- NIveau :
- Niveau :
- Niveau :
- Boss :
- Cinématique : Déblocage de l’Antenne

CHAPITRE 3 :

Troisième biome : Ville abandonnée

- Niveau :
- NIveau :
- Niveau :
- Niveau :
- Boss :
- Cinématique : Déblocage de l’Antenne

CHAPITRE 4 : 

Centre industrielle

- Niveau :
- NIveau :
- Niveau :
- Niveau :
- Boss :
- Cinématique : Déblocage de l’Antenne


## Fonctionnalités

**Elements de gameplay :**

- Platformer
    - trajectoire gravitationelle
    - collisions
- Pistolet :
    - trajectoire prévisualisée
    - interaction avec les éléments du décor
    - c’est de l’eau donc ça a une physique d’eau
    - ça tue les robots ennemis
- Grappin :
    - trajectoire prévisualisée (dans les deux sens)
    - attrape et drag les objets vers le joueur
- Environnement :
    - Objets :
        - Elements destructifs (Ennemis, Dechets) ⇒ Recycler en scrap
        - Elements construcitfs (Améliorer l’eau, le soleil, l’energie) ⇒ impact la texture
        - Elements de passage : Porte, Ponts
- Ennemis :
    - robot type plus élément en fonction biomes
    - ia d’ennemis
        - en vrai juste il se dirige vers lui et il se stoppe quand y a du vide

**Scenes:**

- Menu Accueil
    - Nouvelle partie (un unique fichier)
    - Play
    - Help (commandes, etc.)
    - Credits
    - Quit
- Loading
- Base : gestion de base → amélioration d’arme
    - Amélioration module
    - Fabrication des modules
- Niveau (Generic)
- Map : fog of war, choix du niveau

 **UI :**

- Energie
    - état du robot
- compteurs (scrap, ressources du niveau, niveau de propreté)

**Technique**

- Sauvegarde
    - sauvegarde auto à la fin du niveau
    - joueur peut sauvegarder à la base (unique endroit où sauvegarde possible)
- Chargement de niveaux
- checkpoints dans les niveaux