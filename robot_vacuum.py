"""
Robot Süpürge Modülü
====================
Otonom robot süpürge sınıfı. Robot kendi kararlarını verir,
engelleri algılar ve sistematik temizlik yapar.
"""

import pygame
import math
import random
from typing import List, Tuple, Set
from enum import Enum

class RobotState(Enum):
    EXPLORING = "exploring"
    CLEANING = "cleaning"
    RETURNING = "returning"
    STUCK = "stuck"

class RobotVacuum:
    def __init__(self, x: int, y: int, grid_size: int):
        """
        Robot süpürge sınıfı
        
        Args:
            x, y: Başlangıç pozisyonu (ekran koordinatları)
            grid_size: Grid boyutu
        """
        self.x = float(x)
        self.y = float(y)
        self.start_x = x
        self.start_y = y
        self.grid_size = grid_size
        self.sim_offset_x = 0
        self.sim_offset_y = 0
        
        # Robot özellikleri
        self.radius = 8
        self.speed = 1.5
        self.sensor_range = 30
        
        # LiDAR sistemi
        self.lidar_range = 100
        self.lidar_resolution = 360  # Tam 360 derece için 360 ışın
        self.lidar_rotation = 0
        self.lidar_speed = 0.12  # Dönüş hızı
        self.lidar_data = [self.lidar_range] * self.lidar_resolution  # Mesafe verileri
        
        # Hareket ve yön
        self.angle = random.uniform(0, 2 * math.pi)
        self.target_angle = self.angle
        self.angular_speed = 0.1
        
        # Robot durumu
        self.state = RobotState.EXPLORING
        self.battery = 100
        self.cleaned_area = set()
        self.path_history = []
        
        # Karar verme mekanizması
        self.stuck_counter = 0
        self.last_positions = []
        self.direction_change_timer = 0
        self.wall_following = False
        self.wall_follow_direction = 1  # 1: sağ, -1: sol
        
        # Renk ve görsellik
        self.color = (50, 150, 250)  # Mavi
        self.trail_color = (100, 200, 100, 50)  # Yeşil iz
        
    def update(self, room_grid: List[List[int]], room_generator):
        """Robot durumunu günceller"""
        self.battery = max(0, self.battery - 0.02)
        
        # Pozisyon geçmişini tut
        self.last_positions.append((self.x, self.y))
        if len(self.last_positions) > 50:
            self.last_positions.pop(0)
        
        # Sıkışma kontrolü
        self._check_if_stuck()
        
        # Durum makinesine göre hareket et
        if self.state == RobotState.EXPLORING:
            self._explore_behavior(room_grid, room_generator)
        elif self.state == RobotState.CLEANING:
            self._cleaning_behavior(room_grid, room_generator)
        elif self.state == RobotState.STUCK:
            self._stuck_behavior(room_grid, room_generator)
        
        # Hareketi uygula
        self._move(room_grid, room_generator)
        
        # LiDAR'ı güncelle
        self._update_lidar(room_grid, room_generator)
        
        # Temizliği kaydet
        self._mark_cleaned_area()
    
    def _explore_behavior(self, room_grid: List[List[int]], room_generator):
        """Keşif davranışı - sistematik temizlik"""
        self.direction_change_timer -= 1
        
        # Önde engel var mı kontrol et
        front_distance = self._get_front_distance(room_grid, room_generator)
        
        if front_distance < 25:  # Engele yakın
            if not self.wall_following:
                # Duvar takip moduna geç
                self.wall_following = True
                self.wall_follow_direction = random.choice([1, -1])
            
            # Duvar boyunca git
            self._follow_wall(room_grid, room_generator)
        else:
            self.wall_following = False
            
            # Düz git veya yön değiştir
            if self.direction_change_timer <= 0:
                if random.random() < 0.3:  # %30 şans ile yön değiştir
                    self.target_angle += random.uniform(-math.pi/3, math.pi/3)
                    self.direction_change_timer = random.randint(30, 120)
    
    def _cleaning_behavior(self, room_grid: List[List[int]], room_generator):
        """Sistematik temizlik davranışı"""
        # Spiral hareket veya zigzag temizlik
        if random.random() < 0.1:  # Zaman zaman yön değiştir
            self.target_angle += math.pi / 6
    
    def _stuck_behavior(self, room_grid: List[List[int]], room_generator):
        """Sıkışma durumu davranışı"""
        # Rastgele yöne dön
        self.target_angle += random.uniform(-math.pi, math.pi)
        self.stuck_counter = max(0, self.stuck_counter - 1)
        
        if self.stuck_counter == 0:
            self.state = RobotState.EXPLORING
    
    def _follow_wall(self, room_grid: List[List[int]], room_generator):
        """Duvar takip algoritması"""
        # Sağa veya sola dön (duvar takip yönüne göre)
        turn_angle = math.pi / 4 * self.wall_follow_direction
        self.target_angle = self.angle + turn_angle
    
    def _move(self, room_grid: List[List[int]], room_generator):
        """Robotu hareket ettirir"""
        # Açıyı yumuşak geçiş ile güncelle
        angle_diff = self.target_angle - self.angle
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi
        
        self.angle += angle_diff * self.angular_speed
        
        # Yeni pozisyonu hesapla
        new_x = self.x + math.cos(self.angle) * self.speed
        new_y = self.y + math.sin(self.angle) * self.speed
        
        # Grid koordinatlarına dönüştür (offset olmadan)
        grid_check_x = int(new_x - self.sim_offset_x)
        grid_check_y = int(new_y - self.sim_offset_y)
        
        # Çarpışma kontrolü
        if room_generator.is_valid_position(room_grid, grid_check_x, grid_check_y):
            self.x = new_x
            self.y = new_y
        else:
            # Engele çarptı, yön değiştir
            self.target_angle += random.uniform(math.pi/2, math.pi)
    
    def _get_front_distance(self, room_grid: List[List[int]], room_generator) -> float:
        """Önündeki engele olan mesafeyi ölçer"""
        for distance in range(5, self.sensor_range, 5):
            check_x = self.x + math.cos(self.angle) * distance
            check_y = self.y + math.sin(self.angle) * distance
            
            # Grid koordinatlarına dönüştür
            grid_check_x = int(check_x - self.sim_offset_x)
            grid_check_y = int(check_y - self.sim_offset_y)
            
            if not room_generator.is_valid_position(room_grid, grid_check_x, grid_check_y):
                return distance
        
        return self.sensor_range
    
    def _check_if_stuck(self):
        """Robot sıkışmış mı kontrol eder"""
        if len(self.last_positions) >= 30:
            # Son 30 pozisyonun ortalama hareketi
            recent_positions = self.last_positions[-30:]
            total_movement = 0
            
            for i in range(1, len(recent_positions)):
                dx = recent_positions[i][0] - recent_positions[i-1][0]
                dy = recent_positions[i][1] - recent_positions[i-1][1]
                total_movement += math.sqrt(dx*dx + dy*dy)
            
            if total_movement < 20:  # Çok az hareket
                self.stuck_counter = 60
                self.state = RobotState.STUCK
    
    def _update_lidar(self, room_grid: List[List[int]], room_generator):
        """LiDAR sistemini günceller"""
        # LiDAR rotasyonu
        self.lidar_rotation += self.lidar_speed
        if self.lidar_rotation >= 2 * math.pi:
            self.lidar_rotation = 0
        
        # Sadece dönen bölümdeki açıları güncelle (performans için)
        scan_width = 30  # Aynı anda 30 açı tara
        start_angle_index = int((self.lidar_rotation / (2 * math.pi)) * self.lidar_resolution)
        
        for i in range(scan_width):
            angle_index = (start_angle_index + i) % self.lidar_resolution
            angle = (angle_index / self.lidar_resolution) * 2 * math.pi
            distance = self._lidar_scan(angle, room_grid, room_generator)
            self.lidar_data[angle_index] = distance
    
    def _lidar_scan(self, angle: float, room_grid: List[List[int]], room_generator) -> float:
        """Belirli açıda LiDAR taraması yapar"""
        step_size = 1  # Daha hassas tarama
        
        for distance in range(self.radius + 2, self.lidar_range, step_size):
            scan_x = self.x + math.cos(angle) * distance
            scan_y = self.y + math.sin(angle) * distance
            
            # Grid koordinatlarına dönüştür
            grid_scan_x = int(scan_x - self.sim_offset_x)
            grid_scan_y = int(scan_y - self.sim_offset_y)
            
            # Sınır kontrolü
            if (grid_scan_x < 0 or grid_scan_y < 0 or 
                grid_scan_x >= room_generator.grid_width * room_generator.grid_size or 
                grid_scan_y >= room_generator.grid_height * room_generator.grid_size):
                return distance
            
            # Engel kontrolü
            if not room_generator.is_valid_position(room_grid, grid_scan_x, grid_scan_y):
                return distance
        
        return self.lidar_range
    
    def _mark_cleaned_area(self):
        """Mevcut pozisyonu temizlenmiş olarak işaretle"""
        # Grid koordinatlarına dönüştür
        grid_x = int((self.x - self.sim_offset_x) // self.grid_size)
        grid_y = int((self.y - self.sim_offset_y) // self.grid_size)
        
        # Robot çevresindeki alanı temizle
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                self.cleaned_area.add((grid_x + dx, grid_y + dy))
    
    def draw(self, screen: pygame.Surface):
        """Robotu çizer"""
        # Temizlenmiş alanları çiz
        for (gx, gy) in self.cleaned_area:
            rect = pygame.Rect(
                gx * self.grid_size + self.sim_offset_x, 
                gy * self.grid_size + self.sim_offset_y, 
                self.grid_size, 
                self.grid_size
            )
            pygame.draw.rect(screen, (200, 255, 200), rect)
        
        # Yol geçmişini çiz
        if len(self.path_history) > 1:
            for i in range(1, len(self.path_history)):
                start_pos = self.path_history[i-1]
                end_pos = self.path_history[i]
                alpha = min(255, 50 + i * 2)  # Yakın geçmiş daha parlak
                pygame.draw.line(screen, (150, 150, 255), start_pos, end_pos, 2)
        
        # Robot gövdesini çiz
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (30, 100, 200), (int(self.x), int(self.y)), self.radius, 2)
        
        # LiDAR modülünü çiz (üstte dönen küçük daire)
        lidar_radius = 4
        lidar_y = self.y - 2  # Robot merkezinin biraz üstünde
        pygame.draw.circle(screen, (20, 20, 20), (int(self.x), int(lidar_y)), lidar_radius)
        pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(lidar_y)), lidar_radius, 1)
        
        # LiDAR rotasyon göstergesi
        lidar_indicator_x = self.x + math.cos(self.lidar_rotation) * (lidar_radius - 1)
        lidar_indicator_y = lidar_y + math.sin(self.lidar_rotation) * (lidar_radius - 1)
        pygame.draw.circle(screen, (255, 100, 100), 
                          (int(lidar_indicator_x), int(lidar_indicator_y)), 2)
        
        # Yön göstergesi
        end_x = self.x + math.cos(self.angle) * (self.radius + 5)
        end_y = self.y + math.sin(self.angle) * (self.radius + 5)
        pygame.draw.line(screen, (255, 255, 255), 
                        (int(self.x), int(self.y)), 
                        (int(end_x), int(end_y)), 3)
        
        # Sensör alanını göster (debug)
        sensor_points = []
        for angle_offset in [-math.pi/6, 0, math.pi/6]:
            sensor_angle = self.angle + angle_offset
            sensor_x = self.x + math.cos(sensor_angle) * 20
            sensor_y = self.y + math.sin(sensor_angle) * 20
            sensor_points.append((sensor_x, sensor_y))
        
        for point in sensor_points:
            pygame.draw.circle(screen, (255, 200, 100), (int(point[0]), int(point[1])), 3)
    
    def set_simulation_offset(self, offset_x: int, offset_y: int):
        """Simülasyon offset değerlerini ayarlar"""
        self.sim_offset_x = offset_x
        self.sim_offset_y = offset_y
    
    def reset(self, x: int, y: int):
        """Robotu sıfırlar"""
        self.x = float(x)
        self.y = float(y)
        self.angle = random.uniform(0, 2 * math.pi)
        self.target_angle = self.angle
        self.state = RobotState.EXPLORING
        self.battery = 100
        self.cleaned_area.clear()
        self.path_history.clear()
        self.last_positions.clear()
        self.stuck_counter = 0
        self.wall_following = False
        
        # LiDAR'ı sıfırla
        self.lidar_rotation = 0
        self.lidar_data = [0] * self.lidar_resolution
    
    def draw_lidar_view(self, screen: pygame.Surface, view_x: int, view_y: int, view_size: int):
        """LiDAR görüntüsünü çizer - robotun gözünden radar tarzı"""
        # LiDAR görüntü alanı
        view_rect = pygame.Rect(view_x, view_y, view_size, view_size)
        pygame.draw.rect(screen, (0, 0, 0), view_rect)  # Siyah arka plan
        pygame.draw.rect(screen, (0, 255, 0), view_rect, 2)  # Yeşil çerçeve (radar tarzı)
        
        # Başlık
        font = pygame.font.Font(None, 20)
        title = font.render("RADAR VIEW", True, (0, 255, 0))
        screen.blit(title, (view_x + 5, view_y - 22))
        
        # Merkez noktası (robot pozisyonu)
        center_x = view_x + view_size // 2
        center_y = view_y + view_size // 2
        max_radius = view_size // 2 - 15
        
        # Radar çemberleri (mesafe göstergesi)
        for i, radius in enumerate([max_radius//3, (max_radius*2)//3, max_radius]):
            pygame.draw.circle(screen, (0, 100, 0), (center_x, center_y), radius, 1)
            # Mesafe etiketleri
            distance_label = f"{int((radius/max_radius) * self.lidar_range)}px"
            label_surface = pygame.font.Font(None, 16).render(distance_label, True, (0, 150, 0))
            screen.blit(label_surface, (center_x + radius - 25, center_y - 8))
        
        # Radar tarama çizgileri (sabit 8 yön)
        for i in range(8):
            angle = (i / 8) * 2 * math.pi
            end_x = center_x + math.cos(angle) * max_radius
            end_y = center_y + math.sin(angle) * max_radius
            pygame.draw.line(screen, (0, 80, 0), (center_x, center_y), (int(end_x), int(end_y)), 1)
        
        # LiDAR verilerini engel noktaları olarak çiz
        obstacle_points = []
        for i, distance in enumerate(self.lidar_data):
            if distance < self.lidar_range * 0.95:  # Sadece gerçek engelleri göster
                angle = (i / self.lidar_resolution) * 2 * math.pi
                
                # Mesafeyi görüntü alanına ölçekle
                scaled_distance = (distance / self.lidar_range) * max_radius
                
                # Engel noktasını hesapla
                point_x = center_x + math.cos(angle) * scaled_distance
                point_y = center_y + math.sin(angle) * scaled_distance
                
                # Mesafeye göre parlaklık (yakın=parlak yeşil, uzak=koyu yeşil)
                distance_ratio = distance / self.lidar_range
                if distance_ratio < 0.3:  # Çok yakın - kırmızı
                    color = (255, int(100 + distance_ratio * 155), 0)
                    size = 3
                elif distance_ratio < 0.6:  # Orta mesafe - sarı
                    color = (255, 255, int(distance_ratio * 255))
                    size = 2
                else:  # Uzak - yeşil
                    color = (0, int(150 + distance_ratio * 105), 0)
                    size = 2
                
                obstacle_points.append((int(point_x), int(point_y), color, size))
        
        # Engel noktalarını çiz
        for point_x, point_y, color, size in obstacle_points:
            pygame.draw.circle(screen, color, (point_x, point_y), size)
            # Yakın engeller için glow efekti
            if color[0] > 200:  # Kırmızı renkli yakın engeller
                pygame.draw.circle(screen, (color[0]//3, color[1]//3, color[2]//3), 
                                 (point_x, point_y), size + 2, 1)
        
        # Robot merkezi
        pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), 4)
        pygame.draw.circle(screen, (0, 255, 0), (center_x, center_y), 4, 1)
        
        # Robot yön göstergesi (dinamik)
        direction_length = 20
        direction_x = center_x + math.cos(self.angle) * direction_length
        direction_y = center_y + math.sin(self.angle) * direction_length
        pygame.draw.line(screen, (255, 255, 0), 
                        (center_x, center_y), 
                        (int(direction_x), int(direction_y)), 3)
        
        # LiDAR döner çizgi (tarama konumu)
        scan_line_x = center_x + math.cos(self.lidar_rotation) * max_radius
        scan_line_y = center_y + math.sin(self.lidar_rotation) * max_radius
        pygame.draw.line(screen, (0, 255, 255), 
                        (center_x, center_y), 
                        (int(scan_line_x), int(scan_line_y)), 2)
        
        # Durumu göster
        status_font = pygame.font.Font(None, 16)
        status_text = f"Objects: {len(obstacle_points)}"
        status_surface = status_font.render(status_text, True, (0, 200, 0))
        screen.blit(status_surface, (view_x + 5, view_y + view_size - 20))
    
    def get_status(self) -> dict:
        """Robot durumu bilgilerini döndürür"""
        return {
            'state': self.state.value,
            'battery': self.battery,
            'cleaned_tiles': len(self.cleaned_area),
            'position': (int(self.x), int(self.y)),
            'lidar_rotation': self.lidar_rotation
        }