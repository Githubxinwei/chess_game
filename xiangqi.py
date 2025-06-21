import pygame
import sys
import random
import time

# 常量
BOARD_SIZE = 9, 10
CELL_SIZE = 60
MARGIN = 50
WINDOW_SIZE = (BOARD_SIZE[0] * CELL_SIZE + 2 * MARGIN, BOARD_SIZE[1] * CELL_SIZE + 2 * MARGIN)

# 颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)

class Piece:
    def __init__(self, name, color, x, y):
        self.name = name
        self.color = color
        self.x, self.y = x, y
        self.selected = False
    
    def can_move(self, new_x, new_y, board):
        if new_x < 0 or new_x > 8 or new_y < 0 or new_y > 9:
            return False
        
        target = board.get_piece(new_x, new_y)
        if target and target.color == self.color:
            return False
        
        dx, dy = abs(new_x - self.x), abs(new_y - self.y)
        
        if self.name == '车':
            if self.x != new_x and self.y != new_y:
                return False
            return board.is_path_clear(self.x, self.y, new_x, new_y)
        
        elif self.name == '马':
            if (dx == 2 and dy == 1) or (dx == 1 and dy == 2):
                # 检查马腿
                if dx == 2:
                    block_x = self.x + (1 if new_x > self.x else -1)
                    return not board.get_piece(block_x, self.y)
                else:
                    block_y = self.y + (1 if new_y > self.y else -1)
                    return not board.get_piece(self.x, block_y)
            return False
        
        elif self.name in ['象', '相']:
            if dx == 2 and dy == 2:
                # 不能过河
                if self.color == 'red' and new_y < 5:
                    return False
                if self.color == 'black' and new_y > 4:
                    return False
                # 检查象眼
                block_x = self.x + (1 if new_x > self.x else -1)
                block_y = self.y + (1 if new_y > self.y else -1)
                return not board.get_piece(block_x, block_y)
            return False
        
        elif self.name in ['士', '仕']:
            if dx == 1 and dy == 1:
                # 只能在九宫格内
                if new_x < 3 or new_x > 5:
                    return False
                if self.color == 'red' and (new_y < 7 or new_y > 9):
                    return False
                if self.color == 'black' and (new_y < 0 or new_y > 2):
                    return False
                return True
            return False
        
        elif self.name in ['将', '帅']:
            if (dx == 1 and dy == 0) or (dx == 0 and dy == 1):
                # 只能在九宫格内
                if new_x < 3 or new_x > 5:
                    return False
                if self.color == 'red' and (new_y < 7 or new_y > 9):
                    return False
                if self.color == 'black' and (new_y < 0 or new_y > 2):
                    return False
                return True
            return False
        
        elif self.name == '炮':
            if self.x != new_x and self.y != new_y:
                return False
            pieces_between = board.count_pieces_between(self.x, self.y, new_x, new_y)
            if target:
                return pieces_between == 1  # 吃子必须隔一个子
            else:
                return pieces_between == 0  # 移动时路径必须无阻挡
        
        elif self.name in ['兵', '卒']:
            if self.color == 'red':
                if self.y > 4:  # 未过河
                    return dx == 0 and dy == 1 and new_y < self.y
                else:  # 已过河
                    return (dx == 0 and dy == 1 and new_y < self.y) or (dx == 1 and dy == 0)
            else:  # 黑卒
                if self.y < 5:  # 未过河
                    return dx == 0 and dy == 1 and new_y > self.y
                else:  # 已过河
                    return (dx == 0 and dy == 1 and new_y > self.y) or (dx == 1 and dy == 0)
        
        return False

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("中国象棋")
        self.clock = pygame.time.Clock()
        # 加载中文字体
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/Library/Fonts/Arial Unicode MS.ttf"
        ]
        self.font = None
        for font_path in font_paths:
            try:
                self.font = pygame.font.Font(font_path, 24)
                break
            except:
                continue
        if not self.font:
            self.font = pygame.font.Font(None, 32)
        self.pieces = self._init_pieces()
        self.current_player = 'red'
        self.selected_piece = None
        self.last_move_time = time.time()
        self.game_over = False
        self.winner = None
        self.win_time = None
        
        # 初始化音效
        pygame.mixer.init()
        self.sounds = self._create_voice_sounds()
    
    def _init_pieces(self):
        pieces = []
        # 黑方
        pieces.extend([
            Piece('车', 'black', 0, 0), Piece('车', 'black', 8, 0),
            Piece('马', 'black', 1, 0), Piece('马', 'black', 7, 0),
            Piece('象', 'black', 2, 0), Piece('象', 'black', 6, 0),
            Piece('士', 'black', 3, 0), Piece('士', 'black', 5, 0),
            Piece('将', 'black', 4, 0),
            Piece('炮', 'black', 1, 2), Piece('炮', 'black', 7, 2),
            Piece('卒', 'black', 0, 3), Piece('卒', 'black', 2, 3),
            Piece('卒', 'black', 4, 3), Piece('卒', 'black', 6, 3),
            Piece('卒', 'black', 8, 3)
        ])
        # 红方
        pieces.extend([
            Piece('车', 'red', 0, 9), Piece('车', 'red', 8, 9),
            Piece('马', 'red', 1, 9), Piece('马', 'red', 7, 9),
            Piece('相', 'red', 2, 9), Piece('相', 'red', 6, 9),
            Piece('仕', 'red', 3, 9), Piece('仕', 'red', 5, 9),
            Piece('帅', 'red', 4, 9),
            Piece('炮', 'red', 1, 7), Piece('炮', 'red', 7, 7),
            Piece('兵', 'red', 0, 6), Piece('兵', 'red', 2, 6),
            Piece('兵', 'red', 4, 6), Piece('兵', 'red', 6, 6),
            Piece('兵', 'red', 8, 6)
        ])
        return pieces
    
    def _create_voice_sounds(self):
        import subprocess
        import threading
        import numpy as np
        
        def play_voice(text):
            def _play():
                try:
                    subprocess.run(['say', text], check=False, timeout=3)
                except:
                    pass
            threading.Thread(target=_play, daemon=True).start()
        
        def create_sound_effect(freq, duration, pattern='single'):
            sample_rate = 22050
            frames = int(duration * sample_rate)
            arr = np.zeros((frames, 2), dtype=np.int16)
            
            if pattern == 'gallop':  # 马踏震动声
                for i in range(frames):
                    t = i / sample_rate
                    # 创建震动效果，模拟马踏地面
                    beat = int(t * 6) % 2  # 6次/秒的节拍
                    if beat == 0:
                        wave = int(1500 * np.sin(2 * np.pi * 80 * t) * (1 + 0.5 * np.sin(2 * np.pi * 20 * t)))
                    else:
                        wave = int(800 * np.sin(2 * np.pi * 60 * t))
                    arr[i] = [wave, wave]
            elif pattern == 'hit':  # 吃子声
                for i in range(frames):
                    t = i / sample_rate
                    wave = int(3000 * np.sin(2 * np.pi * freq * t) * np.exp(-t * 5))
                    arr[i] = [wave, wave]
            elif pattern == 'alert':  # 将军声
                for i in range(frames):
                    t = i / sample_rate
                    wave = int(2500 * np.sin(2 * np.pi * (freq + 200 * np.sin(10 * t)) * t))
                    arr[i] = [wave, wave]
            
            return pygame.sndarray.make_sound(arr)
        
        return {
            'voice': play_voice,
            'move': create_sound_effect(400, 0.3, 'gallop'),
            'capture': create_sound_effect(600, 0.4, 'hit'),
            'check': create_sound_effect(800, 0.6, 'alert')
        }
    
    def get_voice_text(self, piece, target, new_x, new_y):
        """获取语音提示文本"""
        piece_names = {
            '车': '车', '马': '马', '炮': '炮', '象': '象', '相': '相',
            '士': '士', '仕': '仕', '将': '将', '帅': '帅', '兵': '兵', '卒': '卒'
        }
        
        piece_name = piece_names.get(piece.name, piece.name)
        
        # 检查是否将军
        if self.is_check_after_move(piece, new_x, new_y):
            if target:
                return f"{piece_name}吃{piece_names.get(target.name, target.name)}，将军"
            else:
                return f"{piece_name}，将军"
        
        # 特殊情况
        if piece.name == '炮':
            if new_x == 4:  # 中路
                return f"当门炮"
            elif target:
                return f"炮打{piece_names.get(target.name, target.name)}"
            else:
                return f"炮走{self.get_position_name(new_x, new_y)}"
        
        elif piece.name in ['车']:
            if target:
                return f"车吃{piece_names.get(target.name, target.name)}"
            else:
                return f"车走{self.get_position_name(new_x, new_y)}"
        
        elif piece.name == '马':
            if target:
                return f"马踏{piece_names.get(target.name, target.name)}"
            else:
                return f"马走{self.get_position_name(new_x, new_y)}"
        
        # 默认情况
        if target:
            return f"{piece_name}吃{piece_names.get(target.name, target.name)}"
        else:
            return f"{piece_name}走{self.get_position_name(new_x, new_y)}"
    
    def get_position_name(self, x, y):
        """获取位置名称"""
        cols = ['一', '二', '三', '四', '五', '六', '七', '八', '九']
        rows = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
        return f"{cols[x]}{rows[y]}"
    
    def is_check_after_move(self, piece, new_x, new_y):
        """检查移动后是否将军"""
        # 简化实现，检查是否攻击对方将/帅
        enemy_king = '将' if piece.color == 'red' else '帅'
        king = next((p for p in self.pieces if p.name == enemy_king), None)
        
        if not king:
            return False
        
        # 模拟移动后检查是否能攻击到对方将/帅
        old_x, old_y = piece.x, piece.y
        piece.x, piece.y = new_x, new_y
        can_attack = piece.can_move(king.x, king.y, self)
        piece.x, piece.y = old_x, old_y
        
        return can_attack
    
    def get_piece(self, x, y):
        return next((p for p in self.pieces if p.x == x and p.y == y), None)
    
    def check_game_over(self):
        """检查游戏是否结束"""
        red_king = next((p for p in self.pieces if p.name == '帅'), None)
        black_king = next((p for p in self.pieces if p.name == '将'), None)
        
        if not red_king:
            self.game_over = True
            self.winner = 'black'
            self.win_time = time.time()
            self.sounds['voice']('黑方胜利')
        elif not black_king:
            self.game_over = True
            self.winner = 'red'
            self.win_time = time.time()
            self.sounds['voice']('红方胜利')
    
    def is_path_clear(self, x1, y1, x2, y2):
        if x1 == x2:  # 垂直移动
            start_y, end_y = min(y1, y2), max(y1, y2)
            for y in range(start_y + 1, end_y):
                if self.get_piece(x1, y):
                    return False
        else:  # 水平移动
            start_x, end_x = min(x1, x2), max(x1, x2)
            for x in range(start_x + 1, end_x):
                if self.get_piece(x, y1):
                    return False
        return True
    
    def count_pieces_between(self, x1, y1, x2, y2):
        count = 0
        if x1 == x2:  # 垂直
            start_y, end_y = min(y1, y2), max(y1, y2)
            for y in range(start_y + 1, end_y):
                if self.get_piece(x1, y):
                    count += 1
        else:  # 水平
            start_x, end_x = min(x1, x2), max(x1, x2)
            for x in range(start_x + 1, end_x):
                if self.get_piece(x, y1):
                    count += 1
        return count
    
    def draw_board(self):
        self.screen.fill(BROWN)
        # 绘制线条
        for i in range(9):
            x = MARGIN + i * CELL_SIZE
            pygame.draw.line(self.screen, BLACK, (x, MARGIN), (x, MARGIN + 9 * CELL_SIZE), 2)
        for i in range(10):
            y = MARGIN + i * CELL_SIZE
            pygame.draw.line(self.screen, BLACK, (MARGIN, y), (MARGIN + 8 * CELL_SIZE, y), 2)
        
        # 绘制楚河汉界区域
        river_y = MARGIN + 4 * CELL_SIZE
        river_height = CELL_SIZE
        
        # 绘制河界背景
        pygame.draw.rect(self.screen, (200, 200, 150), 
                        (MARGIN, river_y, 8 * CELL_SIZE, river_height))
        
        # 绘制河界边框
        pygame.draw.rect(self.screen, BLACK, 
                        (MARGIN, river_y, 8 * CELL_SIZE, river_height), 3)
        
        # 绘制楚河汉界文字
        if self.font:
            text1 = self.font.render("楚河", True, BLACK)
            text2 = self.font.render("汉界", True, BLACK)
            self.screen.blit(text1, (MARGIN + 1.5 * CELL_SIZE, river_y + 15))
            self.screen.blit(text2, (MARGIN + 5.5 * CELL_SIZE, river_y + 15))
    
    def draw_pieces(self):
        for piece in self.pieces:
            x = MARGIN + piece.x * CELL_SIZE
            y = MARGIN + piece.y * CELL_SIZE
            color = RED if piece.color == 'red' else BLACK
            
            pygame.draw.circle(self.screen, WHITE, (x, y), 25)
            pygame.draw.circle(self.screen, color, (x, y), 25, 3)
            
            if piece.selected:
                pygame.draw.circle(self.screen, YELLOW, (x, y), 30, 3)
            
            text = self.font.render(piece.name, True, color)
            text_rect = text.get_rect(center=(x, y))
            self.screen.blit(text, text_rect)
    
    def get_board_pos(self, mouse_pos):
        x, y = mouse_pos
        board_x = round((x - MARGIN) / CELL_SIZE)
        board_y = round((y - MARGIN) / CELL_SIZE)
        if 0 <= board_x < 9 and 0 <= board_y < 10:
            return board_x, board_y
        return None
    
    def handle_click(self, pos):
        if self.game_over:
            return
            
        board_pos = self.get_board_pos(pos)
        if not board_pos:
            return
        
        x, y = board_pos
        clicked_piece = self.get_piece(x, y)
        
        if self.selected_piece:
            if clicked_piece and clicked_piece.color == self.current_player:
                self.selected_piece.selected = False
                self.selected_piece = clicked_piece
                clicked_piece.selected = True
            else:
                # 检查移动是否合法
                if self.selected_piece.can_move(x, y, self):
                    target = self.get_piece(x, y)
                    if target:
                        self.pieces.remove(target)
                        if self.is_check_after_move(self.selected_piece, x, y):
                            self.sounds['check'].play()
                            self.sounds['voice']('将军')
                        else:
                            self.sounds['capture'].play()
                            self.sounds['voice']('吃')
                    else:
                        if self.is_check_after_move(self.selected_piece, x, y):
                            self.sounds['check'].play()
                            self.sounds['voice']('将军')
                        else:
                            self.sounds['move'].play()
                    
                    self.selected_piece.x, self.selected_piece.y = x, y
                    self.selected_piece.selected = False
                    self.selected_piece = None
                    self.current_player = 'black'
                    self.last_move_time = time.time()
                    self.check_game_over()
        else:
            if clicked_piece and clicked_piece.color == self.current_player:
                self.selected_piece = clicked_piece
                clicked_piece.selected = True
    
    def ai_move(self):
        """简单AI移动"""
        black_pieces = [p for p in self.pieces if p.color == 'black']
        if not black_pieces:
            return
        
        # 随机选择一个棋子和目标位置
        for _ in range(100):  # 最多尝试100次
            piece = random.choice(black_pieces)
            new_x = random.randint(0, 8)
            new_y = random.randint(0, 9)
            
            if piece.can_move(new_x, new_y, self):
                target = self.get_piece(new_x, new_y)
                if target:
                    self.pieces.remove(target)
                    if self.is_check_after_move(piece, new_x, new_y):
                        self.sounds['check'].play()
                        self.sounds['voice']('将军')
                    else:
                        self.sounds['capture'].play()
                        self.sounds['voice']('吃')
                else:
                    if self.is_check_after_move(piece, new_x, new_y):
                        self.sounds['check'].play()
                        self.sounds['voice']('将军')
                    else:
                        self.sounds['move'].play()
                piece.x, piece.y = new_x, new_y
                self.current_player = 'red'
                self.check_game_over()
                break
    
    def run(self):
        running = True
        while running:
            current_time = time.time()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and self.current_player == 'red':
                        self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and self.game_over:
                        self.__init__()  # 重新开始游戏
            
            # 胜利后3秒自动重置
            if self.game_over and self.win_time and current_time - self.win_time > 3.0:
                self.__init__()
            
            # AI自动走棋
            if not self.game_over and self.current_player == 'black' and current_time - self.last_move_time > 1.0:
                self.ai_move()
                self.last_move_time = current_time
            
            self.draw_board()
            self.draw_pieces()
            
            # 显示游戏状态
            if self.game_over:
                winner_text = "红方胜利!" if self.winner == 'red' else "黑方胜利!"
                text = self.font.render(winner_text, True, RED if self.winner == 'red' else BLACK)
                self.screen.blit(text, (10, 10))
                restart_text = self.font.render("3秒后自动重置", True, BLACK)
                self.screen.blit(restart_text, (10, 40))
            else:
                player_text = "红方" if self.current_player == 'red' else "黑方(AI)"
                text = self.font.render(f"当前: {player_text}", True, BLACK)
                self.screen.blit(text, (10, 10))
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()