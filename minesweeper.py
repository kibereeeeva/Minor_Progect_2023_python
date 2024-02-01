import tkinter as tk          
from random import shuffle     
from tkinter.messagebox import showinfo, showerror    

colors = {                      
    0: 'white',
    1: 'blue',           
    2: '#008200',
    3: '#FF0000',
    4: '#000084',
    5: '#840000',
    6: '#008284',
    7: '#840084',
    8: '#000000',
}


class MyButton(tk.Button): 
    """Класс MyButton который наследуется из обычной ткинтеровской кнопки, 
    в экземпляре такого класса, будут хранится координаты и поведение кнопки (мина или нет?)"""

    def __init__(self, master, x:int, y:int, number=0, *args, **kwargs): 
        """Метод создания экземпляра класса MyButton. Master - родительский виджет(окно tkinter) где веселится кнопка, 
        *args и **kwargs принимаем все аргументы для определенной кнопки, 
        переменное количество позиционных и именованных аргументов соответственно. 
        Они позволяют передавать дополнительные аргументы при создании экземпляра 
        класса MyButton и передавать их дальше в конструктор родительского класса."""
        super(MyButton, self).__init__(master, width=3, font='Calibri 15 bold', *args, **kwargs) 
        #передача аргументов в конструктор родительского класса
        self.x = x
        self.y = y
        self.number = number      
        self.is_mine = False       
        self.count_bomb = 0
        self.is_open = False

    def __repr__(self):       
        """определяет вывод внутри консоли"""
        return f'MyButton {self.x}{self.y}{self.number}{self.is_mine}'  # вывод кнопок с их координатами и номерами


class MineSweeper:   
    """основной класс нашей игры (тут вся логика) с атрибутами/данными
         и поведение/методы при нажатии кнопок или запуска игры"""
    window = tk.Tk()     
    ROW = 7
    COLUMNS = 10         
    MINES = 20
    IS_GAME_OVER = False    
    IS_FIRST_CLICK = True

    def __init__(self):    
        """метод __init__ для инициализации игры, т.е. создание данных для дальнейшей обработки, например, кнопки"""
        self.buttons = []   #кнопки хранятся внутри класса как экземпляры, к которым мы обращаемся через  self.
        for i in range(MineSweeper.ROW +2):
            temp = []                                   
            for j in range(MineSweeper.COLUMNS + 2):
                btn = MyButton(MineSweeper.window, x=i, y=j)
                btn.config(command=lambda button=btn: self.click(button)) #чтобы корректно работало нажатие, с помощью метода config передаем кнопку, а через анонимную функию-посредник приминмаем кнопку и вызываем click
                btn.bind("<Button-2>", self.right_click) #Связка действия (вызов функции self.right_click) с событием (щелчок правой кнопкой мыши). 
                #"<Button-2>" - это спецификация события, которое представляет собой щелчок правой кнопкой мыши. "self.right_click" - это ссылка на метод или функцию, которая будет вызвана при возникновении этого события
                temp.append(btn)
            self.buttons.append(temp)

    def right_click(self, event):
        if MineSweeper.IS_GAME_OVER:
            return
        cur_btn = event.widget
        if cur_btn['state'] == 'normal':
            cur_btn['state'] = 'disabled'
            cur_btn['text'] = '❄️'
        elif cur_btn['text'] == '❄️':
            cur_btn['text'] = ''
            cur_btn['state'] = 'normal'


    def click(self, clicked_button: MyButton):  
        """обрабатываем нажатие кнопки: вывод мины или цифры, 
        причем расположен метод в MineSweeper, так как отжатая кнопка должна знать и о своих соседях"""
                                                 
        if MineSweeper.IS_GAME_OVER:
            return

        if MineSweeper.IS_FIRST_CLICK:
            self.insert_mines(clicked_button.number)
            self.count_mines_in_buttons()
            self.print_buttons()
            MineSweeper.IS_FIRST_CLICK = False

        if clicked_button.is_mine:              
            clicked_button.config(text='🎄', background='red', disabledforeground='black')
            clicked_button.is_open = True
            MineSweeper.IS_GAME_OVER = True
            showinfo('Game over','Вы проиграли! С Новым Годом! ')
            for i in range(1, MineSweeper.ROW + 1):
                for j in range(1, MineSweeper.COLUMNS + 1):
                    btn = self.buttons[i][j]
                    if btn.is_mine:
                        btn['text'] = '🎄'
        else:                                                            
            color = colors.get(clicked_button.count_bomb, 'black')
            if clicked_button.count_bomb:
                clicked_button.config(text=clicked_button.count_bomb, disabledforeground=color)
                clicked_button.is_open = True
            else:
                self.breadth_first_search(clicked_button) #далее создаем алгоритм обхода в ширину для открытия кнопок в игровом поле
        clicked_button.config(state='disabled')            
        clicked_button.config(relief=tk.SUNKEN)

    def breadth_first_search(self, btn: MyButton): 
        """Если количество бомб вокруг текущей кнопки равно нулю, 
        то происходит обход соседних кнопок. Для каждой соседней кнопки проверяется, 
        что она еще не открыта и находится в пределах игрового поля. Если это условие выполняется, 
        то соседняя кнопка добавляется в очередь queue для дальнейшего обхода."""

        queue = [btn]
        while queue:

            cur_btn = queue.pop()
            color = colors.get(cur_btn.count_bomb, 'black')
            if cur_btn.count_bomb:
                cur_btn.config(text=cur_btn.count_bomb, disabledforeground=color)
            else:
                cur_btn.config(text='', disabledforeground=color)
            cur_btn.is_open = True
            cur_btn.config(state='disabled')
            cur_btn.config(relief=tk.SUNKEN)

            if cur_btn.count_bomb == 0:
                 x, y = cur_btn.x, cur_btn.y       
                 for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if not abs(dx - dy) == 1:
                            continue

                        next_btn = self.buttons[x+dx][y+dy]
                        if not next_btn.is_open and 1<=next_btn.x<=MineSweeper.ROW and \
                                1 <= next_btn.y <= MineSweeper.COLUMNS and next_btn not in queue:   
                            queue.append(next_btn)

    def reload(self):
        """перезапуск игры: методом destroy() через обход элементов window.winfo_children
      и заново создаем виджеты через create_widgets"""
        [child.destroy() for child in self.window.winfo_children()]
        self.__init__()
        self.create_widgets()
        MineSweeper.IS_FIRST_CLICK = True
        MineSweeper.IS_GAME_OVER = False


    def create_settings_win(self):
        """Создаем меню настроек с изменяющимися параметрами, 
        пользуемся методом grid для локализации в окне"""
        win_settings = tk.Toplevel(self.window)
        win_settings.wm_title('Настройки')
        tk.Label(win_settings, text='Количество строк').grid(row=0, column=0)
        row_entry = tk.Entry(win_settings)
        row_entry.insert(0, MineSweeper.ROW)
        row_entry.grid(row=0, column=1, padx=20, pady=20)
        tk.Label(win_settings, text='Количество колонок').grid(row=1, column=0)
        column_entry = tk.Entry(win_settings)
        column_entry.insert(0, MineSweeper.COLUMNS)
        column_entry.grid(row=1, column=1, padx=20, pady=20)
        tk.Label(win_settings, text='Количество мин').grid(row=2, column=0)
        mines_entry = tk.Entry(win_settings)
        mines_entry.insert(0, MineSweeper.MINES)
        mines_entry.grid(row=2, column=1, padx=20, pady=20)
        save_btn = tk.Button(win_settings, text='Применить',
                             command=lambda :self.change_settings(row_entry, column_entry,mines_entry))
        save_btn.grid(row=3, column=0, columnspan=2)

    def change_settings(self, row: tk.Entry, column: tk.Entry, mines: tk.Entry):
        """пользовательская проверка на правильность ввведенных параметров меню"""
        try:
            int(row.get()), int(column.get()), int(mines.get())
        except ValueError:
            showerror('Ошибка', 'Вы ввели неправильное значение!')
            return
        MineSweeper.ROW = int(row.get())
        MineSweeper.COLUMNS = int(column.get())
        MineSweeper.MINES = int(mines.get())
        self.reload()

    def create_widgets(self):
        """создаем каскадное меню с лейблами, для каждой кнопки описываем событие"""

        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)

        setting_menu = tk.Menu(menubar, tearoff=0)
        setting_menu.add_command(label='Играть', command=self.reload) #сброс до начальных настроек методом .reload
        setting_menu.add_command(label='Настройки', command=self.create_settings_win) #дочернее окно с числом колонок, строк и мин
        setting_menu.add_command(label='Выход', command=self.window.destroy)
        menubar.add_cascade(label='Файл', menu=setting_menu)

        count = 1                                  
        for i in range(1, MineSweeper.ROW + 1):      
            for j in range(1, MineSweeper.COLUMNS + 1):    #учли барьерные кнопки, начиная с 1
                btn = self.buttons[i][j]
                btn.number = count                         
                btn.grid(row=i, column=j, stick='NWES')
                count += 1

        for i in range(1, MineSweeper.ROW + 1):
            tk.Grid.rowconfigure(self.window, i, weight=1)    

        for i in range(1, MineSweeper.COLUMNS + 1):
            tk.Grid.columnconfigure(self.window, i, weight=1)

    def open_all_buttons(self):
        """создаем нейтральные барьерные элементы"""
        for i in range(MineSweeper.ROW + 2):
            for j in range(MineSweeper.COLUMNS + 2):
                btn =  self.buttons[i][j]
                if btn.is_mine:
                    btn.config(text='*', background='red', disabledforeground='black') #раскрашиваем кнопки
                # elif btn.count_bomb == 1:
                #    btn.config(text=btn.count_bomb, fg='blue')
                # elif btn.count_bomb == 2:
                #    btn.config(text=btn.count_bomb, fg='green')
                elif btn.count_bomb in colors:                        #проверка на наличие нужного ключа
                    color = colors.get(btn.count_bomb, 'black')      #кнопка - не бомба, получаем ее цвет через значение ключа, если ключа нет, по умолчанию возвращаем черный цвет
                    btn.config(text=btn.count_bomb, fg=color)

    def start(self):
        """инкапсулируем методы, запускаем выпод игрового окна"""
        self.create_widgets()     #инкапсулируем нужные нам методы (заключается в сокрытии внутреннего устройства класса за интерфейсом, состоящим из методов класса)
        #self.open_all_buttons()
        MineSweeper.window.mainloop() #отображение игрового окна

    def print_buttons(self):
        """выводим учитанные бомбы из count_mines_in_buttons"""
        for i in range(1, MineSweeper.ROW + 1):           #редактируем вывод в консоль: бомба - "В" или сколько мин вокруг кнопки
            for j in range(1, MineSweeper.COLUMNS + 1):
                btn = self.buttons[i][j]
                if btn.is_mine:
                    print('B', end='')               
                else:
                    print(btn.count_bomb, end='')
            print()                                    #перенос для вывода в консоль н-мерного списка

    def insert_mines(self, number:int):
        """располаем бомбы на игровом поле с помощью списка индексов имеющихся мин"""
        index_mines = self.get_mines_places(number)      # список индексов мин
        print(index_mines)                                #счетчик пристваемвается всем кнопкам, кроме барьерных
        count = 1
        for i in range(1, MineSweeper.ROW + 1):             #проходим по рядам и по кнопкам в ним
            for j in range(1, MineSweeper.COLUMNS + 1):      #спрашиваем - если индекс кнопки в списке index_mines,если - да,  изменяем значение is_mine на True
                btn = self.buttons[i][j]
                if btn.number in index_mines:
                    btn.is_mine = True

    def count_mines_in_buttons(self):
        """здесь учитываем соседей наших бомб """
        for i in range(1, MineSweeper.ROW + 1):
            for j in range(1, MineSweeper.COLUMNS + 1):  #проходим по всем игровым кнопкам 
                btn = self.buttons[i][j]                 #позиционируемся на конкретной бомбе
                count_bomb = 0                           
                if not btn.is_mine:                       #обращаемся к соседям конкретной кнопки с конкретным координатным отступом
                    for row_dx in [-1, 0, 1]:
                        for col_dx in [-1, 0, 1]:
                            neighbour = self.buttons[i + row_dx][j + col_dx]
                            if neighbour.is_mine:
                                count_bomb += 1          #с помощью всевозможных сочетаний получаем всех соседей кнопки-не-бомбы и если этот сосед - мина, увеличиваем счетчик
                btn.count_bomb = count_bomb              #создаем новый антрибут, в который просавляем числе с счетчика

    @staticmethod                                  #тут мы не работаем с экземплярами, те сами мины не расставляет, self не нужен, метод может стать статичным
    def get_mines_places(exclude_number:int):
        """получаем перемешаннные индексы имеющихся кнопок для минирования поля"""
        indexes = list(range(1, MineSweeper.COLUMNS * MineSweeper.ROW + 1)) #формруем числа от 1 д общего количества кнопок
        print(f'Исключаем кнопку номер {exclude_number}')
        indexes.remove(exclude_number)
        shuffle(indexes)                      #перемешиваем наши индексы
        return indexes[:MineSweeper.MINES]     #возвращаем некоторое количество мин


game = MineSweeper()   #переменная game сохраняет MineSweeper() и тут создадутся кнопки
game.start()           #строчки ниже не выполняются
