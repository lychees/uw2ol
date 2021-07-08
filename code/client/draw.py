import pygame

# add relative directory to python_path
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

# import from common(dir)
import constants as c
from hashes.hash_ports_meta_data import hash_ports_meta_data

from sprites import Explosion

def draw(self):
    """argument self is game"""
    # clear
    self.screen_surface.fill(c.BLACK)

    # draw
    if self.my_role:
        draw_logged_in_state(self)
        self.all_sprites.update()
        self.mark_sprites.update()
        self.ui_manager.draw_ui(self.screen_surface)
    else:
        draw_not_logged_in_state(self)

    # flip
    pygame.display.flip()

def draw_logged_in_state(self):
    # draw map
    now_map = self.my_role.map

        # in port
    if now_map.isdigit():
        x = self.screen_surface_rect.centerx - self.my_role.x
        y = self.screen_surface_rect.centery - self.my_role.y
        self.screen_surface.blit(self.images['port'], (x, y))

            # to cover port edges

                # bottom
        self.screen_surface.blit(self.images['building_bg'],
                                 (50, y + (c.PORT_TILES_COUNT * c.PIXELS_COVERED_EACH_MOVE)))
                # top
        self.screen_surface.blit(self.images['building_bg'],
                                 (50, y - c.BUILDING_BG_SIZE))
                # left
        self.screen_surface.blit(self.images['building_bg'],
                                 (x - c.BUILDING_BG_SIZE, 0))

                # right
        self.screen_surface.blit(self.images['building_bg'],
                                 (x + (c.PORT_TILES_COUNT * c.PIXELS_COVERED_EACH_MOVE), 0))

        # at sea
    elif now_map == 'sea':
        x = -(c.PARTIAL_WORLD_MAP_TILES_IN_ONE_DIRECTION * c.PIXELS_COVERED_EACH_MOVE
              - self.screen_surface_rect.centerx + self.my_role.x
              - self.map_maker.x_tile * c.PIXELS_COVERED_EACH_MOVE)
        y = -(c.PARTIAL_WORLD_MAP_TILES_IN_ONE_DIRECTION * c.PIXELS_COVERED_EACH_MOVE
              - self.screen_surface_rect.centery + self.my_role.y
              - self.map_maker.y_tile * c.PIXELS_COVERED_EACH_MOVE)

        self.screen_surface.blit(self.images['sea'], (x, y))

        # in battle
    else:
        self.screen_surface.blit(self.images['battle'], (0, 0))

    # draw based on map

        # in building
    if self.my_role.in_building_type:
            # bg
        self.screen_surface.blit(self.images['building_bg'], (c.HUD_WIDTH, 0))
            # person
        self.screen_surface.blit(self.building_image, (c.HUD_WIDTH + 5, 5))

            # dialog box
        self.screen_surface.blit(self.images['building_chat'], (c.HUD_WIDTH + c.BUILDING_PERSON_WIDTH + 10, 0))
            # dialog
        building_text_trans = self.translator.translate(self.building_text)
        blit_text(self.screen_surface, building_text_trans, (c.HUD_WIDTH + c.BUILDING_PERSON_WIDTH + 10 + 10, 5), self.font)
        draw_hud(self)

        # not in building
    else:
            # in port
        if now_map.isdigit():
            draw_in_port(self)
            draw_hud(self)

            # at sea
        elif now_map == 'sea':
            draw_at_sea(self)
            draw_hud(self)

                # at sea text
            draw_text(self, self.translator.translate('At Sea'), c.WINDOW_WIDTH - 100, 15)

                # max days at sea
            draw_text(self, self.translator.translate('Max Days'), c.WINDOW_WIDTH - 100, 120)
            if self.my_role.additioanl_days_at_sea:
                draw_text(self, str(self.max_days_at_sea) + '*', c.WINDOW_WIDTH - 100, 140)
            else:
                draw_text(self, str(self.max_days_at_sea), c.WINDOW_WIDTH - 100, 140)

                # days spent at sea
            draw_text(self, self.translator.translate('Days Spent'), c.WINDOW_WIDTH - 100, 160)
            draw_text(self, str(self.days_spent_at_sea), c.WINDOW_WIDTH - 100, 180)

            # in battle
        else:
            draw_in_battle(self)

    # draw speach
    draw_speech(self)

def draw_hud(self):
    # left hud
    self.screen_surface.blit(self.images['hud_left'], (0, 0))
    hud_left_rect = self.images['hud_left'].get_rect()

        # year and time of day
    trans = self.translator
    draw_text(self, trans.translate('A.D. 1492'), 10, 25)
    draw_text(self, trans.translate('Godspeed'), 10, 139)

        # LV
    draw_text(self, 'Lv', 10, c.WINDOW_HIGHT - 120 - 40)
    draw_text(self, str(self.my_role.mates[0].lv), 10, c.WINDOW_HIGHT - 120 - 20)

        # gold ingots
    gold_ingots = int(self.my_role.gold / 10000)
    gold_coins = self.my_role.gold - (gold_ingots * 10000)

    draw_text(self, trans.translate('Gold Ingots'), 10, c.WINDOW_HIGHT - 120)
    draw_text(self, str(gold_ingots), 10, c.WINDOW_HIGHT - 120 + 20)

        # gold coins
    draw_text(self, trans.translate('Gold Coins'), 10, c.WINDOW_HIGHT - 120 +40)
    draw_text(self, str(gold_coins), 10, c.WINDOW_HIGHT - 120 + 60)

    # right hud
    self.screen_surface.blit(self.images['hud_right'], (c.WINDOW_WIDTH - hud_left_rect.width, 0))

        # if in port
    if self.my_role.map.isdigit():

        # if normal ports
        if int(self.my_role.map) <= 99:
            # port name
            port_name = hash_ports_meta_data[int(self.my_role.map) + 1]['name']
            port_name = self.trans(port_name)
            draw_text(self, port_name, c.WINDOW_WIDTH - 100, 5)

            economy_id = hash_ports_meta_data[int(self.my_role.map) + 1]['economyId']
            region_name = hash_ports_meta_data['markets'][economy_id]
            draw_text(self, self.translator.translate(region_name), c.WINDOW_WIDTH - 100, 20)

            # index
            economy_index = self.my_role.port_economy
            industry_index = self.my_role.port_industry

            draw_text(self, self.translator.translate('Economy'), c.WINDOW_WIDTH - 100, 80)
            draw_text(self, str(economy_index), c.WINDOW_WIDTH - 100, 100)

            draw_text(self, self.translator.translate('Industry'), c.WINDOW_WIDTH - 100, 120)
            draw_text(self, str(industry_index), c.WINDOW_WIDTH - 100, 140)

        # supply ports
        else:
            port_name = hash_ports_meta_data[int(self.my_role.map) + 1]['name']
            port_name = self.trans(port_name)
            draw_text(self, port_name, c.WINDOW_WIDTH - 100, 5)

        # at sea
    else:
        draw_text(self, self.translator.translate('Speed'), c.WINDOW_WIDTH - 100, 80)
        draw_text(self, str(self.my_role.speed) + ' ' +
                  self.translator.translate('knots'), c.WINDOW_WIDTH - 100, 100)

def draw_text(self, text, x, y, color=c.BLACK):
    text_img = self.font.render(text, True, color)
    self.screen_surface.blit(text_img, (x, y))

def draw_in_port(self):
    # draw npcs
        # static
    if self.dog:
        self.dog.draw()
    if self.old_man:
        self.old_man.draw()
    if self.agent:
        self.agent.draw()
        # dynamic
    if self.man:
        self.man.draw()
    if self.woman:
        self.woman.draw()

    # draw my role

        # image
    direction = self.my_role.direction
    frame = self.my_role.person_frame
    person_rect = person_direction_2_rect_in_sprite_sheet(self, direction, frame)

    self.screen_surface.blit(self.images['person_tileset'], self.screen_surface_rect.center, person_rect)

        # name
        # draw_text(self, str(self.my_role.name), c.WINDOW_WIDTH / 2, -15 + c.WINDOW_HIGHT / 2, c.YELLOW)

    # draw other roles
    self.other_roles_rects = {}
    for role in self.other_roles.values():
        # image
        direction = role.direction
        frame = role.person_frame
        person_rect = person_direction_2_rect_in_sprite_sheet(self, direction, frame)

        x = self.screen_surface_rect.centerx - self.my_role.x + role.x
        y = self.screen_surface_rect.centery - self.my_role.y + role.y

        self.screen_surface.blit(self.images['person_tileset'], (x, y), person_rect)

        # set image rect
        image_rect = pygame.Rect(x, y, c.SHIP_SIZE_IN_PIXEL, c.SHIP_SIZE_IN_PIXEL)
        self.other_roles_rects[role.name] = image_rect

        # name
        draw_text(self, str(role.name), x, -15 + y, c.YELLOW)

        # target sign
        if self.my_role.enemy_name and role.name == self.my_role.enemy_name:
            draw_text(self, '[+]', x, -30 + y, c.YELLOW)

def draw_at_sea(self):
    # draw my role

        # image
    direction = self.my_role.direction
    ship_rect = ship_direction_2_rect_in_sprite_sheet(self, direction)

    self.screen_surface.blit(self.images['ship-tileset'], self.screen_surface_rect.center, ship_rect)

        # name
        # draw_text(self, str(self.my_role.name), c.WINDOW_WIDTH / 2, -15 + c.WINDOW_HIGHT / 2, c.YELLOW)

    # draw other roles
    self.other_roles_rects = {}
    for role in self.other_roles.values():
        # only draw nearby ones
        delta_x = abs(self.my_role.x - role.x)
        delta_y = abs(self.my_role.y - role.y)

        if delta_x <= 16 * c.PIXELS_COVERED_EACH_MOVE and delta_y <= 16 * c.PIXELS_COVERED_EACH_MOVE:
            # image
            direction = role.direction
            ship_rect = ship_direction_2_rect_in_sprite_sheet(self, direction, others=True)

            x = self.screen_surface_rect.centerx - self.my_role.x + role.x
            y = self.screen_surface_rect.centery - self.my_role.y + role.y

            self.screen_surface.blit(self.images['ship-tileset'], (x, y), ship_rect)

            # set image rect
            image_rect = pygame.Rect(x, y, c.SHIP_SIZE_IN_PIXEL, c.SHIP_SIZE_IN_PIXEL)
            self.other_roles_rects[role.name] = image_rect

            # name
            if role.is_npc():
                pass
            else:
                draw_text(self, str(role.name), x, -15 + y, c.YELLOW)

            # target sign
            if self.my_role.enemy_name and role.name == self.my_role.enemy_name:
                draw_text(self, '[+]', x, -30 + y, c.YELLOW)

def ship_direction_2_rect_in_sprite_sheet(self, direction, others=False):
    ship_rect = self.images['ship_at_sea'].get_rect()

    # my ship or others ship
    row_in_sprite = 1
    if others:
        row_in_sprite = 3

    # frame 1
    if self.ship_frame == 1:
        if direction == 'right':
            ship_rect = ship_rect.move(c.SHIP_SIZE_IN_PIXEL * 2, c.SHIP_SIZE_IN_PIXEL * row_in_sprite)
        elif direction == 'left':
            ship_rect = ship_rect.move(c.SHIP_SIZE_IN_PIXEL * 6, c.SHIP_SIZE_IN_PIXEL * row_in_sprite)
        elif direction == 'up':
            ship_rect = ship_rect.move(c.SHIP_SIZE_IN_PIXEL * 0, c.SHIP_SIZE_IN_PIXEL * row_in_sprite)
        elif direction == 'down':
            ship_rect = ship_rect.move(c.SHIP_SIZE_IN_PIXEL * 4, c.SHIP_SIZE_IN_PIXEL * row_in_sprite)

        elif direction == 'ne':
            ship_rect = ship_rect.move(c.SHIP_SIZE_IN_PIXEL * 2, c.SHIP_SIZE_IN_PIXEL * row_in_sprite)
        elif direction == 'nw':
            ship_rect = ship_rect.move(c.SHIP_SIZE_IN_PIXEL * 6, c.SHIP_SIZE_IN_PIXEL * row_in_sprite)
        elif direction == 'se':
            ship_rect = ship_rect.move(c.SHIP_SIZE_IN_PIXEL * 2, c.SHIP_SIZE_IN_PIXEL * row_in_sprite)
        elif direction == 'sw':
            ship_rect = ship_rect.move(c.SHIP_SIZE_IN_PIXEL * 6, c.SHIP_SIZE_IN_PIXEL * row_in_sprite)

    # frame 2
    else:
        if direction == 'right':
            ship_rect = ship_rect.move(c.SHIP_SIZE_IN_PIXEL * 3, c.SHIP_SIZE_IN_PIXEL * row_in_sprite)
        elif direction == 'left':
            ship_rect = ship_rect.move(c.SHIP_SIZE_IN_PIXEL * 7, c.SHIP_SIZE_IN_PIXEL * row_in_sprite)
        elif direction == 'up':
            ship_rect = ship_rect.move(c.SHIP_SIZE_IN_PIXEL * 1, c.SHIP_SIZE_IN_PIXEL * row_in_sprite)
        elif direction == 'down':
            ship_rect = ship_rect.move(c.SHIP_SIZE_IN_PIXEL * 5, c.SHIP_SIZE_IN_PIXEL * row_in_sprite)

        elif direction == 'ne':
            ship_rect = ship_rect.move(c.SHIP_SIZE_IN_PIXEL * 3, c.SHIP_SIZE_IN_PIXEL * row_in_sprite)
        elif direction == 'nw':
            ship_rect = ship_rect.move(c.SHIP_SIZE_IN_PIXEL * 7, c.SHIP_SIZE_IN_PIXEL * row_in_sprite)
        elif direction == 'se':
            ship_rect = ship_rect.move(c.SHIP_SIZE_IN_PIXEL * 3, c.SHIP_SIZE_IN_PIXEL * row_in_sprite)
        elif direction == 'sw':
            ship_rect = ship_rect.move(c.SHIP_SIZE_IN_PIXEL * 7, c.SHIP_SIZE_IN_PIXEL * row_in_sprite)

    return ship_rect

def person_direction_2_rect_in_sprite_sheet(self, direction, frame):
    person_rect = self.images['person_in_port'].get_rect()
    # frame 1
    if frame == 1:
        if direction == 'right':
            person_rect = person_rect.move(c.SHIP_SIZE_IN_PIXEL * 2, 0)
        elif direction == 'left':
            person_rect = person_rect.move(c.SHIP_SIZE_IN_PIXEL * 6, 0)
        elif direction == 'up':
            person_rect = person_rect.move(c.SHIP_SIZE_IN_PIXEL * 0, 0)
        elif direction == 'down':
            person_rect = person_rect.move(c.SHIP_SIZE_IN_PIXEL * 4, 0)

    # frame 2
    else:
        if direction == 'right':
            person_rect = person_rect.move(c.SHIP_SIZE_IN_PIXEL * 3, 0)
        elif direction == 'left':
            person_rect = person_rect.move(c.SHIP_SIZE_IN_PIXEL * 7, 0)
        elif direction == 'up':
            person_rect = person_rect.move(c.SHIP_SIZE_IN_PIXEL * 1, 0)
        elif direction == 'down':
            person_rect = person_rect.move(c.SHIP_SIZE_IN_PIXEL * 5, 0)

    return person_rect

def draw_in_battle(self):
    draw_my_ships(self)
    draw_enemy_ships(self)
    self.battle_state_sprites.update()

def draw_my_ships(self):
    # my ships
    index = 0
    if self.my_role.ships:
        flag_ship = self.my_role.ships[0]
        for ship in self.my_role.ships:
            index += 1

            # ship
            ship_image = self.images['ship_in_battle'][ship.direction]
            ship_rect = ship_image.get_rect()

                # flag ship
            x = y = 1
            if index == 1:
                x = self.screen_surface_rect.centerx
                y = self.screen_surface_rect.centery

                self.screen_surface.blit(ship_image, (x, y), ship_rect)

                # other ships
            else:
                x = self.screen_surface_rect.centerx - (flag_ship.x - ship.x) * c.BATTLE_TILE_SIZE
                y = self.screen_surface_rect.centery - (flag_ship.y - ship.y) * c.BATTLE_TILE_SIZE

                self.screen_surface.blit(ship_image, (x, y), ship_rect)

            # ship number
            draw_ship_number_bg(ship_image)

            if ship.crew > 0:
                draw_text(self, str(index-1), x, y, c.WHITE)

def draw_ship_number_bg(ship_image):
    ship_number_bg = pygame.Surface((10, 20))
    ship_number_bg.fill(c.BLUE)
    number_bg_rect = ship_number_bg.get_rect()
    ship_image.blit(ship_number_bg, number_bg_rect)

def draw_enemy_ships(self):
    # enemy ships
    index = 0
    if self.my_role.ships:
        flag_ship = self.my_role.ships[0]
        for ship in self.other_roles[self.my_role.enemy_name].ships:
            index += 1

            # ship
            ship_image = self.images['enemy_ship_in_battle'][ship.direction]
            ship_rect = ship_image.get_rect()

            x = self.screen_surface_rect.centerx - (flag_ship.x - ship.x) * c.BATTLE_TILE_SIZE
            y = self.screen_surface_rect.centery - (flag_ship.y - ship.y) * c.BATTLE_TILE_SIZE

            self.screen_surface.blit(ship_image, (x, y), ship_rect)

            # ship number
            draw_ship_number_bg(ship_image)

            if ship.crew > 0:
                draw_text(self, str(index - 1), x, y, c.YELLOW)

def draw_speech(self):
    # my
    my_speak_img = self.font.render(self.my_role.speak_msg, True, c.YELLOW)
    x = self.screen_surface_rect.centerx
    y = self.screen_surface_rect.centery - 40
    self.screen_surface.blit(my_speak_img, (x, y))

    # others
    for role in self.other_roles.values():
        speak_img = self.font.render(role.speak_msg, True, c.YELLOW)
        x = self.screen_surface_rect.centerx - self.my_role.x + role.x
        y = self.screen_surface_rect.centery - self.my_role.y + role.y - 40
        self.screen_surface.blit(speak_img, (x, y))

def draw_not_logged_in_state(self):
    """argument self is game"""
    # bg
    self.screen_surface.blit(self.images['login_bg'], (0,0))

    # text
    text_surface = self.font.render(self.login_state_text, True, c.BLACK)
    self.screen_surface.blit(text_surface, (5, 5))

    # ui
    self.ui_manager.draw_ui(self.screen_surface)

    # hide password
    _hide_password(self)

    # hide parts of ui
    self.screen_surface.blit(self.images['login_bg'], (200 + 55, c.WINDOW_HIGHT - 30))
    self.screen_surface.blit(self.images['login_bg'], (-c.WINDOW_WIDTH + 145 + 55, c.WINDOW_HIGHT - 30))

def _hide_password(self):
    if len(self.active_input_boxes) == 2:
        # surface covering passwords
        entry_box_width = 150
        entry_box_height = 28
        surface = pygame.Surface((entry_box_width, entry_box_height))
        surface.fill(c.BLACK)
        rect = surface.get_rect()
        rect.x = 300 - 70 - 3
        rect.y = 300 - 160 - 5
        self.screen_surface.blit(surface, rect)

        # asterisks
        pwd_entry_box = self.active_input_boxes[-1]
        text_in_entry_box = pwd_entry_box.get_text()

        # builtins.AttributeError: 'UITextEntryLine' object has no attribute 'focused'
        # if pwd_entry_box.focused:
        #    asterisks_text = '*' * len(text_in_entry_box) + '|'
        # else:
        #    asterisks_text = '*' * len(text_in_entry_box)
        asterisks_text = '*' * len(text_in_entry_box)
        draw_text(self, asterisks_text, 300 - 70, 300 - 160, c.WHITE)

def blit_text(surface, text, pos, font, color=pygame.Color('black')):
    """draws text block in multiple lines"""
    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    # max_width, max_height = surface.get_size()
    max_width, max_height = (c.BUILDING_CHAT_WIDTH, c.BUILDING_CHAT_HIGHT)
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, 0, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]  # Reset the x.
                y += word_height  # Start on new row.
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]  # Reset the x.
        y += word_height  # Start on new row.