from settings import *
from game_sprites import *
from menu_sprites import *
from support import *
from groups import AllMenuSprites, AllSprites

pygame.init()
pygame.mixer.init()
if FULLSCREEN:
    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
else: 
    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Burger Bash')
icon = import_image('images', 'icon')
pygame.display.set_icon(icon)
clock = pygame.time.Clock()



class Game:
    def __init__(self, num_players, fillings):
        # setup
        self.display_surface = pygame.display.get_surface()
        self.clock = clock
        self.running = True
        self.play_again = False

        # groups
        self.all_sprites = AllSprites()
        self.player_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.entity_sprites = pygame.sprite.Group()
        self.tile_sprites = pygame.sprite.Group()
        self.landing_zone_sprites = pygame.sprite.Group()
        self.profile_sprites = pygame.sprite.Group()
        self.highlight_sprites = pygame.sprite.Group()
        self.item_select_sprites = pygame.sprite.Group()
        self.item_sprites = pygame.sprite.Group()
        self.toaster_sprites = pygame.sprite.Group()
        self.bread_sprites = pygame.sprite.Group()
        self.wall_sprites = []
        self.drop_sprites = pygame.sprite.Group()

        # button just pressed
        self.mouse_l_just_pressed = False
        self.mouse_l_held = False
        self.mouse_r_held = False

        # landing zones
        self.next_landing_zone = num_players + 1

        # sodas
        self.sodas = {}

        # pointer
        self.pointer_exists = False

        # multiplayer
        self.num_players = num_players
        self.fillings = fillings
        self.max_fillings = 1
        self.filling_num_order = []
        self.filling_order_by_name = ['burger']
        for filling in fillings:
            self.max_fillings += 1 if fillings[filling][0] else 0
            self.filling_num_order.append(fillings[filling][1]) if fillings[filling][0] else None
            self.filling_order_by_name.append(filling) if fillings[filling][0] else None
        self.players = {}
        self.shadows = {}
        self.num_of_players = num_players
        self.current_player = 'player0'
        self.starting_player = 'player0'
        self.phase = 'launch'
        self.profiles = {}
        self.collisions = 0
        self.winner = None

        # turns
        self.turning = False
        self.total_rounds = 0
        self.you = None

        # items
        self.current_item = None

        # fonts
        self.rounds_font = pygame.font.Font(join('fonts', 'DiloWorld.ttf'), 60)
        self.time_font = pygame.font.Font(join('fonts', 'DiloWorld.ttf'), 80)
        self.rounds_alpha = 0

        # audio
        self.music = randint(1, 2)
        self.music_channel = None
        self.music_fade_out = False
        self.play_music = True

        # timers
        self.round_end_time = 0
        self.round_pause_duration = ROUND_PAUSE_TIME
        self.current_time = pygame.time.get_ticks()
        self.win_screen_dur = WIN_SCREEN_DUR
        self.start_time = pygame.time.get_ticks()
        self.start_dur = 3500

        # fade out
        self.rect_alpha = 0
        self.time_left = 15

        # framerate
        self.i = 0
        self.fps_update_rate = 100

        # setup
        self.audio_imports()
        self.setup()

        # music cause of weird bug
        mixer.music.load(join('audio', 'music', 'game music 1.mp3')) if self.music == 1 else None
        mixer.music.load(join('audio', 'music', 'game music 2.mp3')) if self.music == 2 else None 
        mixer.music.set_volume(0.3)
        mixer.music.play()
        mixer.music.set_pos(79) if self.music == 1 else None

    def input(self, dt):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            self.running = False

        # get just pressed
        if pygame.mouse.get_pressed()[0] and not self.mouse_l_held:
            self.mouse_l_just_pressed = True
            self.mouse_l_held = True
        elif pygame.mouse.get_pressed()[0]:
            self.mouse_l_just_pressed = False
        else:
            self.mouse_l_held = False
            # call launch
            if self.pointer_exists:
                self.you.kill()
                self.you = None
                self.players[self.current_player].squash = 0
                self.change_phase('launch', None, dt)
                self.players[self.current_player].launch(self.aimer.point_dir * -1,
                                        self.aimer.mouse_dist)
                self.shadows[self.current_player].launch(0,0)
                self.aimer.kill()
                self.pointer_exists = False
                for toaster in self.toaster_sprites:
                    toaster.animate = True
                    toaster.bread_left = 3
                    toaster.current_frame = toaster.def_frame

        # pointer
        if self.phase == 'aim' and not self.mouse_r_held:
            if self.you: self.you.visible = True
            clicked_on_player = False
            if self.mouse_l_just_pressed:
                if self.players[self.current_player].rect.collidepoint(pygame.mouse.get_pos()):
                    clicked_on_player = True
                self.pointer_exists = True
                self.create_pointer(clicked_on_player)
        elif self.phase == 'aim':
            if self.you: self.you.visible = False

        if pygame.mouse.get_just_pressed()[2]:
            if self.pointer_exists:
                self.aimer.kill()
                self.pointer_exists = False
                self.mouse_r_held = True
                self.players[self.current_player].squash = 0
                self.pointer.kill()
        else:
            self.mouse_r_held = False

        if self.you and self.pointer_exists: self.you.visible = False

    def create_pointer(self, clicked_on_player):
        if clicked_on_player:
            click_pos = self.players[self.current_player].rect.center
        else:
            click_pos = pygame.mouse.get_pos()

        aimer_pos = self.players[self.current_player].rect.center # click_pos

        self.aimer = Aimer(self.aimer_surfs[int(self.current_player[-1]) - 1], aimer_pos, click_pos, self.players[self.current_player].fillings, self.all_sprites)
        self.pointer = Pointer(self.pointer_surfs[int(self.current_player[-1]) - 1], self.players[self.current_player].rect.center, click_pos, self.all_sprites)

    def create_landing_zone(self, first = False):
        pos_x = randint(ceil(WALL_PADDING_X + LANDING_ZONE_PADDING/2), floor(WINDOW_WIDTH - WALL_PADDING_X - LANDING_ZONE_PADDING/2))
        pos_y = randint(ceil(WALL_PADDING_Y + LANDING_ZONE_PADDING/2), floor(WINDOW_HEIGHT - WALL_PADDING_Y - LANDING_ZONE_PADDING/2))
        self.landing_zone = LandingZone(self.zone_surfs, (pos_x, pos_y), self.players, self.landing_zone_sprites, (self.all_sprites, self.entity_sprites, self.landing_zone_sprites), self.zone_dot_surfs, self.all_sprites, self.profiles, self.num_players, self.max_fillings, first)

    def create_highlight(self, player):
        Highlight(self.highlight_surfs[player-1], PROFILE_POS[player-1], (self.all_sprites, self.highlight_sprites))

    def activate_item_select(self):
        self.item_screen.should_fade = 'in'
        self.item_screen.alpha = 0
        for item in self.item_select_sprites:
            item.should_fade = 'in'
            item.alpha = 0

    def update_item_select(self):
        mouse_down = pygame.mouse.get_just_pressed()[0]

        for item in self.item_select_sprites:
            if item.current_surf == 1 and mouse_down:
                self.click_1.play()
                self.item_screen.should_fade = 'out'
                self.item_screen.alpha = 255
                self.current_item = item.type
                for item in self.item_select_sprites:
                    item.should_fade = 'out'
                    item.alpha = 255
                surf = None
                surf = self.garbage_can_surfs[0] if self.current_item == 'garbage' and not surf else surf
                surf = self.toaster_surfs if self.current_item == 'toaster' and not surf else surf
                surf = self.ketchup_surf if self.current_item == 'ketchup' and not surf else surf
                self.item_placer = ItemPlacer(surf, self.current_item, (self.all_sprites), self.players, self.landing_zone, self.item_sprites)
                self.rotate = Rotate(self.rotate_surf, (self.all_sprites), self.item_placer) if self.current_item == 'toaster' else None

    def place_item(self):
        if self.item_placer.tint and pygame.mouse.get_just_pressed()[0]:
            type = self.item_placer.type
            dir = self.item_placer.dir if type == 'toaster' else None
            pos = self.item_placer.rect.center

            toaster = Toaster(self.toaster_surfs[dir], pos, dir, (self.all_sprites, self.item_sprites, self.toaster_sprites)) if type == 'toaster' else None
            garbage = GarbageCan(self.garbage_can_surfs, pos, (self.all_sprites, self.item_sprites)) if type == 'garbage' else None
            ketchup = Ketchup(self.ketchup_surf, pos, (self.all_sprites, self.item_sprites)) if type == 'ketchup' else None

            self.ketchup_place_sounds[randint(0,2)].play() if type == 'ketchup' else None
            self.toaster_set.play() if type == 'toaster' else None
            self.garbage_can_sounds[randint(0, 2)].play() if type == 'garbage' else None

            for player in self.players.values():
                player.ketchups.append(ketchup) if ketchup else None
                player.garbages.append(garbage) if garbage else None
                player.toasters.append(toaster) if toaster else None

            self.phase = 'aim'
            self.item_placer.kill()
            self.rotate.kill() if self.rotate else None

    def toaster_shoot(self):
        for toaster in self.toaster_sprites:
            if toaster.shoot:
                for sound in self.bread_eject_sounds:
                    sound.set_volume(uniform(0.6, 1))
                self.bread_eject_sounds[randint(0, 2)].play()
                toaster.shoot = False
                sodas = [soda for soda in self.sodas.values()]
                Bread(self.bread_surfs[toaster.dir], toaster.pos, toaster.dir, (self.all_sprites, self.bread_sprites), sodas, self.wall_sprites, self.players, self.item_sprites, toaster, self.bread_hit_sounds)
                toaster.bread_left -= 1

    def update_drop(self):
        drop_sprites_num = len(self.drop_sprites.sprites())
        i = 0
        for sprite in self.drop_sprites:
            if sprite.active:
                return
            else:
                i += 1
        
        if i == drop_sprites_num and self.phase == 'dropping':
            self.phase = 'round_end'
            self.players[self.landing_zone.drop_to].fillings += 1 if self.players[self.landing_zone.drop_to].fillings != self.max_fillings else 0
            self.players[self.landing_zone.drop_to].angle = 0
            self.profiles[self.landing_zone.drop_to].update_image()
            for id in range(0, 5):
                Star(self.star_surf, self.players[self.landing_zone.drop_to].rect.center, id, (self.all_sprites))
            for sprite in self.drop_sprites:
                sprite.kill()

            self.star_hum_sounds[(self.players[self.landing_zone.drop_to].fillings)-1].play()
            self.star_final.play() if self.players[self.landing_zone.drop_to].fillings == self.max_fillings else None

            self.round_end_time = pygame.time.get_ticks()

    def tick_entities(self, next_current_player, dt):
        for entity in self.entity_sprites: entity.tick(dt)

        self.next_landing_zone -= 1
        if self.next_landing_zone <= 0:
            if self.landing_zone.drop_to:
                self.phase = 'dropping' 
                type = self.players[self.landing_zone.drop_to].all_fillings[self.players[self.landing_zone.drop_to].fillings]
                Drop(self.burger_surf, self.burger_shadow_surf, self.players[self.landing_zone.drop_to].rect.center, (self.all_sprites, self.drop_sprites), self.star_sounds) if type == 'burger' else None
                Drop(self.cheese_surf, self.cheese_shadow_surf, self.players[self.landing_zone.drop_to].rect.center, (self.all_sprites, self.drop_sprites), self.star_sounds) if type == 'cheese' else None
                Drop(self.lettuce_surf, self.lettuce_shadow_surf, self.players[self.landing_zone.drop_to].rect.center, (self.all_sprites, self.drop_sprites), self.star_sounds) if type == 'lettuce' else None
                Drop(self.tomato_surf, self.tomato_shadow_surf, self.players[self.landing_zone.drop_to].rect.center, (self.all_sprites, self.drop_sprites), self.star_sounds) if type == 'tomato' else None
                Drop(self.pickle_surf, self.pickle_shadow_surf, (self.players[self.landing_zone.drop_to].rect.centerx, self.players[self.landing_zone.drop_to].rect.centery - 20), (self.all_sprites, self.drop_sprites), self.star_sounds, id = 1) if type == 'pickles' else None
                Drop(self.pickle_surf, self.pickle_shadow_surf, (self.players[self.landing_zone.drop_to].rect.centerx + 20, self.players[self.landing_zone.drop_to].rect.centery+15), (self.all_sprites, self.drop_sprites), self.star_sounds, id = 2) if type == 'pickles' else None
                Drop(self.pickle_surf, self.pickle_shadow_surf, (self.players[self.landing_zone.drop_to].rect.centerx - 20, self.players[self.landing_zone.drop_to].rect.centery+20), (self.all_sprites, self.drop_sprites), self.star_sounds, id = 3) if type == 'pickles' else None
            else:
                self.round_end_time = pygame.time.get_ticks()
        else:
            self.phase = 'turning'
            self.turning = True
            self.turn_sprites[next_current_player].active = True
            for highlight in self.highlight_sprites:
                    highlight.kill()
            self.create_highlight(int(next_current_player[-1]))
            self.round_end_time = 0
            
    def change_player(self):
        self.current_player = int(self.current_player[-1]) + 1
        self.current_item = None

        if self.current_player > self.num_of_players:
            self.current_player = 1

        if self.current_player == int(self.starting_player[-1]):
            self.starting_player = int(self.starting_player[-1]) + 1 if not int(self.starting_player[-1]) >= self.num_of_players else 1
            self.current_player = self.starting_player

        self.current_player = 'player' + str(self.current_player)
        self.starting_player = 'player' + str(self.starting_player) if self.starting_player != 'player0' else 'player1'

        self.you = You(self.you_surfs[self.current_player], (self.players[self.current_player].rect.centerx, self.players[self.current_player].rect.centery - 85), (self.all_sprites))

    def change_phase(self, phase, next_current_player, dt):
        if phase == 'launch':
            self.phase = 'launch'
            return

        if self.phase == 'launch' and self.round_end_time == 0:
            i = 0
            for key in self.players:
                if self.players[key].velocity:
                    return
            for bread in self.bread_sprites:
                return
            for toaster in self.toaster_sprites:
                if toaster.bread_left:
                    return
            for player in self.players:
                self.players[player].initial_pos = pygame.Vector2(self.players[player].rect.center)
            for toaster in self.toaster_sprites:
                toaster.animate = False
                toaster.shoot = False
                toaster.shoot_time = 0
            for bread in self.bread_sprites:
                bread.kill()
            self.tick_entities(next_current_player, dt)
            return
        
        if self.phase == 'item select' and self.item_screen.should_fade == False:
            self.phase = 'item placement'

    def display_win_screen_text(self, dt):
        self.rounds_alpha += MAIN_MENU_FADE_SPD * dt if self.rounds_alpha < 255 else 0
        self.rounds_alpha = 255 if self.rounds_alpha > 255 else self.rounds_alpha
        original_score_surf = self.rounds_font.render(str(self.total_rounds), True, 'white')
        rounds_surf = original_score_surf.copy()
        rounds_surf.fill((255, 255, 255, self.rounds_alpha), None, pygame.BLEND_RGBA_MULT)
        rounds_rect = rounds_surf.get_frect(center = (WINDOW_WIDTH - 490, WINDOW_HEIGHT - 148))
        self.display_surface.blit(rounds_surf, rounds_rect)

        self.time_left = round((self.win_screen_dur - (pygame.time.get_ticks() - self.win_screen_time))/1000)
        self.time_left = 0 if self.time_left <= 0 else self.time_left
        original_time_surf = self.time_font.render(str(self.time_left), True, 'white')
        time_surf = original_time_surf.copy()
        time_rect = time_surf.get_frect(center = (WINDOW_WIDTH - 50, WINDOW_HEIGHT - 50))
        self.display_surface.blit(time_surf, time_rect) if self.time_left <= 10 else None
        if self.time_left <= 4 and not self.music_fade_out:
            mixer.music.fadeout(4500)
            self.music_fade_out = True
            self.play_music = False

    def audio_imports(self):
        self.click_1 = mixer.Sound(join('audio', 'clicks', 'click 7.wav'))

        ketchup_1 = mixer.Sound(join('audio', 'game', 'ketchup 1.mp3'))
        ketchup_2 = mixer.Sound(join('audio', 'game', 'ketchup 2.mp3'))
        ketchup_3 = mixer.Sound(join('audio', 'game', 'ketchup 3.mp3'))
        self.ketchup_place_sounds = [ketchup_1, ketchup_2, ketchup_3]
        ketchup_stuck_1 = mixer.Sound(join('audio', 'game', 'ketchup stuck 1.mp3'))
        ketchup_stuck_2 = mixer.Sound(join('audio', 'game', 'ketchup stuck 2.mp3'))
        ketchup_stuck_3 = mixer.Sound(join('audio', 'game', 'ketchup stuck 3.mp3'))
        ketchup_stuck_4 = mixer.Sound(join('audio', 'game', 'ketchup stuck 4.mp3'))
        ketchup_stuck_5 = mixer.Sound(join('audio', 'game', 'ketchup stuck 5.mp3'))
        ketchup_stuck_6 = mixer.Sound(join('audio', 'game', 'ketchup stuck 6.mp3'))
        ketchup_stuck_7 = mixer.Sound(join('audio', 'game', 'ketchup stuck 7.mp3'))
        ketchup_stuck_8 = mixer.Sound(join('audio', 'game', 'ketchup stuck 8.mp3'))
        self.ketchup_stucks_sounds = [ketchup_stuck_1, ketchup_stuck_2, ketchup_stuck_3, ketchup_stuck_4, ketchup_stuck_5, ketchup_stuck_6, ketchup_stuck_7, ketchup_stuck_8]

        bread_eject_1 = mixer.Sound(join('audio', 'game', 'bread eject 1.mp3'))
        bread_eject_2 = mixer.Sound(join('audio', 'game', 'bread eject 2.mp3'))
        bread_eject_3 = mixer.Sound(join('audio', 'game', 'bread eject 3.mp3'))
        self.bread_eject_sounds = [bread_eject_1, bread_eject_2, bread_eject_3]
        self.toaster_set = mixer.Sound(join('audio', 'game', 'toaster set.mp3'))
        bread_hit_1 = mixer.Sound(join('audio', 'game', 'bread hit 1.mp3'))
        bread_hit_2 = mixer.Sound(join('audio', 'game', 'bread hit 2.mp3'))
        bread_hit_3 = mixer.Sound(join('audio', 'game', 'bread hit 3.mp3'))
        bread_hit_4 = mixer.Sound(join('audio', 'game', 'bread hit 4.mp3'))
        bread_hit_1.set_volume(1)
        bread_hit_2.set_volume(1)
        bread_hit_3.set_volume(0.8)
        bread_hit_4.set_volume(1)
        self.bread_hit_sounds = [bread_hit_1, bread_hit_2]

        garbage_can_1 = mixer.Sound(join('audio', 'game', 'garbage can 1.mp3'))
        garbage_can_2 = mixer.Sound(join('audio', 'game', 'garbage can 2 v2.mp3'))
        garbage_can_3 = mixer.Sound(join('audio', 'game', 'garbage can 3 v2.mp3'))
        self.garbage_can_sounds = [garbage_can_1, garbage_can_2, garbage_can_3]

        star_break_1 = mixer.Sound(join('audio', 'game', 'star 1.wav'))
        star_break_2 = mixer.Sound(join('audio', 'game', 'star 2.wav'))
        star_break_3 = mixer.Sound(join('audio', 'game', 'star 3.wav'))
        star_hum_1 = mixer.Sound(join('audio', 'game', 'star collect 1.mp3'))
        star_hum_2 = mixer.Sound(join('audio', 'game', 'star collect 2.mp3'))
        star_hum_3 = mixer.Sound(join('audio', 'game', 'star collect 3.mp3'))
        star_hum_4 = mixer.Sound(join('audio', 'game', 'star collect 4.mp3'))
        star_hum_5 = mixer.Sound(join('audio', 'game', 'star collect 5.mp3'))
        star_break_1.set_volume(0.8)
        star_break_2.set_volume(0.8)
        star_break_3.set_volume(0.8)
        star_hum_1.set_volume(1)
        star_hum_2.set_volume(1)
        star_hum_3.set_volume(1)
        star_hum_4.set_volume(1)
        star_hum_5.set_volume(1)
        self.star_sounds = [star_break_1, star_break_2, star_break_3]
        self.star_hum_sounds = [star_hum_1, star_hum_2, star_hum_3, star_hum_4, star_hum_5]
        self.star_final = mixer.Sound(join('audio', 'game', 'star final.wav'))
        self.star_final.set_volume(0.3)

        bun_hit_1 = mixer.Sound(join('audio', 'game', 'bun hit 1.mp3'))
        bun_hit_2 = mixer.Sound(join('audio', 'game', 'bun hit 2.mp3'))
        bun_hit_3 = mixer.Sound(join('audio', 'game', 'bun hit 3.mp3'))
        bun_hit_4 = mixer.Sound(join('audio', 'game', 'bun hit 4.mp3'))
        bun_hit_5 = mixer.Sound(join('audio', 'game', 'bun hit 5.mp3'))
        self.bun_hit_sounds = [bun_hit_1, bun_hit_2, bun_hit_3, bun_hit_4, bun_hit_5]

    def manage_music(self):
        if not mixer.music.get_busy() and self.play_music:
            if self.music == 1:
                print('music 2')
                self.music = 2
                mixer.music.load(join('audio', 'music', 'game music 2.mp3'))
            else:
                print('music 1')
                self.music = 1
                mixer.music.load(join('audio', 'music', 'game music 1.mp3'))
                
                
            mixer.music.set_volume(0.3)
            mixer.music.play()
            mixer.music.set_pos(79) if self.music == 1 else None

    def setup(self):
        # image imports
            # players
        player1_surf = import_image('images', 'buns', 'LB', 'LB')
        player2_surf = import_image('images', 'buns', 'DB', 'DB')
        player3_surf = import_image('images', 'buns', 'LSB', 'LSB')
        player4_surf = import_image('images', 'buns', 'DSB', 'DSB')
        self.player_surfs = [player1_surf, player2_surf, player3_surf, player4_surf]

            # LB Fillings
        burger = import_image('images', 'buns', 'LB', 'burger')
        burgercheese = import_image('images', 'buns', 'LB', 'burgercheese')
        burgerlettuce = import_image('images', 'buns', 'LB', 'burgerlettuce')
        burgertomato = import_image('images', 'buns', 'LB', 'burgertomato')
        burgerpickles = import_image('images', 'buns', 'LB', 'burgerpickles')
        burgercheeselettuce = import_image('images', 'buns', 'LB', 'burgercheeselettuce')
        burgercheesetomato = import_image('images', 'buns', 'LB', 'burgercheesetomato')
        burgercheesepickles = import_image('images', 'buns', 'LB', 'burgercheesepickles')
        burgerlettucetomato = import_image('images', 'buns', 'LB', 'burgerlettucetomato')
        burgerlettucepickles = import_image('images', 'buns', 'LB', 'burgerlettucepickles')
        burgertomatopickles = import_image('images', 'buns', 'LB', 'burgertomatopickles')
        burgercheeselettucetomato = import_image('images', 'buns', 'LB', 'burgercheeselettucetomato')
        burgercheeselettucepickles = import_image('images', 'buns', 'LB', 'burgercheeselettucepickles')
        burgercheesetomatopickles = import_image('images', 'buns', 'LB', 'burgercheesetomatopickles')
        burgerlettucetomatopickles = import_image('images', 'buns', 'LB', 'burgerlettucetomatopickles')
        burgercheeselettucetomatopickles = import_image('images', 'buns', 'LB', 'burgercheeselettucetomatopickles')
        player1_filling_surfs = {'burger': burger,
                                 'burgercheese': burgercheese,
                                 'burgerlettuce': burgerlettuce,
                                 'burgertomato': burgertomato,
                                 'burgerpickles': burgerpickles,
                                 'burgercheeselettuce': burgercheeselettuce,
                                 'burgercheesetomato': burgercheesetomato,
                                 'burgercheesepickles': burgercheesepickles,
                                 'burgerlettucetomato': burgerlettucetomato,
                                 'burgerlettucepickles': burgerlettucepickles,
                                 'burgertomatopickles': burgertomatopickles,
                                 'burgercheeselettucetomato': burgercheeselettucetomato,
                                 'burgercheeselettucepickles': burgercheeselettucepickles,
                                 'burgercheesetomatopickles': burgercheesetomatopickles,
                                 'burgerlettucetomatopickles': burgerlettucetomatopickles,
                                 'burgercheeselettucetomatopickles': burgercheeselettucetomatopickles
                                }
        
            # LSB Fillings
        burger = import_image('images', 'buns', 'LSB', 'burger')
        burgercheese = import_image('images', 'buns', 'LSB', 'burgercheese')
        burgerlettuce = import_image('images', 'buns', 'LSB', 'burgerlettuce')
        burgertomato = import_image('images', 'buns', 'LSB', 'burgertomato')
        burgerpickles = import_image('images', 'buns', 'LSB', 'burgerpickles')
        burgercheeselettuce = import_image('images', 'buns', 'LSB', 'burgercheeselettuce')
        burgercheesetomato = import_image('images', 'buns', 'LSB', 'burgercheesetomato')
        burgercheesepickles = import_image('images', 'buns', 'LSB', 'burgercheesepickles')
        burgerlettucetomato = import_image('images', 'buns', 'LSB', 'burgerlettucetomato')
        burgerlettucepickles = import_image('images', 'buns', 'LSB', 'burgerlettucepickles')
        burgertomatopickles = import_image('images', 'buns', 'LSB', 'burgertomatopickles')
        burgercheeselettucetomato = import_image('images', 'buns', 'LSB', 'burgercheeselettucetomato')
        burgercheeselettucepickles = import_image('images', 'buns', 'LSB', 'burgercheeselettucepickles')
        burgercheesetomatopickles = import_image('images', 'buns', 'LSB', 'burgercheesetomatopickles')
        burgerlettucetomatopickles = import_image('images', 'buns', 'LSB', 'burgerlettucetomatopickles')
        burgercheeselettucetomatopickles = import_image('images', 'buns', 'LSB', 'burgercheeselettucetomatopickles')
        player3_filling_surfs = {'burger': burger,
                                 'burgercheese': burgercheese,
                                 'burgerlettuce': burgerlettuce,
                                 'burgertomato': burgertomato,
                                 'burgerpickles': burgerpickles,
                                 'burgercheeselettuce': burgercheeselettuce,
                                 'burgercheesetomato': burgercheesetomato,
                                 'burgercheesepickles': burgercheesepickles,
                                 'burgerlettucetomato': burgerlettucetomato,
                                 'burgerlettucepickles': burgerlettucepickles,
                                 'burgertomatopickles': burgertomatopickles,
                                 'burgercheeselettucetomato': burgercheeselettucetomato,
                                 'burgercheeselettucepickles': burgercheeselettucepickles,
                                 'burgercheesetomatopickles': burgercheesetomatopickles,
                                 'burgerlettucetomatopickles': burgerlettucetomatopickles,
                                 'burgercheeselettucetomatopickles': burgercheeselettucetomatopickles
                                }
        
            # DB Fillings
        burger = import_image('images', 'buns', 'DB', 'burger')
        burgercheese = import_image('images', 'buns', 'DB', 'burgercheese')
        burgerlettuce = import_image('images', 'buns', 'DB', 'burgerlettuce')
        burgertomato = import_image('images', 'buns', 'DB', 'burgertomato')
        burgerpickles = import_image('images', 'buns', 'DB', 'burgerpickles')
        burgercheeselettuce = import_image('images', 'buns', 'DB', 'burgercheeselettuce')
        burgercheesetomato = import_image('images', 'buns', 'DB', 'burgercheesetomato')
        burgercheesepickles = import_image('images', 'buns', 'DB', 'burgercheesepickles')
        burgerlettucetomato = import_image('images', 'buns', 'DB', 'burgerlettucetomato')
        burgerlettucepickles = import_image('images', 'buns', 'DB', 'burgerlettucepickles')
        burgertomatopickles = import_image('images', 'buns', 'DB', 'burgertomatopickles')
        burgercheeselettucetomato = import_image('images', 'buns', 'DB', 'burgercheeselettucetomato')
        burgercheeselettucepickles = import_image('images', 'buns', 'DB', 'burgercheeselettucepickles')
        burgercheesetomatopickles = import_image('images', 'buns', 'DB', 'burgercheesetomatopickles')
        burgerlettucetomatopickles = import_image('images', 'buns', 'DB', 'burgerlettucetomatopickles')
        burgercheeselettucetomatopickles = import_image('images', 'buns', 'DB', 'burgercheeselettucetomatopickles')
        player2_filling_surfs = {'burger': burger,
                                 'burgercheese': burgercheese,
                                 'burgerlettuce': burgerlettuce,
                                 'burgertomato': burgertomato,
                                 'burgerpickles': burgerpickles,
                                 'burgercheeselettuce': burgercheeselettuce,
                                 'burgercheesetomato': burgercheesetomato,
                                 'burgercheesepickles': burgercheesepickles,
                                 'burgerlettucetomato': burgerlettucetomato,
                                 'burgerlettucepickles': burgerlettucepickles,
                                 'burgertomatopickles': burgertomatopickles,
                                 'burgercheeselettucetomato': burgercheeselettucetomato,
                                 'burgercheeselettucepickles': burgercheeselettucepickles,
                                 'burgercheesetomatopickles': burgercheesetomatopickles,
                                 'burgerlettucetomatopickles': burgerlettucetomatopickles,
                                 'burgercheeselettucetomatopickles': burgercheeselettucetomatopickles
                                }
        
            # DSB Fillings
        burger = import_image('images', 'buns', 'DSB', 'burger')
        burgercheese = import_image('images', 'buns', 'DSB', 'burgercheese')
        burgerlettuce = import_image('images', 'buns', 'DSB', 'burgerlettuce')
        burgertomato = import_image('images', 'buns', 'DSB', 'burgertomato')
        burgerpickles = import_image('images', 'buns', 'DSB', 'burgerpickles')
        burgercheeselettuce = import_image('images', 'buns', 'DSB', 'burgercheeselettuce')
        burgercheesetomato = import_image('images', 'buns', 'DSB', 'burgercheesetomato')
        burgercheesepickles = import_image('images', 'buns', 'DSB', 'burgercheesepickles')
        burgerlettucetomato = import_image('images', 'buns', 'DSB', 'burgerlettucetomato')
        burgerlettucepickles = import_image('images', 'buns', 'DSB', 'burgerlettucepickles')
        burgertomatopickles = import_image('images', 'buns', 'DSB', 'burgertomatopickles')
        burgercheeselettucetomato = import_image('images', 'buns', 'DSB', 'burgercheeselettucetomato')
        burgercheeselettucepickles = import_image('images', 'buns', 'DSB', 'burgercheeselettucepickles')
        burgercheesetomatopickles = import_image('images', 'buns', 'DSB', 'burgercheesetomatopickles')
        burgerlettucetomatopickles = import_image('images', 'buns', 'DSB', 'burgerlettucetomatopickles')
        burgercheeselettucetomatopickles = import_image('images', 'buns', 'DSB', 'burgercheeselettucetomatopickles')
        player4_filling_surfs = {'burger': burger,
                                 'burgercheese': burgercheese,
                                 'burgerlettuce': burgerlettuce,
                                 'burgertomato': burgertomato,
                                 'burgerpickles': burgerpickles,
                                 'burgercheeselettuce': burgercheeselettuce,
                                 'burgercheesetomato': burgercheesetomato,
                                 'burgercheesepickles': burgercheesepickles,
                                 'burgerlettucetomato': burgerlettucetomato,
                                 'burgerlettucepickles': burgerlettucepickles,
                                 'burgertomatopickles': burgertomatopickles,
                                 'burgercheeselettucetomato': burgercheeselettucetomato,
                                 'burgercheeselettucepickles': burgercheeselettucepickles,
                                 'burgercheesetomatopickles': burgercheesetomatopickles,
                                 'burgerlettucetomatopickles': burgerlettucetomatopickles,
                                 'burgercheeselettucetomatopickles': burgercheeselettucetomatopickles
                                }

        self.player_filling_surfs = [player1_filling_surfs, player2_filling_surfs, player3_filling_surfs, player4_filling_surfs]
            # landing zones
                # zones
        empty_zone = import_image('images', 'landing zones', 'zones', 'Empty Zone')
        LB_zone = import_image('images', 'landing zones', 'zones', 'LB Zone')
        LSB_zone = import_image('images', 'landing zones', 'zones', 'LSB Zone')
        DB_zone = import_image('images', 'landing zones', 'zones', 'DB Zone')
        DSB_zone = import_image('images', 'landing zones', 'zones', 'DSB Zone')
        self.zone_surfs = {'empty':empty_zone, 'player1':LB_zone, 'player3':LSB_zone, 'player2':DB_zone, 'player4':DSB_zone}
                # dots
        empty_zone_dots = import_image('images', 'landing zones', 'dots', 'Empty Zone Dots')
        LB_zone_dots = import_image('images', 'landing zones', 'dots', 'LB Zone Dots')
        LSB_zone_dots = import_image('images', 'landing zones', 'dots', 'LSB Zone Dots')
        DB_zone_dots = import_image('images', 'landing zones', 'dots', 'DB Zone Dots')
        DSB_zone_dots = import_image('images', 'landing zones', 'dots', 'DSB Zone Dots')
        self.zone_dot_surfs = {'empty':empty_zone_dots, 'player1':LB_zone_dots, 'player3':LSB_zone_dots, 'player2':DB_zone_dots, 'player4':DSB_zone_dots}
            # pointers
                # pointers
        self.pointer_surfs = import_folder('images', 'pointers', 'pointers')
                # aimers
        self.aimer_surfs = import_folder('images', 'pointers', 'aimers')
            # profiles
                # profiles
        LB_profiles = import_folder('images', 'profiles', 'profiles', 'LB')
        LSB_profiles = import_folder('images', 'profiles', 'profiles', 'LSB')
        DB_profiles = import_folder('images', 'profiles', 'profiles', 'DB')
        DSB_profiles = import_folder('images', 'profiles', 'profiles', 'DSB')
        self.profile_surfs = [LB_profiles, DB_profiles, LSB_profiles, DSB_profiles]
                # highlights
        LB_HL = import_image('images', 'profiles', 'highlights', 'LB HL')
        LSB_HL = import_image('images', 'profiles', 'highlights', 'LSB HL')
        DB_HL = import_image('images', 'profiles', 'highlights', 'DB HL')
        DSB_HL = import_image('images', 'profiles', 'highlights', 'DSB HL')
        self.highlight_surfs = [LB_HL, DB_HL, LSB_HL, DSB_HL]
            # tiles
        random_tile = randint(0, len(TILES)-1)
        tile = TILES[random_tile] + ' tile' if not TILE_OVERIDE else TILE + ' tile'
        tile_format = TILE_TYPE if TILE_OVERIDE else TILE_TYPES[random_tile]
        self.tile_surf = import_image('images', 'tiles', tile, format = tile_format)
            # bun shadow
        self.bun_shadow_surf = import_image('images', 'buns', 'shadow', format = 'png')
            # arena
        self.arena_walls = import_image('images', 'arena', 'arena walls 2')
        arena_soda1 = import_image('images', 'arena', 'soda1')
        arena_soda2 = import_image('images', 'arena', 'soda2')
        arena_soda3 = import_image('images', 'arena', 'soda3')
        arena_soda4 = import_image('images', 'arena', 'soda4')
        self.soda_surfs = [arena_soda1, arena_soda2, arena_soda3, arena_soda4]
            # turns
        self.blue_turn_surf = import_image('images', 'turn indicators', 'blue turn', format = 'png')
        self.green_turn_surf = import_image('images', 'turn indicators', 'green turn', format = 'png')
        self.yellow_turn_surf = import_image('images', 'turn indicators', 'yellow turn', format = 'png')
        self.red_turn_surf = import_image('images', 'turn indicators', 'red turn', format = 'png')
        blue_you_surf = import_image('images', 'turn indicators', 'blue you', format = 'png')
        green_you_surf = import_image('images', 'turn indicators', 'green you', format = 'png')
        yellow_you_surf = import_image('images', 'turn indicators', 'yellow you', format = 'png')
        red_you_surf = import_image('images', 'turn indicators', 'red you', format = 'png')
        self.you_surfs = {'player1': blue_you_surf, 'player2': green_you_surf, 'player3': yellow_you_surf, 'player4': red_you_surf}
            # items
        self.item_screen_surf = import_image('images', 'items', 'item screen', format = 'png')
        toaster_unselected_surf = import_image('images', 'items', 'toaster unselected', format = 'png')
        toaster_selected_surf = import_image('images', 'items', 'toaster selected', format = 'png')
        garbage_unselected_surf = import_image('images', 'items', 'garbage unselected', format = 'png')
        garbage_selected_surf = import_image('images', 'items', 'garbage selected', format = 'png')
        ketchup_unselected_surf = import_image('images', 'items', 'ketchup unselected', format = 'png')
        ketchup_selected_surf = import_image('images', 'items', 'ketchup selected', format = 'png')
        self.item_select_surfs = [[toaster_unselected_surf, toaster_selected_surf], [garbage_unselected_surf, garbage_selected_surf], [ketchup_unselected_surf, ketchup_selected_surf]]
        self.garbage_can_surfs = import_folder('images', 'items', 'garbage')
        self.ketchup_surf = import_image('images', 'items', 'ketchup', format = 'png')
        self.toaster_surfs = [
                            import_folder('images', 'items', 'toaster', 'up'),
                            import_folder('images', 'items', 'toaster', 'right'),
                            import_folder('images', 'items', 'toaster', 'down'),
                            import_folder('images', 'items', 'toaster', 'left')
                            ]
        self.bread_surfs = import_folder('images', 'items', 'bread')
        self.rotate_surf = import_image('images', 'items', 'rotate', format = 'png')
            # drop surfs
        self.burger_surf = import_image('images', 'drop fillings', 'burger', format = 'png')
        self.cheese_surf = import_image('images', 'drop fillings', 'cheese', format = 'png')
        self.lettuce_surf = import_image('images', 'drop fillings', 'lettuce', format = 'png')
        self.tomato_surf = import_image('images', 'drop fillings', 'tomato', format = 'png')
        self.pickle_surf = import_image('images', 'drop fillings', 'pickle', format = 'png')
        self.burger_shadow_surf = import_image('images', 'drop fillings', 'burger shadow', format = 'png')
        self.cheese_shadow_surf = import_image('images', 'drop fillings', 'cheese shadow', format = 'png')
        self.lettuce_shadow_surf = import_image('images', 'drop fillings', 'lettuce shadow', format = 'png')
        self.tomato_shadow_surf = import_image('images', 'drop fillings', 'tomato shadow', format = 'png')
        self.pickle_shadow_surf = import_image('images', 'drop fillings', 'pickle shadow', format = 'png')
        self.star_surf = import_image('images', 'drop fillings', 'star', format = 'png')

            # Blue win screen
        burger = import_image('images', 'win screens', 'blue', 'burger', format = 'png')
        burgercheese = import_image('images', 'win screens', 'blue', 'burgercheese', format = 'png')
        burgerlettuce = import_image('images', 'win screens', 'blue', 'burgerlettuce', format = 'png')
        burgertomato = import_image('images', 'win screens', 'blue', 'burgertomato', format = 'png')
        burgerpickles = import_image('images', 'win screens', 'blue', 'burgerpickles', format = 'png')
        burgercheeselettuce = import_image('images', 'win screens', 'blue', 'burgercheeselettuce', format = 'png')
        burgercheesetomato = import_image('images', 'win screens', 'blue', 'burgercheesetomato', format = 'png')
        burgercheesepickles = import_image('images', 'win screens', 'blue', 'burgercheesepickles', format = 'png')
        burgerlettucetomato = import_image('images', 'win screens', 'blue', 'burgerlettucetomato', format = 'png')
        burgerlettucepickles = import_image('images', 'win screens', 'blue', 'burgerlettucepickles', format = 'png')
        burgertomatopickles = import_image('images', 'win screens', 'blue', 'burgertomatopickles', format = 'png')
        burgercheeselettucetomato = import_image('images', 'win screens', 'blue', 'burgercheeselettucetomato', format = 'png')
        burgercheeselettucepickles = import_image('images', 'win screens', 'blue', 'burgercheeselettucepickles', format = 'png')
        burgercheesetomatopickles = import_image('images', 'win screens', 'blue', 'burgercheesetomatopickles', format = 'png')
        burgerlettucetomatopickles = import_image('images', 'win screens', 'blue', 'burgerlettucetomatopickles', format = 'png')
        burgercheeselettucetomatopickles = import_image('images', 'win screens', 'blue', 'burgercheeselettucetomatopickles', format = 'png')
        blue_win_surfs = {'burger': burger,
                                 'burgercheese': burgercheese,
                                 'burgerlettuce': burgerlettuce,
                                 'burgertomato': burgertomato,
                                 'burgerpickles': burgerpickles,
                                 'burgercheeselettuce': burgercheeselettuce,
                                 'burgercheesetomato': burgercheesetomato,
                                 'burgercheesepickles': burgercheesepickles,
                                 'burgerlettucetomato': burgerlettucetomato,
                                 'burgerlettucepickles': burgerlettucepickles,
                                 'burgertomatopickles': burgertomatopickles,
                                 'burgercheeselettucetomato': burgercheeselettucetomato,
                                 'burgercheeselettucepickles': burgercheeselettucepickles,
                                 'burgercheesetomatopickles': burgercheesetomatopickles,
                                 'burgerlettucetomatopickles': burgerlettucetomatopickles,
                                 'burgercheeselettucetomatopickles': burgercheeselettucetomatopickles
                                }
        # Green win screen
        burger = import_image('images', 'win screens', 'green', 'burger', format = 'png')
        burgercheese = import_image('images', 'win screens', 'green', 'burgercheese', format = 'png')
        burgerlettuce = import_image('images', 'win screens', 'green', 'burgerlettuce', format = 'png')
        burgertomato = import_image('images', 'win screens', 'green', 'burgertomato', format = 'png')
        burgerpickles = import_image('images', 'win screens', 'green', 'burgerpickles', format = 'png')
        burgercheeselettuce = import_image('images', 'win screens', 'green', 'burgercheeselettuce', format = 'png')
        burgercheesetomato = import_image('images', 'win screens', 'green', 'burgercheesetomato', format = 'png')
        burgercheesepickles = import_image('images', 'win screens', 'green', 'burgercheesepickles', format = 'png')
        burgerlettucetomato = import_image('images', 'win screens', 'green', 'burgerlettucetomato', format = 'png')
        burgerlettucepickles = import_image('images', 'win screens', 'green', 'burgerlettucepickles', format = 'png')
        burgertomatopickles = import_image('images', 'win screens', 'green', 'burgertomatopickles', format = 'png')
        burgercheeselettucetomato = import_image('images', 'win screens', 'green', 'burgercheeselettucetomato', format = 'png')
        burgercheeselettucepickles = import_image('images', 'win screens', 'green', 'burgercheeselettucepickles', format = 'png')
        burgercheesetomatopickles = import_image('images', 'win screens', 'green', 'burgercheesetomatopickles', format = 'png')
        burgerlettucetomatopickles = import_image('images', 'win screens', 'green', 'burgerlettucetomatopickles', format = 'png')
        burgercheeselettucetomatopickles = import_image('images', 'win screens', 'green', 'burgercheeselettucetomatopickles', format = 'png')
        green_win_surfs = {'burger': burger,
                                 'burgercheese': burgercheese,
                                 'burgerlettuce': burgerlettuce,
                                 'burgertomato': burgertomato,
                                 'burgerpickles': burgerpickles,
                                 'burgercheeselettuce': burgercheeselettuce,
                                 'burgercheesetomato': burgercheesetomato,
                                 'burgercheesepickles': burgercheesepickles,
                                 'burgerlettucetomato': burgerlettucetomato,
                                 'burgerlettucepickles': burgerlettucepickles,
                                 'burgertomatopickles': burgertomatopickles,
                                 'burgercheeselettucetomato': burgercheeselettucetomato,
                                 'burgercheeselettucepickles': burgercheeselettucepickles,
                                 'burgercheesetomatopickles': burgercheesetomatopickles,
                                 'burgerlettucetomatopickles': burgerlettucetomatopickles,
                                 'burgercheeselettucetomatopickles': burgercheeselettucetomatopickles
                                }
        # Yellow win screen
        burger = import_image('images', 'win screens', 'yellow', 'burger', format = 'png')
        burgercheese = import_image('images', 'win screens', 'yellow', 'burgercheese', format = 'png')
        burgerlettuce = import_image('images', 'win screens', 'yellow', 'burgerlettuce', format = 'png')
        burgertomato = import_image('images', 'win screens', 'yellow', 'burgertomato', format = 'png')
        burgerpickles = import_image('images', 'win screens', 'yellow', 'burgerpickles', format = 'png')
        burgercheeselettuce = import_image('images', 'win screens', 'yellow', 'burgercheeselettuce', format = 'png')
        burgercheesetomato = import_image('images', 'win screens', 'yellow', 'burgercheesetomato', format = 'png')
        burgercheesepickles = import_image('images', 'win screens', 'yellow', 'burgercheesepickles', format = 'png')
        burgerlettucetomato = import_image('images', 'win screens', 'yellow', 'burgerlettucetomato', format = 'png')
        burgerlettucepickles = import_image('images', 'win screens', 'yellow', 'burgerlettucepickles', format = 'png')
        burgertomatopickles = import_image('images', 'win screens', 'yellow', 'burgertomatopickles', format = 'png')
        burgercheeselettucetomato = import_image('images', 'win screens', 'yellow', 'burgercheeselettucetomato', format = 'png')
        burgercheeselettucepickles = import_image('images', 'win screens', 'yellow', 'burgercheeselettucepickles', format = 'png')
        burgercheesetomatopickles = import_image('images', 'win screens', 'yellow', 'burgercheesetomatopickles', format = 'png')
        burgerlettucetomatopickles = import_image('images', 'win screens', 'yellow', 'burgerlettucetomatopickles', format = 'png')
        burgercheeselettucetomatopickles = import_image('images', 'win screens', 'yellow', 'burgercheeselettucetomatopickles', format = 'png')
        yellow_win_surfs = {'burger': burger,
                                 'burgercheese': burgercheese,
                                 'burgerlettuce': burgerlettuce,
                                 'burgertomato': burgertomato,
                                 'burgerpickles': burgerpickles,
                                 'burgercheeselettuce': burgercheeselettuce,
                                 'burgercheesetomato': burgercheesetomato,
                                 'burgercheesepickles': burgercheesepickles,
                                 'burgerlettucetomato': burgerlettucetomato,
                                 'burgerlettucepickles': burgerlettucepickles,
                                 'burgertomatopickles': burgertomatopickles,
                                 'burgercheeselettucetomato': burgercheeselettucetomato,
                                 'burgercheeselettucepickles': burgercheeselettucepickles,
                                 'burgercheesetomatopickles': burgercheesetomatopickles,
                                 'burgerlettucetomatopickles': burgerlettucetomatopickles,
                                 'burgercheeselettucetomatopickles': burgercheeselettucetomatopickles
                                }
        # Red win screen
        burger = import_image('images', 'win screens', 'red', 'burger', format = 'png')
        burgercheese = import_image('images', 'win screens', 'red', 'burgercheese', format = 'png')
        burgerlettuce = import_image('images', 'win screens', 'red', 'burgerlettuce', format = 'png')
        burgertomato = import_image('images', 'win screens', 'red', 'burgertomato', format = 'png')
        burgerpickles = import_image('images', 'win screens', 'red', 'burgerpickles', format = 'png')
        burgercheeselettuce = import_image('images', 'win screens', 'red', 'burgercheeselettuce', format = 'png')
        burgercheesetomato = import_image('images', 'win screens', 'red', 'burgercheesetomato', format = 'png')
        burgercheesepickles = import_image('images', 'win screens', 'red', 'burgercheesepickles', format = 'png')
        burgerlettucetomato = import_image('images', 'win screens', 'red', 'burgerlettucetomato', format = 'png')
        burgerlettucepickles = import_image('images', 'win screens', 'red', 'burgerlettucepickles', format = 'png')
        burgertomatopickles = import_image('images', 'win screens', 'red', 'burgertomatopickles', format = 'png')
        burgercheeselettucetomato = import_image('images', 'win screens', 'red', 'burgercheeselettucetomato', format = 'png')
        burgercheeselettucepickles = import_image('images', 'win screens', 'red', 'burgercheeselettucepickles', format = 'png')
        burgercheesetomatopickles = import_image('images', 'win screens', 'red', 'burgercheesetomatopickles', format = 'png')
        burgerlettucetomatopickles = import_image('images', 'win screens', 'red', 'burgerlettucetomatopickles', format = 'png')
        burgercheeselettucetomatopickles = import_image('images', 'win screens', 'red', 'burgercheeselettucetomatopickles', format = 'png')
        red_win_surfs = {'burger': burger,
                                 'burgercheese': burgercheese,
                                 'burgerlettuce': burgerlettuce,
                                 'burgertomato': burgertomato,
                                 'burgerpickles': burgerpickles,
                                 'burgercheeselettuce': burgercheeselettuce,
                                 'burgercheesetomato': burgercheesetomato,
                                 'burgercheesepickles': burgercheesepickles,
                                 'burgerlettucetomato': burgerlettucetomato,
                                 'burgerlettucepickles': burgerlettucepickles,
                                 'burgertomatopickles': burgertomatopickles,
                                 'burgercheeselettucetomato': burgercheeselettucetomato,
                                 'burgercheeselettucepickles': burgercheeselettucepickles,
                                 'burgercheesetomatopickles': burgercheesetomatopickles,
                                 'burgerlettucetomatopickles': burgerlettucetomatopickles,
                                 'burgercheeselettucetomatopickles': burgercheeselettucetomatopickles
                                }
        
        self.win_screen_surfs = {'player1': blue_win_surfs, 'player2': green_win_surfs, 'player3': yellow_win_surfs, 'player4': red_win_surfs}

        
        # tiles
        for i in range(0, TILE_NUM):
            Tile(self.tile_surf, (((i%NUM_TILES_WIDTH)*BG_TILE_SIZE) + TILE_OFFSET_X, ((floor((i)/NUM_TILES_WIDTH))*BG_TILE_SIZE) + TILE_OFFSET_Y), (self.all_sprites, self.tile_sprites))

        # arena
            # walls
        Arena(self.arena_walls, (WINDOW_WIDTH/2, WINDOW_HEIGHT/2), (WALL_OFFSET_X, WALL_OFFSET_Y), WALL_SCALE, self.all_sprites)
            # sodas
        for soda in range(1, 5):
            key = 'soda' + str(soda)
            value = Soda(self.soda_surfs[soda-1], (SODA_POS_X[soda-1], SODA_POS_Y[soda-1]), SODA_SCALE, self.all_sprites)
            self.sodas[key] = value

        # players + shadows
        for player in range(1, self.num_of_players + 1):
            id = player
            # players
            key = 'player' + str(player)
            value = Player(self.player_surfs[player - 1], PLAYER_SPAWNS[player],
                             (self.all_sprites, self.player_sprites),
                             self.collision_sprites, self.players, self.sodas, self.player_filling_surfs[id-1], id, self.filling_order_by_name, self.ketchup_stucks_sounds, self.garbage_can_sounds, self.bun_hit_sounds)
            self.players[key] = value
            
            # shadows
            value = BunShadow(self.bun_shadow_surf, self.players[key].rect.center,
                             self.all_sprites,
                             self.collision_sprites, self.players[key], self.players, self.sodas, self.player_filling_surfs, id)
            self.shadows[key] = value  
            
            # profiles
            value = Profile(self.profile_surfs[player-1], PROFILE_POS[player-1], (self.all_sprites, self.profile_sprites), self.players[key], self.filling_num_order)
            self.profiles[key] = value
        self.all_sprites.players = self.players
        self.all_sprites.max_fillings = self.max_fillings

        # landing zone
        self.create_landing_zone(first = True)

        # highlight
        self.create_highlight(1)

        # walls
            # left
        self.wall_sprites.append(Wall((WALL_PADDING_X - WALL_SIZE[0], 0),
             (WALL_SIZE[0], WALL_SIZE[1]),
             (self.all_sprites, self.collision_sprites), 'left'))
            # right
        self.wall_sprites.append(Wall((WINDOW_WIDTH - WALL_PADDING_X, 0),
             (WALL_SIZE[0], WALL_SIZE[1]),
             (self.all_sprites, self.collision_sprites), 'right'))
            # top
        self.wall_sprites.append(Wall((0, WALL_PADDING_Y - WALL_SIZE[0]), (WALL_SIZE[1], WALL_SIZE[0]),
             (self.all_sprites, self.collision_sprites), 'top'))
            # bottom
        self.wall_sprites.append(Wall((0, WINDOW_HEIGHT - WALL_PADDING_Y), (WALL_SIZE[1], WALL_SIZE[0]),
             (self.all_sprites, self.collision_sprites), 'bottom'))

        # turns
        self.blue_turn = TurnIndicator(self.blue_turn_surf, (-1500, WINDOW_HEIGHT/2), 'blue', (self.all_sprites))
        self.green_turn = TurnIndicator(self.green_turn_surf, (-1500, WINDOW_HEIGHT/2), 'green', (self.all_sprites))
        self.yellow_turn = TurnIndicator(self.yellow_turn_surf, (-1500, WINDOW_HEIGHT/2), 'yellow', (self.all_sprites))
        self.red_turn = TurnIndicator(self.red_turn_surf, (-1500, WINDOW_HEIGHT/2), 'red', (self.all_sprites))
        self.turn_sprites = {'player1': self.blue_turn, 'player2': self.green_turn, 'player3': self.yellow_turn, 'player4': self.red_turn}

        # item select
        self.item_screen = ItemScreen(self.item_screen_surf, (WINDOW_WIDTH/2, (WINDOW_HEIGHT/2) - 4), (self.all_sprites))
        for i in range(0, 3):
            ItemSelector(self.item_select_surfs[i], ITEM_SELECTOR_POS[i], ITEM_TYPES[i], (self.all_sprites, self.item_select_sprites))

    def run(self):
        while self.running:
            # delta time
            start_time = time.time()
            dt = self.clock.tick(FRAMERATE) / 1000

            # next player
            next_current_player = 'player' + str(int(self.current_player[-1]) + 1) if int(self.current_player[-1]) != self.num_players else 'player1'
            if int(next_current_player[-1]) == int(self.starting_player[-1]):
                next_current_player = 'player' + str(int(self.starting_player[-1]) + 1) if not int(self.starting_player[-1]) >= self.num_of_players else 'player1'

            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # timers
            if self.round_end_time != 0 and not self.winner:
                self.current_time = pygame.time.get_ticks()
                if self.current_time - self.round_end_time >= self.round_pause_duration:
                    self.total_rounds += 1
                    self.create_landing_zone()
                    self.next_landing_zone = self.num_of_players
                    self.round_end_time = 0
                    self.turning = True
                    self.phase = 'turning'
                    self.turn_sprites[next_current_player].active = True
                    for highlight in self.highlight_sprites:
                        highlight.kill()
                    self.create_highlight(int(next_current_player[-1]))
                    self.round_end_time = 0
                    for item in self.item_sprites:
                        item.kill()
                    for player in self.players.values():
                        player.ketchups = []
                        player.garbages = []
                        player.toasters = []
            elif self.round_end_time != 0 and self.winner and self.phase != 'win screen':
                self.current_time = pygame.time.get_ticks()
                if self.current_time - self.round_end_time >= self.round_pause_duration:
                    surf = ''
                    for filling in self.filling_order_by_name:
                        surf += filling
                    WinScreen(self.win_screen_surfs[self.winner][surf], (WINDOW_WIDTH/2, WINDOW_HEIGHT/2), (self.all_sprites))
                    self.phase = 'win screen'
                    self.total_rounds += 1
                    self.win_screen_time = pygame.time.get_ticks()

            # change turns animation
            if self.turning:
                if not self.turn_sprites[next_current_player].active:
                    self.turning = False
                    self.change_player()
                    self.phase = 'item select'
                    self.activate_item_select()
            
            # updates + methods
            self.input(dt)
            self.change_phase('_', next_current_player, dt) if pygame.time.get_ticks() - self.start_time >= self.start_dur else None
            self.update_item_select() if self.phase == 'item select' else None
            self.place_item() if self.phase == 'item placement' else None
            self.toaster_shoot() if self.phase == 'launch' else None
            self.update_drop() if self.phase == 'dropping' else None
            if self.pointer_exists:
                self.players[self.current_player].squash = self.aimer.mouse_dist / PLAYER_SQUASH_AMOUNTS[self.players[self.current_player].fillings]
                self.players[self.current_player].angle = self.pointer.angle
                self.shadows[self.current_player].squash = self.aimer.mouse_dist / PLAYER_SQUASH_AMOUNTS[self.players[self.current_player].fillings]
                self.shadows[self.current_player].angle = self.pointer.angle
            self.all_sprites.update(dt)
            for shadow in self.shadows:
                self.shadows[shadow].move(dt)
            if self.pointer_exists:
                self.players[self.current_player].shake(self.aimer.mouse_dist)
                self.shadows[self.current_player].move(dt)
            

            # draw
            self.display_surface.fill(BG_COLOR)
            self.all_sprites.draw()
            i = 1
            for player in self.players:
                score = str(self.max_fillings - self.players[player].fillings)

                if score == '0':
                    self.profiles[player].current_surf = 4
                    self.winner = player
            
                i += 1
            self.display_win_screen_text(dt) if self.phase == 'win screen' else None
            if self.time_left == 0 and self.rect_alpha >= 1500:
                self.running = False
                self.play_again = True
            if self.time_left == 0:
                self.rect_alpha += MAIN_MENU_FADE_SPD * dt
                fade = pygame.Surface((1280, 720))
                fade.set_alpha(self.rect_alpha)
                fade.fill((0, 0, 0))
                self.display_surface.blit(fade, (0, 0))
            pygame.display.update()

            # music
            self.manage_music()

            # print
            print("FPS: ", 1.0 / (time.time() - start_time)) if self.i % self.fps_update_rate == 0 else None
            self.i += 1

        if self.play_again:
            main_menu = MainMenu()
            main_menu.run()
        pygame.quit()
        


class MainMenu:
    def __init__(self):
        # setup
        self.display_surface = pygame.display.get_surface()
        self.clock = clock
        self.running = True
        self.early_leave = False
        self.i = 0

        # settings
        self.num_players = 0
        self.max_fillings = 1

        # groups
        self.all_sprites = AllMenuSprites()
        self.ui_sprites = pygame.sprite.Group()
        self.select_sprites = pygame.sprite.Group()
        self.highlight_sprites = pygame.sprite.Group()
        self.main_sprites = pygame.sprite.Group()
        self.burner_sprites = []
        self.knob_sprites = []
        self.pan_sprites = [None, None, None, None]
        self.fire_sprites = [None, None, None, None]
        self.burger_sprites = [None, None, None, None]
        self.pink_burger_sprites = [None, None, None, None]

        # screen seperation
        self.screen = 'main'
        
        # timers
        self.begin_loading_time = 0
        self.loading_dur = 3000 if not LOADING_SCREEN_SKIP else 0

        # setup
        self.audio_imports()
        self.setup()

    def input(self, screen):
        mouse_pressed = pygame.mouse.get_pressed()[0]
        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            self.running = False
            self.early_leave = True

        if screen == 'main':
            if keys[pygame.K_SPACE]:
                self.click_1.play() if not self.title.should_fade else None
                self.title.should_fade = True
                self.play.should_fade = True  
                self.loading_bg.should_exit = True
                self.loading_bg.amplitude = 1500
            if self.play.should_fade and self.play.alpha <= 0:
                self.screen = 'select'
                self.cheese_select.active = True
                self.lettuce_select.active = True
                self.pickle_select.active = True
                self.tomato_select.active = True
                self.bash.active = True
                for burner in self.burner_sprites:
                    burner.active = True
                for knob in self.knob_sprites:
                    knob.active = True
                self.title.kill()
                self.play.kill()
                self.question.active = True
                
        if screen == 'select':
            if self.bash.clicked():
                self.screen = 'loading'
                self.begin_loading_time = pygame.time.get_ticks()

                self.click_1.play()

                self.loading_bg.should_enter = True
                self.loading_bg.should_exit = False
                self.loading_bg.amplitude = 1450
                self.loading_bg.frame_count = 100
                self.loading_spinner.alpha = -500
                self.loading_spinner.should_fade = 'in'
                self.loading_bun.alpha = -500
                self.loading_bun.should_fade = 'in'
                self.loading_tip.change_tip()
                self.loading_tip.alpha = -500
                self.loading_tip.should_fade = 'in'

                if not self.cheese_select.alive() and self.cheese_highlight.filling_select_sprite:
                    self.cheese_highlight.filling_select_sprite.active = False
                if not self.lettuce_select.alive() and self.lettuce_highlight.filling_select_sprite:
                    self.lettuce_highlight.filling_select_sprite.active = False
                if not self.tomato_select.alive() and self.tomato_highlight.filling_select_sprite:
                    self.tomato_highlight.filling_select_sprite.active = False
                if not self.pickle_select.alive() and self.pickle_highlight.filling_select_sprite:
                    self.pickle_highlight.filling_select_sprite.active = False
                self.cheese_highlight.interactable = False
                self.lettuce_highlight.interactable = False
                self.pickle_highlight.interactable = False
                self.tomato_highlight.interactable = False
                self.bash.active = False
                for burner in self.burner_sprites:
                    burner.active = False
                for knob in self.knob_sprites:
                    knob.active = False
                for pan in self.pan_sprites:
                    if pan:
                        pan.interactable = False
                self.question.active = False

                mixer.music.fadeout(3000)

            if self.question.current_surf == 1 and pygame.mouse.get_just_pressed()[0]:
                self.click_1.play()
                
                if not self.cheese_select.alive() and self.cheese_highlight.filling_select_sprite:
                    self.cheese_highlight.filling_select_sprite.active = False
                if not self.lettuce_select.alive() and self.lettuce_highlight.filling_select_sprite:
                    self.lettuce_highlight.filling_select_sprite.active = False
                if not self.tomato_select.alive() and self.tomato_highlight.filling_select_sprite:
                    self.tomato_highlight.filling_select_sprite.active = False
                if not self.pickle_select.alive() and self.pickle_highlight.filling_select_sprite:
                    self.pickle_highlight.filling_select_sprite.active = False
                self.cheese_highlight.interactable = False
                self.lettuce_highlight.interactable = False
                self.pickle_highlight.interactable = False
                self.tomato_highlight.interactable = False
                self.bash.active = False
                for burner in self.burner_sprites:
                    burner.interactable = False
                for knob in self.knob_sprites:
                    knob.interactable = False
                for pan in self.pan_sprites:
                    if pan:
                        pan.interactable = False
                self.question.active = False

                self.tutorial.visible = True
                self.tutorial.current_surf = 0
                self.left.active = True
                self.right.active = True

            if self.left.current_surf == 1 and pygame.mouse.get_just_pressed()[0]:
                if self.tutorial.current_surf != 0: self.tutorial.current_surf -= 1
                self.click_1.play()

            if self.right.current_surf == 1 and pygame.mouse.get_just_pressed()[0]:
                self.tutorial.current_surf += 1
                self.click_1.play()

                if self.tutorial.current_surf >= 9:
                    self.tutorial.current_surf = 0

                    if not self.cheese_select.alive() and self.cheese_highlight.filling_select_sprite:
                        self.cheese_highlight.filling_select_sprite.active = True
                    if not self.lettuce_select.alive() and self.lettuce_highlight.filling_select_sprite:
                        self.lettuce_highlight.filling_select_sprite.active = True
                    if not self.tomato_select.alive() and self.tomato_highlight.filling_select_sprite:
                        self.tomato_highlight.filling_select_sprite.active = True
                    if not self.pickle_select.alive() and self.pickle_highlight.filling_select_sprite:
                        self.pickle_highlight.filling_select_sprite.active = True
                    self.cheese_highlight.interactable = True
                    self.lettuce_highlight.interactable = True
                    self.pickle_highlight.interactable = True
                    self.tomato_highlight.interactable = True
                    self.bash.active = True
                    for burner in self.burner_sprites:
                        burner.interactable = True
                    for knob in self.knob_sprites:
                        knob.interactable = True
                    for pan in self.pan_sprites:
                        if pan:
                            pan.interactable = True
                    self.question.active = True

                    self.tutorial.active = False
                    self.tutorial.visible = False
                    self.left.active = False
                    self.right.active = False


        if screen == 'loading':
            if keys[pygame.K_SPACE]:
                self.screen = 'none'
                self.loading_bg.should_enter = False
                self.loading_bg.should_exit = True
                self.loading_bg.amplitude = 1500
                self.loading_bg.frame_count = 0
                self.loading_spinner.alpha = 255
                self.loading_spinner.should_fade = 'out'
                self.loading_bun.alpha = 255
                self.loading_bun.should_fade = 'out'

    def oven_update(self, id):
        clicked = False
        burner = self.burner_sprites[id]
        knob = self.knob_sprites[id]
        pan = self.pan_sprites[id]

        if burner.active and self.screen == 'select' and burner.interactable:
            clicked = burner.input(clicked)
            knob.on = True if clicked == 'burner' else False
            clicked = knob.input(clicked) if not clicked else clicked

            if clicked:
                self.sizzle_1.set_volume(uniform(0.5, 1))
                self.sizzle_2.set_volume(uniform(0.5, 1))
                self.pan_drop_1.play() if randint(0, 1) == 0 else self.pan_drop_2.play()
                self.sizzle_1.play() if randint(0, 1) == 0 else self.sizzle_2.play()
                self.num_players += 1
                self.bash.players += 1
                burner.active = False
                self.player_counter.player_num += 1
                fire = Fire(self.fire_surf, (burner.rect.centerx, burner.rect.centery - 7), (self.all_sprites))
                pan = Pan(self.pan_surfs, (burner.rect.centerx, burner.rect.centery - 7), (self.all_sprites), self.garbage_surf)
                burger = Burger(self.burger_surf, (burner.rect.centerx, burner.rect.centery - 7), (self.all_sprites))
                pink_burger = PinkBurger(self.pink_burger_surf, (burner.rect.centerx, burner.rect.centery - 7), (self.all_sprites))

                self.fire_sprites[id] = fire
                self.pan_sprites[id] = pan
                self.burger_sprites[id] = burger
                self.pink_burger_sprites[id] = pink_burger

        elif self.screen == 'select' and not self.tutorial.visible:
            clicked = pan.input(clicked)
            knob.on = False if clicked == 'pan' else True
            clicked = knob.input(clicked) if not clicked else clicked

            if clicked:
                self.garbage_sound.play()
                self.num_players -= 1
                self.bash.players -= 1
                burner.active = True
                self.player_counter.player_num -= 1
                self.fire_sprites[id].kill()
                self.pan_sprites[id].kill()
                self.burger_sprites[id].kill()
                self.pink_burger_sprites[id].kill()

    def audio_imports(self):
        mixer.music.load(join('audio', 'music', 'menu music.mp3'))
        mixer.music.set_volume(0.5)
        mixer.music.play(-1)
        mixer.music.set_pos(0) 

        # clicks
        self.click_1 = mixer.Sound(join('audio', 'clicks', 'click 7.wav'))

        self.pan_drop_1 = mixer.Sound(join('audio', 'menu', 'pan drop 1.wav'))
        self.pan_drop_2 = mixer.Sound(join('audio', 'menu', 'pan drop 2.wav'))
        self.pan_drop_1.set_volume(0.5)
        self.pan_drop_2.set_volume(0.5)
        self.sizzle_1 = mixer.Sound(join('audio', 'menu', 'sizzle 1.mp3'))
        self.sizzle_2 = mixer.Sound(join('audio', 'menu', 'sizzle 2.mp3'))

        self.garbage_sound = mixer.Sound(join('audio', 'menu', 'garbage.wav'))

    def setup(self): 
        # imports
        self.counter_surf = import_image('images', 'menu', 'def counter')
        self.oven_surf = import_image('images', 'menu', 'oven')
        play_unpressed_surf = import_image('images', 'menu', 'play_1', format = 'png')
        play_pressed_surf = import_image('images', 'menu', 'play_2', format = 'png')
        self.play_surfs = [play_unpressed_surf, play_pressed_surf]
        self.title_surf = import_image('images', 'menu', 'title', format = 'png')
        self.board_surf = import_image('images', 'menu', 'cutting board', format = 'png')
            # select fillings
        cheese_select_surf = import_image('images', 'menu', 'filling select', 'cheese', 'cheese select')
        cheese_select_highlight_surf = import_image('images', 'menu', 'filling select', 'cheese', 'cheese select highlight')
        lettuce_select_surf = import_image('images', 'menu', 'filling select', 'lettuce', 'lettuce select')
        lettuce_select_highlight_surf = import_image('images', 'menu', 'filling select', 'lettuce', 'lettuce select highlight')
        pickle_select_surf = import_image('images', 'menu', 'filling select', 'pickle', 'pickle select')
        pickle_select_highlight_surf = import_image('images', 'menu', 'filling select', 'pickle', 'pickle select highlight')
        tomato_select_surf = import_image('images', 'menu', 'filling select', 'tomato', 'tomato select')
        tomato_select_highlight_surf = import_image('images', 'menu', 'filling select', 'tomato', 'tomato select highlight')
        self.cheese_select_surfs = [cheese_select_surf, cheese_select_highlight_surf]
        self.lettuce_select_surfs = [lettuce_select_surf, lettuce_select_highlight_surf]
        self.pickle_select_surfs = [pickle_select_surf, pickle_select_highlight_surf]
        self.tomato_select_surfs = [tomato_select_surf, tomato_select_highlight_surf]
            # cheese fillings
        cheese_filling_surf = import_image('images', 'menu', 'filling select', 'cheese', 'cheese filling')
        cheese_filling_surf2 = import_image('images', 'menu', 'filling select', 'cheese', 'cheese filling 2')
        cheese_highlight_surf = import_image('images', 'menu', 'filling select', 'cheese', 'cheese highlight')
            # lettuce fillings
        lettuce_filling_surf = import_image('images', 'menu', 'filling select', 'lettuce', 'lettuce filling')
        lettuce_filling_surf2 = import_image('images', 'menu', 'filling select', 'lettuce', 'lettuce filling 2')
        lettuce_highlight_surf = import_image('images', 'menu', 'filling select', 'lettuce', 'lettuce highlight')
            # pickle fillings
        pickle_filling_surf = import_image('images', 'menu', 'filling select', 'pickle', 'pickle filling')
        pickle_filling_surf2 = import_image('images', 'menu', 'filling select', 'pickle', 'pickle filling 2')
        pickle_highlight_surf = import_image('images', 'menu', 'filling select', 'pickle', 'pickle highlight')
            # tomato fillings
        tomato_filling_surf = import_image('images', 'menu', 'filling select', 'tomato', 'tomato filling')
        tomato_filling_surf2 = import_image('images', 'menu', 'filling select', 'tomato', 'tomato filling 2')
        tomato_highlight_surf = import_image('images', 'menu', 'filling select', 'tomato', 'tomato highlight')
        self.filling_surfs = {
            'cheese': [cheese_filling_surf, cheese_filling_surf2, cheese_highlight_surf],
            'lettuce': [lettuce_filling_surf, lettuce_filling_surf2, lettuce_highlight_surf],
            'pickle': [pickle_filling_surf, pickle_filling_surf2, pickle_highlight_surf],
            'tomato': [tomato_filling_surf, tomato_filling_surf2, tomato_highlight_surf]
            }
        self.garbage_surf = import_image('images', 'menu', 'garbage')
        bash_gray_surf = import_image('images', 'menu', 'bash gray', format = 'png')
        bash_surf = import_image('images', 'menu', 'bash', format = 'png')
        bash_hover_surf = import_image('images', 'menu', 'bash hover', format = 'png')
        self.bash_surfs = [bash_surf, bash_hover_surf, bash_gray_surf]
        self.min_surf = import_image('images', 'menu', 'minimum players', format = 'png')

        # player select
        burner_surf = import_image('images', 'menu', 'oven', 'burner')
        burner_hover_surf = import_image('images', 'menu', 'oven', 'burner hover')
        self.burner_surfs = [burner_surf, burner_hover_surf]
        knob_off_surf = import_image('images', 'menu', 'oven', 'knob off')
        knob_off_hover_surf = import_image('images', 'menu', 'oven', 'knob off hover')
        knob_on_surf = import_image('images', 'menu', 'oven', 'knob on')
        knob_on_hover_surf = import_image('images', 'menu', 'oven', 'knob on hover')
        self.knob_surfs = [knob_off_surf, knob_off_hover_surf, knob_on_surf, knob_on_hover_surf]
        self.burger_surf = import_image('images', 'menu', 'oven', 'burger')
        self.pink_burger_surf = import_image('images', 'menu', 'oven', 'pink burger')
        counter_0_surf = import_image('images', 'menu', 'oven', 'player counter', '0', format = 'png')
        counter_1_surf = import_image('images', 'menu', 'oven', 'player counter', '1', format = 'png')
        counter_2_surf = import_image('images', 'menu', 'oven', 'player counter', '2', format = 'png')
        counter_3_surf = import_image('images', 'menu', 'oven', 'player counter', '3', format = 'png')
        counter_4_surf = import_image('images', 'menu', 'oven', 'player counter', '4', format = 'png')
        self.counter_surfs = [counter_0_surf, counter_1_surf, counter_2_surf, counter_3_surf, counter_4_surf]
        self.fire_surf = import_image('images', 'menu', 'oven', 'fire')
        pan_surf = import_image('images', 'menu', 'oven', 'pan')
        pan_hover_surf = import_image('images', 'menu', 'oven', 'pan hover')
        self.pan_surfs = [pan_surf, pan_hover_surf]

        # loading screen
        self.loading_bg_frames = import_folder('images', 'menu', 'loading bg')
        self.loading_spinner_surf = import_image('images', 'menu', 'loading spinner', format = 'png')
        self.loading_bun_surf = import_image('images', 'menu', 'loading bun', format = 'png')
        self.loading_tip_surfs = import_folder('images', 'menu', 'tips')

        # tutorial
        question_surf = import_image('images', 'menu', 'question', format = 'png')
        question_highlight_surf = import_image('images', 'menu', 'question highlight', format = 'png')
        self.question_surfs = [question_surf, question_highlight_surf]
        tutorial_1 = import_image('images', 'menu', 'tutorial', '1', format = 'png')
        tutorial_2 = import_image('images', 'menu', 'tutorial', '2', format = 'png')
        tutorial_3 = import_image('images', 'menu', 'tutorial', '3', format = 'png')
        tutorial_4 = import_image('images', 'menu', 'tutorial', '4', format = 'png')
        tutorial_5 = import_image('images', 'menu', 'tutorial', '5', format = 'png')
        tutorial_6 = import_image('images', 'menu', 'tutorial', '6', format = 'png')
        tutorial_7 = import_image('images', 'menu', 'tutorial', '7', format = 'png')
        tutorial_8 = import_image('images', 'menu', 'tutorial', '8', format = 'png')
        tutorial_9 = import_image('images', 'menu', 'tutorial', '9', format = 'png')
        self.tutorial_surfs = [tutorial_1, tutorial_2, tutorial_3, tutorial_4, tutorial_5, tutorial_6, tutorial_7, tutorial_8, tutorial_9]
        left_arrow = import_image('images', 'menu', 'tutorial', 'left', format = 'png')
        left_highlight_arrow = import_image('images', 'menu', 'tutorial', 'left highlight', format = 'png')
        right_arrow = import_image('images', 'menu', 'tutorial', 'right', format = 'png')
        right_highlight_arrow = import_image('images', 'menu', 'tutorial', 'right highlight', format = 'png')
        self.left_surfs = [left_arrow, left_highlight_arrow]
        self.right_surfs = [right_arrow, right_highlight_arrow]



        # sprites
        MenuCounter(self.counter_surf, (WINDOW_WIDTH-1080, WINDOW_HEIGHT/2), (self.all_sprites, self.select_sprites))
        MenuCounter(self.oven_surf, (WINDOW_WIDTH-360, WINDOW_HEIGHT/2), (self.all_sprites, self.select_sprites))
        StaticSprite(self.board_surf, ((WINDOW_WIDTH/2) - 373, (WINDOW_HEIGHT/2) - 30), (self.all_sprites, self.select_sprites))
        self.play = Play(self.play_surfs, ((WINDOW_WIDTH/2)-6, 584), (self.all_sprites, self.main_sprites))
        self.title = Title(self.title_surf, ((WINDOW_WIDTH/2)-0, 264), (self.all_sprites, self.main_sprites))
        
        self.loading_bg = LoadingBg(self.loading_bg_frames, (WINDOW_WIDTH/2, (WINDOW_HEIGHT/2) + 27), (self.all_sprites))
        self.loading_spinner = LoadingSpinner(self.loading_spinner_surf, (WINDOW_WIDTH/2, WINDOW_HEIGHT/2), (self.all_sprites))
        self.loading_bun = LoadingBun(self.loading_bun_surf, (WINDOW_WIDTH/2, WINDOW_HEIGHT/2), (self.all_sprites))
        self.loading_tip = LoadingTip(self.loading_tip_surfs, (WINDOW_WIDTH/2, WINDOW_HEIGHT -80), (self.all_sprites))

        self.cheese_highlight = CheeseHighlight(self.filling_surfs['cheese'][2], self.garbage_surf, [self.cheese_select_surfs, self.filling_surfs], (165, 313), (self.all_sprites, self.highlight_sprites), 'cheese')
        self.cheese_select = FillingSelect(self.cheese_select_surfs, self.filling_surfs, ((WINDOW_WIDTH/2) - 473, (WINDOW_HEIGHT/2) - 50), (self.all_sprites, self.select_sprites), 'cheese', self.cheese_highlight, False)
        self.lettuce_highlight = LettuceHighlight(self.filling_surfs['lettuce'][2], self.garbage_surf, [self.lettuce_select_surfs, self.filling_surfs], (375, 310), (self.all_sprites, self.highlight_sprites), 'lettuce')
        self.lettuce_select = FillingSelect(self.lettuce_select_surfs, self.filling_surfs, ((WINDOW_WIDTH/2) - 273, (WINDOW_HEIGHT/2) - 50), (self.all_sprites, self.select_sprites), 'lettuce', self.lettuce_highlight, False)
        self.pickle_highlight = PickleHighlight(self.filling_surfs['pickle'][2], self.garbage_surf, [self.pickle_select_surfs, self.filling_surfs], (168, 520), (self.all_sprites, self.highlight_sprites), 'pickles')
        self.pickle_select = FillingSelect(self.pickle_select_surfs, self.filling_surfs, ((WINDOW_WIDTH/2) - 473, (WINDOW_HEIGHT/2) + 160), (self.all_sprites, self.select_sprites), 'pickle', self.pickle_highlight, False)
        self.tomato_highlight = TomatoHighlight(self.filling_surfs['tomato'][2], self.garbage_surf, [self.tomato_select_surfs, self.filling_surfs], (367, 523), (self.all_sprites, self.highlight_sprites), 'tomato')
        self.tomato_select = FillingSelect(self.tomato_select_surfs, self.filling_surfs, ((WINDOW_WIDTH/2) - 273, (WINDOW_HEIGHT/2) + 160), (self.all_sprites, self.select_sprites), 'tomato', self.tomato_highlight, False)
        self.bash = Bash(self.bash_surfs, ((WINDOW_WIDTH/2) - 373, 675), self.min_surf, (self.all_sprites, self.select_sprites))

        for id_ in range(1,5):
            burner = Burner(self.burner_surfs, MENU_BURNER_POS[id_ - 1], id_, (self.all_sprites))
            self.burner_sprites.append(burner)
        for id_ in range(1,5):
            knob = Knob(self.knob_surfs, MENU_KNOB_POS[id_ - 1], id_, (self.all_sprites))
            self.knob_sprites.append(knob)
        self.player_counter = PlayerCounter(self.counter_surfs, (560+360, 650), id_, (self.all_sprites))

        self.question = Question(self.question_surfs, (WINDOW_WIDTH - 60, 50), (self.all_sprites))
        self.tutorial = Tutorial(self.tutorial_surfs, (WINDOW_WIDTH/2, WINDOW_HEIGHT/2), (self.all_sprites))
        self.left = Arrow(self.left_surfs, ((WINDOW_WIDTH/2) - 380, (WINDOW_HEIGHT/2) - 0), (self.all_sprites))
        self.right = Arrow(self.right_surfs, ((WINDOW_WIDTH/2) + 380, (WINDOW_HEIGHT/2) - 0), (self.all_sprites))

    def run(self):  
        while self.running:
            # delta time
            start_time = time.time()
            dt = self.clock.tick(FRAMERATE) / 1000
            current_time = pygame.time.get_ticks()

            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.early_leave = True

            # updates
            for id in range(0, 4):
                self.oven_update(id) if self.screen == 'select' else None
            self.all_sprites.update(dt)

            # draw
            self.display_surface.fill(BG_COLOR)
            self.all_sprites.draw()
            pygame.display.update()
                    
            # input
            self.input(self.screen)

            self.running = False if current_time - self.begin_loading_time > self.loading_dur and self.begin_loading_time != 0 else self.running

            print("FPS: ", 1.0 / (time.time() - start_time)) if self.i % 100 == 0 else None
            self.i += 1
        if not self.early_leave:
            fillings = {'cheese': [False, -1], 'lettuce': [False, -1], 'tomato': [False, -1], 'pickles': [False, -1]}
            for sprite in self.highlight_sprites:
                if not hasattr(sprite, 'not_highlight'):
                    if sprite.type != 'garbage' and sprite.active:
                        fillings[sprite.type] = [True, sprite.num]
            game = Game(self.num_players, fillings)
            mixer.music.stop()
            game.run()
        print('-GAME ENDED-')
        pygame.quit()

if __name__ == '__main__':
    game = None
    main_menu = MainMenu()
    main_menu.run()