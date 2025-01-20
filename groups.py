from settings import *

# show hitbox: pygame.draw.rect(self.DISPLAYSURF, 'blue', sprite.hitbox)

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.DISPLAYSURF = pygame.display.get_surface()
        self.zone_font = pygame.font.Font(join('fonts', 'DiloWorld.ttf'), 80)
        self.score_font = pygame.font.Font(join('fonts', 'DiloWorld.ttf'), 60)
        self.players = None
        self.max_fillings = None

    def display_zone_ticks(self):
        for zone in self.landing_zone_sprites:
            if not hasattr(zone, 'dot'):
                if zone.size == zone.max_size:
                    zone_tick_surf = self.zone_font.render(str(zone.ticks), True, ZONE_FONT_COLORS[zone.get_color(True)])
                    zone_tick_rect = zone_tick_surf.get_frect(center = zone.rect.center)
                    self.DISPLAYSURF.blit(zone_tick_surf, zone_tick_rect)

    def display_scores(self):
        i = 1

        for player in self.players:
            score = str(self.max_fillings - self.players[player].fillings)
            score_surf = self.score_font.render(score, True, 'white')
            score_rect = score_surf.get_frect(center = SCORE_POS[i-1])
            self.DISPLAYSURF.blit(score_surf, score_rect)
            
            i += 1

    def draw(self):
        tile_sprites = [sprite for sprite in self if hasattr(sprite, 'tile')]
        ketchup_sprites = [sprite for sprite in self if hasattr(sprite, 'ketchup')]
        self.landing_zone_sprites = [sprite for sprite in self if hasattr(sprite, 'landing_zone')]
        shadow_sprites = [sprite for sprite in self if hasattr(sprite, 'shadow')]
        wall_sprites = [sprite for sprite in self if hasattr(sprite, 'wall')]
        pointer_sprites = [sprite for sprite in self if hasattr(sprite, 'pointer')]
        bread_sprites = [sprite for sprite in self if hasattr(sprite, 'bread')]
        item_sprites = [sprite for sprite in self if hasattr(sprite, 'item')]
        star_sprites = [sprite for sprite in self if hasattr(sprite, 'star')]
        you_sprites = [sprite for sprite in self if hasattr(sprite, 'you')]
        rotate_sprite = [sprite for sprite in self if hasattr(sprite, 'rotate')]
        dropping_sprites = [sprite for sprite in self if hasattr(sprite, 'dropping')]
        highlight_sprites = [sprite for sprite in self if hasattr(sprite, 'highlight')]
        profile_sprites = [sprite for sprite in self if hasattr(sprite, 'profile')]
        turn_indicator_sprites = [sprite for sprite in self if hasattr(sprite, 'turn_indicator')]
        item_screen_sprite = [sprite for sprite in self if hasattr(sprite, 'item_screen')]
        win_screen_sprite = [sprite for sprite in self if hasattr(sprite, 'win_screen')]
        item_selector_sprites = [sprite for sprite in self if hasattr(sprite, 'item_selector')]
        general_sprites = [sprite for sprite in self if not hasattr(sprite, 'pointer') and not hasattr(sprite, 'wall') and not hasattr(sprite, 'tile') and not hasattr(sprite, 'shadow') and not hasattr(sprite, 'landing_zone') and not hasattr(sprite, 'highlight') and not hasattr(sprite, 'profile') and not hasattr(sprite, 'item_screen') and not hasattr(sprite, 'item_selector') and not hasattr(sprite, 'item') and not hasattr(sprite, 'ketchup') and not hasattr(sprite, 'bread') and not hasattr(sprite, 'dropping') and not hasattr(sprite, 'star') and not hasattr(sprite, 'win_screen') and not hasattr(sprite, 'rotate') and not hasattr(sprite, 'you')]

        for sprite in tile_sprites:
            self.DISPLAYSURF.blit(sprite.image, sprite.rect.topleft)
        for sprite in ketchup_sprites:
            self.DISPLAYSURF.blit(sprite.image, sprite.rect.topleft)
        for sprite in self.landing_zone_sprites:
            self.DISPLAYSURF.blit(sprite.image, sprite.rect.topleft)
        self.display_zone_ticks()
        for sprite in shadow_sprites:
            self.DISPLAYSURF.blit(sprite.image, sprite.rect.topleft)
        for sprite in wall_sprites:
            self.DISPLAYSURF.blit(sprite.image, sprite.rect.topleft)
        for sprite in pointer_sprites:
            self.DISPLAYSURF.blit(sprite.image, sprite.rect.topleft)
        for sprite in bread_sprites:
            self.DISPLAYSURF.blit(sprite.image, sprite.rect.topleft)
        for sprite in item_sprites:
            self.DISPLAYSURF.blit(sprite.image, sprite.rect.topleft)
        for sprite in star_sprites:
            self.DISPLAYSURF.blit(sprite.image, sprite.rect.topleft)
        for sprite in general_sprites:
            self.DISPLAYSURF.blit(sprite.image, sprite.rect.topleft)
        for sprite in you_sprites:
            self.DISPLAYSURF.blit(sprite.image, sprite.rect.topleft) if sprite.visible else None
        for sprite in rotate_sprite:
            self.DISPLAYSURF.blit(sprite.image, sprite.rect.topleft)
        for sprite in dropping_sprites:
            self.DISPLAYSURF.blit(sprite.image, sprite.rect.topleft) if sprite.visible else None
        for sprite in highlight_sprites:
            self.DISPLAYSURF.blit(sprite.image, sprite.rect.topleft)
        for sprite in profile_sprites:
            self.DISPLAYSURF.blit(sprite.image, sprite.rect.topleft)
        self.display_scores()
        for sprite in item_screen_sprite:
            self.DISPLAYSURF.blit(sprite.image, sprite.rect.topleft) if sprite.visible else None
        for sprite in item_selector_sprites:
            self.DISPLAYSURF.blit(sprite.image, sprite.rect.topleft) if sprite.visible else None
        for sprite in turn_indicator_sprites:
            self.DISPLAYSURF.blit(sprite.image, sprite.rect.topleft) if sprite.visible else None
        for sprite in win_screen_sprite:
            self.DISPLAYSURF.blit(sprite.image, sprite.rect.topleft) if sprite.visible else None

class AllMenuSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

    def draw(self):
        counter_sprites = (sprite for sprite in self if hasattr(sprite, 'counter'))
        static_select_sprites = (sprite for sprite in self if hasattr(sprite, 'static_select'))
        filling_highlight_sprites = (sprite for sprite in self if hasattr(sprite, 'filling_highlight'))
        filling_select_sprites = (sprite for sprite in self if hasattr(sprite, 'filling_select'))
        burner_sprites = (sprite for sprite in self if hasattr(sprite, 'burner'))
        knob_sprites = (sprite for sprite in self if hasattr(sprite, 'knob'))
        player_counter_sprite = (sprite for sprite in self if hasattr(sprite, 'player_counter'))
        fire_sprites = (sprite for sprite in self if hasattr(sprite, 'fire'))
        pan_sprites = (sprite for sprite in self if hasattr(sprite, 'pan'))
        burger_sprites = (sprite for sprite in self if hasattr(sprite, 'burger'))
        pink_burger_sprites = (sprite for sprite in self if hasattr(sprite, 'pink_burger'))
        garbage_sprites = (sprite for sprite in self if hasattr(sprite, 'garbage_ui'))
        select_ui_sprites = (sprite for sprite in self if hasattr(sprite, 'select_ui'))
        question_sprite = (sprite for sprite in self if hasattr(sprite, 'question'))
        tutorial_sprite = (sprite for sprite in self if hasattr(sprite, 'tutorial'))
        arrow_sprites = (sprite for sprite in self if hasattr(sprite, 'arrow'))
        min_text_sprites = (sprite for sprite in self if hasattr(sprite, 'min_text'))
        loading_bg_sprite = (sprite for sprite in self if hasattr(sprite, 'loading_bg'))
        loading_obj_sprites = (sprite for sprite in self if hasattr(sprite, 'loading_obj'))
        main_menu_sprites = (sprite for sprite in self if hasattr(sprite, 'main_menu'))

        for sprite in counter_sprites:
            self.display_surface.blit(sprite.image, sprite.rect.topleft)
        for sprite in static_select_sprites:
            self.display_surface.blit(sprite.image, sprite.rect.topleft)
        for sprite in filling_highlight_sprites:
            self.display_surface.blit(sprite.image, sprite.rect.topleft) if sprite.visible else None
        for sprite in filling_select_sprites:
            self.display_surface.blit(sprite.image, sprite.rect.topleft)
        for sprite in burner_sprites:
            self.display_surface.blit(sprite.image, sprite.rect.topleft)
        for sprite in knob_sprites:
            self.display_surface.blit(sprite.image, sprite.rect.topleft)
        for sprite in player_counter_sprite:
            self.display_surface.blit(sprite.image, sprite.rect.topleft)
        for sprite in fire_sprites:
            self.display_surface.blit(sprite.image, sprite.rect.topleft) if sprite.visible else None
        for sprite in pan_sprites:
            self.display_surface.blit(sprite.image, sprite.rect.topleft) if sprite.visible else None
        for sprite in burger_sprites:
            self.display_surface.blit(sprite.image, sprite.rect.topleft) if sprite.visible else None
        for sprite in pink_burger_sprites:
            self.display_surface.blit(sprite.image, sprite.rect.topleft) if sprite.visible else None
        for sprite in garbage_sprites:
            self.display_surface.blit(sprite.image, sprite.rect.topleft) if sprite.visible else None
        for sprite in select_ui_sprites:
            self.display_surface.blit(sprite.image, sprite.rect.topleft) if sprite.visible else None
        for sprite in question_sprite:
            self.display_surface.blit(sprite.image, sprite.rect.topleft) if sprite.visible else None
        for sprite in min_text_sprites:
            self.display_surface.blit(sprite.image, sprite.rect.topleft) if sprite.visible else None
        for sprite in tutorial_sprite:
            self.display_surface.blit(sprite.image, sprite.rect.topleft) if sprite.visible else None
        for sprite in arrow_sprites:
            self.display_surface.blit(sprite.image, sprite.rect.topleft) if sprite.visible else None
        for sprite in loading_bg_sprite:
            self.display_surface.blit(sprite.image, sprite.rect.topleft) if sprite.visible else None
        for sprite in loading_obj_sprites:
            self.display_surface.blit(sprite.image, sprite.rect.topleft) if sprite.visible else None
        for sprite in main_menu_sprites:
            self.display_surface.blit(sprite.image, sprite.rect.topleft)
        