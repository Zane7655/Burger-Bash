from settings import *

class Sprite(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = pos)

class Arena(pygame.sprite.Sprite):
    def __init__(self, surf, pos, offset, scale, groups):
        super().__init__(groups)
        self.image = surf
        self.image = pygame.transform.scale_by(self.image, scale)
        self.rect = self.image.get_frect(center = (pos[0] - offset[0], pos[1] + offset[1]))

class Soda(Arena):
    def __init__(self, surf, pos, scale, groups, offset = (0,0)):
        super().__init__(surf, pos, offset, scale, groups)
        self.size = self.image.get_width()
        self.radius = self.size/2
        self.mass = SODA_MASS

class Tile(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.image = pygame.transform.smoothscale(self.image, (BG_TILE_SIZE, BG_TILE_SIZE))
        self.rect = self.image.get_rect(topleft = pos)
        self.tile = True

class Wall(pygame.sprite.Sprite):
    def __init__(self, pos, size, groups, type):
        super().__init__(groups)
        self.image = pygame.Surface(size)
        self.image.fill('blue')
        self.image.set_alpha(0) if not SHOW_WALLS else None
        self.rect = self.image.get_rect(topleft = pos)
        self.wall = True
        self.type = type

class Aimer(pygame.sprite.Sprite):
    def __init__(self, surf, pos, click_pos, fillings, groups):
        super().__init__(groups)
        self.clean_surf = surf
        self.image = self.clean_surf.copy()
        self.pos = pos
        self.rect = self.image.get_rect(center = self.pos)
        self.point_dir = pygame.Vector2((0,0))
        self.click_pos = pygame.Vector2(click_pos)
        self.fillings = fillings
        self.max_height = PLAYER_MAX_HEIGHTS[self.fillings]
        self.width = 32
        self.height = 9
        self.offset = 0
        self.padding = 40
        self.pointer = True
        self.mouse_dist = 0

    def update(self, _):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        self.mouse_dist = round(hypot(mouse_pos.x - self.click_pos.x, mouse_pos.y - self.click_pos.y)) - 50
        if self.mouse_dist < 0:
            self.mouse_dist = 0
        if self.mouse_dist > self.max_height:
            self.mouse_dist = self.max_height
        self.point_dir = (mouse_pos - self.click_pos).normalize() if mouse_pos - self.click_pos else self.point_dir
        angle = (degrees(atan2(self.point_dir.x, self.point_dir.y)))

        # Create a scaled surface for the aimer
        scaled_aimer_surf = pygame.transform.smoothscale(self.clean_surf, (self.width, self.mouse_dist))

        # Rotate the scaled surface
        self.image = pygame.transform.rotate(scaled_aimer_surf, angle)

        self.rect = self.image.get_rect(center = self.pos)

        self.offset = self.mouse_dist/2 + self.padding
        if self.point_dir:
            self.rect.centerx += round(self.point_dir.x * self.offset)
            self.rect.centery += round(self.point_dir.y * self.offset)
        else:
            self.rect.centery += round(self.offset)

class Pointer(Sprite):
    def __init__(self, surf, pos, click_pos, groups):
        super().__init__(surf, pos, groups)
        self.clean_surf = surf
        self.image = self.clean_surf.copy()
        self.pos = pos
        self.pointer = True
        self.click_pos = click_pos
        self.offset = -6
        self.point_dir = pygame.Vector2((0, 0))
        self.angle = 0
        
    def update(self, dt):
        if not pygame.mouse.get_pressed()[0]:
            self.kill()
            
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        self.point_dir = (mouse_pos - self.click_pos).normalize() if mouse_pos - self.click_pos else self.point_dir
        self.angle = (degrees(atan2(self.point_dir.x, self.point_dir.y)))
        
        self.image = pygame.transform.rotozoom(self.clean_surf, self.angle, 1)
        self.rect = self.image.get_rect(center=self.pos)

        if self.point_dir:
            self.rect.centerx += round(self.point_dir.x * self.offset)
            self.rect.centery += round(self.point_dir.y * self.offset)
        else:
            self.rect.centery += self.offset

class Entity(Sprite):
    def __init__(self, surf, pos, players, groups):
        super().__init__(surf, pos, groups)
        self.players = players
        self.ticks = 4

    def trigger_event(self, dt):
        pass

    def tick(self, dt):
        self.ticks -= 1
        if self.ticks <= 0:
            self.trigger_event(dt)

class LandingZone(Entity):
    def __init__(self, surfs, pos, players, landing_zone_sprites, groups, dot_surfs, all_sprites, profiles, num_players, max_fillings, first):
        super().__init__(surfs['empty'], pos, players, groups)
        self.profiles = profiles
        self.surfs = surfs
        self.max_fillings = max_fillings
        self.dot_surfs = dot_surfs
        self.all_sprites = all_sprites
        self.radius = (LANDING_ZONE_SIZE - LANDING_ZONE_PADDING)/2
        self.current_color = self.get_color(False)
        self.image = pygame.transform.smoothscale(self.current_color, (LANDING_ZONE_SIZE - LANDING_ZONE_PADDING, LANDING_ZONE_SIZE - LANDING_ZONE_PADDING))
        self.ticks = num_players
        self.ticks += 1 if first else 0
        self.landing_zone_sprites = landing_zone_sprites
        self.distances = []
        self.landing_zone = True
        self.max_size = LANDING_ZONE_SIZE - LANDING_ZONE_PADDING
        self.size = self.max_size/ZONE_SPAWN_SPEED
        self.size_step = self.size
        self.despawn = False
        self.drop_to = None
        self.check_for_space()
        self.enter_sound = mixer.Sound(join('audio', 'game', 'enter zone.wav'))
        self.exit_sound = mixer.Sound(join('audio', 'game', 'exit zone.wav'))
        self.enter_sound.set_volume(0.7)
        self.exit_sound.set_volume(0.7)

    def get_closest_player(self, value):
        distances = {}
        closest_player = None

        for player in self.players:
            distances[player] = (hypot(self.players[player].rect.centerx - self.rect.centerx, self.players[player].rect.centery - self.rect.centery))

        closest_player = min(distances, key=distances.get)
        return closest_player if value == 'name' else distances[closest_player]

    def get_color(self, dots):
        closest_player = self.get_closest_player('name')
        d = hypot(self.rect.centerx - self.players[closest_player].rect.centerx, self.rect.centery - self.players[closest_player].rect.centery)
        total_radii = self.radius + self.players[closest_player].radius
        if not dots:
            return self.surfs[closest_player] if d < total_radii else self.surfs['empty']
        else:
            return closest_player if d < total_radii else 'empty'

    def trigger_event(self, dt):
        closest_player = self.get_closest_player('name')

        d = hypot(self.rect.centerx - self.players[closest_player].rect.centerx, self.rect.centery - self.players[closest_player].rect.centery)
        total_radii = self.radius + self.players[closest_player].radius

        if d < total_radii:
            self.drop_to = closest_player
        self.despawn = True
        self.dots.despawn = True

    def new_pos(self):
        self.rect.centerx = randint(ceil(WALL_PADDING_X + LANDING_ZONE_SIZE + LANDING_ZONE_PADDING/2), floor(WINDOW_WIDTH - WALL_PADDING_X - LANDING_ZONE_SIZE - LANDING_ZONE_PADDING/2))
        self.rect.centery = randint(ceil(WALL_PADDING_Y + LANDING_ZONE_SIZE + LANDING_ZONE_PADDING/2), floor(WINDOW_HEIGHT - WALL_PADDING_Y - LANDING_ZONE_SIZE - LANDING_ZONE_PADDING/2))

    def get_dists(self):
        self.distances = []
        for zone in self.landing_zone_sprites:
            if zone is not self:
                self.distances.append(hypot(self.rect.centerx - zone.rect.centerx, self.rect.centery - zone.rect.centery))

    def check_for_space(self):
        self.get_dists()

        closest_zone = min(self.distances) if self.distances else 1000
        closest_player = self.get_closest_player('distance')

        attempts = 0
        while closest_zone <= LANDING_ZONE_SPACE_BUBBLE or closest_player <= LANDING_ZONE_SPACE_BUBBLE:
            self.new_pos()
            self.get_dists()
            closest_zone = min(self.distances) if self.distances else 1000
            closest_player = self.get_closest_player('distance')
            attempts += 1
            if attempts >= 1000:
                self.new_pos()
                print('ERR 1> NO SPACE')
                break
        self.dots = ZoneDots(self.dot_surfs, self.rect.center, (self.all_sprites), self)

    def update(self, dt):
        old_color = self.current_color
        self.current_color = self.get_color(False)
        if old_color != self.current_color and self.current_color == self.surfs['empty']:
            self.exit_sound.play()
        elif old_color != self.current_color:
            self.enter_sound.play()
        self.image = pygame.transform.smoothscale(self.current_color, (self.size, self.size))
        self.rect = self.image.get_rect(center=self.rect.center)

        if self.size < self.max_size and not self.despawn:
            self.size += self.size_step
        else:
            self.size = self.max_size if not self.despawn else self.size

        if self.despawn:
            self.size -= self.size_step
            if self.size <= 0:
                self.kill()
                self.dots.kill()

class ZoneDots(Sprite):
    def __init__ (self, surfs, pos, groups, zone):
        surf = surfs['empty']
        super().__init__(surf, pos, groups)
        self.surfs = surfs
        self.zone = zone
        self.angle = 0
        self.landing_zone = True
        self.dot = True
        self.scale = ZONE_DOTS_SCALE/ZONE_SPAWN_SPEED
        self.scale_step = self.scale
        self.max_scale = ZONE_DOTS_SCALE
        self.despawn = False
        self.transform()

    def transform(self):
        self.image = pygame.transform.rotozoom(self.surfs[self.zone.get_color(True)], self.angle, self.scale)
        self.rect = self.image.get_rect(center=self.rect.center)
        if self.scale < self.max_scale and not self.despawn:
            self.scale += self.scale_step
        else:
            self.scale = ZONE_DOTS_SCALE if not self.despawn else self.scale

    def update(self, dt):
        self.transform()
        self.angle += ZONE_DOTS_SPD * dt

        if self.despawn:
            self.scale -= self.scale_step
            if self.scale <= 0:
                self.kill()

class Player(Sprite):
    def __init__(self, surf, pos, groups, collision_sprites, players, sodas, filling_surfs, id, all_fillings, ketchup_sounds, garbage_can_sounds, bun_hit_sounds):
        super().__init__(surf, pos, groups)
        # general
        self.all_fillings = all_fillings
        self.clean_surf = surf
        self.collision_sprites = collision_sprites
        self.fillings = 0
        self.width = self.image.get_width()
        self.height = self.width
        self.players = players
        self.sodas = sodas
        self.ketchups = []
        self.garbages = []
        self.toasters = []
        self.id = id

        # movement & collision
        self.friction = PLAYER_FRICTION[self.fillings]
        self.dir = pygame.Vector2()
        self.spd = 0
        self.velocity = pygame.Vector2(self.dir * self.spd)
        self.old_rect = self.rect.copy()
        self.penetration_depth = pygame.Vector2()
        self.radius = floor(PLAYER_RADIUS/2)
        self.mass = PLAYER_MASS[self.fillings]
        self.pos_x = self.rect.centerx
        self.pos_y = self.rect.centery
        
        # animate
        self.angle = 0
        self.squash = 0
        self.initial_pos = pygame.Vector2(pos)
        self.filling_surfs = filling_surfs

        # sounds
        self.garbage_can_sounds = garbage_can_sounds
        self.ketchup_sounds = ketchup_sounds
        self.old_in_ketchup = False
        self.bun_hit_sounds = bun_hit_sounds
        self.minimum_sound_speed = 500

        # shake
        self.max_shake = PLAYER_AIM_MAX_SHAKE
        self.shake_amount = pygame.Vector2(PLAYER_AIM_MAX_SHAKE, PLAYER_AIM_MAX_SHAKE)
        
    def update_attrs(self):
        self.friction = PLAYER_FRICTION[self.fillings]
        self.mass = PLAYER_MASS[self.fillings]

    def update_sprite(self):
        surf_name = ''
        for i in range(0, self.fillings):
            surf_name += self.all_fillings[i]
        self.clean_surf = self.filling_surfs[surf_name] if self.fillings > 0 else self.clean_surf
        self.width = self.clean_surf.get_width()
        self.height = self.width
        
    def launch(self, dir, spd):
        self.rect.center = self.initial_pos
        self.dir = dir
        self.spd = spd * PLAYER_SPEED_MULTIPLYER
        self.velocity = pygame.Vector2(self.dir * self.spd)
        self.image = pygame.transform.scale(self.clean_surf, (self.width, self.height))

    def move(self, dt):
        # adjust position
        self.pos_x += self.velocity.x * dt
        self.rect.centerx = self.pos_x
        self.wall_collision('horizontal')
        self.toaster_collision('horizontal')
        self.pos_y += self.velocity.y * dt
        self.rect.centery = self.pos_y
        self.ketchup_collision()
        self.garbage_collision()
        self.soda_collision()
        self.wall_collision('vertical')
        self.toaster_collision('vertical')
        self.player_collisions()

        # print('initial_pos: ', self.initial_pos)
        # print('rect: ', self.rect.center)

        velocity_magnitude = self.velocity.magnitude()
        if velocity_magnitude > 5:
            self.velocity *= 1 - (self.friction * (dt*PLAYER_FRICTION_MULTIPLYER))  # Apply friction proportionally
        else:
            self.velocity = pygame.Vector2(0, 0)  # Stop if velocity is zero 

    def transform(self):
        self.image = pygame.transform.smoothscale(self.clean_surf, (self.width - round(self.squash), self.height))
        if self.angle != 0:
            self.image = pygame.transform.rotozoom(self.image, self.angle, 1)
        else:
            self.image = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def shake(self, max_shake):
        self.max_shake = max_shake / 40 if max_shake / 40 < PLAYER_AIM_MAX_SHAKE else PLAYER_AIM_MAX_SHAKE
        # self.rect.center = self.initial_pos
        # self.rect.centerx = self.initial_pos.x + self.shake_amount.x
        # self.rect.centery = self.initial_pos.y + self.shake_amount.y
        
        if self.shake_amount.x > 0: self.shake_amount.x = -1 * (uniform(1, self.max_shake))
        if self.shake_amount.y > 0: self.shake_amount.y = -1 * (uniform(1, self.max_shake))
        if self.shake_amount.x < 0: self.shake_amount.x = uniform(1, self.max_shake)
        if self.shake_amount.y < 0: self.shake_amount.y = uniform(1, self.max_shake)

    def wall_collision(self, direction):
        for sprite in self.collision_sprites:
            dist_rx = abs(self.rect.centerx - sprite.rect.left)
            dist_lx = abs(self.rect.centerx - sprite.rect.right)
            dist_by = abs(self.rect.centery - sprite.rect.top)
            dist_ty = abs(self.rect.centery - sprite.rect.bottom)
            # horizontal
            if direction == 'horizontal':
                # left wall
                if self.rect.centerx - self.radius <= sprite.rect.right and sprite.type == 'left':
                    self.rect.centerx = sprite.rect.right + self.radius + 1
                    # reverse direction & update pos
                    self.velocity.x *= -PLAYER_SOFTNESS[self.fillings]
                    self.pos_x = self.rect.centerx
                    self.bun_hit_sounds[randint(0, 4)].play()
                # right wall
                if self.rect.centerx + self.radius >= sprite.rect.left and sprite.type == 'right':
                    self.rect.centerx = sprite.rect.left - self.radius - 1
                # reverse direction & update pos
                    self.velocity.x *= -PLAYER_SOFTNESS[self.fillings]
                    self.pos_x = self.rect.centerx
                    self.bun_hit_sounds[randint(0, 4)].play()

            # vertical
            if direction == 'vertical':
                # top wall
                if self.rect.centery - self.radius <= sprite.rect.bottom and sprite.type == 'top':
                    self.rect.centery = sprite.rect.bottom + self.radius + 1
                    # reverse direction & update pos
                    self.velocity.y *= -PLAYER_SOFTNESS[self.fillings]
                    self.pos_y = self.rect.centery
                    self.bun_hit_sounds[randint(0, 4)].play()
                # bottom wall
                if self.rect.centery + self.radius >= sprite.rect.top and sprite.type == 'bottom':
                    self.rect.centery = sprite.rect.top - self.radius - 1
                    # reverse direction & update pos
                    self.velocity.y *= -PLAYER_SOFTNESS[self.fillings]
                    self.pos_y = self.rect.centery
                    self.bun_hit_sounds[randint(0, 4)].play()

    def soda_collision(self):
        for soda in self.sodas:
            collided_sprites = []
            # check if self than get values
            dx = self.rect.centerx - self.sodas[soda].rect.centerx
            dy = self.rect.centery - self.sodas[soda].rect.centery
            distance = sqrt((dx ** 2) + (dy ** 2))
            total_radii = self.radius + self.sodas[soda].radius
            depth = total_radii - distance
             # check if distance is less than the total radius
            if distance <= total_radii:
                collided_sprites.append(soda)

            # collision resolution
            if collided_sprites:
                for soda in collided_sprites:
                    # general
                    dx = self.rect.centerx - self.sodas[soda].rect.centerx
                    dy = self.rect.centery - self.sodas[soda].rect.centery
                    distance = sqrt((dx ** 2) + (dy ** 2))
                    impact_line = pygame.Vector2(self.sodas[soda].rect.centerx - self.rect.centerx, self.sodas[soda].rect.centery - self.rect.centery)

                    # overlap reslolution
                    overlap = distance - (self.radius + self.sodas[soda].radius)
                    dir = impact_line.copy()
                    dir = dir.normalize() * overlap
                    self.rect.centerx += dir.x
                    self.rect.centery += dir.y

                    # more general
                    mass_sum = self.mass + self.sodas[soda].mass
                    velocity_diff = pygame.Vector2(-self.velocity)

                    # consistent in formula for both
                    numerator = velocity_diff.dot(impact_line)
                    denominator = mass_sum * distance * distance

                    # self
                    delta_velocity_A = impact_line.copy()
                    delta_velocity_A *= 2 * self.sodas[soda].mass * numerator/denominator
                    self.velocity += delta_velocity_A * SODA_SPEED_MULTIPLYER
                    
                    if self.velocity.magnitude() > SODA_MAX_SPEED:
                        self.velocity.scale_to_length(SODA_MAX_SPEED)

                    # update pos
                    self.pos_x = self.rect.centerx
                    self.pos_y = self.rect.centery

    def garbage_collision(self):
        for garbage in self.garbages:
            collided_sprites = []
            # check if self than get values
            dx = self.rect.centerx - garbage.rect.centerx
            dy = self.rect.centery - garbage.rect.centery
            distance = sqrt((dx ** 2) + (dy ** 2))
            total_radii = self.radius + garbage.radius
            depth = total_radii - distance
             # check if distance is less than the total radius
            if distance <= total_radii:
                collided_sprites.append(garbage)

            # collision resolution
            if collided_sprites:
                self.garbage_can_sounds[randint(0, 2)].play()
                for garbage in collided_sprites:
                    # animate
                    garbage.animate = True

                    # general
                    dx = self.rect.centerx - garbage.rect.centerx
                    dy = self.rect.centery - garbage.rect.centery
                    distance = sqrt((dx ** 2) + (dy ** 2))
                    impact_line = pygame.Vector2(garbage.rect.centerx - self.rect.centerx, garbage.rect.centery - self.rect.centery)

                    # overlap reslolution
                    overlap = distance - (self.radius + garbage.radius)
                    dir = impact_line.copy()
                    dir = dir.normalize() * overlap
                    self.rect.centerx += dir.x
                    self.rect.centery += dir.y

                    # more general
                    mass_sum = self.mass + garbage.mass
                    velocity_diff = pygame.Vector2(-self.velocity)

                    # consistent in formula for both
                    numerator = velocity_diff.dot(impact_line)
                    denominator = mass_sum * distance * distance

                    # self
                    delta_velocity_A = impact_line.copy()
                    delta_velocity_A *= 2 * garbage.mass * numerator/denominator
                    self.velocity += delta_velocity_A * GARBAGE_SPEED_MULTIPLYER
                    
                    if self.velocity.magnitude() > GARBAGE_MAX_SPEED:
                        self.velocity.scale_to_length(GARBAGE_MAX_SPEED)

                    # update pos
                    self.pos_x = self.rect.centerx
                    self.pos_y = self.rect.centery

    def ketchup_collision(self):
        in_ketchup = False
        for ketchup in self.ketchups:
            collide_sprites = self.rect.colliderect(ketchup.hitbox)
            if collide_sprites:
                self.ketchup_sounds[randint(0, 7)].play() if not self.old_in_ketchup and self.velocity else None
                in_ketchup = True
                self.friction = KETCHUP_FRICTION
            else:
                self.friction = PLAYER_FRICTION[self.fillings]
        self.old_in_ketchup = in_ketchup

    def toaster_collision(self, direction):
        for sprite in self.toasters:
            cx = self.rect.centerx
            cy = self.rect.centery
            rx = sprite.hitbox.left
            ry = sprite.hitbox.top
            rw = sprite.hitbox.width
            rh = sprite.hitbox.height

            testx = cx
            testy = cy

            if (cx < rx): testx = rx # left edge
            elif (cx > rx + rw): testx = rx + rw # right edge

            if (cy < ry): testy = ry # top edge
            elif (cy > ry + rh): testy = ry + rh # bottom edge

            distx = cx-testx
            disty = cy-testy
            distance = sqrt((distx*distx) + (disty*disty))

            if distance <= self.radius:
                self.bun_hit_sounds[randint(0, 4)].play()
                if direction == 'horizontal':
                    if self.velocity.x > 0: self.rect.right = sprite.hitbox.left - 1
                    if self.velocity.x < 0: self.rect.left = sprite.hitbox.right + 1
                    self.pos_x = self.rect.centerx
                    self.velocity.x *= -PLAYER_SOFTNESS[self.fillings]
                else:
                    if self.velocity.y > 0: self.rect.bottom = sprite.hitbox.top - 1
                    if self.velocity.y < 0: self.rect.top = sprite.hitbox.bottom + 1
                    self.pos_y = self.rect.centery
                    self.velocity.y *= -PLAYER_SOFTNESS[self.fillings]

    def player_collisions(self):
        for player_inst_2 in self.players:
            collided_sprites = []
            # check if self than get values
            if self is not self.players[player_inst_2]:
                dx = self.rect.centerx - self.players[player_inst_2].rect.centerx
                dy = self.rect.centery - self.players[player_inst_2].rect.centery
                distance = sqrt((dx ** 2) + (dy ** 2))
                total_radii = self.radius + self.players[player_inst_2].radius
                depth = total_radii - distance
                # check if distance is less than the total radius
                if distance <= total_radii:
                    collided_sprites.append(player_inst_2)
                    
            # collision resolution
            if collided_sprites:
                self.bun_hit_sounds[randint(0, 4)].play()
                for player_inst_2 in collided_sprites:
                    # general
                    dx = self.rect.centerx - self.players[player_inst_2].rect.centerx
                    dy = self.rect.centery - self.players[player_inst_2].rect.centery
                    distance = sqrt((dx ** 2) + (dy ** 2))
                    impact_line = pygame.Vector2(self.players[player_inst_2].rect.centerx - self.rect.centerx, self.players[player_inst_2].rect.centery - self.rect.centery)

                    # overlap reslolution
                    overlap = distance - (self.radius + self.players[player_inst_2].radius)
                    dir = impact_line.copy()
                    dir = dir.normalize() * (overlap * 0.5)
                    if self.rect.centerx <= self.players[player_inst_2].rect.centerx:
                        self.rect.centerx -= dir.x + 1
                        self.players[player_inst_2].rect.centerx += dir.x + 1
                    else:
                        self.rect.centerx += dir.x + 1
                        self.players[player_inst_2].rect.centerx -= dir.x + 1
                        
                    if self.rect.centery <= self.players[player_inst_2].rect.centery:
                        self.rect.centery -= dir.y + 1
                        self.players[player_inst_2].rect.centery += dir.y + 1
                    else:
                        self.rect.centery += dir.y + 1
                        self.players[player_inst_2].rect.centery -= dir.y + 1

                    # more general
                    mass_sum = self.mass + self.players[player_inst_2].mass
                    velocity_diff = pygame.Vector2(self.players[player_inst_2].velocity - self.velocity)

                    # consistent in formula for both
                    numerator = velocity_diff.dot(impact_line)
                    denominator = mass_sum * distance * distance

                    # self
                    delta_velocity_A = impact_line.copy()
                    delta_velocity_A *= 2 * self.players[player_inst_2].mass * numerator/denominator
                    self.velocity += delta_velocity_A

                    # player_inst_2
                    delta_velocity_B = impact_line.copy()
                    delta_velocity_B *= -2 * self.players[player_inst_2].mass * numerator/denominator
                    self.players[player_inst_2].velocity += delta_velocity_B

                    # update pos
                    self.pos_x = self.rect.centerx
                    self.pos_y = self.rect.centery

    def update(self, dt):
        self.old_rect = self.rect.copy()
        self.update_sprite()
        self.update_attrs()
        self.transform()
        self.move(dt)

class BunShadow(Player):
    def __init__(self, surf, pos, groups, _, player, __, ___, ____, _____):
        super().__init__(surf, pos, groups, _, __, ___, ____, _____, None, None, None, None)
        self.player = player
        self.offset = pygame.Vector2(8, 8)
        self.shadow = True
        self.width = 77
        self.height = 77

    def move(self, dt):
        self.rect.center = self.player.rect.center + self.offset

    def wall_collision(self, direction):
        pass

    def shake(self, max_shake):
        pass

    def update_attrs(self):
        pass

    def launch(self, dir, spd):
        self.image = self.clean_surf
        self.squash = 0
        self.angle = 0

class Profile(Sprite):
    def __init__(self, surfs, pos, groups, player, filling_num_order):
        super().__init__(surfs[0], pos, groups)
        self.surfs = surfs
        self.player = player
        self.profile = True
        self.current_surf = 0
        self.image = self.surfs[self.current_surf]
        self.rect = self.image.get_rect(center = pos)
        self.filling_num_order = filling_num_order

    def update_image(self):
        try:
            self.image = self.surfs[self.filling_num_order[self.player.fillings-1]]
        except:
            self.image = self.surfs[5]
        self.rect = self.image.get_rect(center = self.rect.center)

class Highlight(Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(surf, pos, groups)
        self.highlight = True
    
class TurnIndicator(Sprite):
    def __init__(self, surf, pos, id, groups):
        super().__init__(surf, pos, groups)
        self.id = id
        self.visible = False
        self.active = False
        self.turn_indicator = True
        self.spd = 6000
        self.wait_dur = 1000
        self.wait_start_time = -1000
        self.pos = pos

    def update(self, dt):
        current_time = pygame.time.get_ticks()

        self.visible = True if self.active else False
        self.rect.centerx += self.spd * dt if self.active and current_time - self.wait_start_time > self.wait_dur else 0
        if self.active and self.rect.centerx > WINDOW_WIDTH/2 and self.wait_start_time == -1000:
            self.rect.centerx = WINDOW_WIDTH/2
            self.wait_start_time = pygame.time.get_ticks()
        if self.rect.left >= WINDOW_WIDTH:
            self.active = False
            self.rect.center = self.pos
            self.wait_start_time = -1000

class You(Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(surf, pos, groups)
        self.visible = True
        self.you = True
        
class ItemScreen(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.clean_surf = surf
        self.image = self.clean_surf.copy()
        self.rect = self.image.get_frect(center = pos)
        self.alpha = 0
        self.image.fill((255, 255, 255, self.alpha), None, pygame.BLEND_RGBA_MULT)
        self.visible = False
        self.should_fade = False
        self.fade_spd = 750
        self.item_screen = True

    def fade(self, dt):
        self.image = self.clean_surf
        self.image = self.image.copy()
        self.alpha += self.fade_spd * dt if self.should_fade == 'in' else -self.fade_spd * dt
        alpha = self.alpha
        alpha = 0 if self.alpha < 0 else alpha
        alpha = 255 if self.alpha > 255 else alpha
        self.image.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)

    def update(self, dt):
        self.visible = True if self.should_fade and not pygame.mouse.get_pressed()[2] else False
        self.fade(dt) if self.should_fade else None
        if self.alpha <= 0 and self.should_fade == 'out':
            self.should_fade = False

class ItemSelector(pygame.sprite.Sprite):
    def __init__(self, surfs, pos, type, groups):
        super().__init__(groups)
        self.clean_surfs = surfs
        self.image = self.clean_surfs[0].copy()
        self.rect = self.image.get_frect()
        self.rect = self.image.get_frect(center = pos)
        self.rect.top = pos[1]
        self.alpha = 0
        self.image.fill((255, 255, 255, self.alpha), None, pygame.BLEND_RGBA_MULT)
        self.visible = False
        self.should_fade = False
        self.fade_spd = 750
        self.item_selector = True
        self.current_surf = 0
        self.collision_rect = self.rect.inflate(-160, -260)
        self.collision_rect.move_ip(0, -115)
        self.type = type
        self.click_2 = mixer.Sound(join('audio', 'clicks', 'click 10.wav'))
        self.click_2.set_volume(0.2)
        self.old_hover = False

    def fade(self, dt):
        self.image = self.clean_surfs[self.current_surf]
        self.image = self.image.copy()
        self.alpha += self.fade_spd * dt if self.should_fade == 'in' else -self.fade_spd * dt
        alpha = self.alpha
        alpha = 0 if self.alpha < 0 else alpha
        alpha = 255 if self.alpha > 255 else alpha
        self.image.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        if self.collision_rect.collidepoint(mouse_pos) and self.should_fade == 'in' and not pygame.mouse.get_pressed()[2]:
            self.current_surf = 1
            self.click_2.play() if not self.old_hover else None
            self.old_hover = True
        else:
            self.current_surf = 0
            self.old_hover = False

        self.visible = True if self.should_fade and not pygame.mouse.get_pressed()[2] else False
        self.fade(dt) if self.should_fade else None

        if self.alpha <= 0 and self.should_fade == 'out':
            self.should_fade = False

class ItemPlacer(pygame.sprite.Sprite):
    def __init__(self, surfs, type, groups, players, zone, items):
        super().__init__(groups)
        self.type = type
        self.clean_surfs = surfs
        self.image = self.clean_surfs[0][0].copy() if self.type == 'toaster' else self.clean_surfs.copy()
        self.rect = self.image.get_frect(center = pygame.mouse.get_pos())
        self.tint = 255
        self.snap = 49.5
        self.snapx_offset = -3
        self.snapy_offset = 14
        self.players = players
        self.zone = zone
        self.items = items
        self.radius = 50
        self.dir = 0 # 0 = up | 1 = right | 2 = down | 3 = left
        self.item = True
        self.transform()
        self.click_delay = 50
        self.click_time = -1000
        self.click_sound = mixer.Sound(join('audio', 'clicks', 'click 3 v2.wav'))
        self.click_sound.set_volume(0.4)
        if self.type == 'toaster':
            rotate_volume = 0.8
            rotate_sound_1 = mixer.Sound(join('audio', 'game', 'toaster rotate 1.mp3'))
            rotate_sound_1.set_volume(rotate_volume)
            rotate_sound_2 = mixer.Sound(join('audio', 'game', 'toaster rotate 2.mp3'))
            rotate_sound_2.set_volume(rotate_volume)
            rotate_sound_3 = mixer.Sound(join('audio', 'game', 'toaster rotate 3.mp3'))
            rotate_sound_3.set_volume(rotate_volume)
            self.rotate_sounds = [rotate_sound_1, rotate_sound_2, rotate_sound_3]

    def transform(self):
        self.image = self.clean_surfs.copy() if self.type != 'toaster' else self.clean_surfs[self.dir][0].copy()
        self.image.fill((255, self.tint, self.tint, 190), None, pygame.BLEND_RGBA_MIN)

    def rotate(self):
        keys = pygame.key.get_just_pressed()

        if keys[pygame.K_r]:
            self.rotate_sounds[randint(0, 2)].play()
            self.dir = self.dir + 1 if self.dir != 3 else 0
            self.transform()

    def check_can_place(self):
        if self.rect.centerx < 344 or self.rect.centerx > WINDOW_WIDTH - 350:
            return 0
        elif self.rect.centery < 64 or self.rect.centery > WINDOW_HEIGHT - 70:
            return 0
        elif self.rect.centerx < 440 and self.rect.centery < 200 or self.rect.centerx < 450 and self.rect.centery < 115:
            if self.type != 'ketchup':
                return 0
        elif self.rect.centerx > WINDOW_WIDTH - 440 and self.rect.centery < 200 or self.rect.centerx > WINDOW_WIDTH - 450 and self.rect.centery < 115:
            if self.type != 'ketchup':
                return 0
        elif self.rect.centerx < 440 and self.rect.centery > WINDOW_HEIGHT - 200 or self.rect.centerx < 450 and self.rect.centery > WINDOW_HEIGHT - 115:
            if self.type != 'ketchup':
                return 0
        elif self.rect.centerx > WINDOW_WIDTH - 440 and self.rect.centery > WINDOW_HEIGHT - 200 or self.rect.centerx > WINDOW_WIDTH - 450 and self.rect.centery > WINDOW_HEIGHT - 115:
            if self.type != 'ketchup':
                return 0
        
        if self.type != 'ketchup':
            for player in self.players.values():
                d = sqrt(((self.rect.centerx - player.rect.centerx)**2) + ((self.rect.centery - player.rect.centery)**2))
                if d <= self.radius + player.radius:
                    return 0
        
        if self.type != 'ketchup':
            d = sqrt(((self.rect.centerx - self.zone.rect.centerx)**2) + ((self.rect.centery - self.zone.rect.centery)**2))
            if d <= self.radius + self.zone.radius:
                return 0
            
        if self.type != 'ketchup':
            for sprite in self.items:
                if sprite.type != 'ketchup':
                    if self.rect.colliderect(sprite.rect.inflate(-100, -100)):
                        return 0

        return 255

    def update(self, dt):
        old_rect_center = self.rect.center
        old_tint = self.tint
        mouse_pos = pygame.mouse.get_pos()

        self.rotate() if self.type == 'toaster' else None

        self.tint = self.check_can_place()
        self.transform() if self.tint != old_tint else None

        x = round(mouse_pos[0]/self.snap)
        y = round(mouse_pos[1]/self.snap)
        self.rect.centerx = x * self.snap + self.snapx_offset
        self.rect.centery = y * self.snap + self.snapy_offset

        if old_rect_center != self.rect.center:
            if pygame.time.get_ticks() - self.click_time >= self.click_delay:
                self.click_sound.play()
                self.click_time = pygame.time.get_ticks()

class GarbageCan(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.clean_frames = frames
        self.frames_num = len(self.clean_frames)
        self.image = self.clean_frames[0].copy()
        self.rect = self.image.get_frect(center = pos)
        self.current_frame = 0
        self.radius = 50
        self.animate_spd = 40
        self.item = True
        self.animate = False
        self.mass = GARBAGE_MASS
        self.type = 'garbage'

    def update(self, dt):
        old_current_frame = self.current_frame
        self.current_frame = self.current_frame + (self.animate_spd * dt) if self.animate else 0
        if self.current_frame > self.frames_num:
            self.current_frame = 0
            self.animate = False
        
        self.image = self.clean_frames[floor(self.current_frame)].copy() if old_current_frame != self.current_frame else self.image

class Ketchup(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.clean_surf = surf
        self.image = self.clean_surf.copy()
        self.rect = self.image.get_frect(center = pos)
        self.hitbox = self.rect.copy().inflate(-20, -20)
        self.ketchup = True
        self.type = 'ketchup'

    def update(self, dt):
        pass

class Toaster(pygame.sprite.Sprite):
    def __init__(self, frames, pos, dir, groups):
        super().__init__(groups)
        self.clean_frames = frames
        self.frames_num = len(self.clean_frames)
        self.image = self.clean_frames[0].copy()
        self.rect = self.image.get_frect(center = pos)
        if dir == 0: self.hitbox = self.rect.copy().inflate(-36, -50).move(0, 2)
        if dir == 2: self.hitbox = self.rect.copy().inflate(-36, -50).move(0, -2)
        if dir == 1: self.hitbox = self.rect.copy().inflate(-50, -36).move(-2, 0)
        if dir == 3: self.hitbox = self.rect.copy().inflate(-50, -36).move(2, 0)
        self.def_frame = len(self.clean_frames) - 3
        self.current_frame = self.def_frame
        self.animate_spd = 50
        self.item = True
        self.animate = False
        self.shoot = False
        self.shoot_delay = 150
        self.shoot_time = 0
        self.dir = dir
        self.pos = pos
        self.type = 'toaster'
        self.mask = pygame.mask.from_surface(self.image)
        self.bread_left = 3

    def animation(self, dt):
        old_current_frame = self.current_frame
        self.current_frame = self.current_frame + (self.animate_spd * dt) if self.animate else 0
        self.shoot_time = 0

        if self.current_frame >= self.frames_num and self.bread_left > 0:
            self.current_frame = 0
            self.shoot_time = pygame.time.get_ticks() if self.bread_left > 0 else None
            self.shoot = True if self.bread_left > 0 else False
        
        if self.bread_left > 0:
            self.image = self.clean_frames[floor(self.current_frame)].copy() if old_current_frame != self.current_frame else self.image
        else:
            self.image = self.clean_frames[0].copy() if old_current_frame != self.current_frame else self.image

    def update(self, dt):
        self.animation(dt) if pygame.time.get_ticks() - self.shoot_time >= self.shoot_delay or not self.shoot_time else None
        self.image = self.clean_frames[self.def_frame].copy() if not self.animate else self.image
        
class Bread(pygame.sprite.Sprite):
    def __init__(self, surf, pos, dir, groups, sodas, walls, players, items, home_toaster, hit_sounds):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.coll_rect = self.rect.inflate(-10, -20)
        self.spd = BREAD_SPEED
        self.sodas = sodas
        self.walls = walls
        self.players = players
        self.items = items
        self.home_toaster = home_toaster
        self.bread = True
        self.dir = dir
        self.radius = 30
        self.mass = BREAD_MASS
        self.velocity = pygame.Vector2(0, -1 * self.spd) if self.dir == 0 else None
        self.velocity = pygame.Vector2(1 * self.spd, 0) if self.dir == 1 else self.velocity
        self.velocity = pygame.Vector2(0, 1 * self.spd) if self.dir == 2 else self.velocity
        self.velocity = pygame.Vector2(-1 * self.spd, 0) if self.dir == 3 else self.velocity

        self.hit_sounds = hit_sounds

        if self.dir % 2:
            self.rect.centerx += 25 if self.dir == 1 else -25
        else:
            self.rect.centery += 25 if self.dir == 2 else -25

    def check_collisions(self, dt):
        self.coll_rect.center = self.rect.center

        for sprite in self.sodas:
            d = sqrt(((self.coll_rect.centerx - sprite.rect.centerx)**2)+((self.coll_rect.centery - sprite.rect.centery)**2))

            if d <= self.radius + sprite.radius:
                self.hit_sounds[randint(0, len(self.hit_sounds)-1)].play()
                self.kill()

        for sprite in self.walls:
            if self.coll_rect.colliderect(sprite.rect):
                self.hit_sounds[randint(0, len(self.hit_sounds)-1)].play()
                self.kill()

        for sprite in self.items:
            if self.coll_rect.colliderect(sprite.rect) and not hasattr(sprite, 'ketchup') and sprite != self.home_toaster:
                self.hit_sounds[randint(0, len(self.hit_sounds)-1)].play()
                self.kill()

        self.player_collision()

    def player_collision(self):
        for player in self.players.values():
            collided_sprites = []
            # check if self than get values
            dx = self.rect.centerx - player.rect.centerx
            dy = self.rect.centery - player.rect.centery
            distance = sqrt((dx ** 2) + (dy ** 2))
            total_radii = self.radius + player.radius
            depth = total_radii - distance
            # check if distance is less than the total radius
            if distance <= total_radii:
                collided_sprites.append(player)
                    
            # collision resolution
            if collided_sprites:
                self.hit_sounds[randint(0, len(self.hit_sounds)-1)].play()
                for player in collided_sprites:
                    # general
                    dx = self.rect.centerx - player.rect.centerx
                    dy = self.rect.centery - player.rect.centery
                    distance = sqrt((dx ** 2) + (dy ** 2))
                    impact_line = pygame.Vector2(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)

                    # overlap reslolution
                    overlap = distance - (self.radius + player.radius)
                    dir = impact_line.copy()
                    dir = dir.normalize() * (overlap * 0.5)
                    self.rect.centerx += dir.x
                    self.rect.centery += dir.y
                    player.rect.centerx -= dir.x
                    player.rect.centery -= dir.y

                    # more general
                    mass_sum = self.mass + player.mass
                    velocity_diff = pygame.Vector2(player.velocity - self.velocity)

                    # consistent in formula for both
                    numerator = velocity_diff.dot(impact_line)
                    denominator = mass_sum * distance * distance

                    # self
                    delta_velocity_A = impact_line.copy()
                    delta_velocity_A *= 2 * player.mass * numerator/denominator
                    self.velocity += delta_velocity_A

                    # player
                    delta_velocity_B = impact_line.copy()
                    delta_velocity_B *= (-2 * player.mass * numerator/denominator)/BREAD_POWER
                    player.velocity += delta_velocity_B

                    # update pos
                    player.pos_x = player.rect.centerx
                    player.pos_y = player.rect.centery

                    self.kill()

    def update(self, dt):
        if self.dir % 2:
            self.rect.centerx += self.spd * dt if self.dir == 1 else -self.spd * dt
        else:
            self.rect.centery += self.spd * dt if self.dir == 2 else -self.spd * dt

        self.check_collisions(dt)

class Rotate(pygame.sprite.Sprite):
    def __init__(self, surf, groups, item_placer):
        super().__init__(groups)
        self.item_placer = item_placer
        self.image = surf
        self.rect = self.image.get_frect(center = self.item_placer.rect.center)
        self.rect.centery -= 70
        self.rotate = True
        
    def update(self, dt):
        self.rect.center = self.item_placer.rect.center
        self.rect.centery -= 70

class Drop(pygame.sprite.Sprite):
    def __init__(self, surf, shadow_surf, pos, groups, star_sounds, id = False):
        super().__init__(groups)
        self.id = id
        self.surf = surf
        self.shadow_surf = shadow_surf
        self.image = shadow_surf
        self.rect = self.image.get_frect(center = pos)
        self.size = 0.7
        self.start_drop_size = 0.5
        self.shadow_drop_spd = 1
        self.drop_spd = 7
        self.on_screen = False
        self.dropping = True
        self.pos = pos
        self.active = True if not id else False
        self.visible = True if not id else False
        self.id = id
        self.spawn_time = False
        self.star_sounds = star_sounds
        self.audio_played = False
        if self.id == 1:
            self.active = True
            self.visible = True
        elif self.id == 2:
            self.spawn_time = pygame.time.get_ticks()
            self.spawn_delay = 100
        elif self.id == 3:
            self.spawn_time = pygame.time.get_ticks()
            self.spawn_delay = 200

    def transform(self):
        self.image = self.surf.copy() if self.on_screen else self.shadow_surf.copy()
        self.image = \
            pygame.transform.smoothscale(self.image, (self.surf.get_width()/self.size, self.surf.get_height()/self.size)) \
            if self.on_screen else \
            pygame.transform.smoothscale(self.image, (self.shadow_surf.get_width()/self.size, self.shadow_surf.get_height()/self.size))
        self.rect = self.image.get_frect(center = self.pos)

    def update(self, dt):
        if self.spawn_time:
            current_time = pygame.time.get_ticks()
            if current_time - self.spawn_time >= self.spawn_delay:
                self.active = True
                self.visible = True
        if self.active:
            self.transform()

            self.size += self.drop_spd * dt if self.on_screen else self.shadow_drop_spd * dt

            if self.size >= 2 and not self.on_screen:
                self.size = self.start_drop_size
                self.on_screen = True

            if self.size >= 2.5 and self.on_screen:
                if not self.audio_played: self.star_sounds[randint(0, 2)].play()
                self.audio_played = True
                self.active = False
                self.visible = False

class Star(pygame.sprite.Sprite):
    def __init__(self, surf, pos, id, groups):
        super().__init__(groups)
        self.id = id
        self.pos = pos
        self.dir = pygame.Vector2(0, -1)
        self.dir.rotate_ip(id * -72)
        self.surf = surf
        self.image = self.surf.copy()
        self.rect = self.image.get_frect(center = self.pos)
        self.alpha = 400
        self.spd = 600
        self.spd_decline = 1000
        self.spin_spd = 150
        self.star = True
        self.velocity = pygame.Vector2(self.dir.x, self.dir.y) * self.spd
        self.fade_spd = 800
        self.angle = 0
        self.dir_spin_spd = 150

    def update(self, dt):
        self.rect.centerx += self.velocity.x * dt
        self.rect.centery += self.velocity.y * dt

        self.spd = self.spd - (self.spd_decline * dt) if self.spd > 200 else 200
        self.velocity = pygame.Vector2(self.dir.x, self.dir.y) * self.spd
        self.alpha -= self.fade_spd * dt
        alpha = self.alpha if not self.alpha > 255 else 255
        self.angle -= self.spin_spd * dt
        self.dir.rotate_ip(self.dir_spin_spd * dt)

        if self.alpha <= 0:
            self.kill()
        else:
            self.image = self.surf.copy()
            self.image = pygame.transform.rotate(self.image, self.angle)
            self.image.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)

class WinScreen(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.surf = surf
        self.pos = pos
        self.image = self.surf.copy()
        self.rect = self.image.get_frect(center = self.pos)
        self.alpha = 0
        self.image.fill((255, 255, 255, self.alpha), None, pygame.BLEND_RGBA_MULT)
        self.fade_spd = MAIN_MENU_FADE_SPD
        self.win_screen = True
        self.visible = True

    def update(self, dt):
        pass
        old_alpha = self.alpha
        self.alpha += self.fade_spd * dt if self.alpha != 255 else 0
        self.alpha = 255 if self.alpha > 255 else self.alpha
        if self.alpha != old_alpha:
            self.image = self.surf.copy()
            self.image.fill((255, 255, 255, self.alpha), None, pygame.BLEND_RGBA_MULT)
