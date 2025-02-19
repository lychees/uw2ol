import pygame
from twisted.internet import reactor, task
import random

# add relative directory to python_path
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

# import from common(dir)
import constants as c
from hashes.hash_ports_meta_data import hash_ports_meta_data
import gui
from pygame_gui._constants import UI_WINDOW_CLOSE
from port_npc import Dog, OldMan, Agent, Man, Woman
import port_npc
import tkinter as tk

EVENT_MOVE = pygame.USEREVENT + 1
EVENT_HEART_BEAT = pygame.USEREVENT + 2

def handle_pygame_event(self, event):
    """argument self is game"""
    # quit
    if event.type == pygame.QUIT:
        quit(self, event)
    # key down
    elif event.type == pygame.KEYDOWN:
        key_down(self, event)
    # key up
    elif event.type == pygame.KEYUP:
        key_up(self, event)
    # mouse button down
    elif event.type == pygame.MOUSEBUTTONDOWN:
        mouse_button_down(self, event)
    # user defined events
    user_defined_events(self, event)

def key_down(self, event):
    # return (focus text entry)
    if event.key > 256:
        return

    if event.key == pygame.K_RETURN:
        msg = self.text_entry.get()
        if msg:
            self.change_and_send('speak', [msg])
            self.text_entry.delete(0, "end")
            self.embed.focus()
            self.text_entry_active = False
        else:
            self.text_entry.focus()
            self.text_entry_active = True

    # escape
    if event.key == pygame.K_ESCAPE:
        escape(self, event)
    # other keys
    if not self.text_entry_active:
        # in game
        if self.my_role:
            other_keys_down(self, event)
        # not in game
        else:
            # logins
            if chr(event.key).isdigit():
                self.connection.send('login', [chr(event.key), chr(event.key)])

def mouse_button_down(self, event):
    if self.my_role:
        # left button
        if event.button == 1:
            # in battle
            if self.my_role.is_in_battle():
                for s in self.mark_sprites:
                    if s.rect.collidepoint(event.pos):
                        s.clicked()
            # not in battle
            else:
                if self.other_roles_rects:
                    # set target
                    for name, rect in self.other_roles_rects.items():
                        if rect.collidepoint(event.pos):
                            self.my_role.enemy_name = name
                            print('target set to:', name)
                            break

                if self.my_role_rect.collidepoint(event.pos):
                    self.my_role.enemy_name = None

        # right button
        elif event.button == 3:
            if self.other_roles_rects:
                # set target
                for name, rect in self.other_roles_rects.items():
                    if rect.collidepoint(event.pos):
                        self.my_role.enemy_name = name
                        print('target set to:', name)
                        gui.target_clicked(self)
                        return

def user_defined_events(self, event):
    if event.type == EVENT_MOVE:
        user_event_move(self, event)
    elif event.type == EVENT_HEART_BEAT:
        self.change_and_send('heart_beat', [])
    # ui window close event
    elif event.type == pygame.USEREVENT:
        if event.user_type == UI_WINDOW_CLOSE:
            if self.menu_stack:
                self.menu_stack.pop()
                self.selection_list_stack.pop()
                print('event ui window close!')
                print('stack length:', len(self.menu_stack))

                if self.my_role:
                    # not in building
                    if self.my_role.in_building_type == None:
                        pass
                    # in building
                    elif len(self.menu_stack) == 0:
                        self.my_role.in_building_type = None
                else:
                    self.active_input_boxes.clear()
                    pass


def quit(self, *event):
    # when in game
    if self.my_role:
        if self.my_role.map.isdigit():
            reactor.stop()
            self.root.quit()
            pygame.quit()
            sys.exit()
        else:
            self.button_click_handler. \
                make_message_box('Exit while in port please.')
            print('Exit while in port please.')
    # when not in game
    else:
        self.root.quit()
        pygame.quit()
        reactor.stop()
        sys.exit()

def escape(self, event):

    # exit building
    if len(self.menu_stack) == 1:
        if self.my_role:
            self.my_role.in_building_type = None

    # pop menu_stack
    if len(self.menu_stack) > 0:
        menu_to_kill = self.menu_stack[-1]
        menu_to_kill.kill()
    print('escape pressed!')

    # clear buttons_in_windows dict
    self.buttons_in_windows.clear()
    print('buttons_in_windows dict cleared!')

    # deactivate text entry
    self.text_entry_active = False

    # clear input boxes
    self.active_input_boxes.clear()

def other_keys_down(self, event):
    # not in battle
    if not self.my_role.is_in_battle():
        _not_in_battle_keys(self, event)
    # in battle
    else:
        _in_battle_keys(self, event)
    # developer keys
    if c.DEVELOPER_MODE_ON:
        pass

def _not_in_battle_keys(self, event):
    # start move
    if not self.my_role.is_in_building():
        if event.key == ord('d'):
            self.change_and_send('start_move', [self.my_role.x, self.my_role.y, 'right'])
        elif event.key == ord('a'):
            self.change_and_send('start_move', [self.my_role.x, self.my_role.y, 'left'])
        elif event.key == ord('w'):
            self.change_and_send('start_move', [self.my_role.x, self.my_role.y, 'up'])
        elif event.key == ord('s'):
            self.change_and_send('start_move', [self.my_role.x, self.my_role.y, 'down'])

        elif event.key == ord('e'):
            self.change_and_send('start_move', [self.my_role.x, self.my_role.y, 'ne'])
        elif event.key == ord('q'):
            self.change_and_send('start_move', [self.my_role.x, self.my_role.y, 'nw'])
        elif event.key == ord('z'):
            self.change_and_send('start_move', [self.my_role.x, self.my_role.y, 'sw'])
        elif event.key == ord('x'):
            self.change_and_send('start_move', [self.my_role.x, self.my_role.y, 'se'])

    # change map to sea
    if event.key == ord('n'):
        if c.DEVELOPER_MODE_ON:
            self.button_click_handler.menu_click_handler.port.port._sail_ok()

    # change map to port
    elif event.key == ord('m'):
        self.button_click_handler.menu_click_handler.cmds.enter_port()

    # enter building
    if event.key == ord('f'):
        pass
        # self.button_click_handler.menu_click_handler.cmds.enter_building()

    # go ashore
    if event.key == ord('g'):
        self.button_click_handler.menu_click_handler.cmds.go_ashore()

    # enter battle
    if event.key == ord('b'):
        self.button_click_handler.menu_click_handler.cmds.battle()

    # change language
    if event.key == ord('l'):
        if self.translator.to_langguage == 'EN':
            self.button_click_handler.menu_click_handler.options._set_to_chinese()
        else:
            self.button_click_handler.menu_click_handler.options._set_to_english()

def _in_battle_keys(self, event):
    if event.key == ord('b'):
        self.button_click_handler.menu_click_handler.battle.escape_battle()
    elif event.key == ord('k'):
        self.button_click_handler.menu_click_handler.battle.all_ships_move()
    elif event.key == ord('l'):
        self.change_and_send('set_all_ships_target', [0])
    elif event.key == ord('o'):
        self.change_and_send('set_all_ships_attack_method', [0])
    elif event.key == ord('i'):
        self.change_and_send('set_all_ships_attack_method', [1])

def move_right_and_then_back(self):
    self.change_and_send('start_move', [self.my_role.x, self.my_role.y, 'right'])
    reactor.callLater(2, send_stop_moving, self)
    reactor.callLater(2.5, start_moving_left, self)
    reactor.callLater(4.5, send_stop_moving, self)

def send_stop_moving(self):
    self.change_and_send('stop_move', [self.my_role.x, self.my_role.y])

def start_moving_left(self):
    self.change_and_send('start_move', [self.my_role.x, self.my_role.y, 'left'])

def key_up(self, event):
    if event.key > 256:
        return
    if not self.text_entry_active:
        key = chr(event.key)
        # stop moving
        if key in ['w', 's', 'a', 'd', 'e', 'q', 'z', 'x']:
            try:
                self.change_and_send('stop_move', [self.my_role.x, self.my_role.y])
            except:
                pass

def user_event_move(self, event):
    if self.my_role:
        if self.move_direction == 1:
            self.change_and_send('move', ['right'])
        else:
            self.change_and_send('move', ['left'])

        self.move_count += 1

        if self.move_count >= 15:
            self.move_count = 0
            self.move_direction *= -1