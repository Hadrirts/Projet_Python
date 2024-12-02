import math
class Competence:
    def __init__(self, nom, degats, portee, type_competence, cout):
        self.nom = nom
        self.degats = degats
        self.portee = portee
        self.type_competence = type_competence
        self.cout = cout
    
    def utiliser(self, caster, target):
        """Applique l'effet de la compétence si la cible est dans la portée."""
        raise NotImplementedError("La méthode 'utiliser' doit être implémentée dans les sous-classes.")
class BouleDeFeu(Competence):
    def __init__(self):
        super().__init__("Boule de feu", 10, 3, "skillshot", 3)
        self.zone_type = "cercle"
        self.rayon = 2

    def utiliser(self, caster, x, y, enemy_units):
        """Utilise la boule de feu, affectant une zone circulaire autour de la cible."""
        if abs(caster.x - x) <= self.portee and abs(caster.y - y) <= self.portee:
            affected_units = self.get_units_in_cercle(x, y, enemy_units)
            for unit in affected_units:
                unit.health -= self.degats
                if unit.health <= 0:
                    enemy_units.remove(unit)
            return f"utilise {self.nom} et touche {len(affected_units)} unités dans la zone circulaire, causant {self.degats} dégâts."
        else:
            return f"La cible est hors de portée pour {self.nom}."

    def get_units_in_cercle(self, x, y, enemy_units):
        """Retourne les unités dans une zone circulaire autour de la cible."""
        affected_units = []
        for unit in enemy_units:
            distance = math.sqrt((unit.x - x)**2 + (unit.y - y)**2)
            if distance <= self.rayon:  # Vérifie si l'unité est dans la zone d'impact
                affected_units.append(unit)
        return affected_units
class Tir(Competence):
    def __init__(self):
        super().__init__("Tir", 10, 3, "skillshot", 2)
        self.zone_type = "ligne"
        self.direction = "horizontale"

    def utiliser(self, caster, target, enemy_units):
        """Utilise le tir en ligne, affectant une ligne droite dans la direction spécifiée."""
        if abs(caster.x - target.x) <= self.portee and abs(caster.y - target.y) <= self.portee:
            affected_units = self.get_units_in_ligne(caster, target, enemy_units)
            for unit in affected_units:
                unit.health -= self.degats
            return f"utilise {self.nom} et touche {len(affected_units)} unités dans la ligne, causant {self.degats} dégâts."
        return f"{target.name} est hors de portée pour {self.nom}."

    def get_units_in_ligne(self, caster, target, enemy_units):
        """Retourne les unités dans une ligne droite horizontale autour de la cible."""
        affected_units = []
        if self.direction == "horizontale":
            for unit in enemy_units:
                if unit.y == target.y and abs(unit.x - target.x) <= self.portee:
                    affected_units.append(unit)
        elif self.direction == "verticale":
            for unit in enemy_units:
                if unit.x == target.x and abs(unit.y - target.y) <= self.portee:
                    affected_units.append(unit)
        return affected_units
class Soin(Competence):
    def __init__(self):
        super().__init__("Soin", -10, 1, "Cible", 2)
    
    def utiliser(self, caster, target, enemy_units):
        """Utilise le soin sur une unité alliée."""
        if abs(caster.x - target.x) <= self.portee and abs(caster.y - target.y) <= self.portee:
            target.health += self.degats  # Le soin est un effet positif, donc on ajoute les points de vie
            return f"{caster.name} utilise {self.nom} et soigne {target.name} de {abs(self.degats)} points de vie."
        return f"{target.name} est hors de portée pour {self.nom}."
class Spin(Competence):
    def __init__(self):
        super().__init__("Spin", 20, 1, "skillshot", 5)
        self.zone_type = "cercle"
        self.rayon = 1

    def utiliser(self, caster, target, enemy_units):
        """Utilise le Spin pour infliger des dégâts dans un rayon autour du caster."""
        affected_units = self.get_units_in_cercle(caster, target, enemy_units)
        for unit in affected_units:
            unit.health -= self.degats
        return f"{caster.name} utilise {self.nom} et touche {len(affected_units)} unités dans la zone circulaire, causant {self.degats} dégâts."

    def get_units_in_cercle(self, caster, target, enemy_units):
        """Retourne les unités dans une zone circulaire autour du caster."""
        affected_units = []
        for unit in enemy_units:
            distance = math.sqrt((unit.x - caster.x)**2 + (unit.y - caster.y)**2)
            if distance <= self.rayon:  # Vérifie si l'unité est dans la zone d'impact
                affected_units.append(unit)
        return affected_units