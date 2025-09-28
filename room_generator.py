"""
Oda Üretici Modülü
==================
Rastgele oda krokileri oluşturur. Odalar farklı şekillerde engeller,
duvarlar ve mobilyalar içerebilir.
"""

import random
import math
from typing import List, Tuple

class RoomGenerator:
    def __init__(self, width: int, height: int):
        """
        Oda üretici sınıfı
        
        Args:
            width: Oda genişliği
            height: Oda yüksekliği
        """
        self.width = width
        self.height = height
        self.grid_size = 20  # Her grid karesi 20x20 pixel
        self.grid_width = width // self.grid_size
        self.grid_height = height // self.grid_size
        
    def generate_room(self) -> Tuple[List[List[int]], Tuple[int, int]]:
        """
        Rastgele bir oda oluşturur
        
        Returns:
            grid: 2D liste (0=boş, 1=engel, 2=duvar)
            start_pos: Robot başlangıç pozisyonu
        """
        # Grid'i başlat (tüm hücreler boş)
        grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        # Dış duvarları ekle
        self._add_outer_walls(grid)
        
        # Rastgele engeller ekle
        self._add_random_obstacles(grid)
        
        # L-şekilli odalar oluştur
        if random.random() < 0.3:  # %30 şans
            self._create_l_shaped_room(grid)
        
        # Mobilya benzeri büyük engeller ekle
        self._add_furniture(grid)
        
        # Robot için başlangıç pozisyonu bul
        start_pos = self._find_start_position(grid)
        
        return grid, start_pos
    
    def _add_outer_walls(self, grid: List[List[int]]):
        """Dış duvarları ekler"""
        for i in range(self.grid_height):
            for j in range(self.grid_width):
                if i == 0 or i == self.grid_height-1 or j == 0 or j == self.grid_width-1:
                    grid[i][j] = 2  # Duvar
    
    def _add_random_obstacles(self, grid: List[List[int]]):
        """Rastgele küçük engeller ekler"""
        obstacle_count = random.randint(5, 15)
        
        for _ in range(obstacle_count):
            x = random.randint(2, self.grid_width - 3)
            y = random.randint(2, self.grid_height - 3)
            
            # Küçük engel grupları oluştur
            size = random.randint(1, 3)
            for dx in range(size):
                for dy in range(size):
                    if (x + dx < self.grid_width - 1 and 
                        y + dy < self.grid_height - 1):
                        grid[y + dy][x + dx] = 1  # Engel
    
    def _create_l_shaped_room(self, grid: List[List[int]]):
        """L-şekilli oda oluşturur"""
        # Odanın bir köşesini kapatır
        corner = random.choice(['top-left', 'top-right', 'bottom-left', 'bottom-right'])
        
        block_width = random.randint(3, 8)
        block_height = random.randint(3, 8)
        
        if corner == 'top-left':
            for i in range(1, block_height):
                for j in range(1, block_width):
                    if i < self.grid_height and j < self.grid_width:
                        grid[i][j] = 2
        elif corner == 'top-right':
            for i in range(1, block_height):
                for j in range(self.grid_width - block_width, self.grid_width - 1):
                    if i < self.grid_height and j >= 0:
                        grid[i][j] = 2
        elif corner == 'bottom-left':
            for i in range(self.grid_height - block_height, self.grid_height - 1):
                for j in range(1, block_width):
                    if i >= 0 and j < self.grid_width:
                        grid[i][j] = 2
        elif corner == 'bottom-right':
            for i in range(self.grid_height - block_height, self.grid_height - 1):
                for j in range(self.grid_width - block_width, self.grid_width - 1):
                    if i >= 0 and j >= 0:
                        grid[i][j] = 2
    
    def _add_furniture(self, grid: List[List[int]]):
        """Mobilya benzeri büyük engeller ekler"""
        furniture_count = random.randint(2, 5)
        
        for _ in range(furniture_count):
            # Mobilya boyutu
            width = random.randint(2, 4)
            height = random.randint(2, 4)
            
            # Rastgele pozisyon
            x = random.randint(3, self.grid_width - width - 3)
            y = random.randint(3, self.grid_height - height - 3)
            
            # Mobilyayı yerleştir
            for i in range(height):
                for j in range(width):
                    if (y + i < self.grid_height - 1 and 
                        x + j < self.grid_width - 1):
                        grid[y + i][x + j] = 1
    
    def _find_start_position(self, grid: List[List[int]]) -> Tuple[int, int]:
        """Robot için uygun başlangıç pozisyonu bulur"""
        attempts = 0
        while attempts < 100:
            x = random.randint(2, self.grid_width - 3)
            y = random.randint(2, self.grid_height - 3)
            
            # Pozisyon boş mu ve etrafında yer var mı?
            if (grid[y][x] == 0 and 
                grid[y-1][x] == 0 and grid[y+1][x] == 0 and
                grid[y][x-1] == 0 and grid[y][x+1] == 0):
                return (x * self.grid_size + self.grid_size // 2, 
                       y * self.grid_size + self.grid_size // 2)
            
            attempts += 1
        
        # Varsayılan pozisyon
        return (50, 50)
    
    def is_valid_position(self, grid: List[List[int]], x: int, y: int) -> bool:
        """Verilen pozisyonun geçerli olup olmadığını kontrol eder"""
        grid_x = x // self.grid_size
        grid_y = y // self.grid_size
        
        if (0 <= grid_x < self.grid_width and 
            0 <= grid_y < self.grid_height):
            return grid[grid_y][grid_x] == 0
        return False