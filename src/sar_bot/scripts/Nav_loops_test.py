#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped
import math  # Importé pour utiliser math.pi (pour les rotations)

def create_pose(navigator, x, y, z_rot=0.0, w_rot=1.0):
    """Fonction utilitaire pour créer un point de destination (PoseStamped)"""
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    # Utiliser l'horloge du navigateur pour la synchronisation
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.orientation.z = z_rot
    pose.pose.orientation.w = w_rot
    return pose

def main():
    rclpy.init()

    # Initialiser le navigateur
    navigator = BasicNavigator()

    print("En attente des serveurs d'action de Nav2...")
    # Vu qu'on n'utilise pas AMCL, on attend manuellement chaque serveur dont on a besoin :
    navigator.follow_waypoints_client.wait_for_server() # Pour la patrouille
    navigator.nav_to_pose_client.wait_for_server()      # Pour le retour à l'origine
    navigator.spin_client.wait_for_server()             # Pour les rotations sur place
    print("Nav2 est prêt avec SLAM Toolbox !")

    # ---------------------------------------------------------
    # 1. DÉFINITION DES POINTS (Coordonnées récupérées via RViz)
    # ---------------------------------------------------------
    point_1 = create_pose(navigator, x=-0.506, y=1.548)
    point_2 = create_pose(navigator, x=-5.891, y=-0.588)
    point_3 = create_pose(navigator, x=-5.035, y=-1.523)
    point_4 = create_pose(navigator, x=-2.417, y=-4.675)
    
    # Point d'origine
    origine = create_pose(navigator, x=0.0, y=0.0)

    # ---------------------------------------------------------
    # ÉTAPE 1 : FAIRE LA PATROUILLE 2 FOIS
    # ---------------------------------------------------------
    for i in range(2):
        print(f"\n--- Début de la patrouille {i+1}/2 ---")
        
        # Envoyer la liste de waypoints
        waypoints = [point_1, point_2, point_3, point_4]
        navigator.followWaypoints(waypoints)

        # Boucle d'attente pendant le trajet
        while not navigator.isTaskComplete():
            feedback = navigator.getFeedback()
            if feedback:
                print(f"En route vers le point n°{feedback.current_waypoint} de la patrouille...")

        # Vérification à la fin de la patrouille
        if navigator.getResult() == TaskResult.SUCCEEDED:
            print(f"Patrouille {i+1} terminée !")
        else:
            print("Erreur pendant la patrouille. Annulation du script.")
            return # Arrête le script si un problème survient

    # ---------------------------------------------------------
    # ÉTAPE 2 : RETOURNER À L'ORIGINE (0, 0)
    # ---------------------------------------------------------
    print("\n--- Patrouilles terminées. Retour à l'origine (0, 0) ---")
    # On utilise goToPose (et non followWaypoints) car c'est une destination unique
    navigator.goToPose(origine)

    while not navigator.isTaskComplete():
        feedback = navigator.getFeedback()
        if feedback:
            # On affiche la distance restante jusqu'à l'origine (arrondie à 2 décimales)
            print(f"Retour à la base... Distance restante : {feedback.distance_remaining:.2f} mètres")

    if navigator.getResult() == TaskResult.SUCCEEDED:
        print("Robot arrivé à l'origine !")

    # ---------------------------------------------------------
    # ÉTAPE 3 : FAIRE 5 ROTATIONS SUR LUI-MÊME
    # ---------------------------------------------------------
    print("\n--- Début des 2 rotations sur place ---")
    
    for i in range(2):
        print(f"Rotation {i+1}/5 en cours...")
        # L'action spin demande un angle en radians. 1 tour complet = 2 * PI.
        # Par sécurité, on fait les tours 1 par 1.
        navigator.spin(spin_dist=2.0 * math.pi)

        while not navigator.isTaskComplete():
            # Pas besoin de feedback ici, on attend juste qu'il finisse de tourner
            pass

    print("\n🎉 Toutes les missions sont terminées avec succès !")
    
    # Fermer proprement
    rclpy.shutdown()

if __name__ == '__main__':
    main()