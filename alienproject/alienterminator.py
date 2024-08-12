import pygame
import random
import sys
import math
import time

# Inicializar o PyGame
pygame.init()
pygame.mixer.init()  # Inicializar o mixer para sons

# Definir cores
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Definir dimensões da tela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Alien Terminator")

# Definir FPS (frames por segundo)
clock = pygame.time.Clock()
FPS = 60

# Carregar imagens
player_img = pygame.image.load('assets/player.png')
background_img = pygame.image.load('assets/background.png')
predator_img = pygame.image.load('assets/predator.png')
predator_laser_img = pygame.image.load('assets/predator_laser.png')
predator_laser2_img = pygame.image.load('assets/predator_laser2.png')
heart_img = pygame.image.load('assets/heart.png') 
player_rect = player_img.get_rect(midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))

# Carregar sons
shoot_sound = pygame.mixer.Sound('assets/shoot.wav')
damage_sound = pygame.mixer.Sound('assets/damage.wav')
special_shot_sound = pygame.mixer.Sound('assets/special_shot.wav')  # Carregar som do tiro especial
background_music = 'assets/background_music.mp3'

# Ajustar o volume dos sons
shoot_sound.set_volume(0.1)  # Definir o volume do som de tiro para 10%
damage_sound.set_volume(0.1)  # Definir o volume do som de dano para 10%
special_shot_sound.set_volume(0.3)  # Definir o volume do som de tiro especial para 30%

# Variável para controlar o cooldown dos tiros especiais
special_shot_cooldown = 0.5  # 0.5 segundos entre os tiros especiais
last_special_shot_time = 0

# Função para criar uma onda de aliens
def create_alien_wave(num_aliens):
    aliens = []
    for _ in range(num_aliens):
        alien_img = pygame.image.load('assets/alien.png')
        alien_rect = alien_img.get_rect(topleft=(random.randint(0, SCREEN_WIDTH-40), random.randint(-1000, -40)))
        aliens.append((alien_img, alien_rect))
    return aliens

# Função para criar meteoros
def create_meteorites(num_meteorites):
    meteorites = []
    for _ in range(num_meteorites):
        meteorite_img = pygame.image.load('assets/meteorite.png')
        meteorite_rect = meteorite_img.get_rect(topleft=(random.randint(0, SCREEN_WIDTH-60), random.randint(-1000, -40)))
        meteorites.append((meteorite_img, meteorite_rect))
    return meteorites

# Função para mover os aliens
def move_aliens(aliens):
    for alien_img, alien_rect in aliens:
        alien_rect.y += 5
        if alien_rect.top > SCREEN_HEIGHT:
            alien_rect.y = random.randint(-1000, -40)
            alien_rect.x = random.randint(0, SCREEN_WIDTH-40)

# Função para mover os meteoros
def move_meteorites(meteorites):
    for meteorite_img, meteorite_rect in meteorites:
        meteorite_rect.y += 5
        if meteorite_rect.top > SCREEN_HEIGHT:
            meteorite_rect.y = random.randint(-1000, -40)
            meteorite_rect.x = random.randint(0, SCREEN_WIDTH-60)

# Função para verificar colisões e atualizar o score
def check_collisions(player, aliens, bullets, meteorites, predator, predator_lasers, predator_lasers2, score, predator_health, power_kills, total_kills, predator_kills, special_bullets):
    for bullet in bullets[:]:
        for alien_img, alien_rect in aliens[:]:
            if bullet.colliderect(alien_rect):
                aliens.remove((alien_img, alien_rect))
                bullets.remove(bullet)
                score[0] += 10  # Atualizar o score
                power_kills[0] += 1  # Atualizar o contador de kills para o poder especial
                total_kills[0] += 1  # Atualizar o contador cumulativo de kills
                damage_sound.play()  # Reproduzir som de dano
                break

    # Verificar colisões entre tiros especiais e aliens
    for special_bullet_rect, _ in special_bullets[:]:
        for alien_img, alien_rect in aliens[:]:
            if special_bullet_rect.colliderect(alien_rect):
                aliens.remove((alien_img, alien_rect))
                score[0] += 10  # Atualizar o score
                power_kills[0] += 1  # Atualizar o contador de kills para o poder especial
                total_kills[0] += 1  # Atualizar o contador cumulativo de kills
                special_bullets.remove((special_bullet_rect, _))
                damage_sound.play()  # Reproduzir som de dano
                break

    # Verificar se algum alien tocou o player
    for alien_img, alien_rect in aliens:
        if alien_rect.colliderect(player):
            damage_sound.play()  # Reproduzir som de dano
            return False  # Game over

    # Verificar se algum meteorito tocou o player
    for meteorite_img, meteorite_rect in meteorites:
        if meteorite_rect.colliderect(player):
            damage_sound.play()  # Reproduzir som de dano
            return False  # Game over

    # Verificar se algum laser do Predator tocou o player
    for laser in predator_lasers:
        if laser.colliderect(player):
            damage_sound.play()  # Reproduzir som de dano
            return False  # Game over
    for laser in predator_lasers2:
        if laser.colliderect(player):
            damage_sound.play()  # Reproduzir som de dano
            return False  # Game over

    # Verificar se o Predator tocou o player
    if predator and predator.colliderect(player):
        damage_sound.play()  # Reproduzir som de dano
        return False  # Game over

    # Verificar se algum tiro acertou o Predator
    if predator:
        for bullet in bullets[:]:
            if bullet.colliderect(predator):
                bullets.remove(bullet)
                predator_health[0] -= 1
                damage_sound.play()  # Reproduzir som de dano
                if predator_health[0] <= 0:
                    predator_kills[0] += 1  # Atualizar o contador de kills de Predator
                    return 'Predator defeated'  # Predator derrotado
                break

    return True

# Função para mostrar o placar e os contadores de kills
def display_score_and_kills(score, power_kills, total_kills, predator_kills, power_ready, special_uses):
    font = pygame.font.Font(None, 24)
    score_text = font.render(f'Score: {score[0]}', True, WHITE)
    power_kills_text = font.render(f'Power(15): {power_kills[0]}', True, WHITE)  # Exibir o contador de kills para o poder especial
    total_kills_text = font.render(f'Total Kills: {total_kills[0]}', True, WHITE)  # Exibir o contador cumulativo de kills
    predator_kills_text = font.render(f'Predator Kills: {predator_kills[0]}', True, WHITE)
    
    screen.blit(score_text, (10, 10))
    screen.blit(power_kills_text, (10, 50))
    screen.blit(total_kills_text, (10, 90))
    screen.blit(predator_kills_text, (10, 130))

    # Mostrar "Power ready - Press B" se o poder estiver disponível e quantas vezes ele pode ser usado
    if power_ready:
        power_text = font.render(f'Power ready - Press B ({special_uses} left)', True, GREEN)
        screen.blit(power_text, (SCREEN_WIDTH - power_text.get_width() - 10, SCREEN_HEIGHT - power_text.get_height() - 10))

# Função para mostrar a tela de game over
def display_game_over(score, total_kills, predator_kills):
    font = pygame.font.Font(None, 48)
    game_over_text = font.render('GAME OVER', True, RED)
    score_text = font.render(f'Final Score: {score[0]}', True, WHITE)
    total_kills_text = font.render(f'Total Kills: {total_kills[0]}', True, WHITE)
    predator_kills_text = font.render(f'Predator Kills: {predator_kills[0]}', True, WHITE)
    restart_text = font.render('Press ESC to return to the main menu', True, WHITE)
    
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
    screen.blit(total_kills_text, (SCREEN_WIDTH // 2 - total_kills_text.get_width() // 2, SCREEN_HEIGHT // 2 + 70))
    screen.blit(predator_kills_text, (SCREEN_WIDTH // 2 - predator_kills_text.get_width() // 2, SCREEN_HEIGHT // 2 + 130))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 190))

    # Parar a música de fundo ao finalizar o jogo
    pygame.mixer.music.stop()

# Função para mostrar a tela de vitória
def display_level_complete(score):
    font = pygame.font.Font(None, 48)
    level_complete_text = font.render('LEVEL COMPLETE', True, GREEN)
    score_text = font.render(f'Score: {score[0]}', True, WHITE)
    screen.blit(level_complete_text, (SCREEN_WIDTH // 2 - level_complete_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))

# Função para exibir o menu principal
def display_main_menu(selected_option):
    screen.fill(BLACK)
    font = pygame.font.Font(None, 74)
    title_text = font.render('ALIEN TERMINATOR', True, WHITE)
    play_text = pygame.font.Font(None, 48).render('Start', True, WHITE)
    instructions_text = pygame.font.Font(None, 48).render('Instructions', True, WHITE)
    quit_text = pygame.font.Font(None, 48).render('Quit', True, WHITE)

    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(play_text, (SCREEN_WIDTH // 2 - play_text.get_width() // 2, SCREEN_HEIGHT // 2))
    screen.blit(instructions_text, (SCREEN_WIDTH // 2 - instructions_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))

    # Destaque a opção selecionada
    if selected_option == 'play':
        pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 - play_text.get_width() // 2 - 10, SCREEN_HEIGHT // 2 - 10, play_text.get_width() + 20, play_text.get_height() + 20), 2)
    elif selected_option == 'instructions':
        pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 - instructions_text.get_width() // 2 - 10, SCREEN_HEIGHT // 2 + 40, instructions_text.get_width() + 20, instructions_text.get_height() + 20), 2)
    elif selected_option == 'quit':
        pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2 - 10, SCREEN_HEIGHT // 2 + 90, quit_text.get_width() + 20, quit_text.get_height() + 20), 2)

# Função para exibir a tela de instruções
def display_instructions():
    instructions = True
    while instructions:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                instructions = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                instructions = False

        screen.fill(BLACK)
        font = pygame.font.Font(None, 36)
        instructions_text = [
            'Use the arrow keys to move the player.',
            'Use ESPACEBAR to shoot.',
            'Destroy as many alliens as you can.',
            'Meteorites are not destructible, avoid them.',
            'Be careful with the predator.',
            'Press ESC to return to main menu.'
        ]
        title_text = pygame.font.Font(None, 74).render('INSTRUÇÕES', True, WHITE)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 200))
        for i, line in enumerate(instructions_text):
            text = font.render(line, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 100 + i * 40))

        pygame.display.flip()
        clock.tick(FPS)

# Função para desenhar a barra de vida do Predator
def draw_predator_health(health):
    for i in range(health):
        screen.blit(heart_img, (SCREEN_WIDTH - 150 + i * 30, 10))

# Função para lançar o tiro especial
def launch_special_shot(player_rect, special_bullets):
    global last_special_shot_time
    current_time = time.time()
    
    if current_time - last_special_shot_time >= special_shot_cooldown:
        angles = [-30, -15, 0, 15, 30]  # Ângulos de disparo para os 5 tiros
        for angle in angles:
            radians = math.radians(angle)
            for i in range(4):  # 4 sequências de tiros
                bullet_rect = pygame.Rect(player_rect.centerx - 2, player_rect.top - 10, 4, 10)
                velocity = pygame.Vector2(10 * math.sin(radians), -10 * math.cos(radians))  # Direcionado para cima
                special_bullets.append((bullet_rect, velocity))
        special_shot_sound.play()  # Reproduzir som do tiro especial
        last_special_shot_time = current_time  # Atualizar o tempo do último tiro especial

# Função para mover e desenhar os tiros especiais
def move_and_draw_special_bullets(special_bullets):
    for bullet_rect, velocity in special_bullets[:]:
        bullet_rect.x += velocity.x
        bullet_rect.y += velocity.y
        pygame.draw.rect(screen, GREEN, bullet_rect)
        if bullet_rect.right < 0 or bullet_rect.left > SCREEN_WIDTH or bullet_rect.bottom < 0:
            special_bullets.remove((bullet_rect, velocity))

# Função para o loop principal do jogo
def game_loop():
    # Tocar música de fundo ao iniciar o jogo
    pygame.mixer.music.load(background_music)
    pygame.mixer.music.set_volume(0.1)  # Definir o volume da música de fundo para 20%
    pygame.mixer.music.play(-1)  # -1 faz com que a música toque em loop

    player_speed = 7
    bullets = []
    special_bullets = []
    aliens = create_alien_wave(10)
    meteorites = create_meteorites(5)
    predator = None  # Inicialmente, não há chefe Predator
    predator_lasers = []
    predator_lasers2 = []
    predator_health = [5]  # Vida do Predator, começa com 5
    predator_defeated = False  # Flag para indicar se o Predator foi derrotado
    score = [0]  # Usar lista para mutabilidade
    power_kills = [0]  # Contador de kills de aliens para o poder especial
    total_kills = [0]  # Contador cumulativo de kills de aliens
    predator_kills = [0]  # Contador de kills de Predator
    game_over = False
    power_ready = False  # Flag para indicar se o poder especial está disponível
    special_uses = 3  # Inicia com 3 usos disponíveis
    next_predator_appearance = 100  # Score para a primeira aparição do Predator
    predator_active = False  # Flag para indicar se o Predator está ativo

    while True:
        screen.blit(background_img, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    bullet = pygame.Rect(player_rect.centerx - 2, player_rect.top - 10, 4, 10)
                    bullets.append(bullet)
                    shoot_sound.play()  # Tocar som de tiro
                if event.key == pygame.K_b and power_ready and not game_over and special_uses > 0:
                    launch_special_shot(player_rect, special_bullets)
                    special_uses -= 1  # Reduzir o número de usos restantes
                    if special_uses == 0:
                        power_ready = False  # Desativar o poder quando os tiros especiais acabarem
                if event.key == pygame.K_ESCAPE:
                    return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_rect.left > 0:
            player_rect.x -= player_speed
        if keys[pygame.K_RIGHT] and player_rect.right < SCREEN_WIDTH:
            player_rect.x += player_speed

        if not game_over:
            for bullet in bullets:
                bullet.y -= 10
                if bullet.bottom < 0:
                    bullets.remove(bullet)

            move_and_draw_special_bullets(special_bullets)  # Mover e desenhar os tiros especiais
            move_aliens(aliens)
            move_meteorites(meteorites)

            # Chefe "Predator" aparece ao atingir 100 pontos inicialmente, e a cada 200 pontos após a primeira aparição
            if score[0] >= next_predator_appearance and not predator_active:
                predator = predator_img.get_rect(midtop=(SCREEN_WIDTH, 50))  # Aparece na parte superior direita
                predator_health[0] = 5  # Reiniciar a vida do Predator
                predator_active = True  # Ativar o Predator
                next_predator_appearance += 200  # Próxima aparição será em mais 200 pontos

            if predator_active and predator:
                predator.x -= 5  # Movimentar o chefe para a esquerda
                if predator.right < 0:  # Se sair da tela, reaparecer na direita
                    predator.left = SCREEN_WIDTH

                if predator.top > 0 and random.random() < 0.02:
                    laser = predator_laser_img.get_rect(midtop=(predator.centerx, predator.bottom))
                    predator_lasers.append(laser)
                if predator.top > 0 and random.random() < 0.02:
                    laser2 = predator_laser2_img.get_rect(midtop=(predator.centerx - 20, predator.bottom))
                    predator_lasers2.append(laser2)

                for laser in predator_lasers:
                    laser.y += 8
                    if laser.top > SCREEN_HEIGHT:
                        predator_lasers.remove(laser)
                for laser2 in predator_lasers2:
                    laser2.y += 6
                    if laser2.top > SCREEN_HEIGHT:
                        predator_lasers2.remove(laser2)

                screen.blit(predator_img, predator)
                draw_predator_health(predator_health[0])  # Desenhar a barra de vida do Predator
                for laser in predator_lasers:
                    screen.blit(predator_laser_img, laser)
                for laser2 in predator_lasers2:
                    screen.blit(predator_laser2_img, laser2)

            else:
                predator_active = False  # Predator não está ativo
                if len(aliens) == 0:  # Se todos os aliens foram destruídos, criar uma nova onda
                    aliens = create_alien_wave(10)
                if len(meteorites) == 0:  # Se todos os meteoros foram destruídos, criar novos meteoros
                    meteorites = create_meteorites(5)

            # Verificar se o poder especial pode ser recarregado
            if power_kills[0] >= 15 and not power_ready:
                power_ready = True
                special_uses = 3  # Recarregar o poder para 3 usos após matar 15 aliens
                power_kills[0] -= 15  # Subtrair 15 kills para que o contador continue corretamente

            screen.blit(player_img, player_rect)
            for bullet in bullets:
                pygame.draw.rect(screen, RED, bullet)  # Alterado para vermelho
            for alien_img, alien_rect in aliens:
                screen.blit(alien_img, alien_rect)
            for meteorite_img, meteorite_rect in meteorites:
                screen.blit(meteorite_img, meteorite_rect)

            collision_result = check_collisions(player_rect, aliens, bullets, meteorites, predator, predator_lasers, predator_lasers2, score, predator_health, power_kills, total_kills, predator_kills, special_bullets)
            if collision_result == False:
                game_over = True
            elif collision_result == 'Predator defeated':
                predator = None  # Predator derrotado, remove-o do jogo
                predator_active = False  # Desativar o Predator

            display_score_and_kills(score, power_kills, total_kills, predator_kills,power_ready, special_uses)

        else:
            display_game_over(score, total_kills, predator_kills)

        pygame.display.flip()
        clock.tick(FPS)


# Loop principal do jogo
def main():
    menu = True
    selected_option = 'play'
    while menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if selected_option == 'play':
                        game_loop()
                    elif selected_option == 'instructions':
                        display_instructions()
                    elif selected_option == 'quit':
                        menu = False
                if event.key == pygame.K_DOWN:
                    if selected_option == 'play':
                        selected_option = 'instructions'
                    elif selected_option == 'instructions':
                        selected_option = 'quit'
                    elif selected_option == 'quit':
                        selected_option = 'play'
                if event.key == pygame.K_UP:
                    if selected_option == 'play':
                        selected_option = 'quit'
                    elif selected_option == 'instructions':
                        selected_option = 'play'
                    elif selected_option == 'quit':
                        selected_option = 'instructions'
                if event.key == pygame.K_i:  # Adicionando a opção para pressionar 'I' para instruções
                    selected_option = 'instructions'
                if event.key == pygame.K_ESCAPE:
                    menu = False

        display_main_menu(selected_option)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
