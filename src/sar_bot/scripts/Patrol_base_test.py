#!/usr/bin/env python3

import rclpy
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped
from std_srvs.srv import Trigger

def create_pose(navigator, x, y):
    """Crée un point de destination avec un timestamp mis à jour"""
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x = float(x)
    pose.pose.position.y = float(y)
    pose.pose.orientation.w = 1.0 
    return pose

def main():
    rclpy.init()
    navigator = BasicNavigator()

    # ---------------------------------------------------------
    # 1. VARIABLES D'ÉTAT ET SIGNAUX
    # ---------------------------------------------------------
    state = 'PATROUILLE' 
    alert_triggered = False
    resume_triggered = False

    # --- Fonctions appelées quand on reçoit un signal (Services) ---
    def alert_callback(request, response):
        nonlocal alert_triggered
        alert_triggered = True
        print("\n[ SIGNAL REÇU ] ALERTE ! Interruption demandée...")
        response.success = True
        response.message = "Retour à la base enclenché."
        return response

    def resume_callback(request, response):
        nonlocal resume_triggered
        resume_triggered = True
        print("\n[ SIGNAL REÇU ] REPRISE ! Reprise de la patrouille...")
        response.success = True
        response.message = "Patrouille reprise."
        return response

    # ---------------------------------------------------------
    # 2. CRÉATION DES SERVICES (Créés AVANT l'attente)
    # ---------------------------------------------------------
    navigator.create_service(Trigger, 'trigger_alert', alert_callback)
    navigator.create_service(Trigger, 'resume_patrol', resume_callback)
    print("Services '/trigger_alert' et '/resume_patrol' sont DISPONIBLES !")

    # ---------------------------------------------------------
    # 3. ATTENTE DE NAV2 (L'ASTUCE SLAM TOOLBOX)
    # ---------------------------------------------------------
    print("En attente de Nav2 (bypass de AMCL en cours)...")
    # On trompe le système pour qu'il n'attende pas l'état de AMCL
    navigator.waitUntilNav2Active(localizer='bt_navigator')
    print("Nav2 est prêt avec SLAM Toolbox !")

    # ---------------------------------------------------------
    # 4. VOS COORDONNÉES EXACTES
    # ---------------------------------------------------------
    BASE_X, BASE_Y = -5.115876, 3.737485
    
    PATROL_POINTS =[
        (-1.14845, -0.07592),
        (-0.86556, -3.42356),
        (-3.40655, -3.76083),
        (-5.78129, -1.09006)
    ]

    print("\n=== DÉBUT DU CYCLE DE SURVEILLANCE ===")

    # ---------------------------------------------------------
    # BOUCLE PRINCIPALE (Machine à États)
    # ---------------------------------------------------------
    while rclpy.ok():
        
        # ÉTAT 1 : PATROUILLE CONTINUE
        if state == 'PATROUILLE':
            waypoints =[create_pose(navigator, x, y) for x, y in PATROL_POINTS]
            print("\n-> Démarrage d'un cycle de patrouille...")
            navigator.followWaypoints(waypoints)

            while not navigator.isTaskComplete():
                if alert_triggered:
                    print("-> Annulation de la patrouille en cours...")
                    navigator.cancelTask()
                    while not navigator.isTaskComplete():
                        pass
                    break 

            if alert_triggered:
                alert_triggered = False 
                state = 'RETOUR_BASE'   
            else:
                print("-> Cycle terminé. Recommencement dans 2 secondes...")
                start_time = navigator.get_clock().now().nanoseconds
                while (navigator.get_clock().now().nanoseconds - start_time) < 2e9:
                    rclpy.spin_once(navigator, timeout_sec=0.1)

        # ÉTAT 2 : RETOUR VERS LA BASE
        elif state == 'RETOUR_BASE':
            print("\n-> Navigation vers la Base...")
            base_pose = create_pose(navigator, BASE_X, BASE_Y)
            navigator.goToPose(base_pose)

            while not navigator.isTaskComplete():
                if resume_triggered:
                    print("-> Fausse alerte, annulation du retour à la base...")
                    navigator.cancelTask()
                    while not navigator.isTaskComplete():
                        pass
                    break
            
            if resume_triggered:
                resume_triggered = False
                state = 'PATROUILLE'
            else:
                result = navigator.getResult()
                if result == TaskResult.SUCCEEDED:
                    print("-> Arrivé à la BASE avec succès. En attente...")
                else:
                    print("-> Problème pour atteindre la base. En attente...")
                state = 'A_LA_BASE'

        # ÉTAT 3 : À L'ARRÊT À LA BASE
        elif state == 'A_LA_BASE':
            rclpy.spin_once(navigator, timeout_sec=0.5)
            if resume_triggered:
                resume_triggered = False
                state = 'PATROUILLE'

##ros2 service call /trigger_alert std_srvs/srv/Trigger
##ros2 service call /resume_patrol std_srvs/srv/Trigger

    rclpy.shutdown()

if __name__ == '__main__':
    main()