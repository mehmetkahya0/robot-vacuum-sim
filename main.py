"""
Robot Vacuum Simulator
======================
Bu simülasyon robot süpürgelerin karar verme mekanizmalarını gösterir.
Robot rastgele oluşturulan odalarda otonom olarak hareket eder ve temizlik yapar.
"""

import pygame
import sys
from robot_vacuum import RobotVacuum
from room_generator import RoomGenerator
from simulation import Simulation

def main():
    """Ana simülasyon döngüsü"""
    # Pygame'i başlat
    pygame.init()
    
    # Ekran boyutları
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 800
    
    # Ekranı oluştur
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Robot Vacuum Simulator - Otonom Temizlik")
    
    # Saat objesi
    clock = pygame.time.Clock()
    
    # Simülasyonu başlat
    simulation = Simulation(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Ana döngü
    running = True
    while running:
        # Olayları kontrol et
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Boşluk tuşu ile yeni oda oluştur
                    simulation.generate_new_room()
                elif event.key == pygame.K_r:
                    # R tuşu ile robotu sıfırla
                    simulation.reset_robot()
        
        # Simülasyonu güncelle
        simulation.update()
        
        # Ekranı temizle
        screen.fill((240, 240, 240))  # Açık gri arka plan
        
        # Simülasyonu çiz
        simulation.draw(screen)
        
        # Kontrol bilgilerini göster
        font = pygame.font.Font(None, 36)
        text1 = font.render("SPACE: Yeni Oda | R: Robot Sıfırla", True, (50, 50, 50))
        text2 = font.render("Robot Otonom Hareket Ediyor", True, (50, 50, 50))
        screen.blit(text1, (10, 10))
        screen.blit(text2, (10, 45))
        
        # Ekranı güncelle
        pygame.display.flip()
        clock.tick(60)  # 60 FPS
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()