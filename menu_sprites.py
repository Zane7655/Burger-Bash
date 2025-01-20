from settings import *

class MenuSprite(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
            super().__init__(groups)
            self.image = surf
            self.image = pygame.transform.smoothscale(self.image, (self.image.get_width()/self.size.x, self.image.get_height()/self.size.y))
            self.rect = self.image.get_frect(center = pos)



class StaticSprite(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.static_select = True

class MenuCounter(MenuSprite):
    def __init__(self, surf, pos, groups):
        self.size = pygame.Vector2(MENU_COUNTER_SIZE_X, MENU_COUNTER_SIZE_Y)
        super().__init__(surf, pos, groups)
        self.counter = True

    def update(self, dt):
        pass

class Play(MenuSprite):
    def __init__(self, frames, pos, groups):
        self.size = pygame.Vector2(MENU_PLAY_SIZE_X, MENU_PLAY_SIZE_Y)
        self.clean_frames = frames
        self.current_frame = 0
        super().__init__(self.clean_frames[self.current_frame], pos, groups)
        self.press_time = 0
        self.press_dur = 200
        self.raise_time = pygame.time.get_ticks()
        self.raise_dur = 800
        self.current_time = pygame.time.get_ticks()
        self.main_menu = True
        self.alpha = 255
        self.fade_spd = MAIN_MENU_FADE_SPD
        self.should_fade = False

    def transform(self):
        self.image = self.clean_frames[self.current_frame]
        self.image = pygame.transform.smoothscale(self.image, (self.image.get_width()/self.size.x, self.image.get_height()/self.size.y))
        self.rect = self.image.get_frect(center = self.rect.center)

    def fade(self, dt):
        self.alpha -= self.fade_spd * dt
        self.alpha = self.alpha if self.alpha > 0 else 0 
        self.image.fill((255, 255, 255, self.alpha), None, pygame.BLEND_RGBA_MULT)

    def update(self, dt):
        self.current_time = pygame.time.get_ticks()
        if self.raise_time and self.current_time - self.raise_time >= self.raise_dur:
             self.raise_time = 0
             self.press_time = self.current_time
             self.current_frame = 1
        elif self.press_time and self.current_time - self.press_time >= self.press_dur:
             self.press_time = 0
             self.raise_time = self.current_time
             self.current_frame = 0

        self.transform()
        self.fade(dt) if self.should_fade else None

class Title(MenuSprite):
    def __init__(self, surf, pos, groups):
        self.clean_surf = surf
        self.size = pygame.Vector2(MENU_TITLE_SIZE_X, MENU_TITLE_SIZE_Y)
        super().__init__(surf, pos, groups)
        self.main_menu = True
        self.alpha = 255
        self.fade_spd = MAIN_MENU_FADE_SPD
        self.should_fade = False

    def transform(self):
        self.image = self.clean_surf.copy()
        self.image = pygame.transform.smoothscale(self.image, (self.image.get_width()/self.size.x, self.image.get_height()/self.size.y))
        self.rect = self.image.get_frect(center = self.rect.center)

    def fade(self, dt):
        self.alpha -= self.fade_spd * dt
        self.alpha = self.alpha if self.alpha > 0 else 0 
        self.image.fill((255, 255, 255, self.alpha), None, pygame.BLEND_RGBA_MULT)

    def update(self, dt):
        self.transform() if self.should_fade else None
        self.fade(dt) if self.should_fade else None
    


class LoadingBg(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.image = frames[0]
        self.rect = self.image.get_frect(center = pos)
        self.loading_bg = True
        self.visible = True
        self.current_frame = 0
        self.frames = frames
        self.animate_spd = 30
        self.should_exit = False
        self.should_enter = False
        self.amplitude = 0
        self.period = 200
        self.frame_count = 0

    def exit(self, dt):
        self.frame_count += 1
        self.rect.bottom -= self.amplitude * (sin(TWO_PI * self.frame_count / self.period) * dt)

    def enter(self, dt):
        self.frame_count += 1
        self.rect.bottom -= self.amplitude * (sin(TWO_PI * self.frame_count / self.period) * dt)

    def update(self, dt):
        self.current_frame = self.current_frame + (self.animate_spd * dt) if not self.current_frame >= 40 else 0
        self.current_frame = 0 if self.current_frame >= 40 else self.current_frame
        self.image = self.frames[floor(self.current_frame)]
        self.exit(dt) if self.should_exit and self.rect.bottom > 0 else None
        self.rect.bottom = 0 if self.should_exit and self.rect.bottom <= 0 else self.rect.bottom
        self.enter(dt) if self.should_enter and self.rect.bottom < 765 else None
        self.rect.centery = (WINDOW_HEIGHT/2) + 27 if self.should_enter and self.rect.bottom >= 765 else self.rect.centery

class LoadingSpinner(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.clean_surf = surf
        self.image = surf.copy()
        self.rect = self.image.get_frect(center = pos)
        self.rotation = 0
        self.rotate_spd = 100
        self.should_fade = None
        self.pos = pos
        self.alpha = 0
        self.fade_spd = MAIN_MENU_FADE_SPD
        self.loading_obj = True
        self.visible = False

    def fade(self, dt):
        self.alpha += self.fade_spd * dt if self.should_fade == 'in' else -self.fade_spd * dt
        alpha = self.alpha
        alpha = 0 if self.alpha < 0 else alpha
        alpha = 255 if self.alpha > 255 else alpha
        self.image.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)

    def rotate(self, dt):
        self.rotation -= self.rotate_spd * dt
        self.image = self.clean_surf.copy()
        self.image = pygame.transform.rotozoom(self.image, self.rotation, 1)
        self.rect = self.image.get_frect(center = self.pos)

    def update(self, dt):
        self.visible = True if self.should_fade else False
        self.rotate(dt) if self.visible else None
        self.fade(dt) if self.should_fade else None

class LoadingBun(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.clean_surf = surf
        self.image = surf.copy()
        self.rect = self.image.get_frect(center = pos)
        self.image.fill((255, 255, 255, 0), None, pygame.BLEND_RGBA_MULT)
        self.should_fade = None
        self.pos = pos
        self.alpha = 0
        self.fade_spd = MAIN_MENU_FADE_SPD
        self.loading_obj = True
        self.visible = False

    def fade(self, dt):
        self.image = self.clean_surf
        self.image = self.image.copy()
        self.alpha += self.fade_spd * dt if self.should_fade == 'in' else -self.fade_spd * dt
        alpha = self.alpha
        alpha = 0 if self.alpha < 0 else alpha
        alpha = 255 if self.alpha > 255 else alpha
        self.image.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)

    def update(self, dt):
        self.visible = True if self.should_fade else False
        self.fade(dt) if self.should_fade else None

class LoadingTip(pygame.sprite.Sprite):
    def __init__(self, surfs, pos, groups):
        super().__init__(groups)
        self.clean_surfs = surfs
        self.current_tip = randint(0, len(self.clean_surfs)-1)
        self.image = self.clean_surfs[self.current_tip].copy()
        self.rect = self.image.get_frect(center = pos)
        self.should_fade = None
        self.pos = pos
        self.alpha = 0
        self.fade_spd = MAIN_MENU_FADE_SPD
        self.loading_obj = True
        self.visible = False

    def change_tip(self):
        old_current_tip = self.current_tip
        while self.current_tip == old_current_tip:
            self.current_tip = randint(0, len(self.clean_surfs)-1)
        self.image = self.clean_surfs[self.current_tip].copy()
        self.rect = self.image.get_frect(center = self.pos)

    def fade(self, dt):
        self.image = self.clean_surfs[self.current_tip]
        self.image = self.image.copy()
        self.alpha += self.fade_spd * dt if self.should_fade == 'in' else -self.fade_spd * dt
        alpha = self.alpha
        alpha = 0 if self.alpha < 0 else alpha
        alpha = 255 if self.alpha > 255 else alpha
        self.image.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)

    def update(self, dt):
        self.visible = True if self.should_fade else False
        self.fade(dt) if self.should_fade else None



class FillingSelect(MenuSprite):
    def __init__(self, frames, filling_surfs, pos, groups, type, highlight, active):
        self.active = active
        self.frames = frames
        self.current_frame = 0
        self.not_highlight = True
        self.size = pygame.Vector2(MENU_FILLING_SIZES[type], MENU_FILLING_SIZES[type])
        super().__init__(self.frames[self.current_frame], pos, groups)
        self.filling_select = True
        self.filling_select_2 = True
        self.type = type
        self.click_sound = mixer.Sound(join('audio', 'clicks', 'click 7.wav'))
        self.click_2 = mixer.Sound(join('audio', 'clicks', 'click 10.wav'))
        self.click_2.set_volume(0.2)
        self.highlight = highlight
        self.filling_surf = filling_surfs[self.type]
        self.pos = pos
        self.old_hover = False
        self.groups_ = groups
        if self.type == 'cheese':
            self.rect_shrink_x = -58
            self.rect_shrink_y = -60
        elif self.type == 'lettuce':
            self.radius = 100
        elif self.type == 'pickle':
            self.radius = 62
        elif self.type == 'tomato':
            self.radius = 62

    def transform(self):
        self.image = self.frames[self.current_frame].copy()
        self.image = pygame.transform.smoothscale(self.image, (self.image.get_width()/self.size.x, self.image.get_height()/self.size.y))
        self.rect = self.image.get_frect(center = self.rect.center)

    def update(self, dt):
        if self.active:
            mouse_pos = pygame.mouse.get_pos()
            old_current_frame = self.current_frame
            if self.type == 'cheese':
                collision_rect = self.rect #.inflate(self.rect_shrink_x, self.rect_shrink_y)
                # collision_rect.move_ip(0, -3)

                if collision_rect.collidepoint(mouse_pos):
                    self.current_frame = 1
                    self.click_2.play() if not self.old_hover else None
                    self.old_hover = True
                else:
                    self.old_hover = False
                    self.current_frame = 0
                
                if old_current_frame != self.current_frame:
                        self.transform()
                if self.current_frame == 1 and pygame.mouse.get_just_pressed()[0]:
                    self.click_sound.play()
                    for id in range(0, 4):
                        CheeseFilling(self.filling_surf, self.groups_, id, self.highlight)
                    self.kill()
            else:
                d = dist([mouse_pos[0], mouse_pos[1]], [self.pos[0], self.pos[1]])

                if d <= self.radius:
                    self.current_frame = 1
                    self.click_2.play() if not self.old_hover else None
                    self.old_hover = True
                else:
                    self.current_frame = 0
                    self.old_hover = False

                if old_current_frame != self.current_frame:
                    self.transform()

                if self.current_frame == 1 and pygame.mouse.get_just_pressed()[0]:
                    self.click_sound.play()
                    if self.type == 'lettuce':
                        for id in range(0, 4):
                            LettuceFilling(self.filling_surf, self.groups_, id, self.highlight)
                    if self.type == 'pickle':
                        for id in range(0, 12):
                            PickleFilling(self.filling_surf, self.groups_, id, self.highlight)
                    if self.type == 'tomato':
                        for id in range(0, 4):
                            TomatoFilling(self.filling_surf, self.groups_, id, self.highlight)
                    self.kill()

class CheeseFilling(MenuSprite):
    def __init__(self, surfs, groups, id, highlight):
        self.size = pygame.Vector2(MENU_FILLING_SIZES['cheese'], MENU_FILLING_SIZES['cheese'])
        super().__init__(surfs[0], (-1000, -1000), groups)
        self.id = id
        self.highlight = highlight
        self.groups_ = groups
        self.surfs = surfs
        self.current_surf = 0
        self.time_created = pygame.time.get_ticks()
        self.spawn_delay = MENU_CHEESE_SPAWN_DELAY[self.id]
        self.filling_select = True
        self.spawn_size = self.drop_size = MENU_FILLING_SPAWN_SIZE
        self.spawn = False
        self.drop_dur = 450
        self.not_highlight = True
        sound = 'filling select fall ' + str(randint(1, 3)) + '.mp3'
        self.fall_sound = mixer.Sound(join('audio', 'menu', sound))
        self.fall_sound.set_volume(0.5)

    def animate_drop(self):
        self.image = self.surfs[self.current_surf].copy()
        self.image = pygame.transform.smoothscale(self.image, (self.surfs[self.current_surf].get_width()/self.drop_size, self.surfs[self.current_surf].get_height()/self.drop_size))
        self.rect = self.image.get_frect(center = self.rect.center)
        self.drop_size += 0.1
        self.drop_size = self.size.x if self.drop_size > self.size.x else self.drop_size
        self.current_surf = 1 if self.drop_size == self.size.x else self.current_surf
        self.fall_sound.play() if self.drop_size == self.size.x else None

    def transform(self):
        self.image = self.surfs[self.current_surf].copy()
        self.image = pygame.transform.smoothscale(self.image, (self.surfs[self.current_surf].get_width()/self.size.x, self.surfs[self.current_surf].get_height()/self.size.y))
        self.rect = self.image.get_frect(center = self.rect.center)

    def update(self, dt):
        current_time = pygame.time.get_ticks()

        if current_time - self.time_created >= self.spawn_delay and self.drop_size == self.spawn_size:
            self.spawn = True
            self.rect.center = MENU_CHEESE_SPAWN_POS[self.id]

        if self.spawn and self.drop_size < self.size.x:
            self.animate_drop()
        elif self.spawn:
            self.image = self.surfs[self.current_surf]

        if current_time - self.time_created >= self.drop_dur and self.spawn:
            self.highlight.active = True if self.id == 0 else self.highlight.active
            self.spawn = False
            self.transform() if self.size.x != self.drop_size else None

        if current_time - self.time_created >= self.drop_dur and not self.spawn:
            if not self.highlight.active:
                self.kill()
            else: 
                self.rect.center = MENU_CHEESE_SPAWN_POS[self.id]
                if self.highlight.visible:
                    self.rect.centery -= 10

class CheeseHighlight(pygame.sprite.Sprite):
    def __init__(self, surf, garbage_surf, select_surfs, pos, groups, type):
        super().__init__(groups)
        self.type = type
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.rect_copy = self.rect.copy()
        self.garbage_surf = garbage_surf
        self.select_surfs = select_surfs
        self.groups_ = groups
        self.active = False
        self.pos = pos
        self.visible = False
        self.filling_highlight = True
        self.garbage = Garbage(self.garbage_surf, (self.rect.centerx, self.rect.centery - 10), self.groups_)
        self.num = 1
        self.click_2 = mixer.Sound(join('audio', 'clicks', 'click 10.wav'))
        self.click_2.set_volume(0.2)
        self.old_hover = False
        self.garbage_sound = mixer.Sound(join('audio', 'menu', 'garbage.wav'))
        self.interactable = True
        self.filling_select_sprite = None

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        collision_rect = self.rect_copy.inflate(-22, -26)
        collision_rect.move_ip(0, -7)

        if self.active:
            if collision_rect.collidepoint(mouse_pos) and self.interactable:
                self.rect.centery -= 10 if not self.visible else 0
                self.visible = True
                self.garbage.visible = True
                self.click_2.play() if not self.old_hover else None
                self.old_hover = True
            else:
                self.rect.centery += 10 if self.visible else 0
                self.visible = False
                self.garbage.visible = False
                self.old_hover = False
            if self.visible and pygame.mouse.get_just_pressed()[0]:
                self.garbage_sound.play()
                self.active = False
                self.visible = False
                self.garbage.visible = False
                self.filling_select_sprite = FillingSelect(self.select_surfs[0], self.select_surfs[1], ((WINDOW_WIDTH/2) - 473, (WINDOW_HEIGHT/2) - 50), self.groups_, 'cheese', self, True)
        else:
            self.rect.centery = self.pos[1]

class LettuceFilling(MenuSprite):
    def __init__(self, surfs, groups, id, highlight):
        self.size = pygame.Vector2(MENU_FILLING_SIZES['lettuce'], MENU_FILLING_SIZES['lettuce'])
        super().__init__(surfs[0], (-1000, -1000), groups)
        self.id = id
        self.highlight = highlight
        self.groups_ = groups
        self.surfs = surfs
        self.current_surf = 0
        self.time_created = pygame.time.get_ticks()
        self.spawn_delay = MENU_LETTUCE_SPAWN_DELAY[self.id]
        self.filling_select = True
        self.spawn_size = self.drop_size = MENU_FILLING_SPAWN_SIZE
        self.spawn = False
        self.drop_dur = 450
        self.not_highlight = True
        sound = 'filling select fall ' + str(randint(1, 3)) + '.mp3'
        self.fall_sound = mixer.Sound(join('audio', 'menu', sound))
        self.fall_sound.set_volume(0.5)

    def animate_drop(self):
        self.image = self.surfs[self.current_surf].copy()
        self.image = pygame.transform.smoothscale(self.image, (self.surfs[self.current_surf].get_width()/self.drop_size, self.surfs[self.current_surf].get_height()/self.drop_size))
        self.rect = self.image.get_frect(center = self.rect.center)
        self.drop_size += 0.1
        self.drop_size = self.size.x if self.drop_size > self.size.x else self.drop_size
        self.current_surf = 1 if self.drop_size == self.size.x else self.current_surf
        self.fall_sound.play() if self.drop_size == self.size.x else None

    def transform(self):
        self.image = self.surfs[self.current_surf].copy()
        self.image = pygame.transform.smoothscale(self.image, (self.surfs[self.current_surf].get_width()/self.size.x, self.surfs[self.current_surf].get_height()/self.size.y))
        self.rect = self.image.get_frect(center = self.rect.center)

    def update(self, dt):
        current_time = pygame.time.get_ticks()

        if current_time - self.time_created >= self.spawn_delay and self.drop_size == self.spawn_size:
            self.spawn = True
            self.rect.center = MENU_LETTUCE_SPAWN_POS[self.id]

        if self.spawn and self.drop_size < self.size.x:
            self.animate_drop()
        elif self.spawn:
            self.image = self.surfs[self.current_surf]

        if current_time - self.time_created >= self.drop_dur and self.spawn:
            self.highlight.active = True if self.id == 0 else self.highlight.active
            self.spawn = False
            self.transform() if self.size.x != self.drop_size else None

        if current_time - self.time_created >= self.drop_dur and not self.spawn:
            if not self.highlight.active:
                self.kill()
            else: 
                self.rect.center = MENU_LETTUCE_SPAWN_POS[self.id]
                if self.highlight.visible:
                    self.rect.centery -= 10

class LettuceHighlight(pygame.sprite.Sprite):
    def __init__(self, surf, garbage_surf, select_surfs, pos, groups, type):
        super().__init__(groups)
        self.type = type
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.rect_copy = self.rect.copy()
        self.garbage_surf = garbage_surf
        self.select_surfs = select_surfs
        self.pos = pos
        self.groups_ = groups
        self.active = False
        self.visible = False
        self.filling_highlight = True
        self.garbage = Garbage(self.garbage_surf, (self.rect.centerx, self.rect.centery - 10), self.groups_)
        self.num = 2
        self.click_2 = mixer.Sound(join('audio', 'clicks', 'click 10.wav'))
        self.click_2.set_volume(0.2)
        self.old_hover = False
        self.garbage_sound = mixer.Sound(join('audio', 'menu', 'garbage.wav'))
        self.interactable = True
        self.filling_select_sprite = None

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        collision_rect = self.rect_copy.inflate(-20, -10)
        # collision_rect.move_ip(0, -3)

        if self.active:
            if collision_rect.collidepoint(mouse_pos) and self.interactable:
                self.rect.centery -= 10 if not self.visible else 0
                self.visible = True
                self.garbage.visible = True
                self.click_2.play() if not self.old_hover else None
                self.old_hover = True
            else:
                self.rect.centery += 10 if self.visible else 0
                self.visible = False
                self.garbage.visible = False
                self.old_hover = False
            if self.visible and pygame.mouse.get_just_pressed()[0]:
                self.garbage_sound.play()
                self.active = False
                self.visible = False
                self.garbage.visible = False
                self.filling_select_sprite = FillingSelect(self.select_surfs[0], self.select_surfs[1], ((WINDOW_WIDTH/2) - 273, (WINDOW_HEIGHT/2) - 50), self.groups_, 'lettuce', self, True)
        else:
            self.rect.centery = self.pos[1]

class PickleFilling(MenuSprite):
    def __init__(self, surfs, groups, id, highlight):
        self.size = pygame.Vector2(MENU_FILLING_SIZES['pickle'], MENU_FILLING_SIZES['pickle'])
        super().__init__(surfs[0], (-1000, -1000), groups)
        self.id = id
        self.highlight = highlight
        self.groups_ = groups
        self.surfs = surfs
        self.current_surf = 0
        self.time_created = pygame.time.get_ticks()
        self.spawn_delay = MENU_PICKLE_SPAWN_DELAY[self.id]
        self.filling_select = True
        self.spawn_size = self.drop_size = MENU_FILLING_SPAWN_SIZE
        self.spawn = False
        self.drop_dur = 700
        self.not_highlight = True
        sound = 'filling select fall ' + str(randint(1, 3)) + '.mp3'
        self.fall_sound = mixer.Sound(join('audio', 'menu', sound))
        self.fall_sound.set_volume(0.5)

    def animate_drop(self):
        self.image = self.surfs[self.current_surf].copy()
        self.image = pygame.transform.smoothscale(self.image, (self.surfs[self.current_surf].get_width()/self.drop_size, self.surfs[self.current_surf].get_height()/self.drop_size))
        self.rect = self.image.get_frect(center = self.rect.center)
        self.drop_size += 0.1
        self.drop_size = self.size.x if self.drop_size > self.size.x else self.drop_size
        self.current_surf = 1 if self.drop_size == self.size.x else self.current_surf
        self.fall_sound.play() if self.drop_size == self.size.x else None

    def transform(self):
        self.image = self.surfs[self.current_surf].copy()
        self.image = pygame.transform.smoothscale(self.image, (self.surfs[self.current_surf].get_width()/self.size.x, self.surfs[self.current_surf].get_height()/self.size.y))
        self.rect = self.image.get_frect(center = self.rect.center)

    def update(self, dt):
        current_time = pygame.time.get_ticks()

        if current_time - self.time_created >= self.spawn_delay and self.drop_size == self.spawn_size:
            self.spawn = True
            self.rect.center = MENU_PICKLE_SPAWN_POS[self.id]

        if self.spawn and self.drop_size < self.size.x:
            self.animate_drop()
        elif self.spawn:
            self.image = self.surfs[self.current_surf]

        if current_time - self.time_created >= self.drop_dur and self.spawn:
            self.highlight.active = True if self.id == 0 else self.highlight.active
            self.spawn = False
            self.transform() if self.size.x != self.drop_size else None

        if current_time - self.time_created >= self.drop_dur and not self.spawn:
            if not self.highlight.active:
                self.kill()
            else: 
                self.rect.center = MENU_PICKLE_SPAWN_POS[self.id]
                if self.highlight.visible:
                    self.rect.centery -= 10

class PickleHighlight(pygame.sprite.Sprite):
    def __init__(self, surf, garbage_surf, select_surfs, pos, groups, type):
        super().__init__(groups)
        self.type = type
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.rect_copy = self.rect.copy()
        self.garbage_surf = garbage_surf
        self.select_surfs = select_surfs
        self.pos = pos
        self.groups_ = groups
        self.active = False
        self.visible = False
        self.filling_highlight = True
        self.garbage = Garbage(self.garbage_surf, (self.rect.centerx, self.rect.centery - 10), self.groups_)
        self.num = 4
        self.click_2 = mixer.Sound(join('audio', 'clicks', 'click 10.wav'))
        self.click_2.set_volume(0.2)
        self.old_hover = False
        self.garbage_sound = mixer.Sound(join('audio', 'menu', 'garbage.wav'))
        self.interactable = True
        self.filling_select_sprite = None

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        collision_rect = self.rect_copy # self.rect.inflate(self.rect_shrink_x, self.rect_shrink_y)
        # collision_rect.move_ip(0, -3)

        if self.active:
            if collision_rect.collidepoint(mouse_pos) and self.interactable:
                self.rect.centery -= 10 if not self.visible else 0
                self.visible = True
                self.garbage.visible = True
                self.click_2.play() if not self.old_hover else None
                self.old_hover = True
            else:
                self.rect.centery += 10 if self.visible else 0
                self.visible = False
                self.garbage.visible = False
                self.old_hover = False
            if self.visible and pygame.mouse.get_just_pressed()[0]:
                self.garbage_sound.play()
                self.active = False
                self.visible = False
                self.garbage.visible = False
                self.filling_select_sprite = FillingSelect(self.select_surfs[0], self.select_surfs[1], ((WINDOW_WIDTH/2) - 473, (WINDOW_HEIGHT/2) + 160), self.groups_, 'pickle', self, True)
        else:
            self.rect.centery = self.pos[1]

class TomatoFilling(MenuSprite):
    def __init__(self, surfs, groups, id, highlight):
        self.size = pygame.Vector2(MENU_FILLING_SIZES['tomato'], MENU_FILLING_SIZES['tomato'])
        super().__init__(surfs[0], (-1000, -1000), groups)
        self.id = id
        self.highlight = highlight
        self.groups_ = groups
        self.surfs = surfs
        self.current_surf = 0
        self.time_created = pygame.time.get_ticks()
        self.spawn_delay = MENU_TOMATO_SPAWN_DELAY[self.id]
        self.filling_select = True
        self.spawn_size = self.drop_size = MENU_FILLING_SPAWN_SIZE
        self.spawn = False
        self.drop_dur = 450
        self.not_highlight = True
        sound = 'filling select fall ' + str(randint(1, 3)) + '.mp3'
        self.fall_sound = mixer.Sound(join('audio', 'menu', sound))
        self.fall_sound.set_volume(0.5)

    def animate_drop(self):
        self.image = self.surfs[self.current_surf].copy()
        self.image = pygame.transform.smoothscale(self.image, (self.surfs[self.current_surf].get_width()/self.drop_size, self.surfs[self.current_surf].get_height()/self.drop_size))
        self.rect = self.image.get_frect(center = self.rect.center)
        self.drop_size += 0.1
        self.drop_size = self.size.x if self.drop_size > self.size.x else self.drop_size
        self.current_surf = 1 if self.drop_size == self.size.x else self.current_surf
        self.fall_sound.play() if self.drop_size == self.size.x else None

    def transform(self):
        self.image = self.surfs[self.current_surf].copy()
        self.image = pygame.transform.smoothscale(self.image, (self.surfs[self.current_surf].get_width()/self.size.x, self.surfs[self.current_surf].get_height()/self.size.y))
        self.rect = self.image.get_frect(center = self.rect.center)

    def update(self, dt):
        current_time = pygame.time.get_ticks()

        if current_time - self.time_created >= self.spawn_delay and self.drop_size == self.spawn_size:
            self.spawn = True
            self.rect.center = MENU_TOMATO_SPAWN_POS[self.id]

        if self.spawn and self.drop_size < self.size.x:
            self.animate_drop()
        elif self.spawn:
            self.image = self.surfs[self.current_surf]

        if current_time - self.time_created >= self.drop_dur and self.spawn:
            self.highlight.active = True if self.id == 0 else self.highlight.active
            self.spawn = False
            self.transform() if self.size.x != self.drop_size else None

        if current_time - self.time_created >= self.drop_dur and not self.spawn:
            if not self.highlight.active:
                self.kill()
            else: 
                self.rect.center = MENU_TOMATO_SPAWN_POS[self.id]
                if self.highlight.visible:
                    self.rect.centery -= 10

class TomatoHighlight(pygame.sprite.Sprite):
    def __init__(self, surf, garbage_surf, select_surfs, pos, groups, type):
        super().__init__(groups)
        self.type = type
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.rect_copy = self.rect.copy()
        self.garbage_surf = garbage_surf
        self.select_surfs = select_surfs
        self.pos = pos
        self.groups_ = groups
        self.active = False
        self.visible = False
        self.filling_highlight = True
        self.garbage = Garbage(self.garbage_surf, (self.rect.centerx, self.rect.centery - 10), self.groups_)
        self.num = 3
        self.click_2 = mixer.Sound(join('audio', 'clicks', 'click 10.wav'))
        self.click_2.set_volume(0.2)
        self.old_hover = False
        self.garbage_sound = mixer.Sound(join('audio', 'menu', 'garbage.wav'))
        self.interactable = True
        self.filling_select_sprite = None

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        collision_rect = self.rect_copy # self.rect.inflate(self.rect_shrink_x, self.rect_shrink_y)
        # collision_rect.move_ip(0, -3)
        if self.active:
            if collision_rect.collidepoint(mouse_pos) and self.interactable:
                self.rect.centery -= 10 if not self.visible else 0
                self.visible = True
                self.garbage.visible = True
                self.click_2.play() if not self.old_hover else None
                self.old_hover = True
            else:
                self.rect.centery += 10 if self.visible else 0
                self.visible = False
                self.garbage.visible = False
                self.old_hover = False
            if self.visible and pygame.mouse.get_just_pressed()[0]:
                self.garbage_sound.play()
                self.active = False
                self.visible = False
                self.garbage.visible = False
                self.filling_select_sprite = FillingSelect(self.select_surfs[0], self.select_surfs[1], ((WINDOW_WIDTH/2) - 273, (WINDOW_HEIGHT/2) + 160), self.groups_, 'tomato', self, True)
        else:
            self.rect.centery = self.pos[1]

class Garbage(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.type = 'garbage'
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.garbage_ui = True
        self.visible = False
        self.active = False # ignore but dont delete

class Bash(pygame.sprite.Sprite):
    def __init__(self, surfs, pos, min_surf, groups):
        super().__init__(groups)
        self.surfs = surfs
        self.image = self.surfs[2]
        self.rect = self.image.get_frect(center = pos)
        self.current_surf = 2
        self.active = False
        self.visible = True
        self.pos = pos
        self.select_ui = True
        self.players = 0
        self.groups_ = groups
        self.min_surf = min_surf
        self.hovering = False
        self.min_text_time = -1000
        self.min_text_delay = 1000
        self.click_2 = mixer.Sound(join('audio', 'clicks', 'click 10.wav'))
        self.click_2.set_volume(0.2)

    def clicked(self):
        if self.current_surf == 1 and pygame.mouse.get_just_pressed()[0]:
            self.image = self.surfs[0].copy()
            self.current_surf = 0
            return True
        else:
            return False

    def hover(self):
        mouse_pos = pygame.mouse.get_pos()
        old_surf = self.current_surf
        self.rect.center = self.pos
        collision_rect = self.rect.inflate(-130, -90)
        collision_rect.move_ip(0, -10)

        if self.active:
            if self.players >= 2:
                if collision_rect.collidepoint(mouse_pos):
                    self.click_2.play() if not self.hovering else None
                    self.hovering = True
                    self.current_surf = 1
                    self.rect.centery -= 5
                else:
                    self.hovering = False
                    self.current_surf = 0
            else:
                self.current_surf = 2
                if collision_rect.collidepoint(mouse_pos) and not self.hovering and pygame.time.get_ticks() - self.min_text_time >= self.min_text_delay:
                    MinText(self.min_surf, (self.rect.centerx, self.rect.centery - 40), self.groups_)
                    self.hovering = True
                    self.min_text_time = pygame.time.get_ticks()
                elif collision_rect.collidepoint(mouse_pos):
                    self.hovering = True
                else:
                    self.hovering = False

    def update(self, dt):
        self.hover()
        self.image = self.surfs[self.current_surf]

class MinText(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.clean_surf = surf
        self.image = self.clean_surf.copy()
        self.rect = self.image.get_frect(center = pos)
        self.alpha = 0
        self.image.fill((255, 255, 255, self.alpha), None, pygame.BLEND_RGBA_MULT)
        self.spd = 50
        self.def_spd = 0
        self.slow_spd = 20
        self.fade_in_spd = 750
        self.fade_out_spd = 250
        self.fade = 'in'
        self.min_text = True
        self.visible = True

    def update(self, dt):
        self.rect.centery -= self.spd * dt
        self.spd -= self.slow_spd * dt
        self.spd = self.def_spd if self.spd <= self.def_spd else self.spd

        self.alpha += self.fade_in_spd * dt if self.fade == 'in' else -self.fade_out_spd * dt
        self.fade = 'out' if self.alpha >= 400 else self.fade
        alpha = self.alpha if self.alpha <= 255 else 255
        alpha = 0 if alpha <= 0 else alpha

        if self.alpha <= 0:
            self.kill()

        self.image = self.clean_surf.copy()
        self.image.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)


class Burner(MenuSprite):
    def __init__(self, surfs, pos, id, groups):
        self.size = pygame.Vector2(3.4, 3.4)
        super().__init__(surfs[0], pos, groups)
        self.surfs = surfs
        self.pos = pos
        self.current_surf = 0
        self.radius = 113
        self.burner = True
        self.active = False
        self.id = id
        self.click_sound = mixer.Sound(join('audio', 'clicks', 'click 7.wav'))
        self.click_2 = mixer.Sound(join('audio', 'clicks', 'click 10.wav'))
        self.click_2.set_volume(0.2)
        self.old_hover = False
        self.interactable = True

    def transform(self):
        self.image = self.surfs[self.current_surf].copy()
        self.image = pygame.transform.smoothscale(self.image, (self.image.get_width()/self.size.x, self.image.get_height()/self.size.y))
        self.rect = self.image.get_frect(center = self.pos)
        self.rect.centery -= 10 if self.current_surf == 1 else 0

    def hover(self):
        mouse_pos = pygame.mouse.get_pos()
        d = dist([mouse_pos[0], mouse_pos[1]], [self.pos[0], self.pos[1] - 9])
        old_surf = self.current_surf

        if d <= self.radius:
            self.current_surf = 1
            self.click_2.play() if not self.old_hover else None
            self.old_hover = True

        else:
            self.current_surf = 0
            self.old_hover = False

        self.transform() if old_surf != self.current_surf else None

    def input(self, clicked):
        if self.current_surf == 1 and pygame.mouse.get_just_pressed()[0]:
            self.image = self.surfs[0]
            self.current_surf = 0
            self.click_sound.play()
            self.transform()
            return 'burner'
        else:
            return clicked

    def update(self, dt):
        self.hover() if self.active and self.interactable else None

class Knob(MenuSprite):
    def __init__(self, surfs, pos, id, groups):
        self.size = pygame.Vector2(3.4, 3.4)
        super().__init__(surfs[0], pos, groups)
        self.surfs = surfs
        self.pos = pos
        self.current_surf = 0
        self.radius = 50
        self.knob = True
        self.on = False
        self.active = False
        self.id = id
        self.dial_sound = mixer.Sound(join('audio', 'menu', 'dial.mp3'))
        self.click_2 = mixer.Sound(join('audio', 'clicks', 'click 10.wav'))
        self.click_2.set_volume(0.2)
        self.old_hover = False
        self.interactable = True

    def transform(self):
        self.image = self.surfs[self.current_surf].copy()
        self.image = pygame.transform.smoothscale(self.image, (self.image.get_width()/self.size.x, self.image.get_height()/self.size.y))
        self.rect = self.image.get_frect(center = self.pos)
        self.rect.centery -= 10 if self.current_surf == 1 or self.current_surf == 3 else 0
        self.rect.centerx += 1 if self.current_surf == 1 or self.current_surf == 3 else 0

    def hover(self):
        mouse_pos = pygame.mouse.get_pos()
        d = dist([mouse_pos[0], mouse_pos[1]], [self.pos[0], self.pos[1] - 3])
        old_surf = self.current_surf

        if not self.on:
            if d <= self.radius:
                self.current_surf = 1
                self.click_2.play() if not self.old_hover else None
                self.old_hover = True
            else:
                self.current_surf = 0
                self.old_hover = False
        else:
            if d <= self.radius:
                self.current_surf = 3
                self.click_2.play() if not self.old_hover else None
                self.old_hover = True
            else:
                self.current_surf = 2
                self.old_hover = False

        self.transform() if old_surf != self.current_surf else None

    def input(self, clicked):
        if self.current_surf == 1 or self.current_surf == 3:
            if pygame.mouse.get_just_pressed()[0]:
                self.on = not self.on
                self.dial_sound.play()
                return 'knob'
        return clicked

    def update(self, dt):
        self.hover() if self.active and self.interactable else None
    
class PlayerCounter(MenuSprite):
    def __init__(self, surfs, pos, id, groups):
        self.size = pygame.Vector2(3.4, 3.4)
        super().__init__(surfs[0], pos, groups)
        self.surfs = surfs
        self.player_num = 0
        self.old_player_num = self.player_num
        self.player_counter = True
        self.id = id

    def transform(self):
        self.image = self.surfs[self.player_num].copy()
        self.image = pygame.transform.smoothscale(self.image, (self.image.get_width()/self.size.x, self.image.get_height()/self.size.y))
        self.rect = self.image.get_frect(center = self.rect.center)
    
    def update(self, dt):
        if self.old_player_num != self.player_num:
            self.transform()

        self.old_player_num = self.player_num

class Fire(MenuSprite):
    def __init__(self, surf, pos, groups):
        self.size = pygame.Vector2(2, 2)
        super().__init__(surf, pos, groups)
        self.surf = surf
        self.pos = pos
        self.spawn_time = pygame.time.get_ticks()
        self.spawn_delay = MENU_FIRE_SPAWN_DELAY
        self.animate_size = 0
        self.amplitude = MENU_FIRE_AMPLITUDE
        self.period = MENU_FIRE_PERIOD
        self.fire = True
        self.visible = False
        self.frame_count = 0
        self.def_size = 1.2

    def transform(self):
        self.image = self.surf.copy()
        try:
            self.image = pygame.transform.scale(self.image, (self.image.get_width()/(self.size.x - self.animate_size), self.image.get_height()/(self.size.y - self.animate_size)))
        except:
            print('ERR: cannot scale to negative size > Fire')
            self.image = pygame.transform.scale(self.image, (0, 0))
        self.rect = self.image.get_frect(center = self.pos)

    def animate(self, dt):
        self.frame_count += 60 * dt if self.size.x <= self.def_size else 0
        self.animate_size = (self.amplitude * sin(TWO_PI * self.frame_count / self.period)) * dt if self.size.x <= self.def_size else self.animate_size
        self.size = self.size - (2.2 * dt, 2.2 * dt) if self.size.x > self.def_size else pygame.Vector2(self.def_size, self.def_size)

    def update(self, dt):
        current_time = pygame.time.get_ticks()

        if current_time - self.spawn_time >= self.spawn_delay:
            self.visible = True
            self.animate(dt)
            self.transform()
        else:
            self.visible = False

class Pan(MenuSprite):
    def __init__(self, surfs, pos, groups, garbage_surf):
        self.size = pygame.Vector2(0.7, 0.7)
        super().__init__(surfs[0], pos, groups)
        self.surfs = surfs
        self.current_surf = 0
        self.pos = pos
        self.radius = 130
        self.pan = True
        self.visible = True
        self.garbage_surf = garbage_surf
        self.drop_spd = pygame.Vector2(2.2, 2.2)
        self.garbage = Garbage(self.garbage_surf, (self.rect.centerx, self.rect.centery), groups)
        self.click_2 = mixer.Sound(join('audio', 'clicks', 'click 10.wav'))
        self.click_2.set_volume(0.2)
        self.old_hover = False
        self.interactable = True

    def transform(self):
        self.image = self.surfs[self.current_surf].copy()
        self.image = pygame.transform.smoothscale(self.image, (self.image.get_width()/self.size.x, self.image.get_height()/self.size.y))
        self.rect = self.image.get_frect(center = self.pos)

    def hover(self):
        self.image = self.surfs[self.current_surf] if self.image != self.surfs[self.current_surf] else self.image
        self.rect = self.image.get_frect(center = self.pos)
        mouse_pos = pygame.mouse.get_pos()
        d = dist([mouse_pos[0], mouse_pos[1]], [self.pos[0], self.pos[1]])
        old_surf = self.current_surf

        if d <= self.radius:
            self.current_surf = 1
            self.click_2.play() if d <= self.radius and not self.old_hover else None
            self.garbage.visible = True
            self.old_hover = True
        else:
            self.current_surf = 0
            self.garbage.visible = False
            self.old_hover = False

    def input(self, clicked):
        if self.current_surf == 1 and pygame.mouse.get_just_pressed()[0]:
            self.garbage.kill()
            return 'pan'
        else:
            return clicked

    def update(self, dt):
        if self.size.x >= 1:
            self.hover() if self.interactable else None
        else:
            self.size = self.size + (self.drop_spd * dt) if not self.size.x >= 1 else pygame.Vector2(1, 1)
            self.transform()

class Burger(MenuSprite):
    def __init__(self, surf, pos, groups):
        self.size = pygame.Vector2(0.9, 0.9)
        super().__init__(surf, pos, groups)
        self.surf = surf
        self.pos = pos
        self.burger = True
        self.time_created = pygame.time.get_ticks()
        self.spawn_delay = 150
        self.visible = False
        self.drop_spd = pygame.Vector2(2.2, 2.2)

    def transform(self):
        self.image = self.surf.copy()
        self.image = pygame.transform.smoothscale(self.image, (self.image.get_width()/self.size.x, self.image.get_height()/self.size.y))
        self.rect = self.image.get_frect(center = self.pos)

    def update(self, dt):
        current_time = pygame.time.get_ticks()

        if current_time - self.time_created >= self.spawn_delay:
            self.visible = True
            self.size = self.size + (self.drop_spd * dt) if not self.size.x >= 1.2 else pygame.Vector2(1.2, 1.2)
            self.transform() if not self.size.x >= 1.2 else None

class PinkBurger(MenuSprite):
    def __init__(self, surf, pos, groups):
        self.size = pygame.Vector2(0.9, 0.9)
        super().__init__(surf, pos, groups)
        self.surf = surf
        self.pos = pos
        self.pink_burger = True
        self.time_created = pygame.time.get_ticks()
        self.spawn_delay = 150
        self.alpha = 255
        self.fade_spd = 2.2
        self.visible = False
        self.drop_spd = pygame.Vector2(2.2, 2.2)

    def transform(self):
        self.image = self.surf.copy()
        self.image = pygame.transform.smoothscale(self.image, (self.image.get_width()/self.size.x, self.image.get_height()/self.size.y))
        self.rect = self.image.get_frect(center = self.pos)

    def fade(self, dt):
        self.alpha -= self.fade_spd * dt
        self.alpha = self.alpha if self.alpha > 0 else 0 
        self.image.fill((255, 255, 255, self.alpha), None, pygame.BLEND_RGBA_MULT)

    def update(self, dt):
        current_time = pygame.time.get_ticks()

        if current_time - self.time_created >= self.spawn_delay:
            self.visible = True
            self.size = self.size + (self.drop_spd * dt) if not self.size.x >= 1.18 else pygame.Vector2(1.18, 1.18)
            self.fade(dt) if current_time - self.time_created >= self.spawn_delay + 100 else None
            self.transform() if not self.size.x >= 1.18 else None



class Question(pygame.sprite.Sprite):
    def __init__(self, surfs, pos, groups):
        super().__init__(groups)
        self.surfs = surfs
        self.pos = pos
        self.current_surf = 0
        self.image = self.surfs[self.current_surf]
        self.rect = self.image.get_frect(center = self.pos)
        self.visible = True
        self.question = True
        self.active = False
        self.hovering = False
        self.click_2 = mixer.Sound(join('audio', 'clicks', 'click 10.wav'))
        self.click_2.set_volume(0.2)

    def hover(self):
        mouse_pos = pygame.mouse.get_pos()
        self.rect.center = self.pos

        if self.active:
            if self.rect.collidepoint(mouse_pos):
                self.click_2.play() if not self.hovering else None
                self.hovering = True
                self.current_surf = 1
                self.rect.centery -= 0
            else:
                self.hovering = False
                self.current_surf = 0
        else:
            self.current_surf = 0

    def update(self, dt):
        self.hover()
        self.image = self.surfs[self.current_surf]

class Tutorial(pygame.sprite.Sprite):
    def __init__(self, surfs, pos, groups):
        super().__init__(groups)
        self.surfs = surfs
        self.pos = pos
        self.current_surf = 0
        self.image = self.surfs[self.current_surf]
        self.rect = self.image.get_frect(center = self.pos)
        self.tutorial = True
        self.visible = False

    def update(self, dt):
        self.image = self.surfs[self.current_surf]

class Arrow(MenuSprite):
    def __init__(self, surfs, pos, groups):
        self.size = pygame.Vector2(3.4, 3.4)
        self.surfs = surfs
        super().__init__(surfs[0], pos, groups)
        self.visible = False
        self.pos = pos
        self.arrow = True
        self.active = False
        self.hovering = False
        self.click_2 = mixer.Sound(join('audio', 'clicks', 'click 10.wav'))
        self.click_2.set_volume(0.2)
        self.current_surf = 0

    def transform(self):
        self.image = self.surfs[self.current_surf].copy()
        self.image = pygame.transform.smoothscale(self.image, (self.image.get_width()/self.size.x, self.image.get_height()/self.size.y))
        self.rect = self.image.get_frect(center = self.rect.center)

    def hover(self):
        mouse_pos = pygame.mouse.get_pos()
        self.rect.center = self.pos

        if self.active:
            if self.rect.collidepoint(mouse_pos):
                self.click_2.play() if not self.hovering else None
                self.hovering = True
                self.current_surf = 1
                self.rect.centery -= 0
            else:
                self.hovering = False
                self.current_surf = 0
        else:
            self.current_surf = 0

    def update(self, dt):
        self.visible = True if self.active else False

        self.image = self.surfs[self.current_surf]
        self.transform() if self.active else None

        self.hover()

