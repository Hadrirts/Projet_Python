class Attack:
    def __init__(self, name, damage, range):
        self.name = name
        self.damage = damage
        self.range = range

    def execute(self, attacker, target):
        if abs(attacker.x - target.x) <= self.range and abs(attacker.y - target.y) <= self.range:
            target.health -= self.damage
            print(f"{attacker.name} used {self.name} on {target.name} for {self.damage} damage!")

class PistolAttack(Attack):
    def __init__(self, name, damage, range):
        super().__init__(name, damage, range)

    def execute(self, attacker, target):
        if abs(attacker.x - target.x) <= self.range and abs(attacker.y - target.y) <= self.range:
            target.health -= self.damage
            print(f"{attacker.name} used {self.name} on {target.name} for {self.damage} damage!")

class SniperAttack(Attack):
    def __init__(self, name, damage, range):
        super().__init__(name, damage, range)

    def get_targets_in_line(self, attacker, game):
        """Retourne toutes les unités dans la ligne de vue"""
        potential_targets = []
        
        # Vérifier les unités sur la même ligne horizontale ***a ameliorer***
        for unit in game.enemy_units:
            # Même ligne
            if unit.y == attacker.y and abs(unit.x - attacker.x) <= self.range:
                potential_targets.append(unit)
            # Même colonne    
            elif unit.x == attacker.x and abs(unit.y - attacker.y) <= self.range:
                potential_targets.append(unit)
            # Diagonales
            elif abs(unit.x - attacker.x) == abs(unit.y - attacker.y) and abs(unit.x - attacker.x) <= self.range:
                potential_targets.append(unit)
                
        return potential_targets

    def execute(self, attacker, game):
        targets = self.get_targets_in_line(attacker, game)
        if targets:
            # Pour l'instant on prend la première cible
            # Plus tard on pourra ajouter une sélection par le joueur
            target = targets[0]
            target.health -= self.damage
            print(f"{attacker.name} used {self.name} on {target.name} for {self.damage} damage!")
    