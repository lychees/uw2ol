import pygame
import random

# add relative directory to python_path
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

# import from common(dir)
from role import Role, Ship, Mate, Port
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
import port_npc
import handle_pygame_event
import constants as c
from hashes.hash_ports_meta_data import hash_ports_meta_data

def process_packet(self, pck_type, message_obj):
    # method not in role (in this file)
    if pck_type not in Role.__dict__:
        func_name = eval(pck_type)
        func_name(self, message_obj)

    # sync packets
    elif pck_type in Role.__dict__:
        list = message_obj
        name = list.pop()
        func_name = pck_type
        if name in self.other_roles:
            role = self.other_roles[name]
            print("trying", func_name, list, "for", name)
            func = getattr(role, func_name)
            func(list)
            print(role, func_name, func, list)

# register responses
def version_wrong(self, message_obj):
    msg = 'Please download the latest version! ' \
                            'Exiting in 5 seconds.'
    msg = self.trans(msg)
    self.login_state_text = msg
    reactor.callLater(2, handle_pygame_event.quit, self)

def register_ok(self, message_obj):
    msg = 'Register OK. Please Login.'
    msg = self.trans(msg)
    self.login_state_text = msg

def account_exists(self, message_obj):
    msg = 'Account exists!'
    msg = self.trans(msg)
    self.login_state_text = msg

# make character response
def must_login_first(self, message_obj):
    msg = "Must login first to create character."
    msg = self.trans(msg)
    self.login_state_text = msg

def new_role_created(self, message_obj):
    msg = 'Character created! Please login again.'
    msg = self.trans(msg)
    self.login_state_text = msg

def name_exists(self, message_obj):
    msg = 'Name used! Please choose another name.'
    msg = self.trans(msg)
    self.login_state_text = msg

# login responses
def login_failed(self, message_obj):
    msg = 'Login failed!'
    msg = self.trans(msg)
    self.login_state_text = msg

def no_role_yet(self, message_obj):
    msg = "Login successful! " \
            "Please create a character. " \
            "Don't use a number as your name."
    msg = self.trans(msg)
    self.login_state_text = msg

def your_role_data_and_others(self, message_obj):
    # my role
    print("got my role data")
    my_role = message_obj[0]
    self.my_role = my_role
    print("my role's x y:", my_role.x, my_role.y, my_role.map, my_role.name)

    if my_role.map.isdigit():
        port_index = int(my_role.map)
        my_role.prev_port_map_id = port_index
        self.port_piddle, self.images['port'] = self.map_maker.make_port_piddle_and_map(port_index, self.time_of_day)

        # normal ports
        if port_index < 100:
            port_npc.init_static_npcs(self, port_index)
            port_npc.init_dynamic_npcs(self, port_index)

    # other roles
    other_roles = message_obj[1]
    for role in other_roles:
        self.other_roles[role.name] = role
    print(other_roles)

    # music    
    port_name = hash_ports_meta_data[int(self.my_role.map) + 1]['name']    
    if port_name in ["Lisbon", "Seville", "London", "Marseille", "Amsterdam", "Venezia"]:
        pygame.mixer.music.load('../../assets/sounds/music/port/' + port_name + '.mp3')
    else:
        pygame.mixer.music.load('../../assets/sounds/music/port.ogg')
    pygame.mixer.music.play()

# someone logged in
def new_role(self, message_obj):
    new_role = message_obj
    self.other_roles[new_role.name] = new_role
    print("got new role named:", new_role.name)

# someone logged out
def logout(self, message_obj):
    name_of_logged_out_role = message_obj
    del self.other_roles[name_of_logged_out_role]

# someone changed map
def role_disappeared(self, message_obj):
    name_of_role_that_disappeared = message_obj
    if name_of_role_that_disappeared in self.other_roles:
        del self.other_roles[name_of_role_that_disappeared]

# change map response
def roles_in_new_map(self, message_obj):
    roles_in_new_map = message_obj
    self.my_role = roles_in_new_map[self.my_role.name]
    del roles_in_new_map[self.my_role.name]
    self.other_roles = roles_in_new_map

    print("now my map:", self.my_role.map)

    # if at sea
    if self.my_role.map == 'sea':
        # clear marks
        self.my_role._clear_marks()
        self.reset_think_time_in_battle()

        # music
        # file_name = random.choice(['sea', 'sea_1'])
        # pygame.mixer.music.load(f"../../assets/sounds/music/{file_name}.ogg")
        # pygame.mixer.music.play(-1)

        # if just lost from battle
        if not self.my_role.ships:
            self.connection.send('change_map', ['29'])
            self.button_click_handler.show_defeat_window()

    # if in port
    elif self.my_role.map.isdigit():
        port_index = int(self.my_role.map)
        self.port_piddle, self.images['port'] = self.map_maker.\
            make_port_piddle_and_map(port_index, self.time_of_day)

def roles_disappeared(self, message_obj):
    """in delete grids"""
    names_of_roles_that_disappeared = message_obj
    for name in names_of_roles_that_disappeared:
        if name in self.other_roles:
            del self.other_roles[name]

def roles_appeared(self, message_obj):
    """in new grids"""
    roles_appeared = message_obj
    self.other_roles = {**self.other_roles, **roles_appeared}


# enter battle responses
def roles_in_battle_map(self, message_obj):
    """in battle now"""
    # get roles
    roles_in_battle_map = message_obj
    self.other_roles = {}
    for name, role in roles_in_battle_map.items():
        if name == self.my_role.name:
            self.my_role = role
        else:
            self.other_roles[name] = role

    # start battle timer
    self.battle_timer = LoopingCall(_check_battle_timer, self)
    self.battle_timer.start(1)

    # music
    pygame.mixer.music.load('../../assets/sounds/music/battle.ogg')
    pygame.mixer.music.play(-1)

def _check_battle_timer(self):
    if self.my_role.map == 'sea' and self.battle_timer:
        self.battle_timer.stop()
    else:
        if self.my_role.your_turn_in_battle:
            # show marks at the beginning of my turn
            if self.think_time_in_battle == c.THINK_TIME_IN_BATTLE:
                self.my_role._show_marks()

            # auto operate when timer <= 0
            self.think_time_in_battle -= 1
            if self.think_time_in_battle <= 0:
                self.change_and_send('all_ships_operate', [False])

def new_roles_from_battle(self, message_obj):
    new_roles_from_battle = message_obj
    for name, role in new_roles_from_battle.items():
        self.other_roles[name] = role

def target_too_far(self, message_obj):
    msg = "target too far or lv too low!"
    msg = self.trans(msg)
    self.button_click_handler.i_speak(msg)

def npc_info(self, message_obj):
    """npc fleet positions"""
    dic = message_obj

    # get 3 lists
    names = []
    destinations = []
    positions = []
    cargoes = []
    for name in dic.keys():
        names.append(dic[name]['mate_name'])
        destinations.append(dic[name]['destination'])
        positions.append(dic[name]['position'])
        cargoes.append(dic[name]['cargo_name'])

    # calc longitude and latitude
    for pos in positions:
        x = int(pos[0] / c.PIXELS_COVERED_EACH_MOVE)
        y = int(pos[1] / c.PIXELS_COVERED_EACH_MOVE)
        longitude, latitude = _calc_longitude_and_latitude(x, y)
        pos[0] = longitude
        pos[1] = latitude

    # maid speak
    t1 = self.trans("'s fleet")
    t2 = self.trans("carrying")
    t3 = self.trans("is heading to")
    t4 = self.trans("and his current location is about")
    t5 = self.trans(cargoes[0])
    t6 = self.trans(cargoes[1])
    t7 = self.trans(destinations[0])
    t8 = self.trans(destinations[1])
    t9 = self.trans(names[0])
    t10 = self.trans(names[1])
    speak_str = f"{t9}{t1}, {t2} {t5}, <br>{t3} {t7} " \
                f"<br>{t4} {positions[0][0]} {positions[0][1]}. <br><br>" \
                f"{t10}{t1}, {t2} {t6}, <br>{t3} {t8} " \
                f"<br>{t4} {positions[1][0]} {positions[1][1]}."
    self.button_click_handler.menu_click_handler.port.bar._maid_speak(speak_str)

def _calc_longitude_and_latitude(x, y):
    # transform to longitude
    longitude = None
    if x >= 900 and x <= 1980:
        longitude = int(( x - 900 )/6)
        longitude = str(longitude) + 'e'
    elif x > 1980:
        longitude = int((900 + 2160 - x)/6)
        longitude = str(longitude) + 'w'
    else:
        longitude = int((900 - x)/6)
        longitude = str(longitude) + 'w'

    # transform to latitude
    latitude = None
    if y <= 640:
        latitude = int((640 - y)/7.2)
        latitude = str(latitude) + 'N'
    else:
        latitude = int((y - 640)/7.2)
        latitude = str(latitude) + 'S'

    return (longitude, latitude)

def allied_ports_and_pi(self, message_obj):
    d = message_obj

    # make my_dict (economy_id: set of dic)
    my_dict = {}
    for map_id, list in d.items():
        port = Port(map_id)
        economy_id = port.economy_id

        pi = list[0]
        economy = list[1]
        industry = list[2]

        port_name = port.name

        if economy_id in my_dict:
            pass
        else:
            my_dict[economy_id] = []
        dic = {
            'port_name': port_name,
            'pi': pi,
            'economy': economy,
            'industry': industry,
        }
        my_dict[economy_id].append(dic)

    # dic to show
    dic = {}
    for k in sorted(my_dict):
        region_name = hash_ports_meta_data['markets'][k]
        dic[region_name] = [_show_allied_ports_for_one_economy_id, [self, region_name, my_dict[k]]]

    self.button_click_handler.make_menu(dic)

def _show_allied_ports_for_one_economy_id(params):
    self = params[0]
    region_name = params[1]
    list_of_dict = params[2]
    port_count = len(list_of_dict)

    t1 = self.trans("In")
    t2 = self.trans("the number of ports allied to us is")
    t3 = self.trans("PI-")
    t4 = self.trans("E-")
    t5 = self.trans("I-")
    t6 = self.trans(region_name)
    msg = f"{t1}{t6}, {t2} {port_count}. <br><br>"
    for d in list_of_dict:
        port_name = self.trans(d['port_name'])
        msg += f"{port_name}: {t3}{d['pi']}, " \
               f"{t4}{d['economy']}, " \
               f"{t5}{d['industry']}<br>"

    self.button_click_handler.make_message_box(msg)

def port_investment_state(self, message_obj):
    port_owner = message_obj[0]
    owner_nation = message_obj[1]
    deposit_ingots = message_obj[2]
    mode = message_obj[3]

    owner_map = message_obj[4]
    owner_x = message_obj[5]
    owner_y = message_obj[6]

    msg = ''
    # owner exists
    if port_owner:
        # owner is online
        t1 = self.trans("The administrator of this port is")
        t2 = self.trans("from")
        t3 = self.trans("The deposit is")
        t4 = self.trans("ingots")
        t5 = self.trans(owner_nation)
        msg = f"{t1} {port_owner} {t2} {t5}. " \
              f"{t3} {deposit_ingots} {t4}. "

        if owner_map:
            if mode == 'easy':
                t1 = self.trans("You can overide the current administrator by investing more than")
                t2 = self.trans("times the deposit")
                msg += f"{t1} {c.EASY_MODE_OVERIDE_RATIO} {t2}."
            elif mode == 'hard':
                # owner at sea
                if owner_map == 'sea':
                    x = int(owner_x / c.PIXELS_COVERED_EACH_MOVE)
                    y = int(owner_y / c.PIXELS_COVERED_EACH_MOVE)
                    longitude, latitude = _calc_longitude_and_latitude(x, y)

                    t1 = self.trans("You can overide the current administrator by investing more than")
                    t2 = self.trans("times the deposit")
                    t3 = self.trans("or defeating the administrator in battle. I heard the administrator is now at")
                    msg += f"{t1} {c.HARD_MODE_OVERIDE_RATIO} {t2} {t3} " \
                          f"{longitude} {latitude}."
                # owner in port
                elif owner_map.isdigit():
                    owner_map = hash_ports_meta_data[int(owner_map)+1]['name']
                    t1 = self.trans("You can overide the current administrator by investing more than")
                    t2 = self.trans("times the deposit")
                    t3 = self.trans("or defeating the administrator in battle. I heard the administrator is now at")
                    t4 = self.trans(owner_map)
                    msg += f"{t1} {c.HARD_MODE_OVERIDE_RATIO} {t2} {t3} " \
                          f"{t4}."
        # owner is offline
        else:
            t1 = self.trans("You can overide the current administrator by investing more than")
            t2 = self.trans("times the deposit")
            msg += f"{t1} {c.EASY_MODE_OVERIDE_RATIO} {t2}."
    else:
        msg = f"We haven't got any investment yet."

    self.button_click_handler.make_message_box(msg)

def got_port(self, message_obj):
    num_of_ingots = message_obj
    self.my_role.gold -= num_of_ingots * 10000
    msg = "Thank you for your investment! Your are the administrator of this port now!"
    self.button_click_handler.building_speak(msg)

def you_won_port_owner(self, message_obj):
    msg = "You defeated the administrator! You are in charge of this port now!"
    self.button_click_handler.building_speak(msg)

def you_have_not_won_port_owner(self, message_obj):
    msg = "Oh? Have you defeated the administrator?"
    self.button_click_handler.building_speak(msg)

def revenue_amount(self, message_obj):
    revenue_amount = message_obj
    t1 = self.trans("Oh! I know you. You can collect")
    msg = f"{t1} {revenue_amount}."
    self.button_click_handler.building_speak(msg)

    d = {
        'Collect All': [_collect_all, self],
        'Set Mode': [_set_mode, self],
    }
    self.button_click_handler.make_menu(d)

def _collect_all(self):
    self.connection.send('collect_all_revenue', '')

def _set_mode(self):
    """port mode: easy or hard. """

    def set_easy_mode():
        self.connection.send('set_port_mode', ['easy'])

    def set_hard_mode():
        self.connection.send('set_port_mode', ['hard'])

    d = {
        'Easy': set_easy_mode,
        'Hard': set_hard_mode,
    }
    self.button_click_handler.make_menu(d)

def port_mode_change(self, message_obj):
    mode = message_obj
    t1 = self.trans('Port mode switched to')
    t2 = self.trans(mode)
    t3 = self.trans("The investment state of this port has changed.")
    msg = f"{t1} {t2}. {t3}"
    self.button_click_handler.building_speak(msg)

def former_revenue_amount(self, message_obj):
    revenue_amount = message_obj
    t1 = self.trans("Oh! Our former sponsor. You can collect")
    msg = f"{t1} {revenue_amount}."
    self.button_click_handler.building_speak(msg)

    d = {
        'Collect All': [_collect_all, self],
    }
    self.button_click_handler.make_menu(d)

def got_revenue(self, message_obj):
    revenue_amount = message_obj
    self.my_role.gold += revenue_amount
    msg = f"You have collected all your revenue."
    self.button_click_handler.building_speak(msg)

def not_your_port(self, message_obj):
    msg = "This is only for the administrator of this port."
    self.button_click_handler.building_speak(msg)

def cannot_afford(self, message_obj):
    msg = "You don't have enough gold."
    self.button_click_handler.building_speak(msg)