from kivy.config import Config
Config.set('graphics', 'fullscreen', 0)
Config.write()
from kivymd.uix.dialog import MDDialog
import requests
import json
from kivy.lang import Builder
from kivy.properties import ObjectProperty
#from kivy.properties import VariableListProperty
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
#from kivymd.uix.gridlayout import MDGridLayout
#from kivymd.uix.stacklayout import StackLayout
from kivymd.uix.card import MDCardSwipe
from kivymd.uix.card import MDCard
from kivy.properties import StringProperty
from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.picker import MDDatePicker
from kivy.uix.dropdown import DropDown
from kivymd.uix.button import MDFlatButton
from datetime import datetime
import calendar
#from kivy.clock import Clock
import timeit
from kivy.uix.button import Button
from kivymd.uix.label import MDLabel
DOUBLE_TAP_TIME = 0.2   # Change time in seconds
LONG_PRESSED_TIME = 0.9  # Change time in seconds
MAX_TIME = 1/30.
MAX_TIME_GROUP = 1/60.
#import os
from kivy.clock import Clock, _default_time as time
from kivymd.uix.card import MDSeparator
from kivy.core.window import Window
from kivy.effects.scroll import ScrollEffect

class rkv_api:
    def __init__(self, app_instance):
        super().__init__()
        self.Flag_config = False
        self.Flag_connection = False
        self.Flag_authent = False
        self.Login = 0
        self.Password = 0
        self.user_id = 0
        self.user_secondname = 0
        self.app_instance = app_instance
        self.srv_adress = ''
        now = datetime.now()
        self.date_now = now.strftime("%Y-%m-%d")
        self.date_start = now.strftime("%Y-%m-") + '01'
        self.date_end = f'{now.strftime("%Y-%m-")}{calendar.monthrange(now.year, now.month)[1]}'
        self.work_list = 0
        self.do_work_list = 0
        self.equipment_list = 0
        self.object_list = 0
        self.users_on_object_list = 0
        self.users_list = 0
        self.last_id_work = 0
        self.last_id_do_work = 0
        self.complex_list = 0
        self.new_do_work = 0

    def init(self):
        print('34')
        try:
            f = open('config.txt', 'r')
        except:
            return ('no_config')
        else:
            conf_str = f.read()
            if conf_str != '':
                self.Flag_config = True
                conf = conf_str.split(',')
                self.srv_adress = conf[2]
                url = self.srv_adress + 'get_work_list(1).php'
                try:
                    res = requests.post(url, data={"login": conf[0], 'pass': conf[1]})
                except:
                    print('no_link')
                    self.Login = conf[0]
                    self.Password = conf[1]
                    self.work_list = self.get_work_list(off_line=True)
                    self.do_work_list = self.get_do_work_list(self.date_start, self.date_end, off_line=True)
                    self.object_list = self.get_object(off_line=True)
                    self.users_list = self.get_users_list(off_line=True)
                    self.equipment_list = self.get_equipment_list(off_line=True)
                    self.complex_list = self.get_complex_list(off_line=True)
                    # self.users_on_object_list = self.get_users_on_object('41')
                    return ('ok')
                else:
                    self.Flag_connection = True
                    answer = json.loads(res.text)
                    print(res.text)
                    if answer['status'] == 'success':
                        self.Flag_authent = True
                        self.Login = conf[0]
                        self.Password = conf[1]
                        self.work_list = self.get_work_list()
                        self.do_work_list = self.get_do_work_list()
                        self.object_list = self.get_object()
                        self.users_list = self.get_users_list()
                        self.equipment_list = self.get_equipment_list()
                        self.complex_list = self.get_complex_list()
                        # self.users_on_object_list = self.get_users_on_object('41')
                        return ('ok')
                    else:
                        self.Login = conf[0]
                        self.Password = conf[1]
                        return ('bad_login')
            f.close()

    def login(self, login=0, password=0, srv_adress=0, Log_in=True):
        if Log_in:
            srv_adress_string = 'http://'+srv_adress+':38654/'

            url = srv_adress_string + 'get_work_list(1).php'
            try:
                res = requests.post(url, data={'login': login,
                                               'pass': password,
                                               'srv_adress': srv_adress
                                               }
                                    )
            except:
                print('нет соединения регистрация')
            else:
                self.Flag_connection = True
                answer = json.loads(res.text)
                print(res.text)
                if answer['status'] == 'success':
                    self.Flag_authent = True
                    with open('config.txt', 'w', encoding="utf-8") as f:
                        f.write(f"{login},{password},{srv_adress_string}")
                    self.Flag_config = True
                    self.init()
                else:
                    print('error_login')
        else:
            with open('config.txt', 'w', encoding="utf-8") as f:
                f.write('')
            self.Flag_config = False
            self.Flag_connection = False
            self.Flag_authent = False

    def get_work_list(self, find_word='', off_line=False):
        if self.work_list == 0:
            url = self.srv_adress + 'get_work_list.php'
            if off_line:
                print('нет соединения выполнения')
                with open('work_list.txt', 'r', encoding="utf-8") as f:
                    return json.loads(f.read())
            else:
                try:
                    res = requests.post(url, data={'find_word': find_word,
                                                   'login': self.Login,
                                                   'pass': self.Password
                                                   })
                except:
                    print('нет соединения выполнения')
                    with open('work_list.txt', 'r', encoding="utf-8") as f:
                        return json.loads(f.read())
                else:
                    with open('work_list.txt', 'w', encoding="utf-8") as f:
                        f.write(res.text)
                    return json.loads(res.text)
        else:
            return self.work_list

    def add_new_do_work(self, array_id_for_new, array_text_for_new):
        url = self.srv_adress + 'add_new.php'
        try:
            res = requests.post(url, data={'223': array_id_for_new['223'],
                                           '239': array_id_for_new['239'],
                                           '224': array_id_for_new['224'],
                                           '237': array_id_for_new['237'],
                                           '252': array_id_for_new['252'],
                                           '267': self.date_now,
                                           '253': array_id_for_new['253'],
                                           'parent_item_id': array_id_for_new['parent_item_id'],
                                           'login': self.Login,
                                           'pass': self.Password
                                           })
        except:

            return {'status': 'no_link'}
        else:

            return json.loads(res.text)

    def update_work_do(self, array_for_update, id_update_item):
        json_array_for_update = json.dumps(array_for_update)
        url = self.srv_adress + 'update_item.php'
        try:
            res = requests.post(url, data={'id': id_update_item,
                                           'data': json_array_for_update,
                                           'login': self.Login,
                                           'pass': self.Password
                                           })
        except:
            return 'no_link'
        else:
            status = json.loads(res.text)
            return status['status']

    def remove_work_do(self, id_remove_item):
        url = self.srv_adress + 'remove_item.php'
        try:
            res = requests.post(url, data={'id': id_remove_item,
                                           'login': self.Login,
                                           'pass': self.Password
                                           })
        except:
            return 'no_link'

        else:
            status = json.loads(res.text)
            return status['status']

    def get_do_work_list(self, date_start=0, date_end=0, object=0, reload=False, off_line = False):
        if date_start == 0:
            date_start = self.date_start
            date_end = self.date_end
        if self.do_work_list == 0 or date_end != self.date_end or reload:
            url = self.srv_adress + 'get_work_do.php'
            if off_line:
                print('нет соединения тип работ')
                with open('do_work_list.txt', 'r', encoding="utf-8") as f:
                    return json.loads(f.read())
            else:
                try:
                    res = requests.post(url, data={'object': object,
                                                   'date_start': date_start,
                                                   'date_end': date_end,
                                                   'login': self.Login,
                                                   'pass': self.Password

                                                   })
                except:
                    print('нет соединения тип работ')
                    with open('do_work_list.txt', 'r', encoding="utf-8") as f:
                        return json.loads(f.read())
                else:
                    self.last_id_do_work = 0
                    with open('do_work_list.txt', 'w', encoding="utf-8") as f:
                        f.write(res.text)
                    return json.loads(res.text)
        else:
            return self.do_work_list

    def get_equipment_list(self, off_line=False):
        if self.equipment_list == 0:
            url = self.srv_adress + 'get_equipment.php'
            if off_line:
                print('нет соединения оборудования')
                with open('equipment_list.txt', 'r', encoding="utf-8") as f:
                    return json.loads(f.read())
            else:
                try:
                    res = requests.post(url, data={
                        'login': self.Login,
                        'pass': self.Password
                    })
                except:
                    print('нет соединения оборудования')
                    with open('equipment_list.txt', 'r', encoding="utf-8") as f:
                        return json.loads(f.read())
                else:
                    with open('equipment_list.txt', 'w', encoding="utf-8") as f:
                        f.write(res.text)
                    return json.loads(res.text)
        else:
            return self.equipment_list

    def get_complex_list(self, off_line=False):
        if self.complex_list == 0:
            url = self.srv_adress + 'get_complex.php'
            if off_line:
                print('нет соединения сложность')
                with open('complex_list.txt', 'r', encoding="utf-8") as f:
                    return json.loads(f.read())
            else:
                try:
                    res = requests.post(url, data={'find_word': ''
                                                   })
                except:
                    print('нет соединения сложность')
                    with open('complex_list.txt', 'r', encoding="utf-8") as f:
                        return json.loads(f.read())
                else:
                    with open('complex_list.txt', 'w', encoding="utf-8") as f:
                        f.write(res.text)
                    return json.loads(res.text)
        else:
            return self.complex_list

    def get_object(self, off_line=False):
        if self.object_list == 0:
            url = self.srv_adress + 'get_object_for_user.php'
            if off_line:
                print('нет соединения объекты')
                with open('object_list.txt', 'r', encoding="utf-8") as f:
                    return json.loads(f.read())
            else:
                try:
                    res = requests.post(url, data={'login': self.Login,
                                                   'pass': self.Password
                                                   })
                except:
                    print('нет соединения объекты')
                    with open('object_list.txt', 'r', encoding="utf-8") as f:
                        return json.loads(f.read())
                else:
                    with open('object_list.txt', 'w', encoding="utf-8") as f:
                        f.write(res.text)
                    return json.loads(res.text)
        else:
            return self.object_list

    def get_users_list(self, off_line=False):
        url = self.srv_adress + 'get_user_list.php'
        if off_line:
            print('нет соединения пользователи')
            with open('users_list.txt', 'r', encoding="utf-8") as f:
                users_list = json.loads(f.read())
            for user in users_list['data']:
                if user['12'] == self.Login:
                    self.user_id = user['id']
                    self.user_secondname = user['8']
            return users_list
        else:
            try:
                res = requests.post(url, data={
                    'login': self.Login,
                    'pass': self.Password
                })
            except:
                print('нет соединения пользователя')
                with open('users_list.txt', 'r', encoding="utf-8") as f:
                    users_list = json.loads(f.read())
                for user in users_list['data']:
                    if user['12'] == self.Login:
                        self.user_id = user['id']
                        self.user_secondname = user['8']
                return users_list
            else:
                with open('users_list.txt', 'w', encoding="utf-8") as f:
                    f.write(res.text)
                users_list = json.loads(res.text)
                for user in users_list['data']:
                    if user['12'] == self.Login:
                        self.user_id = user['id']
                        self.user_secondname = user['8']
                return users_list

    def get_users_on_object(self, id_object):
        for on_object in self.object_list['data']:
            if on_object['id'] == id_object:
                users_on_object = on_object['161'].split(',')
                # print(users_on_object)
                break
        user_list_with_id = {'data': []}
        for user_on_object in users_on_object:
            for user in self.users_list['data']:
                if user_on_object.lstrip()[2:] == user['8']:
                    user_list_with_id['data'].append({'id': user['id'], '8': user['8']})
        return user_list_with_id


#       url = self.srv_adress+'get_work_do.php'
#       print(self.date_start)
#       res = requests.post(url, data={"work_object": work_object,
#                     'date_start': self.date_start,
#                     'date_end': self.date_end})
#       self.last_id_do_work = 0
#       print(json.loads(res.text))
#       return json.loads(res.text)

class ContentNavigationDrawer(MDBoxLayout):
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()
    toolbar = ObjectProperty()
    new = ObjectProperty()


class AddNewWork(MDBoxLayout):
    text = ObjectProperty()


class CustomDropDown(DropDown):
    pass


class ItemForDropDown(Button):
    name_item = ObjectProperty()
    id_item = ObjectProperty()


class SwipeToDeleteItem(MDCard):
    work_do = ObjectProperty()
    object_name = StringProperty()
    unit_name = StringProperty()

    def __init__(self, **kwargs):
        super(SwipeToDeleteItem, self).__init__(**kwargs)
        self.start = 0
        self.press_state = False
        self.register_event_type('on_double_press')
        self.register_event_type('on_long_press')

    def on_touch_down(self, touch):
        if touch.is_touch:
            if not touch.is_mouse_scrolling:

                if self.collide_point(touch.x, touch.y):
                    self.start = timeit.default_timer()

                    if touch.is_triple_tap:
                        self.press_state = True
                        self.dispatch('on_double_press')
                    else:
                        return super(SwipeToDeleteItem, self).on_touch_down(touch)
                else:
                    return super(SwipeToDeleteItem, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.is_touch:
            if not touch.is_mouse_scrolling:

                if self.press_state is False:
                    if self.collide_point(touch.x, touch.y):
                        stop = timeit.default_timer()
                        awaited = stop - self.start
                        print (awaited)
                        if awaited > LONG_PRESSED_TIME and awaited < 5:
                            print('long')
                            self.dispatch('on_long_press')
                            self.start = 0
                        else:
                            return super(SwipeToDeleteItem, self).on_touch_up(touch)
                    else:
                        return super(SwipeToDeleteItem, self).on_touch_up(touch)
                else:
                    #return super(SwipeToDeleteItem, self).on_touch_up(touch)
                    self.press_state = False

    def on_double_press(self):
        pass

    def on_long_press(self):
        pass


class Object_Conteiner(MDBoxLayout):
    object_name = StringProperty()


class Content_do_work(MDLabel):
    work_do = ObjectProperty()
    object_name = StringProperty()
    unit_name = StringProperty()


class WorkTypeCard(MDLabel):
    work_list = ObjectProperty()


class Worker_item(MDBoxLayout):
    name_worker = StringProperty()
    id_worker = StringProperty()


class Button_ok(MDFlatButton):
    instance = ObjectProperty()


class Button_cancel(MDFlatButton):
    instance = ObjectProperty()


class MyApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.theme_style = "Light"
        self.dialog = None
        self.Flag_AddNew = 0
        self.Height = 0
        self.Flag_Update_List = False
        self.Flag_Reload_List = False
        self.Flag_group_by_object = True
        self.rkv = rkv_api(self)
        self.dropdown = CustomDropDown()
        self.activ_text_field = 0
        self.loop = 0
        self.loop_work_do = 0
        self.item_for_builder = []
        self.Flag_color = False
        self.item_for_groupe_bilder = {}
        self.last_object_group_bilder=0
        self.count = 0
        self.scroll =0
        # self.init_date_range = self.date_start + '/' + self.date_end

    def win(self,*args):
        var = len(self.root.ids.md_list.children)
        print (var)
        self.root.ids.scroll_do_work.do_scroll_y = True
        self.root.ids.scroll_do_work.scroll_to(self.root.ids.md_list.children[var-1], padding=10, animate=False)
        print('разверн')


    def on_start(self):
        Window.bind(on_restore=self.win)
        self.rkv.init()
        if self.rkv.Flag_config:
            self.root.ids.adress.text = self.rkv.srv_adress[7:20]
            self.root.ids.login.text = self.rkv.Login
            self.root.ids.password.text = '11111111'
            self.root.ids.singup_btn.text = 'Выйти'
            if self.rkv.Flag_connection:
                self.load_items(self.rkv.work_list, self.rkv.do_work_list)
                print(self.rkv.do_work_list)
                if not self.rkv.Flag_authent:
                    self.root.ids.md_list.add_widget(
                        MDFlatButton(text='Логин или пароль не верны...', pos_hint={"center_x": .5, "center_y": .5}))
                    self.root.ids.singup_btn.text = 'Войти в систему'
                    self.root.ids.password.text = self.rkv.Password
            else:
                self.load_items(self.rkv.work_list, self.rkv.do_work_list)
        else:
            self.root.ids.md_list.add_widget(
                MDFlatButton(text='Войдите в систему...', pos_hint={"center_x": .5, "center_y": .5})
            )

    def button_login(self, instance, instence_adress, instance_login, instance_password):
        if instance.text == 'Войти в систему':
            self.rkv.login(instance_login.text, instance_password.text, instence_adress.text)
            if self.rkv.Flag_authent and self.rkv.Flag_config and self.rkv.Flag_connection:
                instance.text = 'Выйти'
                self.load_items(self.rkv.work_list, self.rkv.do_work_list)
            else:
                print('error_login')
        else:
            self.rkv.login(Log_in=False)
            instance_login.text = ''
            instance_password.text = ''
            instance.text = 'Войти в систему'

    def bilder_for_grope_list(self, *args):
        print('loop')
        print(self.loop_work_do.is_triggered)
        if not self.item_for_groupe_bilder and self.loop_work_do or self.count>=4:
            print('stop')
            self.loop_work_do.cancel()
            print(self.loop_work_do.is_triggered)
        while self.item_for_groupe_bilder and time() < (Clock.get_time() + MAX_TIME_GROUP):
            if self.count<4:
                print(self.count)
                keys = list(self.item_for_groupe_bilder.keys())
                print(keys)
                key_object = keys[0]
                object_name = list(filter(lambda x: x['id'] == key_object,
                                          self.rkv.object_list['data'])).pop()
                if self.item_for_groupe_bilder[key_object]:
                    print(self.item_for_groupe_bilder[key_object])
                    if self.last_object_group_bilder != key_object:
                        print(key_object)
                        self.last_object_group_bilder = key_object

                        self.root.ids.md_list.add_widget(
                            Object_Conteiner(object_name=object_name['158'])
                        )
                        if self.Flag_color:
                            self.root.ids.md_list.children[0].md_bg_color = (0, 0, 0, 0)
                            self.Flag_color = False
                        else:
                            self.root.ids.md_list.children[0].md_bg_color = (0, 0, 0, 0.15)
                            self.Flag_color = True

                    else:
                        self.count += 1
                        work_do_item = self.item_for_groupe_bilder[key_object].pop(0)
                        unit_name = list(filter(lambda x: x['id'] == work_do_item['226'],
                                                     self.rkv.work_list['data'])).pop()
                        self.root.ids.md_list.children[0].add_widget(
                            SwipeToDeleteItem(work_do=work_do_item, object_name=object_name['158'], unit_name = unit_name['243'])
                        )
                        self.root.ids.md_list.children[0].children[0].bind(on_long_press=self.open_remove_dialog)
                        self.root.ids.md_list.children[0].children[0].bind(on_double_press=self.update_item)
                else:
                    self.item_for_groupe_bilder.pop(key_object)



    def group_by_object(self, instance, Flag_reload=False):

        #self.root.ids.md_list1.size
        print(self.root.ids.md_list1.size)
        if self.Flag_group_by_object and self.rkv.Flag_config or Flag_reload:
            self.Flag_group_by_object = False
            Flag_color = True
            self.item_for_groupe_bilder = {}
            #self.rkv.last_id_do_work = 0
            self.last_object_group_bilder = 0
            for work_item in self.rkv.do_work_list['data']:
                if self.item_for_groupe_bilder.get(work_item['parent_item_id']):
                    self.item_for_groupe_bilder[work_item['parent_item_id']].append(work_item)
                else:
                    self.item_for_groupe_bilder[work_item['parent_item_id']] = []
                    self.item_for_groupe_bilder[work_item['parent_item_id']].append(work_item)
            print(self.item_for_groupe_bilder)
            self.root.ids.md_list.clear_widgets()
            self.count = 0
            self.loop_work_do = Clock.schedule_interval(self.bilder_for_grope_list, 0)
        elif self.Flag_group_by_object == False and self.rkv.Flag_config:
            self.item_for_groupe_bilder = {}
            self.last_object_group_bilder = 0
            if self.loop_work_do:
                self.loop_work_do.cancel()
            self.Flag_group_by_object = True
            self.rkv.last_id_do_work = 0
            self.load_items(0, self.rkv.do_work_list)

    def show_date_picker(self):
        if self.rkv.Flag_config:
            if self.rkv.Flag_connection:
                if self.rkv.Flag_authent:
                    date_dialog = MDDatePicker(mode="range",
                                               title="Выберите интервал",
                                               title_input="Введите интервал")
                    date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
                    date_dialog.open()
            else:
                date_dialog = MDDatePicker(mode="range",
                                           title="Выберите интервал",
                                           title_input="Введите интервал")
                date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
                date_dialog.open()


    def on_save(self, instance, value, date_range):
        if date_range:

            date_start = date_range[0].strftime("%Y-%m-%d")
            date_end = date_range[-1].strftime("%Y-%m-%d")
            self.root.ids.toolbar.title = f'{self.rkv.date_start}/{self.rkv.date_end}'
            self.rkv.last_id_do_work = 0
            self.rkv.do_work_list = self.rkv.get_do_work_list(date_start, date_end, '')
            self.load_items(0, self.rkv.do_work_list)
            self.Flag_group_by_object = True


    def on_cancel(self, instance, value):
        '''Events called when the "CANCEL" dialog box button is clicked.'''


    # @staticmethod
    # def remove_item(instance):
    # self.root.ids.md_list.
    # instance.parent.parent.parent.remove_widget(instance.parent.parent)

    def remove_item(self, instance):
        result = self.rkv.remove_work_do(instance.work_do['id'])
        if result != 'no_link':
            if result != 'error':
                print (len(instance.parent.children))
                print (instance.parent.children)
                if not self.Flag_group_by_object and len(instance.parent.children)<=2:
                    print(self.Flag_group_by_object)
                    instance.parent.parent.remove_widget(instance.parent)
                else:
                    instance.parent.remove_widget(instance)
                i = 0
                for work_do in self.rkv.do_work_list['data']:
                    if work_do['id'] == instance.work_do['id']:
                        self.rkv.do_work_list['data'].pop(i)
                    i += 1
                self.dialog.dismiss()
        else:
            self.dialog.text = 'Нет соединения'


    def open_remove_dialog(self, instance):
        self.dialog = MDDialog(
            text="Удалить запись?",
            buttons=[
                Button_ok(instance=instance),
                Button_cancel(instance=instance),
                ],
            )
        self.dialog.open()

        # self.root.ids.md_list.remove_widget(instance)


    def update_item(self, instance):
        print(instance.work_do['id'])

        instance_root = instance
        #FrontBox = instance.parent.parent.ids.FrontBox
        #SwipeBox = instance.parent.parent.ids.SwipeBox
        id_work_do = instance_root.work_do['id']
        amount = instance_root.work_do['224']
        print(instance_root.work_do)

        object = list(filter(lambda x: x['id'] == instance_root.work_do['parent_item_id'], self.rkv.object_list['data'])).pop()

        if instance_root.work_do['252']:
            equipment = list(
                filter(lambda x: x['251'] == instance_root.work_do['252'], self.rkv.equipment_list['data'])).pop()
        else:
            equipment = ''
        work_type = list(
            filter(lambda x: x['219'] == instance_root.work_do['223'], self.rkv.work_list['data'])).pop()
        complex = list(
            filter(lambda x: x['name'] == instance_root.work_do['237'], self.rkv.complex_list['data'])).pop()
        worker = instance_root.work_do['239']
        worker_list = list(
            filter(lambda x: instance_root.work_do['239'].find(x['8']) != -1, self.rkv.users_list['data']))
        notes = instance_root.work_do['253']

        if self.Flag_AddNew == 0 and self.rkv.Flag_config:
            if self.rkv.Flag_connection:
                if self.rkv.Flag_authent:
                        # instance_root.height = 0
                    instance_root.clear_widgets()
                    instance_root.add_widget(AddNewWork(text='hello'))
                    self.Flag_AddNew = 1

                    self.dropdown = CustomDropDown()
            else:
                instance_root.clear_widgets()
                instance_root.add_widget(AddNewWork(text='hello'))
                self.Flag_AddNew = 1
                    # button = self.root.ids.new.children[0].ids.worker.add_widget(
                    #    Worker_item(name_worker=self.rkv.user_secondname, id_worker=self.rkv.user_id)
                    # )
                    # self.root.ids.new.children[0].children[2].bind(on_double_tap=dropdown.open)
                self.dropdown = CustomDropDown()
        instance_root.unbind(on_long_press=self.open_remove_dialog)
        instance_root.unbind(on_double_press=self.update_item)
        instance_new = instance_root.children[0]
        instance_new.ids.object.text = object['158']
        instance_new.ids.object.name = object['id']
        instance_new.ids.object.parent.name = 'not_edit'

        if equipment:
            instance_new.ids.equipment.text = equipment['251']
            instance_new.ids.equipment.name = equipment['id']
            instance_new.ids.equipment.parent.name = 'not_edit'

        instance_new.ids.amount.text = amount
        instance_new.ids.amount.parent.name = 'not_edit'

        instance_new.ids.work_type.text = work_type['219']
        instance_new.ids.work_type.name = work_type['id']
        instance_new.ids.work_type.parent.name = 'not_edit'

        instance_new.ids.complex.text = complex['name']
        instance_new.ids.complex.name = complex['id']
        instance_new.ids.complex.parent.name = 'not_edit'

        instance_new.ids.notes.text = notes
        instance_new.ids.notes.parent.name = 'not_edit'

        for user in worker_list:
            instance_new.ids.worker.add_widget(
                Worker_item(name_worker=user['8'], id_worker=user['id'])
            )


    def bilder_for_list(self, *args):
        print(self.loop_work_do.is_triggered)
        if not self.item_for_groupe_bilder and self.loop_work_do or self.count>=4:
            print('stop')
            self.loop_work_do.cancel()
            print(self.loop_work_do.is_triggered)
        while self.item_for_groupe_bilder and time() < (Clock.get_time() + MAX_TIME_GROUP):
            if self.count<4:
                print(self.count)
                self.count += 1
                work_do_item = self.item_for_groupe_bilder.pop(0)
                object_name = list(filter(lambda x: x['id'] == work_do_item['parent_item_id'],
                                          self.rkv.object_list['data'])).pop()
                print(work_do_item['226'])
                unit_name = list(filter(lambda x: x['id'] == work_do_item['226'],
                                          self.rkv.work_list['data'])).pop()
                self.root.ids.md_list.add_widget(
                    SwipeToDeleteItem(work_do=work_do_item, object_name=object_name['158'], unit_name=unit_name['243'])
                )
                self.root.ids.md_list.children[0].bind(on_long_press=self.open_remove_dialog)
                self.root.ids.md_list.children[0].bind(on_double_press=self.update_item)


    def load_items(self, work_list=0, work_do_list=0):
        if work_do_list != 0:
            if self.loop_work_do:
                self.loop_work_do.cancel()
            self.item_for_groupe_bilder = {}
            self.root.ids.md_list.clear_widgets()
            self.count = 0
            self.item_for_groupe_bilder = work_do_list['data'].copy()
            print(self.item_for_groupe_bilder)
            self.loop_work_do = Clock.schedule_interval(self.bilder_for_list, 0)


        if work_list != 0:
            kollwork = 0
            i = self.rkv.last_id_work
            if i == 0:
                self.root.ids.work_t.clear_widgets()
                i = -1
            for i in range(i+1, len(work_list['data'])):
                if kollwork < 15:
                    self.root.ids.work_t.add_widget(
                        WorkTypeCard(work_list=work_list['data'][i])
                    )
                    self.root.ids.work_t.add_widget(
                        MDSeparator())
                    self.rkv.last_id_work = i
                    kollwork += 1
                else:
                    break


    def add_work(self):
        if self.Flag_AddNew == 0 and self.rkv.Flag_config:
            if self.rkv.Flag_connection:
                if self.rkv.Flag_authent:
                    self.root.ids.new.add_widget(AddNewWork(text='hello'))
                    self.Flag_AddNew = 1
                    button = self.root.ids.new.children[0].children[-2].children[-1].add_widget(
                        Worker_item(name_worker=self.rkv.user_secondname, id_worker=self.rkv.user_id)
                    )
                    self.dropdown = CustomDropDown()
            else:
                self.root.ids.new.add_widget(AddNewWork(text='hello'))
                self.Flag_AddNew = 1
                button = self.root.ids.new.children[0].ids.worker.add_widget(
                    Worker_item(name_worker=self.rkv.user_secondname, id_worker=self.rkv.user_id)
                )
                # self.root.ids.new.children[0].children[2].bind(on_double_tap=dropdown.open)
                self.dropdown = CustomDropDown()
            # widget.bind(text=on_text)
            # self.root.ids.new.children[0].children[1].bind(text=self.on_text)
            # self.root.ids.new.children[0].children[1].bind(text=self.on_text)
            # print(self.root.ids.new.children[0])
        # else:
        # self.root.ids.new.height = self.height


    def button_save_new(self, instance):  # dropdown_fields, text_fields, worker_field):
        Flag_error = False
        if instance.ids.object.name == 'error':
            instance.ids.object.line_color_normal = (1, 0, 0, 1)
            Flag_error = True
        if instance.ids.work_type.name == 'error':
            instance.ids.work_type.line_color_normal = (1, 0, 0, 1)
            Flag_error = True
        if instance.ids.complex.name == 'error':
            instance.ids.complex.line_color_normal = (1, 0, 0, 1)
            Flag_error = True
        if instance.ids.equipment.name == 'error' and instance.ids.equipment.text != '':
            instance.ids.equipment.line_color_normal = (1, 0, 0, 1)
            Flag_error = True
        if instance.ids.amount.text == '' or instance.ids.amount.name == 'error':
            instance.ids.amount.line_color_normal = (1, 0, 0, 1)
            Flag_error = True

        if not Flag_error:
            if type(instance.parent).__name__ == 'MDBoxLayout':
                object_name = instance.ids.object.text
                worker_id_list = ''
                worker_name_list = ''
                for worker_item in instance.ids.worker.walk(restrict=True):
                    if type(worker_item).__name__ == 'Worker_item':
                        worker_id_list += f",{worker_item.name}"
                    if type(worker_item).__name__ == 'Button':
                        worker_name_list += f",{worker_item.text}"
                worker_id_list = worker_id_list[1:]
                worker_name_list = worker_name_list[1:]
                array_id_for_new = {'223': instance.ids.work_type.name,
                                    '239': worker_id_list,
                                    '224': instance.ids.amount.text,
                                    '237': instance.ids.complex.name,
                                    '267': '',
                                    '253': instance.ids.notes.text,
                                    '252': instance.ids.equipment.name,
                                    'parent_item_id': instance.ids.object.name}
                array_text_for_new = {'223': instance.ids.work_type.text,
                                      '239': worker_name_list,
                                      '224': instance.ids.amount.text,
                                      '237': instance.ids.complex.text,
                                      '267': self.rkv.date_now,
                                      '253': instance.ids.notes.text,
                                      'parent_item_id': instance.ids.object.name,
                                      'id': '',
                                      '266': '-',
                                      '252': instance.ids.equipment.text}
                result = self.rkv.add_new_do_work(array_id_for_new, array_text_for_new)
                if result['status']=='success':
                    array_text_for_new['id'] = result['data']['id']
                    self.rkv.do_work_list = self.rkv.get_do_work_list(reload=True)
                    child_index_new_work_do = len(self.root.ids.md_list.children)
                    if self.Flag_group_by_object:
                        unit_name = list(filter(lambda x: x['id'] == instance.ids.work_type.name,
                                                self.rkv.work_list['data'])).pop()
                        self.root.ids.md_list.add_widget(
                            SwipeToDeleteItem(work_do=array_text_for_new, object_name=instance.ids.object.text,unit_name=unit_name['243']),child_index_new_work_do)
                        self.root.ids.new.clear_widgets()
                        self.root.ids.md_list.children[child_index_new_work_do].bind(on_long_press=self.open_remove_dialog)
                        self.root.ids.md_list.children[child_index_new_work_do].bind(on_double_press=self.update_item)
                    else:
                        self.rkv.last_id_do_work = 0
                        self.group_by_object(self.root, True)
                    self.root.ids.new.clear_widgets()
                else:
                    self.dialog = MDDialog(
                        text="Нет соединения",
                        buttons=[
                            Button_cancel(instance=instance),
                        ],
                    )
                    self.dialog.open()


            else:
                array_for_update = {}
                array_for_card = list(
                    filter(lambda x: x['id'] == instance.parent.work_do['id'], self.rkv.do_work_list['data'])).pop()
                orign_array_for_card = array_for_card.copy()
                object_name = instance.ids.object.text
                if instance.ids.object.parent.name == 'edit':
                    array_for_update['parent_item_id'] = instance.ids.object.name
                if instance.ids.work_type.parent.name == 'edit':
                    array_for_update['field_223'] = instance.ids.work_type.name
                    array_for_card['223'] = instance.ids.work_type.text
                if instance.ids.complex.parent.name == 'edit':
                    array_for_update['field_237'] = instance.ids.complex.name
                    array_for_card['237'] = instance.ids.complex.text
                if instance.ids.equipment.parent.name == 'edit' and instance.ids.equipment.text != '':
                    array_for_update['field_252'] = instance.ids.equipment.name
                    array_for_card['252'] = instance.ids.equipment.text
                if instance.ids.amount.parent.name == 'edit':
                    array_for_update['field_224'] = instance.ids.amount.text
                    array_for_card['224'] = instance.ids.amount.text
                if instance.ids.notes.parent.name == 'edit':
                    array_for_update['field_253'] = instance.ids.notes.text
                    array_for_card['253'] = instance.ids.notes.text
                if instance.ids.worker.parent.name == 'edit':
                    worker_id_list = ''
                    worker_name_list = ''
                    for worker_item in instance.ids.worker.walk(restrict=True):
                        if type(worker_item).__name__ == 'Worker_item':
                            worker_id_list += f",{worker_item.name}"
                        if type(worker_item).__name__ == 'Button':
                            worker_name_list += f",{worker_item.text}"
                    worker_name_list = worker_name_list
                    array_for_update['field_239'] = worker_id_list[1:]
                    array_for_card['239'] = worker_name_list[1:]
                result = self.rkv.update_work_do(array_for_update, instance.parent.work_do['id'])

                if result == 'success':
                    print('sucsess')
                    FrontBox = instance.parent
                    unit_name = FrontBox.unit_name
                    FrontBox.clear_widgets()
                    FrontBox.add_widget(
                        Content_do_work(work_do=array_for_card, object_name=object_name, unit_name=unit_name)
                    )
                    FrontBox.bind(on_long_press=self.open_remove_dialog)
                    FrontBox.bind(on_double_press=self.update_item)
                else:
                    instance.parent.work_do = orign_array_for_card
                    for key in array_for_card:
                        array_for_card[key] = orign_array_for_card[key]
                    self.dialog = MDDialog(
                        text="Нет соединения",
                        buttons=[
                            Button_cancel(instance=instance),
                        ],
                    )
                    self.dialog.open()
            self.Flag_AddNew = 0


    def button_close_new(self, instance):
        if type(instance.parent).__name__ == 'SwipeToDeleteItem':
            #work_do = list(filter(lambda x: x['id'] == instance.parent.name, self.rkv.do_work_list['data'])).pop()
            #object = list(filter(lambda x: x['id'] == work_do['parent_item_id'], self.rkv.object_list['data'])).pop()
            FrontBox = instance.parent

            print(FrontBox.unit_name)
            unit_name = FrontBox.unit_name
            FrontBox.clear_widgets()
            FrontBox.add_widget(
                Content_do_work(work_do=FrontBox.work_do, object_name=FrontBox.object_name, unit_name = unit_name)
            )
            FrontBox.bind(on_double_press=self.update_item)
            FrontBox.bind(on_long_press=self.open_remove_dialog)

        else:
            print(instance.parent)
            self.root.ids.new.clear_widgets()
        self.Flag_AddNew = 0


    def on_text(self, instance, value, item_list, field, drop_down=True, root=0):
        if drop_down:
            self.dropdown.clear_widgets()
            instance.name = 'error'
            instance.parent.name = 'edit'
            self.item_for_builder = []
            for item in item_list['data']:
                lower = item[field].lower()
                if lower.find(instance.text.lower()) != -1:
                    element_for_item = []
                    element_for_item.append(item[field])
                    element_for_item.append(item['id'])
                    self.item_for_builder.append(element_for_item)
        else:
            instance.parent.name = 'edit'
            if root != 0:
                if instance == root.ids.amount:
                    if value != '' and value.isdigit():
                        instance.name = 'not_error'
                        print('not_error')
                    else:
                        instance.name = 'error'
                        print('error')

    def list_builder(self, *args):
        while self.item_for_builder and time() < (Clock.get_time() + MAX_TIME):
            item = self.item_for_builder.pop(0)  # i want the first one
            self.dropdown.add_widget(
                ItemForDropDown(name_item=item[0], id_item=item[1])
            )

    def on_focus(self, instance, event_focus, item_list, field):
        self.activ_text_field = instance

        if event_focus:
            self.item_for_builder = []
            self.loop = Clock.schedule_interval(self.list_builder, 0)
            if instance.text:
                self.dropdown.clear_widgets()
                self.dropdown.open(instance)
                for item in item_list['data']:
                    lower = item[field].lower()
                    if lower.find(instance.text.lower()) != -1:
                        element_for_item = []
                        element_for_item.append(item[field])
                        element_for_item.append(item['id'])
                        self.item_for_builder.append(element_for_item)
            else:
                self.dropdown.clear_widgets()
                self.dropdown.open(instance)
                for item in item_list['data']:
                        element_for_item = []
                        element_for_item.append(item[field])
                        element_for_item.append(item['id'])
                        self.item_for_builder.append(element_for_item)
        else:
            print('notfocus')
            self.loop.cancel()
            self.item_for_builder = []


    def remove_worker(self, instance, instance_parent):
        if instance.text != self.rkv.user_secondname:
            instance_parent.parent.parent.name = 'edit'
            instance_parent.parent.remove_widget(instance_parent)


    def click_drop_item(self, text, id_item):
        if self.activ_text_field.name == 'worker':
            self.activ_text_field.parent.name = 'edit'
            self.dropdown.dismiss()
            flag = 0
            for work_item in self.activ_text_field.walk(restrict=True):
                if type(work_item).__name__ == 'Button' and work_item.text == text:
                    flag = 1
            if flag == 0:
                self.activ_text_field.add_widget(
                    Worker_item(name_worker=text, id_worker=str(id_item))
                )
        else:
            self.dropdown.dismiss()
            # self.dropdown.bind(on_select=lambda instance, x: self.root.ids.new.children[0].children[1].text=instance.text)
            self.activ_text_field.text = text
            self.activ_text_field.name = id_item
            self.activ_text_field.parent.name = 'edit'


    def show_drop_worker(self, instance, id_object, instance_object):
        if instance_object.text != '':
            self.activ_text_field = instance
            self.dropdown.clear_widgets()
            self.dropdown.open(instance)
            worker_list = self.rkv.get_users_on_object(id_object)
            for worker in worker_list['data']:
                self.dropdown.add_widget(
                    ItemForDropDown(name_item=worker['8'], id_item=worker['id'])
                )


    def click_drop_worker(self, text, id_item):
        pass
        # self.activ_text_field.error = False
        # print (self.activ_text_field.name)


    def start_load(self, scroll):
        if self.Flag_Update_List:
            self.Flag_Update_List = False
            if scroll.name == 'scroll_work':
                self.load_items(self.rkv.work_list)
            elif scroll.name == 'scroll_do_work':
                if self.Flag_group_by_object:
                    if not self.loop_work_do.is_triggered:
                        self.count = 0
                        self.loop_work_do = Clock.schedule_interval(self.bilder_for_list, 0)
                        self.root.ids.scroll_do_work.do_scroll_y = True
                    #self.load_items(0, self.rkv.do_work_list)
                else:
                    if not self.loop_work_do.is_triggered:
                        self.count = 0
                        self.loop_work_do = Clock.schedule_interval(self.bilder_for_grope_list, 0)
                        self.root.ids.scroll_do_work.do_scroll_y = True


        elif self.Flag_Reload_List:
            self.Flag_Reload_List = False
            if scroll.name == 'scroll_work':
                self.rkv.last_id_work = 0

                self.load_items(self.rkv.work_list)
                self.root.ids.scroll_do_work.do_scroll_y = True
            elif scroll.name == 'scroll_do_work':
                if self.Flag_group_by_object:
                    self.rkv.last_id_do_work = 0
                    self.load_items(0, self.rkv.do_work_list)
                    self.root.ids.scroll_do_work.do_scroll_y = True
                else:
                    self.rkv.last_id_do_work = 0
                    self.group_by_object(self.root,True)
        self.root.ids.spiner.active = False



    def start_event_load(self, scroll):
        if scroll.scroll_y< -2.0 or scroll.scroll_y>3.0:
            print(scroll.scroll_y)
            self.root.ids.scroll_do_work.do_scroll_y = False
            #self.root.ids.scroll_do_work.do_scroll_y = True
            #self.root.ids.scroll_do_work.scroll_to(self.root.ids.md_list.children[var - 1], padding=10, animate=False)
        #if scroll.scroll_y > 1:
            #print(scroll.scroll_y)
            #print(scroll.children[0].children[0].size[1])
            #print(scroll.children[0].size[1] * scroll.scroll_y - scroll.children[0].size[1])
        if (scroll.children[0].size[1] * scroll.scroll_y) < -700:
            self.Flag_Update_List = True
        elif scroll.scroll_y > 1:
            if (scroll.children[0].size[1] / scroll.scroll_y) < scroll.children[0].size[1] - 700:
                self.root.ids.spiner.pos = (self.root.ids.scr1.size[0] / 2, self.root.ids.scr1.size[1] - (
                            (scroll.children[0].size[1] * scroll.scroll_y) - scroll.children[0].size[1]) / 4)
                self.root.ids.spiner.active = True
                self.Flag_Reload_List = True

    def build(self):
        #self.theme_cls.theme_style = "Dark"
        #self.theme_cls.font_styles["Weather"] = ["Weather", 16, False, 0.15]
        self.theme_cls.primary_palette = "BlueGray"
        return Builder.load_string(
        """
#:import ScrollEffect  kivy.effects.scroll.ScrollEffect
<ContentNavigationDrawer>

    ScrollView:
        effect_cls: ScrollEffect
        MDList:
        
            OneLineIconListItem:
                text: "СЕКРЕТ СЕРВИС"
                bg_color: 0,0.2,0.25,0.6
                IconLeftWidget:
                    icon: "eye"
            OneLineIconListItem:
                text: "Выполненые работы"
                font_size: 30
                on_press:
                    root.nav_drawer.set_state("close")
                    root.screen_manager.current = "scr 1"
                    root.toolbar.right_action_items = [["home-city-outline", lambda x: app.group_by_object(self)], ["calendar", lambda x: app.show_date_picker()],["plus", lambda x: app.add_work()]]
                    root.toolbar.title = 'Работы'
                IconLeftWidget:
                    icon: "hammer-screwdriver"
            OneLineIconListItem:
                text: "Список работ"
                
                on_press:
                    root.nav_drawer.set_state("close")
                    root.screen_manager.current = "scr 2"
                    root.toolbar.right_action_items = []
                    root.toolbar.title = "Список работ"
                IconLeftWidget:
                    icon: "server"
            OneLineIconListItem:
                text: "Настройки"
                
                on_press:
                    root.nav_drawer.set_state("close")
                    root.screen_manager.current = "scr 3"
                    root.toolbar.right_action_items = []
                    root.toolbar.title = "Настройки"
                IconLeftWidget:
                    icon: "cog-outline"
                    
            OneLineIconListItem:
                text: "Информация"
                
                on_press:
                    root.nav_drawer.set_state("close")
                    root.screen_manager.current = "scr 4"
                    root.toolbar.right_action_items = []
                    root.toolbar.title = "Информация"
                IconLeftWidget:
                    icon: "information-outline"
MDScreen:
    MDBoxLayout:
        orientation: 'vertical'
        spacing: "10dp"

        MDToolbar:
            id: toolbar
            pos_hint: {"top": 1}
            elevation: 11
            title: 'Работы'
            use_overflow: True
#app.date_start + '/' + app.date_end
            left_action_items: [["menu", lambda x: nav_drawer.set_state("open")]]
            right_action_items: [["home-city-outline", lambda x: app.group_by_object(self)],["calendar", lambda x: app.show_date_picker()],["plus", lambda x: app.add_work()]]
        FloatLayout:
            size_hint_y: None
            height: -20
            MDSpinner:
                id: spiner
                size_hint: None, None
                size: dp(20), dp(20)
                #pos_hint: {'x': .5}
                #pos: 500
                active: False
        MDNavigationLayout:
            x: toolbar.height

            ScreenManager:
                id: screen_manager

                MDScreen:
                    id: scr1
                    name: "scr 1"
                    #size: (self.parent.width, self.parent.height)
                    MDBoxLayout:
                        orientation: "vertical"
                        spacing: "10dp"
                        #size: (self.parent.width, self.parent.height)
                        ScrollView:
                            #always_overscroll: False
                            id: scroll_do_work
                            name: 'scroll_do_work'
                            #size: (self.parent.width, self.parent.height)
                            on_scroll_move: app.start_event_load(self)
                            on_scroll_stop: app.start_load(self)

                            StackLayout:
                                #spacing: "7dp"
                                id: md_list1
                                size_hint_y: None
                                height: self.minimum_height

                                MDBoxLayout:
                                    orientation: "vertical"
                                    id: new
                                    size_hint_y: None
                                    height: self.minimum_height
                                StackLayout:
                                    spacing: "7dp"
                                    id: md_list
                                    size_hint_y: None
                                    height: self.minimum_height

                MDScreen:
                    name: "scr 2"

                    MDBoxLayout:
                        orientation: "vertical"
                        spacing: "10dp"

                        ScrollView:
                            name: 'scroll_work'
                            id: scroll_m
                            #size: (self.parent.width, self.parent.height)
                            on_scroll_move: app.start_event_load(self)
                            on_scroll_stop: app.start_load(self)
                            do_scroll_y: True
                            StackLayout:
                                spacing: "7dp"
                                id: work_t
                                size_hint_y: None
                                height: self.minimum_height


                MDScreen:
                    name: "scr 3"
                    StackLayout:
                        size_hint: 1, 1
                        padding: 5
                        MDTextField:
                            id: adress
                            hint_text: "Multi-line text"
                            #text_color: 0, 0, 0, 1
                            hint_text: "Адрес сервера"
                            helper_text: "Введите адрес сервера"
                            helper_text_mode: "on_focus"
                            icon_right: "web"
                            font_size: Window.width/20

                        MDTextField:
                            id: login
                            hint_text: "Multi-line text"
                            #text_color: 0,0,0,1
                            hint_text: "Имя пользователя"
                            helper_text: "Введите имя пользователя"
                            helper_text_mode: "on_focus"
                            icon_right: "account"
                            font_size: Window.width/20
                        MDTextField:
                            id: password
                            hint_text: "Пароль"
                            #text: "password"
                            helper_text: "Введите пароль"
                            password: True
                            icon_right: "key-variant"
                            size_hint_x: 1
                            helper_text_mode: "on_focus"
                            font_size: Window.width/20
                        BoxLayout:
                            size_hint_y: None
                            height: 10
                        MDRaisedButton:
                            id: singup_btn
                            text: 'Войти в систему'
                            font_size: Window.width/20
                            size_hint_x: 1
                            height: 90
                            pos_hint: {'top':1}
                            on_release: app.button_login(self, root.ids.adress, root.ids.login, root.ids.password)
                MDScreen:
                    name: "scr 4"
                    StackLayout:
                        size_hint: 1, 1
                        padding: 1
                        ScrollView:
                            effect_cls: ScrollEffect
                            do_scroll_y: True
                            
                            StackLayout:
                                size_hint_y: None
                                height: self.minimum_height
                                padding: 3
                                SwipeLabel:
                                    text: 'Перед началом работ зайдите в пункт меню "Настройки" и введите адрес сервера, логин и пароль и нажмите кнопку "Войти в систему" '
                                OneLineIconListItem:
                                    text: "- Кнопка групировки по объектам"
                                    font_size: Window.width/20#self.parent.parent.width/20
                                    IconLeftWidget:
                                        icon: "home-city-outline"  
                        
                                SwipeLabel:
                                    text: " При запуске программы показывается режим сортировки по дате добавления, если хотите переключить в режим группировки работ по объектам нажмите кнопку 'Групировка по объктам'. Чтобы переключиться обратно в режим сортировки по дате - нажмите еще раз эту кнопку"                                          
                                    markup: True
                                OneLineIconListItem:
                                    text: "- Фильтр по дате"
                                    font_size: Window.width/20#self.parent.parent.width/20
                                    IconLeftWidget:
                                        icon: "calendar"  
                        
                                SwipeLabel:
                                    text: "Если хотите просмотреть работы за прошлые месяци нажмите кнопку 'Фильр по дате' выберите дату начала и дату окончания в пределах одного месяца. Если, ввели не то - просто нажмите ОТМЕНА и попробуйте заново"
                                OneLineIconListItem:
                                    text: "- Добавить новую работу"
                                    font_size: Window.width/20#self.parent.parent.width/20
                                    IconLeftWidget:
                                        icon: "plus"  
                                
                                SwipeLabel:
                                    text: "Нажмите эту кнопку если хотите добавить новую выполненую работу. Учтите есть поля обязательные для заполнения, если вы их не введете они обозначаться красным подчеркиванием, введите в них данные и сохраните"
                                
                                OneLineIconListItem:
                                    text: "Редактирование записи"
                                    font_size: Window.width/20#self.parent.parent.width/20 
                                SwipeLabel:
                                    text: " - Для редактирование добавленых работ нажмите три раза на нужную рработу"   
                                OneLineIconListItem:
                                    text: "Удаление записи"
                                    font_size: Window.width/20#self.parent.parent.width/20 
                                SwipeLabel:
                                    text: " - Для удаления добавленой работы нажмите и удерживайте палец над нужной работой в течении 3с" 
    MDNavigationDrawer:
        id: nav_drawer

        ContentNavigationDrawer:
            screen_manager: screen_manager
            nav_drawer: nav_drawer
            toolbar: toolbar
            new: new

<Object_Conteiner>
    name: root.object_name
    padding: "3dp"
    spacing: "5dp"
    size_hint_y: None
    height: self.minimum_height
    orientation: "vertical"

    SwipeLabel:
        text: root.object_name
        height: self.texture_size[1]+30
        bold: True
        #size_hint_x: None
        #width: Window.width
        halign: 'center'

<SwipeLabel@MDLabel>
    size_hint_y: None
    #pos_y: -50
    height: self.texture_size[1]
    font_size: Window.width/20#self.parent.parent.width/20
    #valign: 'top'
    pos_hint: {'x': 0, 'y': 1}

<SwipeBox@MDBoxLayout>
    size_hint_y: None
    height: self.minimum_height

<SwipeToDeleteItem>:
    padding: 4
    #elevation: 15
    size_hint_y: None
    height: self.minimum_height
    orientation: "vertical"
    SwipeLabel:
        id: work_do
        text: f"[i][b]{root.work_do['223']}[/b][/i]\\n[b]Колличество: [/b]   {root.work_do['224']} {root.unit_name}\\n[b]           Кабель: [/b]   {root.work_do['252']}\\n[b]          Объект:[/b]   {root.object_name}\\n[b]               Дата:[/b]   {root.work_do['267']}\\n[b]   Сложность:[/b]   {root.work_do['237']}\\n[b]          Премия:[/b]   {root.work_do['266']}\\n[b]Монтажники:[/b]   {root.work_do['239']}\\n[b] Примечания:[/b]   {root.work_do['253']}"
                #text : "[table][tr][td]table cell 1[/td][td]table cell 2[/td][/tr][/table]"
        markup: True

<Content_do_work>
    size_hint_y: None
    height: self.texture_size[1]
    font_size: Window.width / 20  # self.parent.parent.width/20
    pos_hint: {'x': 0, 'y': 1}
    id: work_type
    text: f"[i][b]{root.work_do['223']}[/b][/i]\\n[b]Колличество: [/b]   {root.work_do['224']} {root.unit_name}\\n[b]           Кабель: [/b]   {root.work_do['252']}\\n[b]          Объект:[/b]   {root.object_name}\\n[b]               Дата:[/b]   {root.work_do['267']}\\n[b]   Сложность:[/b]   {root.work_do['237']}\\n[b]          Премия:[/b]   {root.work_do['266']}\\n[b]Монтажники:[/b]   {root.work_do['239']}\\n[b] Примечания:[/b]   {root.work_do['253']}"
    markup: True

<Worker_item>:
    name: root.id_worker
    size_hint: None, None
    height: self.minimum_height
    width:self.minimum_width
    Button:
        background_normal: ''
        size_hint: None, None
        size: (self.texture_size[0]+10, self.texture_size[1]+5)
        text: root.name_worker
        color: 0,0,0,1
        font_size: Window.width/20#self.parent.parent.width/20
        on_release: app.remove_worker(self, self.parent)
        canvas.before:
            Color:
                rgba: .5, .5, .5, 1
            Line:
                width: 1
                rectangle: self.x, self.y, self.width, self.height

<AddNewWork>:
    id: addwor
    size_hint_y: None
    height: self.minimum_height
    orientation: "vertical"
# Объекты
    BoxLayout:
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
        name: 'not_edit'
        MDTextField:
            name: 'error'
            id: object
            multiline: True
            hint_text: "Multi-line text"
            font_size: Window.width/18
            #text_color: 0,0,0,1
            #line_color_normal: 1, 0, 0, 1
            hint_text: "Объект"
            helper_text: "Выберите обект"
            helper_text_mode: "on_focus"
            on_focus: app.on_focus(self, self.focus,app.rkv.object_list, '158')
            on_text: app.on_text(self, self.text, app.rkv.object_list, '158')
# Монтажники
    BoxLayout:
        size_hint: 1, None
        height: self.minimum_height
        name: 'not_edit'

        StackLayout:
            padding: [0,5,0,5]
            id: worker
            name: 'worker'
            size_hint: 0.9, None
            height: self.minimum_height
            orientation: "lr-tb"

        BoxLayout:
            size_hint: 0.1, 1
            Button:
                background_normal: ''
                color: 0,0,0,1
                #background_color: 0,0.2,0.25,0.6
                #adaptive_size: True
                size_hint: 1, 1
                #size: (self.texture_size[0], self.texture_size[1])self.parent.parent.parent.children[3].children[0].name
                text: '+'
                font_size: Window.width/20#self.parent.parent.width/20
                on_release: app.show_drop_worker(root.ids.worker, root.ids.object.name, root.ids.object)
                canvas.before:
                    Color:
                        rgba: .5, .5, .5, 1
                    Line:
                        width: 1
                        rectangle: self.x, self.y, self.width, self.height
                
    MDSeparator:
    MDLabel:
        size_hint_y: None
        text: 'Выберите напарника'
        height: self.texture_size[1]
        font_size: Window.width/23
        theme_text_color: "Custom"
        text_color: 0, 0, 0, 0.5
#Выбор типа работ
    BoxLayout:
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
        name: 'not_edit'
        MDTextField:
            name: 'error'
            id: work_type
            multiline: True
            font_size: Window.width/18
            hint_text: "Multi-line text"
            text_color: 0,0,0,1
            helper_text_mode: "on_focus"
            hint_text: "Тип работ"
            helper_text: "Выберите нужный тип работ"
            on_focus: app.on_focus(self, self.focus,app.rkv.work_list, '219')
            on_text: app.on_text(self, self.text, app.rkv.work_list, '219')

# Блок Колличество и Сложность работ
        BoxLayout:
            size_hint_y: None
            height: self.minimum_height
            orientation: 'horizontal'
            BoxLayout:
                size_hint_y: None
                height: self.minimum_height
                orientation: 'horizontal'
                size_hint_x: 0.4
                name: 'not_edit'
                MDTextField:
                    name: 'error'
                    id: amount
                    font_size: Window.width/18
                    #text_color: 0,0,0,1
                    hint_text: "Колличество"
                    helper_text: "Введите колличество"
                    helper_text_mode: "on_focus"
                    on_text: app.on_text(self, self.text, 'empty_array', 'ampty_field', False, root)
            BoxLayout:
                size_hint_y: None
                height: self.minimum_height
                orientation: 'horizontal'
                size_hint_x: 0.6
                name: 'not_edit'
                MDTextField:
                    name: 'error'
                    id: complex
                    font_size: Window.width/18
                    text_color_normal: 0, 1, 0, 1
                    hint_text: "Сложность работ"
                    helper_text: "Выберите сложность"
                    helper_text_mode: "on_focus"
                    on_focus: app.on_focus(self, self.focus,app.rkv.complex_list, 'name')
                    on_text: app.on_text(self, self.text, app.rkv.complex_list, 'name')
#Выбор оборудования
        BoxLayout:
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'
            name: 'not_edit'
            MDTextField:
                name: 'error'
                id: equipment
                multiline: True
                font_size: Window.width/18
                hint_text: "Multi-line text"
                text_color: 0,0,0,1
                hint_text: "Оборудовние"
                helper_text: "Выберите используемое оборудование"
                helper_text_mode: "on_focus"
                on_focus: app.on_focus(self, self.focus,app.rkv.equipment_list, '251')
                on_text: app.on_text(self, self.text, app.rkv.equipment_list, '251')

# Примечания
        BoxLayout:
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'
            name: 'not_edit'
            MDTextField:
                name: 'error'
                id: notes
                multiline: True
                font_size: Window.width/18
                hint_text: "Multi-line text"
                text_color: 0,0,0,1
                hint_text: "Примечание"
                helper_text: "Опишите примечание к работе"
                helper_text_mode: "on_focus"
                on_text: app.on_text(self, self.text, 'empty_array', 'ampty_field', False)

# Блок кнопок
    BoxLayout:
        size_hint_y: None
        height: self.minimum_height
        orientation: "horizontal"
        MDRaisedButton:
            size_hint_x: 0.5
            size_hint_y: None
            height: Window.width/10
            text: "Сохранить"
            font_size: Window.width/20#self.parent.parent.width/20
            on_release: app.button_save_new(root)#([root.ids.object, root.ids.work_type, root.ids.complex, root.ids.equipment], [root.ids.amount, root.ids.notes],root.ids.worker)

        MDRaisedButton:
            size_hint_x: 0.5
            height: Window.width/10
            text: "Отменить"
            font_size: Window.width/20#self.parent.parent.width/20
            on_press: app.button_close_new(self.parent.parent)

# Выпадающее меню
<CustomDropDown>:

<ItemForDropdown>:
    id: root.id_item
    border: (10,10,10,2)
    background_normal: ''
    
    text_size: root.width-3, None
    size_hint_y: None
    text: root.name_item
    color: 0,0,0,1
    height: self.texture_size[1]+10
    font_size: Window.width/19
    on_release:app.click_drop_item(root.name_item, root.id_item)
    canvas.before:
        Color:
            rgba: .5, .5, .5, 1
        Line:
            width: 1
            rectangle: self.x, self.y, self.width, self.height

#<ItemForDropdown>:
    #padding: "5dp"
    #name: root.id_item
    #spacing: "2dp"
    #size_hint_y: None
    #height: self.minimum_height
    #orientation: "vertical"

    #Button:


# Тип работ
<WorkTypeCard>:
    size_hint_y: None
    padding_x: "5dp"
    height: self.texture_size[1]
    font_size: Window.width/20#self.parent.parent.width/20
    #valign: 'top'
    pos_hint: {'x': 0, 'y': 1}
    text: f"[b]{root.work_list['219']}[/b]\\nЕдиница измерения: {root.work_list['243']}"
    markup: True
    
<Button_ok>
    text: 'OK'
    on_release: app.remove_item(root.instance)

<Button_cancel>
    text: 'ОТМЕНА'
    on_release: app.dialog.dismiss()
        """)
if __name__ == '__main__':
    MyApp().run()
