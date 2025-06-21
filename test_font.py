import pygame

pygame.init()
try:
    font = pygame.font.Font("/System/Library/Fonts/PingFang.ttc", 24)
    print("PingFang字体加载成功")
    
    # 测试渲染中文
    text = font.render("车马炮", True, (0, 0, 0))
    print("中文渲染成功")
except Exception as e:
    print(f"字体加载失败: {e}")

pygame.quit()