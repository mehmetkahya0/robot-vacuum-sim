"""
Simülasyon Modülü
================
Ana simülasyon sınıfı. Oda üretimi, robot yönetimi ve
görselleştirme işlemlerini koordine eder.
"""

import pygame
import random
import math
from typing import List, Tuple
from robot_vacuum import RobotVacuum
from room_generator import RoomGenerator

class Simulation:
    def __init__(self, width: int, height: int):
        """
        Simülasyon sınıfı
        
        Args:
            width: Ekran genişliği
            height: Ekran yüksekliği
        """
        self.width = width
        self.height = height
        
        # Simülasyon alanı (UI için yer bırak)
        self.sim_width = width - 200
        self.sim_height = height - 100
        self.sim_offset_x = 100
        self.sim_offset_y = 50
        
        # Oda üretici
        self.room_generator = RoomGenerator(self.sim_width, self.sim_height)
        
        # İlk odayı oluştur
        self.room_grid, start_pos = self.room_generator.generate_room()
        
        # Robot süpürgeyi oluştur
        self.robot = RobotVacuum(
            start_pos[0] + self.sim_offset_x, 
            start_pos[1] + self.sim_offset_y, 
            self.room_generator.grid_size
        )
        # Offset bilgisini robota ilet
        self.robot.set_simulation_offset(self.sim_offset_x, self.sim_offset_y)
        
        # Simülasyon istatistikleri
        self.total_tiles = self._count_empty_tiles()
        self.simulation_time = 0
        
        # Fontlar
        pygame.font.init()
        self.font_large = pygame.font.Font(None, 32)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)
    
    def generate_new_room(self):
        """Yeni bir oda oluşturur"""
        self.room_grid, start_pos = self.room_generator.generate_room()
        self.robot.reset(
            start_pos[0] + self.sim_offset_x, 
            start_pos[1] + self.sim_offset_y
        )
        self.robot.set_simulation_offset(self.sim_offset_x, self.sim_offset_y)
        self.total_tiles = self._count_empty_tiles()
        self.simulation_time = 0
    
    def reset_robot(self):
        """Robotu mevcut odada sıfırlar"""
        _, start_pos = self.room_generator.generate_room()  # Sadece pozisyon için
        self.robot.reset(
            start_pos[0] + self.sim_offset_x, 
            start_pos[1] + self.sim_offset_y
        )
        self.robot.set_simulation_offset(self.sim_offset_x, self.sim_offset_y)
        self.simulation_time = 0
    
    def update(self):
        """Simülasyonu günceller"""
        self.simulation_time += 1
        
        # Robotu güncelle - offset'i robot sınıfına ilet
        self.robot.update(self.room_grid, self.room_generator)
        
        # Yol geçmişini kaydet (doğru ekran koordinatlarında)
        self.robot.path_history.append((int(self.robot.x), int(self.robot.y)))
        if len(self.robot.path_history) > 500:
            self.robot.path_history.pop(0)
    
    def draw(self, screen: pygame.Surface):
        """Simülasyonu çizer"""
        # Arka plan
        sim_rect = pygame.Rect(self.sim_offset_x, self.sim_offset_y, 
                              self.sim_width, self.sim_height)
        pygame.draw.rect(screen, (250, 250, 250), sim_rect)
        pygame.draw.rect(screen, (200, 200, 200), sim_rect, 2)
        
        # Odayı çiz
        self._draw_room(screen)
        
        # Robotu çiz
        self.robot.draw(screen)
        
        # LiDAR görüntüsünü çiz (sağ üst köşe)
        lidar_view_size = 180
        lidar_view_x = self.width - lidar_view_size - 10
        lidar_view_y = 50
        self.robot.draw_lidar_view(screen, lidar_view_x, lidar_view_y, lidar_view_size)
        
        # UI'yi çiz
        self._draw_ui(screen)
    
    def _draw_room(self, screen: pygame.Surface):
        """Odayı çizer"""
        grid_size = self.room_generator.grid_size
        
        for y in range(len(self.room_grid)):
            for x in range(len(self.room_grid[0])):
                rect = pygame.Rect(
                    x * grid_size + self.sim_offset_x,
                    y * grid_size + self.sim_offset_y,
                    grid_size,
                    grid_size
                )
                
                cell_value = self.room_grid[y][x]
                
                if cell_value == 1:  # Engel
                    pygame.draw.rect(screen, (139, 69, 19), rect)  # Kahverengi
                    pygame.draw.rect(screen, (101, 67, 33), rect, 1)
                elif cell_value == 2:  # Duvar
                    pygame.draw.rect(screen, (64, 64, 64), rect)  # Koyu gri
                    pygame.draw.rect(screen, (32, 32, 32), rect, 1)
    
    def _draw_ui(self, screen: pygame.Surface):
        """Kullanıcı arayüzünü çizer"""
        # Robot durumu
        status = self.robot.get_status()
        
        # Sol panel - Robot durumu (kompakt)
        panel_x = 10
        panel_y = 80
        
        # Ana durum kutusu
        status_box = pygame.Rect(panel_x - 5, panel_y - 5, 180, 160)
        pygame.draw.rect(screen, (240, 240, 240), status_box)
        pygame.draw.rect(screen, (180, 180, 180), status_box, 2)
        
        # Başlık
        title = self.font_large.render("🤖 ROBOT STATUS", True, (50, 50, 50))
        screen.blit(title, (panel_x, panel_y))
        panel_y += 35
        
        # Durum bilgileri (daha kompakt)
        lidar_angle_deg = int((status['lidar_rotation'] * 180 / math.pi) % 360)
        info_texts = [
            f"Mode: {status['state'].upper()}",
            f"Battery: {status['battery']:.0f}%",
            f"Cleaned: {status['cleaned_tiles']} tiles",
            f"Position: ({status['position'][0]}, {status['position'][1]})",
            f"LiDAR: {lidar_angle_deg}°",
            f"Time: {self.simulation_time // 60}:{self.simulation_time % 60:02d}",
        ]
        
        for i, text in enumerate(info_texts):
            color = (60, 60, 60)
            if i == 0:  # Durum rengini ayarla
                if status['state'] == 'exploring':
                    color = (0, 150, 0)
                elif status['state'] == 'stuck':
                    color = (200, 0, 0)
                elif status['state'] == 'cleaning':
                    color = (0, 0, 200)
            
            rendered_text = self.font_small.render(text, True, color)
            screen.blit(rendered_text, (panel_x + 5, panel_y + i * 20))
        
        # Batarya çubuğu
        battery_rect = pygame.Rect(panel_x + 5, panel_y + len(info_texts) * 20 + 5, 100, 8)
        pygame.draw.rect(screen, (100, 100, 100), battery_rect)
        battery_fill = int((status['battery'] / 100) * 100)
        battery_color = (0, 200, 0) if status['battery'] > 50 else (200, 200, 0) if status['battery'] > 20 else (200, 0, 0)
        pygame.draw.rect(screen, battery_color, pygame.Rect(battery_rect.x, battery_rect.y, battery_fill, 8))
        
        # Temizlik verimliliği
        if self.total_tiles > 0:
            efficiency = (status['cleaned_tiles'] / self.total_tiles) * 100
            efficiency_text = f"Efficiency: {efficiency:.1f}%"
            
            color = (0, 150, 0) if efficiency > 80 else (200, 150, 0) if efficiency > 50 else (200, 0, 0)
            rendered_efficiency = self.font_small.render(efficiency_text, True, color)
            screen.blit(rendered_efficiency, (panel_x + 5, panel_y + len(info_texts) * 20 + 20))
        
        # Sağ panel - LiDAR ve Algoritma bilgileri (LiDAR görüntüsünün altında)
        right_panel_x = self.width - 190
        right_panel_y = 250  # LiDAR görüntüsünün altında
        
        # Sağ panel kutusu
        info_box = pygame.Rect(right_panel_x - 5, right_panel_y - 5, 185, 300)
        pygame.draw.rect(screen, (245, 245, 245), info_box)
        pygame.draw.rect(screen, (180, 180, 180), info_box, 2)
        
        # LiDAR başlığı
        lidar_title = self.font_medium.render("📡 LIDAR SYSTEM", True, (50, 50, 50))
        screen.blit(lidar_title, (right_panel_x, right_panel_y))
        right_panel_y += 30
        
        lidar_info = [
            f"• Range: {self.robot.lidar_range}px",
            f"• Resolution: {self.robot.lidar_resolution} rays",
            f"• Rotation: {lidar_angle_deg}°",
            "• Real-time mapping",
            "• Obstacle detection"
        ]
        
        for i, info in enumerate(lidar_info):
            rendered_info = self.font_small.render(info, True, (80, 80, 80))
            screen.blit(rendered_info, (right_panel_x + 5, right_panel_y + i * 16))
        
        right_panel_y += len(lidar_info) * 16 + 25
        
        # Algoritma başlığı
        algorithm_title = self.font_medium.render("🧠 AI BEHAVIOR", True, (50, 50, 50))
        screen.blit(algorithm_title, (right_panel_x, right_panel_y))
        right_panel_y += 30
        
        algorithm_info = [
            "• Autonomous navigation",
            "• Wall following",
            "• Obstacle avoidance", 
            "• Stuck detection",
            "• Path optimization"
        ]
        
        for i, info in enumerate(algorithm_info):
            rendered_info = self.font_small.render(info, True, (80, 80, 80))
            screen.blit(rendered_info, (right_panel_x + 5, right_panel_y + i * 16))
        
        right_panel_y += len(algorithm_info) * 16 + 25
        
        # Kontrollar başlığı
        controls_title = self.font_medium.render("🎮 CONTROLS", True, (50, 50, 50))
        screen.blit(controls_title, (right_panel_x, right_panel_y))
        right_panel_y += 30
        
        controls_info = [
            "• SPACE: New room",
            "• R: Reset robot",
            "• ESC: Exit"
        ]
        
        for i, info in enumerate(controls_info):
            rendered_info = self.font_small.render(info, True, (80, 80, 80))
            screen.blit(rendered_info, (right_panel_x + 5, right_panel_y + i * 16))
        
        # Alt bilgi çubuğu
        bottom_rect = pygame.Rect(0, self.height - 35, self.width, 35)
        pygame.draw.rect(screen, (220, 220, 220), bottom_rect)
        pygame.draw.line(screen, (180, 180, 180), (0, self.height - 35), (self.width, self.height - 35), 2)
        
        bottom_y = self.height - 25
        status_text = "🤖 AUTONOMOUS ROBOT VACUUM SIMULATION - NO HUMAN INTERVENTION"
        control_text = self.font_small.render(status_text, True, (80, 80, 80))
        text_rect = control_text.get_rect(center=(self.width // 2, bottom_y))
        screen.blit(control_text, text_rect)
    
    def _count_empty_tiles(self) -> int:
        """Boş karoların sayısını hesaplar"""
        count = 0
        for row in self.room_grid:
            for cell in row:
                if cell == 0:  # Boş karo
                    count += 1
        return count