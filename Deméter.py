from tkinter import *
import tkinter.ttk as ttk
from tkinter import messagebox
from tkinter import filedialog
from ttkthemes import ThemedTk

import re

from Database.Database import *

fonte_ = "Verdana 10"

conn = start_data_base()
show_ST()

associated_ = list()

try:
    associated_del = open('Recursos/Associação de Tabelas BD.txt', 'r')
    associated_del.close()
    conf = open('Recursos/Conf.txt', 'r')
    conf.close()
except FileNotFoundError:
    associated_del = open('Recursos/Associação de Tabelas BD.txt', 'a')
    associated_del.close()
    conf = open('Recursos/Conf.txt', 'a')
    conf.close()

with open('Recursos/Conf.txt', 'r') as f:
    text = f.readlines()
with open('Recursos/Conf.txt', 'r+') as f:
    for line in text:
        if 'date:' == line.split()[0]:
            if line.split()[1] != datetime.now().strftime('%d/%m/%Y'):
                f.write(f'date: {datetime.now().strftime("%d/%m/%Y")}\n')
                for table in Product_tables:
                    show_values(table)
                    for column in column_values:
                        reset_today(table, column[0])


class App(ThemedTk):
    """
           A classe "App" é onde fica armazenado todas as outras classes, funções,
       methodos e widgets necessarios para a criação da janela.

       : comando *args: usado para receber a quantidade de argumentos necessários na aplicação.
       : coomando **kwargs: usado para receber a quantidade de palabvras-chabes necessários na aplicação.

           The "App" class is where all other classes, functions,
       methods and widgets needed to create the window are stored.

       : command *args: used to receive a number of arguments needed in the application.
       : command **kwargs: used to receive the necessary number of keywords in the application.
       """

    def __init__(self, *args, **kwargs):
        global tree, tree_

        ThemedTk.__init__(self, *args, **kwargs)

        self.protocol("WM_DELETE_WINDOW", on_closing)

        self.set_theme('black')

        self.state('zoomed')
        self.minsize(1258, 623)

        self.title('DEMÉTER - GERENCIAMENTO DE ESTOQUE')
        self.iconbitmap('icon.ico')

        self.bind("<Control_L>a", open_file)
        self.bind("<Control_L>s", save_data_base())

        self.config(menu=MenuApp(self))

        self.appFrame = Application(self)
        self.appFrame.pack(side=TOP, fill=BOTH, expand=True)

        Tab1(self.appFrame.tab1)
        Tab2(self.appFrame.tab2)
        Tab3(self.appFrame.tab3)

        h = ('código', 'produto', 'unidades', 'categoria', 'descrição')
        c = ['código', 'produto', 'unidades', 'categoria', 'descrição']
        tree = Tree(self.appFrame.tab1, h, c)
        tree.container.grid(row=0, rowspan=10, column=5, pady=18, padx=120)
        tree.att_list()

        h = ('Produto', 'Unidades', 'Preço Compra', 'Preço Vendas', 'Vendas hoje', 'Total')
        c = ['Produto', 'Unidades', 'Preço Compra', 'Preço Vendas', 'Vendas hoje', 'Total']
        tree_ = Tree(self.appFrame.tab2, h, c)
        tree_.container.grid(row=0, rowspan=11, column=5, pady=18, padx=170)
        tree_.att_list()

        StaturBar = ttk.Label(self, relief='sunken')
        StaturBar.pack(side=BOTTOM, fill=X)

        ttk.Button(StaturBar, text='Salvar', command=lambda: save_data_base()).grid(row=0, column=0, sticky='w', padx=5)

        ttk.Button(StaturBar, text='Sair', command=lambda: quit_software()).grid(row=0, column=1, sticky='w', padx=5)

        update_tree()

    def refresh(self):
        self.destroy()
        self.__init__()
        att_tables_stock()
        att_tables_product()
        update_tree()
        update_cbxDel()


class MenuApp(Menu):
    """
        classe responsável por definir as propriedades do Menu na aplicação

    : root usado para definir o master da aplicação no tkinter

        class responsible for defining the application's Menu properties

    : root used to define the application master on tkinter
    """

    def __init__(self, root):
        Menu.__init__(self, root)

        filemenu = Menu(self, tearoff=0, background='#dcdad5')
        backup = Menu(self, tearoff=0, background='#dcdad5')

        filemenu.add_command(label='Abrir         Ctrl+A', command=open_file)
        filemenu.add_command(label='Salvar        Ctrl+S', command=save_data_base)
        filemenu.add_separator()
        filemenu.add_cascade(label='Backup', menu=backup)
        filemenu.add_separator()
        filemenu.add_command(label='Sair', command=lambda: quit())

        backup.add_command(label='Salvar backup', command=create_bckp)
        backup.add_command(label='Buscar backup', command=read_bckp)

        self.add_cascade(labe='Arquivo', menu=filemenu)
        self.add_command(label='Ajuda', command=helpInfo)
        self.add_command(label='Sobre', command=about)


class Application(ttk.Notebook):
    """

        Classe responsável por criar as tabs da aplicação,
    criação por usúario ainda não disponível nesta versão.

    : root usado para definir o master da aplicação no tkinter

        Class responsible for creating the application's tabs,
    user creation not yet available in this version.

    : root used to define the application master on tkinter
    """

    def __init__(self, root, texture='sunken'):
        ttk.Notebook.__init__(self, root)

        self.tab1 = ttk.Frame(self, relief=f'{texture}', borderwidth=2)
        self.tab2 = ttk.Frame(self, relief=f'{texture}', borderwidth=2)
        self.tab3 = ttk.Frame(self, relief=f'{texture}', borderwidth=2)

        self.add(self.tab1, text='Estoque')
        self.add(self.tab2, text='Produtos')
        self.add(self.tab3, text='Tabelas')


class Tree:
    """
        Classe referente a Tree de visualização
    """

    def __init__(self, root, headings, columns):
        self.Headings = headings
        self.Columns = columns

        self.container = ttk.Frame(root)

        self.Tree_init = ttk.Treeview(show="headings", height=25)

        vsb = ttk.Scrollbar(orient="vertical", command=self.Tree_init.yview)
        self.Tree_init.configure(yscrollcommand=vsb.set)

        self.Tree_init.grid(row=0, column=0, sticky='nsew', in_=self.container)
        vsb.grid(row=0, column=1, sticky='ns', in_=self.container)

        self.Tree_init['columns'] = self.Headings
        columns = self.Columns
        for c, i in enumerate(columns):
            self.Tree_init.heading(columns[c], text=columns[c].title(), anchor=W)
            self.Tree_init.column(columns[c], width=90, minwidth=25)

    def att_list(self):
        for row in column_list:
            self.Tree_init.insert('', 'end', values=row[1:])

    def att_newList(self, table, check=True):
        self.Tree_init.delete(*self.Tree_init.get_children())
        one_value_column(f'{table}')
        if check:
            for row in column_list:
                # print(row)
                self.Tree_init.insert('', 'end', values=row[1:])
            column_list.clear()
        else:
            for row in column_list:
                # print(row)
                self.Tree_init.insert('', 'end', values=row[:-1])
            column_list.clear()


def quit_software():
    """
        Salva o banco de dados e fecha o programa por inteiro.

        Saves the database and close the program.
    """
    save_data_base()
    app.destroy()


def dict_stock():
    """
        Cria um dicionário que tem como key do nome de uma coluna presente nas tabela de estoque,
    e no value é inserido as colunas salvas em uma lista que pode ser acessada com o nome da tabela.

        Create a dictionary whose key is the name of a colunmn present in the table of stock, and in value the columns
    saved in a list are inserted that can be accessed with the name of the table.

    :return: Um dicionário com key sendo o nome de uma coluna e value sendo as colunas presentes nela. |
             A dictionary with key being the name of a column and value being the columns present in it.

    """
    dict_column_name = {}
    tables = show_ST()
    for item in tables:
        append_column_name(item, 2)
        temp = []
        for _ in columns_names_list:
            if _ in temp:
                # print(_)
                pass
            else:
                temp.append(_)
        # print(f'<<{temp}>>')
        dict_column_name[f'{item}'] = temp[:]
        # print(dict_column_name)
        temp.clear()
        columns_names_list.clear()
    return dict_column_name


def dict_prod():
    """
        Cria um dicionário que tem como key do nome de uma coluna presente nas tabela de produtos,
    e no value é inserido as colunas salvas em uma lista que pode ser acessada com o nome da tabela.

        Create a dictionary whose key is the name of a colunmn present in the table of product, and in value the columns
    saved in a list are inserted that can be accessed with the name of the table.

    :return: Um dicionário com key sendo o nome de uma coluna e value sendo as colunas presentes nela. |
             A dictionary with key being the name of a column and value being the columns present in it.

    """
    dict_column_name = {}
    tables = show_PT()
    for i in tables:
        append_column_name(i, 0)
        temp = []
        for _ in columns_names_list:
            if _ in temp:
                pass
            else:
                temp.append(_)
        dict_column_name[f'{i}'] = temp[:]
        temp.clear()
        columns_names_list.clear()
    return dict_column_name


def choice_stock(column):
    """
        Usa a função 'dict_' para procurar usando o nome das colunas presentes no banco de dados
    para achar a key correspondente e retornar o value da mesma. Apenas para as tabelas de estoque.

        Use the 'dict_' function to search using the name of the columns in the database
    to find the corresponding key and return its value. Only for tables stock.

    :param column: Usa o nome de uma coluna para achar seu valor correspondente. |
                   Use a column name to find its corresponding value.
    :return: Retorna o value correspondente a coluna pedida. |
             Returns the value corresponding to the requested column.
    """
    a = dict_stock()
    valor = ''
    for _ in a.keys():
        if column in a.keys():
            valor = a[f'{column}']
    return valor


def choice_prod(column):
    """
        Usa a função 'dict_' para procurar usando o nome das colunas presentes no banco de dados
    para achar a key correspondente e retornar o value da mesma. Apenas para as tabelas de produtos.

        Use the 'dict_' function to search using the name of the columns in the database
    to find the corresponding key and return its value. Only for tables products.

    :param column: Usa o nome de uma coluna para achar seu valor correspondente. |
                   Use a column name to find its corresponding value.
    :return: Retorna o value correspondente a coluna pedida. |
             Returns the value corresponding to the requested column.
    """
    a = dict_prod()
    valor = ''
    for _ in a.keys():
        if column in a.keys():
            valor = a[f'{column}']
    return valor


def open_file(event=None):
    file = filedialog.askopenfilename(title='Arquivo de banco de dados', filetypes=(("Data Base File", "*.db"),))
    if file:
        with open('Recursos/Conf.txt', 'r') as f:
            text = f.readlines()
        with open('Recursos/Conf.txt', 'r+') as f:
            for line in text:
                if 'database:' == line.split()[0]:
                    f.write(f'database: {file}\n')
                    messagebox.showwarning('ATENÇÃO',
                                           'É necessario reiniar a aplicação para que a alteraçãos seja salva.'
                                           '\nFavor fechar a aplicação e abrir novamente.')
                else:
                    f.write(line)


def create_bckp():
    file = filedialog.askdirectory(title='Salvar Backup em:')
    backup_db(file)


def read_bckp():
    file = filedialog.askopenfilename(title='Abrir Backup do banco de dados', filetypes=(("Data Base File", "*.sql"),))
    if file:
        read_backup(file)
        app.refresh()


def about():
    about = Toplevel()

    about.title('Sobre o programa')
    about.geometry('540x240+137+70')
    about.configure(background='#424242')
    about.iconbitmap('icon.ico')
    text = f"""
        Programa focado em resolver problemas de estoque comercial, seja ele um pequeno
    comércio ou grande.Programa desenvolvido inteiramente por Ênio Gabriel, usado a linguagem
    Python e SQLITE3 como banco de dados. O mesmo ainda está em desenvolvimento, proximas
    atualizações irão adicionar gráficos de diversos modelos para ter uma imersão em seu negócio,
    afim de dar um maior o aproveitamento possível com seus produtos assim como o crescimento
    de seu negócio.
    Para entrar em contato comigo use o seguinte email: gabrielmoraisdias9@gmail.com


    Agradecimentos a Flaticon por patrocinar icones de qualidade e totalmente gratuitos.
    Link do ícone usado:
    https://www.flaticon.com/br/icone-gratis/esquilo_3069178
    """
    ttk.Label(about, text=text).grid(sticky='w', pady=10, padx=5)


def helpInfo():
    messagebox.showinfo("Ajuda", "Está sendo feito um arquivo PDF para ajudar na utilização do "
                                 "software, pedimos que aguarde algum tempo.")


def Tab1(root):
    global cbx_table_t1, cbx_clm_t1, entry_cod_t1, entry_prod_t1, entry_un_t1, \
        entry_cat_t1, entry_dsc_t1, stringvar_cod_t1, stringvar_un_t1, \
        stringvar_cat_t1, stringvar_dsc_t1

    labelframe = ttk.Labelframe(root)
    labelframe.grid(row=0, rowspan=4, column=0, columnspan=5, sticky='we')

    ttk.Label(labelframe, text='Inserir novo item em:', font=fonte_).grid(row=0, column=0,
                                                                          sticky='w', pady=10, padx=5)
    ttk.Label(labelframe, text='Código:', font=fonte_).grid(row=1, column=0,
                                                            sticky='w', pady=10, padx=5)
    ttk.Label(labelframe, text='Nome do Produto:', font=fonte_).grid(row=1, column=2,
                                                                     sticky='w', pady=10, padx=5)
    ttk.Label(labelframe, text='Unidades:', font=fonte_).grid(row=2, column=0,
                                                              sticky='w', pady=10, padx=5)
    ttk.Label(labelframe, text='Categoria:', font=fonte_).grid(row=2, column=2,
                                                               sticky='w', pady=10, padx=5)
    ttk.Label(labelframe, text='Descrição:', font=fonte_).grid(row=3, column=0,
                                                               sticky='w', pady=10, padx=5)

    cbx_table_t1 = ttk.Combobox(labelframe, state="readonly")
    cbx_table_t1.configure(values=Stock_Tables)
    if len(Stock_Tables) > 0:
        cbx_table_t1.current(0)
    cbx_table_t1.grid(row=0, column=1, sticky='we', pady=10)
    cbx_table_t1.bind("<<ComboboxSelected>>", update_tree)

    entry_cod_t1 = ttk.Entry(labelframe, width=25)
    entry_cod_t1.focus_set()
    entry_cod_t1.grid(row=1, column=1, sticky='w', pady=10)

    entry_prod_t1 = ttk.Entry(labelframe, width=25)
    entry_prod_t1.grid(row=1, column=3, sticky='w', pady=10)

    entry_un_t1 = ttk.Entry(labelframe, width=25)
    entry_un_t1.grid(row=2, column=1, sticky='w', pady=10)

    entry_cat_t1 = ttk.Entry(labelframe, width=25)
    entry_cat_t1.grid(row=2, column=3, sticky='w', pady=10)

    entry_dsc_t1 = ttk.Entry(labelframe, width=75)
    entry_dsc_t1.grid(row=3, column=1, columnspan=3, sticky='w', pady=10)

    ttk.Button(labelframe, text='Adicionar', command=add_values_st).grid(row=4, column=0, sticky='w', padx=5)

    ttk.Separator(labelframe).grid(row=5, columnspan=4, sticky='we', pady=10, padx=5)

    ttk.Label(labelframe, text='Alterar o seguinte item:', font=fonte_).grid(row=6, column=0,
                                                                             sticky='we', pady=10, padx=5)

    cbx_clm_t1 = ttk.Combobox(labelframe, state="readonly")
    cbx_clm_t1.configure(values=choice_stock(cbx_table_t1.get()))
    cbx_clm_t1.grid(row=6, column=1, sticky='we', pady=10, padx=5)
    cbx_clm_t1.bind("<<ComboboxSelected>>", update_entryST)

    ttk.Label(labelframe, text='Código:', font=fonte_).grid(row=7, column=0,
                                                            sticky='w', pady=10, padx=5)
    ttk.Label(labelframe, text='Unidades:', font=fonte_).grid(row=7, column=2,
                                                              sticky='w', pady=10, padx=5)
    ttk.Label(labelframe, text='Categoria:', font=fonte_).grid(row=8, column=0,
                                                               sticky='w', pady=10, padx=5)
    ttk.Label(labelframe, text='Descrição:', font=fonte_).grid(row=9, column=0,
                                                               sticky='w', pady=10, padx=5)

    stringvar_cod_t1 = StringVar()
    ttk.Entry(labelframe, textvariable=stringvar_cod_t1, width=25).grid(row=7, column=1, sticky='w', pady=10, padx=5)

    stringvar_un_t1 = StringVar()
    ttk.Entry(labelframe, textvariable=stringvar_un_t1, width=25).grid(row=7, column=3, sticky='w', pady=10, padx=5)

    stringvar_cat_t1 = StringVar()
    ttk.Entry(labelframe, textvariable=stringvar_cat_t1, width=25).grid(row=8, column=1, sticky='w', pady=10, padx=5)

    stringvar_dsc_t1 = StringVar()
    ttk.Entry(labelframe, textvariable=stringvar_dsc_t1, width=75).grid(row=9, column=1, columnspan=3,
                                                                        sticky='w', pady=10, padx=5)

    ttk.Button(labelframe, text='Atualizar', command=att_column_stock).grid(row=10, column=0, columnspan=2,
                                                                            sticky='w', pady=10, padx=5)

    ttk.Button(labelframe, text='Apagar', command=del_ID).grid(row=10, column=0, columnspan=2,
                                                               sticky='w', pady=10, padx=90)


def Tab2(root):
    global cbx_table_t2, cbx_clm_t2, entry_prod_t2, entry_un_t2, entry_buy_t2, \
        entry_sale_t2, entry_daily, entry_month, stringvar_un_t2, stringvar_buy_t2, stringvar_sale_t2, \
        stringvar_today_t2, stringvar_month_t2, entry_SalC

    labelframe = ttk.Labelframe(root)
    labelframe.grid(row=0, rowspan=4, column=0, columnspan=5, sticky='we')

    ttk.Label(labelframe, text='Inseir novo item em:', font=fonte_).grid(row=0, column=0,
                                                                         sticky='w', pady=10, padx=5)
    ttk.Label(labelframe, text='Nome do produto:', font=fonte_).grid(row=1, column=0,
                                                                     sticky='w', pady=10, padx=5)
    ttk.Label(labelframe, text='Unidades:', font=fonte_).grid(row=2, column=0,
                                                              sticky='w', pady=10, padx=5)
    ttk.Label(labelframe, text='Preço de compra:', font=fonte_).grid(row=3, column=0,
                                                                     sticky='w', pady=10, padx=5)
    ttk.Label(labelframe, text='Preço de venda:', font=fonte_).grid(row=3, column=2,
                                                                    sticky='w', pady=10, padx=5)
    ttk.Label(labelframe, text='Vendas hoje:', font=fonte_).grid(row=4, column=0,
                                                                 sticky='w', pady=10, padx=5)
    ttk.Label(labelframe, text='Vendas totais:', font=fonte_).grid(row=4, column=2,
                                                                   sticky='w', pady=10, padx=5)

    cbx_table_t2 = ttk.Combobox(labelframe, state='readonly')
    cbx_table_t2.configure(values=Product_tables)
    if len(Product_tables) > 0:
        cbx_table_t2.current(0)
    cbx_table_t2.grid(row=0, column=1, sticky='w', pady=10, padx=5)
    cbx_table_t2.bind('<<ComboboxSelected>>', update_tree)

    entry_prod_t2 = ttk.Entry(labelframe, width=40)
    entry_prod_t2.focus_set()
    entry_prod_t2.grid(row=1, column=1, columnspan=3, sticky='w', pady=19, padx=5)

    entry_un_t2 = ttk.Entry(labelframe, width=15)
    entry_un_t2.grid(row=2, column=1, sticky='w', pady=15, padx=5)

    entry_buy_t2 = ttk.Entry(labelframe, width=15)
    entry_buy_t2.grid(row=3, column=1, sticky='w', pady=10, padx=5)

    entry_sale_t2 = ttk.Entry(labelframe, width=15)
    entry_sale_t2.grid(row=3, column=3, sticky='w', pady=10, padx=5)

    entry_daily = ttk.Entry(labelframe, width=15)
    entry_daily.grid(row=4, column=1, sticky='w', pady=10, padx=5)

    entry_month = ttk.Entry(labelframe, width=15)
    entry_month.grid(row=4, column=3, sticky='w', pady=10, padx=5)

    ttk.Button(labelframe, text='Adicionar', command=add_values_prod).grid(row=5, column=0,
                                                                           sticky='w', pady=10, padx=5)

    ttk.Button(labelframe, text='Adicionar desde', command=mingle_2t).grid(row=5, column=0, columnspan=4,
                                                                           sticky='w', pady=10, padx=90)

    ttk.Button(labelframe, text='Associar estoque', command=mingle_tables).grid(row=5, column=0, columnspan=4,
                                                                                sticky='w', pady=10, padx=194)

    ttk.Separator(labelframe).grid(row=6, column=0, columnspan=5, sticky='we')

    ttk.Label(labelframe, text='Item:', font=fonte_).grid(row=7, column=0, sticky='w', pady=10, padx=5)

    ttk.Label(labelframe, text='Unidades', font=fonte_).grid(row=8, column=0, sticky='w', pady=10, padx=5)

    ttk.Label(labelframe, text='Preço de compra:', font=fonte_).grid(row=9, column=0, sticky='w', pady=10, padx=5)

    ttk.Label(labelframe, text='Preço de venda:', font=fonte_).grid(row=9, column=2, sticky='w', pady=10, padx=5)

    ttk.Label(labelframe, text='Vendas hoje:', font=fonte_).grid(row=10, column=0, sticky='w', pady=10, padx=5)

    ttk.Label(labelframe, text='Vendas totais:', font=fonte_).grid(row=10, column=2, sticky='w', pady=10, padx=5)

    cbx_clm_t2 = ttk.Combobox(labelframe, state='readonly', width=40)
    cbx_clm_t2.configure(values=choice_prod(cbx_table_t2.get()))
    cbx_clm_t2.grid(row=7, column=1, columnspan=3, sticky='w', pady=10, padx=5)
    cbx_clm_t2.bind("<<ComboboxSelected>>", update_entryPROD)

    stringvar_un_t2 = StringVar()
    ttk.Entry(labelframe, textvariable=stringvar_un_t2, width=15).grid(row=8, column=1, sticky='w', pady=10, padx=5)

    stringvar_buy_t2 = StringVar()
    ttk.Entry(labelframe, textvariable=stringvar_buy_t2, width=15).grid(row=9, column=1, sticky='w', pady=10, padx=5)

    stringvar_sale_t2 = StringVar()
    ttk.Entry(labelframe, textvariable=stringvar_sale_t2, width=15).grid(row=9, column=3, sticky='w', pady=10, padx=5)

    stringvar_today_t2 = StringVar()
    ttk.Entry(labelframe, textvariable=stringvar_today_t2, width=15).grid(row=10, column=1, sticky='w', pady=10, padx=5)

    stringvar_month_t2 = StringVar()
    ttk.Entry(labelframe, textvariable=stringvar_month_t2, width=15).grid(row=10, column=3, sticky='w', pady=10, padx=5)

    entry_SalC = ttk.Entry(labelframe, width=15)
    entry_SalC.grid(row=11, column=1, sticky='w', pady=10, padx=5)

    ttk.Button(labelframe, text='Cadastrar venda', command=Update_sale).grid(row=11, column=0, sticky='w',
                                                                             pady=10, padx=5)

    ttk.Button(labelframe, text='Apagar', command=lambda: del_ID(check=False)).grid(row=12, column=0, sticky='w',
                                                                                    pady=10, padx=5)
    ttk.Button(labelframe, text='Atualizar', command=att_column_product).grid(row=12, column=0, columnspan=2,
                                                                              sticky='w', pady=10, padx=90)


def Tab3(root):
    global cbx_app_del, check_st, check_pt, entry_tab

    check_st = IntVar()
    check_pt = IntVar()

    cbx_app_del = ttk.Combobox(root, state='readonly')
    cbx_app_del.configure(values=values_cbx_del())
    cbx_app_del.grid(row=0, column=9, sticky='w', pady=10, padx=5)

    ttk.Label(root, text='Nome da nova tabela:', font=fonte_).grid(row=0, column=0,
                                                                   sticky='w', pady=10, padx=5)
    ttk.Label(root, text='Tipo de tabela a ser usada: ', font=fonte_).grid(row=1, column=0,
                                                                           sticky='w', pady=10, padx=5)

    entry_tab = ttk.Entry(root)
    entry_tab.focus_set()
    entry_tab.grid(row=0, column=1, sticky='w', pady=10, padx=5)

    ttk.Checkbutton(root, text='Estoque', variable=check_st).grid(row=2, column=0,
                                                                  sticky='w', padx=5)
    ttk.Checkbutton(root, text='Produtos', variable=check_pt).grid(row=2, column=1,
                                                                   sticky='w', padx=5)

    ttk.Button(root, text='Criar', command=create_tables).grid(row=3, column=0, sticky='w', pady=10, padx=5)

    ttk.Separator(root, orient=VERTICAL).grid(row=0, rowspan=6, column=7, sticky='ns', padx=110, pady=20)

    ttk.Label(root, text='Apagar a seguinte tabela:', font=fonte_).grid(row=0, column=8, sticky='w', pady=10, padx=5)

    ttk.Button(root, text='Apagar', command=lambda: Drop_tables(cbx_app_del.get())).grid(row=0, column=10, sticky='w',
                                                                                         pady=10, padx=5)

    frame_exs = ttk.Labelframe(root, text='Exemplo tabela de Estoque')
    frame_exs.grid(row=4, column=0, columnspan=7,
                   sticky='w', pady=10, padx=5)
    ttk.Label(frame_exs, text='Código:', font=fonte_).grid(row=0, column=0,
                                                           sticky='w', padx=5, pady=10)
    ttk.Label(frame_exs, text='Nome do Produto:', font=fonte_).grid(row=0, column=2,
                                                                    sticky='w', padx=5, pady=10)
    ttk.Label(frame_exs, text='Unidades:', font=fonte_).grid(row=1, column=0,
                                                             sticky='w', pady=10, padx=5)
    ttk.Label(frame_exs, text='Categoria:', font=fonte_).grid(row=1, column=2,
                                                              sticky='w', pady=10, padx=5)
    ttk.Label(frame_exs, text='Descrição:', font=fonte_).grid(row=2, column=0,
                                                              sticky='w', pady=10, padx=5)

    entry_ExCod = ttk.Entry(frame_exs, width=25)
    entry_ExCod.insert(END, 1234567890)
    entry_ExCod['state'] = 'readonly'
    entry_ExCod.grid(row=0, column=1, sticky='w', pady=10, padx=5)

    entry_ExProd = ttk.Entry(frame_exs, width=25)
    entry_ExProd.insert(END, 'Pão de hambúrguer americano')
    entry_ExProd['state'] = 'readonly'
    entry_ExProd.grid(row=0, column=3, sticky='w', pady=10, padx=5)

    entry_ExUn = ttk.Entry(frame_exs, width=25)
    entry_ExUn.insert(END, 40)
    entry_ExUn['state'] = 'readonly'
    entry_ExUn.grid(row=1, column=1, sticky='w', pady=10, padx=5)

    entry_ExCat = ttk.Entry(frame_exs, width=25)
    entry_ExCat.insert(END, 'Pães')
    entry_ExCat['state'] = 'readonly'
    entry_ExCat.grid(row=1, column=3, sticky='w', pady=10, padx=5)

    entry_ExDsc = ttk.Entry(frame_exs, width=75)
    entry_ExDsc.insert(END, 'Pão de hambúrguer tradicional.')
    entry_ExDsc['state'] = 'readonly'
    entry_ExDsc.grid(row=2, column=1, columnspan=3, sticky='w', pady=10, padx=5)

    frame_exs1 = ttk.Labelframe(root, text='Exemplo tabela de produtos')
    frame_exs1.grid(row=5, column=0, columnspan=5, sticky='w', pady=10, padx=5)

    ttk.Label(frame_exs1, text='Nome do produto:', font=fonte_).grid(row=0, column=0,
                                                                     sticky='w', pady=10, padx=5)
    ttk.Label(frame_exs1, text='Unidades:', font=fonte_).grid(row=1, column=0,
                                                              sticky='w', pady=10, padx=5)
    ttk.Label(frame_exs1, text='Preço de compra:', font=fonte_).grid(row=2, column=0,
                                                                     sticky='w', pady=10, padx=5)
    ttk.Label(frame_exs1, text='Preço de venda:', font=fonte_).grid(row=2, column=2,
                                                                    sticky='w', pady=10, padx=5)
    ttk.Label(frame_exs1, text='Vendas hoje:', font=fonte_).grid(row=3, column=0,
                                                                 sticky='w', pady=10, padx=5)
    ttk.Label(frame_exs1, text='Vendas totais:', font=fonte_).grid(row=3, column=2,
                                                                   sticky='w', pady=10, padx=5)

    entry_prod1 = ttk.Entry(frame_exs1, width=40)
    entry_prod1.insert(END, 'Fúria do Dino Esmagador Deck Estrutural')
    entry_prod1['state'] = 'readonly'
    entry_prod1.grid(row=0, column=1, columnspan=2, sticky='w', pady=10, padx=5)

    entry_un = ttk.Entry(frame_exs1, width=15)
    entry_un.insert(END, 150)
    entry_un['state'] = 'readonly'
    entry_un.grid(row=1, column=1, sticky='w', pady=10, padx=5)

    entry_prc = ttk.Entry(frame_exs1, width=15)
    entry_prc.insert(END, '30,00R$')
    entry_prc['state'] = 'readonly'
    entry_prc.grid(row=2, column=1, sticky='w', pady=10, padx=5)

    entry_prv = ttk.Entry(frame_exs1, width=15)
    entry_prv.insert(END, '50,00R$')
    entry_prv['state'] = 'readonly'
    entry_prv.grid(row=2, column=3, sticky='w', pady=10, padx=5)

    entry_sales_today = ttk.Entry(frame_exs1, width=15)
    entry_sales_today.insert(END, 23)
    entry_sales_today['state'] = 'readonly'
    entry_sales_today.grid(row=3, column=1, sticky='w', pady=10, padx=5)

    entry_sales = ttk.Entry(frame_exs1, width=15)
    entry_sales.insert(END, 78)
    entry_sales['state'] = 'readonly'
    entry_sales.grid(row=3, column=3, sticky='w', pady=10, padx=5)


def mingle_2t():
    global Tl_m, cbx_table_tl, cbx_clm_tl, stringvar_name_tl, stringvar_un_tl

    associated_.clear()

    def mingle():
        # print(stringvar_name_tl.get())
        # print(stringvar_un_tl.get())
        entry_prod_t2.insert(0, stringvar_name_tl.get())
        associated_.append(f'{cbx_table_tl.get()}/{stringvar_name_tl.get()}/{stringvar_un_tl.get()}')
        Tl_m.destroy()

    Tl_m = Toplevel()

    Tl_m.title('Associando tabela')
    Tl_m.geometry('660x225+294+70')
    Tl_m.configure(background='#424242')
    Tl_m.iconbitmap('icon.ico')

    cbx_table_tl = ttk.Combobox(Tl_m, state="readonly", width=25)
    cbx_table_tl.configure(values=Stock_Tables)
    if len(Stock_Tables) > 0:
        cbx_table_tl.current(0)
    cbx_table_tl.grid(row=0, column=1, sticky='w', pady=10, padx=5)

    cbx_clm_tl = ttk.Combobox(Tl_m, state="readonly", width=25)
    cbx_clm_tl.configure(values=choice_stock(cbx_table_tl.get()))
    cbx_clm_tl.grid(row=0, column=3, sticky='w', pady=10, padx=5)
    cbx_clm_tl.bind("<<ComboboxSelected>>", update_entryTL)

    ttk.Label(Tl_m, text='Tabela:', font=fonte_).grid(row=0, column=0, sticky='w', pady=10, padx=5)
    ttk.Label(Tl_m, text='Item:', font=fonte_).grid(row=0, column=2, sticky='W', pady=10, padx=5)
    ttk.Label(Tl_m, text='Nome do Produto:', font=fonte_).grid(row=1, column=0, sticky='w', pady=10, padx=5)
    ttk.Label(Tl_m, text='Unidades comprometidas:').grid(row=1, column=2, sticky='w', pady=10, padx=5)

    stringvar_name_tl = StringVar()
    ttk.Entry(Tl_m, state='readonly', width=25, textvariable=stringvar_name_tl).grid(row=1, column=1, sticky='w',
                                                                                     pady=10, padx=5)
    stringvar_un_tl = StringVar()
    ttk.Entry(Tl_m, width=25, textvariable=stringvar_un_tl).grid(row=1, column=3, sticky='w', pady=10, padx=5)

    ttk.Button(Tl_m, text='Associar', command=mingle).grid(row=4, column=0, pady=10, padx=5)
    ttk.Button(Tl_m, text='Sair', command=Tl_m.destroy).grid(row=4, column=1, sticky='w', pady=10, padx=5)


def mingle_tables():
    global Tl_m2, cbx_table_tl2, cbx_clm_tl2, stringvar_name_tl2

    temp = list()
    values = list()
    associated_.clear()

    def mingle():
        for _ in temp:
            if _ not in associated_:
                associated_.append(_)

    def insert_():
        check = True
        for _ in values:
            if stringvar_name_tl2.get() in _:
                check = False
        # print(check)
        if check:
            if len(stringvar_name_tl2.get()) > 0:
                if len(un.get()) > 0:
                    if un.get().isnumeric():
                        values.append(f'{name.get()} | {un.get()}')
                        temp.append(f'{cbx_table_tl2.get()}/{stringvar_name_tl2.get()}/{un.get()}')
                        view_.configure(values=values[:])
                        stringvar_name_tl2.set('')
                        un.delete(0, 'end')
                        cbx_clm_tl2.set('')
                    else:
                        messagebox.showinfo('Erro na associação dos produtos.',
                                            'O campo "Unidades comprometidas" aceita apenas números inteiros.'
                                            '\nFavor, inserir apenas números inteiros.',
                                            parent=Tl_m2)
                else:
                    messagebox.showinfo('Erro na associação dos produtos.',
                                        'O campo "Unidades comprometidas" não pode ficar em branco.'
                                        '\nFavor, informar as unidades que serão comprometidas na associação do produto.',
                                        parent=Tl_m2)
            else:
                messagebox.showinfo('Erro na associação dos produtos.',
                                    'Produto para associação não selecionado.'
                                    '\nFavor, selecionar um produto.',
                                    parent=Tl_m2)
        elif not check:
            messagebox.showinfo('Erro na associação dos produtos.',
                                'Produto já cadastrado.'
                                '\nNão é possível cadastrar o mesmo produto duas vezes.',
                                parent=Tl_m2)
            stringvar_name_tl2.set('')
            un.delete(0, 'end')

    def del_():
        for idx, item in enumerate(values):
            if item in view_.get():
                # print(f'Selected == {item}')
                values.remove(item)
                view_.configure(values=values)
                view_.set('')

    Tl_m2 = Toplevel()

    Tl_m2.title('Associando tabela')
    Tl_m2.geometry('660x365+294+70')
    Tl_m2.configure(background='#424242')
    Tl_m2.iconbitmap('icon.ico')

    cbx_table_tl2 = ttk.Combobox(Tl_m2, state='readonly')
    cbx_table_tl2.configure(values=Stock_Tables)
    if len(Stock_Tables) > 0:
        cbx_table_tl2.current(0)
    cbx_table_tl2.grid(row=0, column=1, sticky='w', pady=10, padx=5)

    cbx_clm_tl2 = ttk.Combobox(Tl_m2, state='readonly')
    cbx_clm_tl2.configure(values=choice_stock(cbx_table_tl2.get()))
    cbx_clm_tl2.grid(row=0, column=3, sticky='w', pady=10, padx=5)
    cbx_clm_tl2.bind('<<ComboboxSelected>>', update_entryTL2)

    ttk.Label(Tl_m2, text='Tabela:', font=fonte_).grid(row=0, column=0, sticky='w', pady=10, padx=5)
    ttk.Label(Tl_m2, text='Item:', font=fonte_).grid(row=0, column=2, sticky='w', pady=10, padx=5)
    ttk.Label(Tl_m2, text='Nome do Produto:', font=fonte_).grid(row=1, column=0, sticky='w', pady=10, padx=5)
    ttk.Label(Tl_m2, text='Unidades comprometidas:', font=fonte_).grid(row=1, column=2, sticky='w', pady=10, padx=5)
    ttk.Label(Tl_m2, text='Produtos associados:', font=fonte_).grid(row=2, column=0, sticky='w', pady=10, padx=5)

    stringvar_name_tl2 = StringVar()
    name = ttk.Entry(Tl_m2, state='readonly', width=22, textvariable=stringvar_name_tl2)
    name.grid(row=1, column=1, sticky='w', pady=10, padx=5)
    un = ttk.Entry(Tl_m2, width=22)
    un.grid(row=1, column=3, sticky='w', pady=10, padx=5)

    view_ = ttk.Combobox(Tl_m2, state='readonly', width=33)
    view_.configure(values=values)
    view_.grid(row=2, column=1, columnspan=2, sticky='w', pady=10, padx=5)

    ttk.Button(Tl_m2, text='Associar', command=insert_).grid(row=4, column=0, sticky='w', pady=10, padx=5)
    ttk.Button(Tl_m2, text='Apagar', command=del_).grid(row=4, column=0, columnspan=2, sticky='w', pady=10, padx=90)
    ttk.Button(Tl_m2, text='Salvar', command=mingle).grid(row=5, column=0, sticky='w', pady=10, padx=5)
    ttk.Button(Tl_m2, text='Sair', command=Tl_m2.destroy).grid(row=5, column=0, columnspan=2,
                                                               sticky='w', pady=10, padx=90)


def on_closing():
    if messagebox.askokcancel('Saindo do programa', 'Tem certeza que deseja fechar o programa?'
                                                    '\nCaso não tenha salvo as alterações, elas serão ser perdidas.'):

        app.destroy()
        try:
            if Tl_m.state() == 'normal':
                Tl_m.destroy()
            if Tl_m2.state() == 'normal':
                Tl_m2.destroy()
        except (NameError, TclError):
            pass


def create_tables():
    a = check_st.get()
    b = check_pt.get()

    if a == b == 1:
        messagebox.showinfo('Erro na criação da tabela.',
                            'Dois tipos de tabelas selecionados.'
                            '\nPor favor, selecione apenas um.')

    elif a == b == 0:
        messagebox.showinfo('Erro na criação da tabela',
                            'Nenhum tipo de tabela selecionado.'
                            '\nPor favor, selecione um tipo valido.')

    elif a == 1 and a != b:
        if len(entry_tab.get()) == 0:
            messagebox.showinfo('Erro na criação da tabela',
                                'Nome da tabela não informado.'
                                '\nFavor inserir um nome valido.')
        else:
            if str(entry_tab.get()).title() in show_PT() or str(entry_tab.get()).title() in show_ST():
                messagebox.showinfo('Erro na criação da tabela.',
                                    'Tabela com o mesmo nome já existente.'
                                    '\nFavor inseir um nome diferente.')
                entry_tab.delete(0, 'end')
            else:
                create_table_stock(str(entry_tab.get()).title())
                att_tables_stock()
                check_st.set(0)

    elif b == 1 and b != a:
        if len(entry_tab.get()) == 0:
            messagebox.showinfo('Erro na criação da tabela',
                                'Nome da tabela não informado.'
                                '\nFavor inserir um nome valido.')
        else:
            if str(entry_tab.get()).title() in show_PT() or str(entry_tab.get()).title() in show_ST():
                messagebox.showinfo('Erro na criação da tabela.',
                                    'Tabela com o mesmo nome já existente.'
                                    '\nFavor inseir um nome diferente.')
                entry_tab.delete(0, 'end')
            else:
                create_table_sales(str(entry_tab.get()).title())
                att_tables_product()
                check_pt.set(0)
    update_cbxDel()


def add_values_st():
    table = cbx_table_t1.get()
    name = entry_prod_t1.get()
    units = entry_un_t1.get()
    cod = entry_cod_t1.get()
    cat = entry_cat_t1.get()
    dsc = entry_dsc_t1.get()

    if len(table) != 0:

        if len(cod) == 0:
            cod = '0'

        if len(cat) == 0:
            cat = '-----'

        if len(dsc) == 0:
            dsc = '-----'

        if units.isnumeric() and int(units) > 0:
            if len(name) == 0 or len(units) == 0:
                if len(name) == len(units):
                    messagebox.showinfo('Erro ao adicionar produto.', 'Os campos "Nome do Produto" e'
                                                                      '"Unidades" não podem ficar vazios.'
                                                                      '\nFavor informar os campos.')

                elif len(name) != len(units) and len(name) == 0:
                    messagebox.showinfo('Erro ao adicionar produto.', 'O campo "Nome do Produto" '
                                                                      'não pode ficar vazio. '
                                                                      '\nFavor informar esté campo.')
            else:
                add_values_column_st(table, name, units, cod, cat, dsc)
                entry_cod_t1.delete(0, END)
                entry_prod_t1.delete(0, END)
                entry_un_t1.delete(0, END)
                entry_cat_t1.delete(0, END)
                entry_dsc_t1.delete(0, END)
        else:
            messagebox.showinfo('Erro ao adicionar produto.', 'O campo "Unidades" aceita apenas números inteiros'
                                                              ' maiores que zero(0).'
                                                              '\nFavor inserir apenas números no campo.')

    else:
        messagebox.showinfo('Erro ao adicionar produto.', 'Tabela não informada.'
                                                          '\nFavor verificar se existem tabelas e selecionar uma.')

    update_tree()


def add_values_prod():
    table = cbx_table_t2.get()
    name = entry_prod_t2.get()
    units = entry_un_t2.get()
    buy_price = entry_buy_t2.get()
    sale_price = entry_sale_t2.get()
    today = entry_daily.get()
    month = entry_month.get()

    chk = True

    if len(table) != 0:

        if len(buy_price) == 0:
            buy_price = int(0)

        if len(sale_price) == 0:
            sale_price = int(0)

        if len(today) == 0:
            today = int(0)

        if len(month) == 0:
            month = int(0)

        if units.isnumeric():
            if len(name) == 0 or len(units) == 0:
                if len(name) == len(units):
                    messagebox.showinfo('Erro ao adicionar produto.', 'Os campos "Nome do Produto" e'
                                                                      '"Unidades" não podem ficar vazios.'
                                                                      '\nFavor informar os campos.')

                elif len(name) != len(units) and len(name) == 0:
                    messagebox.showinfo('Erro ao adicionar produto.', 'O campo "Nome do Produto" '
                                                                      'não pode ficar vazio. '
                                                                      '\nFavor informar esté campo.')
            else:
                if re.search('[a-zA-Z]+', f'{sale_price}') is None:
                    if re.search('[,]+', f'{sale_price}'):
                        sale_price = float(sale_price.replace(',', '.'))
                else:
                    chk = False
                    messagebox.showinfo('Erro na atualização do produto.',
                                        'O campo "Preço de vendas", aceita apenas números decimais ou inteiros.')
                    entry_sale_t2.delete(0, 'end')
                if re.search('[a-zA-Z]+', f'{buy_price}') is None:
                    if re.search('[,]+', f'{buy_price}'):
                        buy_price = float(buy_price.replace(',', '.'))
                else:
                    chk = False
                    messagebox.showinfo('Erro na atualização do produto.',
                                        'O campo "Preço de compra", aceita apenas números decimais ou inteiros.')
                    entry_buy_t2.delete(0, 'end')
                if re.search('[a-zA-Z]+', f'{today}') is None:
                    if type(today) == int:
                        pass
                    else:
                        messagebox.showinfo('Erro na atualização do produto.',
                                            'O campo "Vendas hoje", aceita apenas números decimais ou inteiros.')
                else:
                    messagebox.showinfo('Erro na atualização do produto.',
                                        'O campo "Vendas hoje", aceita apenas números decimais ou inteiros.')
                if re.search('[a-zA-Z]+', f'{month}') is None:
                    if type(month) == int:
                        pass
                    else:
                        messagebox.showinfo('Erro na atualização do produto.',
                                            'O campo "Vendas totais", aceita apenas números decimais ou inteiros.')
                else:
                    messagebox.showinfo('Erro na atualização do produto.',
                                        'O campo "Vendas totais", aceita apenas números decimais ou inteiros.')
            if chk:
                add_values_column_prod(table, name, units, buy_price, sale_price, today, month)
                for c in associated_:
                    tables_2del = open('Recursos/Associação de Tabelas BD.txt', 'a')
                    tables_2del.write(f'{name} {c}\n')
                    tables_2del.close()
                entry_prod_t2.delete(0, END)
                entry_un_t2.delete(0, END)
                entry_buy_t2.delete(0, END)
                entry_sale_t2.delete(0, END)
                entry_daily.delete(0, END)
                entry_month.delete(0, END)
        else:
            messagebox.showinfo('Erro ao adicionar produto.', 'O campo "Unidades" aceita apenas números.'
                                                              '\nFavor inserir apenas números no campo.')

    else:
        messagebox.showinfo('Erro ao adicionar produto.', 'Tabela não informada.'
                                                          '\nFavor verificar se existem tabelas e selecionar uma.')
    update_tree()


def values_cbx_del():
    temp = list()
    temp.clear()
    if len(show_ST()) >= 1 and len(show_PT()) >= 1:
        for _ in show_ST():
            if _ not in temp:
                temp.append(_)
        temp.append('-----')
        for _ in show_PT():
            if _ not in temp:
                temp.append(_)

    elif len(show_ST()) >= 1 and len(show_PT()) == 0:
        for _ in show_ST():
            if _ not in temp:
                temp.append(_)

    elif len(show_ST()) == 0 and len(show_PT()) >= 1:
        for _ in show_PT():
            if _ not in temp:
                temp.append(_)
    return temp


def update_tree(event=None):
    if cbx_table_t1.get() != '':
        tree.att_newList(cbx_table_t1.get())
        append_column_name(cbx_table_t1.get(), 2)
        cbx_clm_t1.configure(values=choice_stock(cbx_table_t1.get()))
    if cbx_table_t2.get() != '':
        tree_.att_newList(cbx_table_t2.get(), check=False)
        append_column_name(cbx_table_t2.get(), 0)
        cbx_clm_t2.configure(values=choice_prod(cbx_table_t2.get()))


def update_entryTL(event=None):
    column_values.clear()
    if cbx_table_tl.get() != '':
        show_values(cbx_table_tl.get())
    _ = column_values
    for c in _:
        if c[2] == cbx_clm_tl.get():
            stringvar_name_tl.set(c[2])


def update_entryTL2(event=None):
    column_values.clear()
    if cbx_table_tl2.get() != '':
        show_values(cbx_table_tl2.get())
    _ = column_values
    for c in _:
        if c[2] == cbx_clm_tl2.get():
            stringvar_name_tl2.set(c[2])


def update_entryST(event=None):
    column_values.clear()
    if cbx_table_t1.get() != '':
        show_values(cbx_table_t1.get())
    _ = column_values
    for c in _:
        if c[2] == cbx_clm_t1.get():
            stringvar_cod_t1.set(c[1])
            stringvar_un_t1.set(c[3])
            stringvar_cat_t1.set(c[4])
            stringvar_dsc_t1.set(c[5])


def update_entryPROD(event=None):
    column_values.clear()
    if cbx_table_t2.get() != '':
        show_values(cbx_table_t2.get())
    _ = column_values
    for c in _:
        if c[0] == cbx_clm_t2.get():
            stringvar_un_t2.set(c[1])
            stringvar_buy_t2.set(c[2])
            stringvar_sale_t2.set(c[3])
            stringvar_today_t2.set(c[4])
            stringvar_month_t2.set(c[5])


def update_cbxDel():
    temp = list()
    if len(show_ST()) >= 1 and len(show_PT()) >= 1:
        for _ in show_ST():
            if _ not in temp:
                temp.append(_)
        temp.append('-----')
        for _ in show_PT():
            if _ not in temp:
                temp.append(_)
        cbx_app_del.configure(values=temp)
        temp.clear()

    elif len(show_ST()) >= 1 and len(show_PT()) == 0:
        for _ in show_ST():
            if _ not in temp:
                temp.append(_)
        cbx_app_del.configure(values=temp)
        temp.clear()

    elif len(show_ST()) == 0 and len(show_PT()) >= 1:
        for _ in show_PT():
            if _ not in temp:
                temp.append(_)
        cbx_app_del.configure(values=temp)
        temp.clear()
    elif len(show_ST()) == 0 and len(show_PT()) == 0:
        cbx_app_del.configure(values=temp)


def att_tables_stock(event=None):
    show_ST().clear()
    cbx_table_t1.configure(values=show_ST())
    try:
        cbx_table_tl.configure(values=show_ST())
    except (NameError, TclError):
        pass
    if len(show_ST()) == 0:
        cbx_table_t1.set('')
    entry_tab.delete(0, END)
    if len(show_ST()) >= 1:
        cbx_table_t1.current(0)


def att_tables_product(event=None):
    show_PT().clear()
    cbx_table_t2.configure(values=show_PT())
    if len(show_PT()) == 0:
        cbx_table_t2.set('')
    entry_tab.delete(0, END)
    if len(show_PT()) >= 1:
        cbx_table_t2.current(0)


def att_column_stock(event=None):
    temp = list()
    if cbx_table_t1.get() != '':
        column_values.clear()
        show_values(cbx_table_t1.get())
    if cbx_clm_t1.get() != '':
        for i, n in enumerate(cbx_clm_t1['values']):
            if n == cbx_clm_t1.get():
                temp.append(column_values[i][0])
                for Id in temp:
                    # print(Id)
                    if stringvar_un_t1.get().isnumeric() and int(stringvar_un_t1.get()) > 0:
                        update_columns_stock(cbx_table_t1.get(), Id, stringvar_cod_t1.get(), stringvar_un_t1.get(),
                                             stringvar_cat_t1.get(), stringvar_dsc_t1.get())
                        update_entryST()
                        update_tree()
                    else:
                        messagebox.showinfo('Erro na atualização da tabela.',
                                            'O campo "Unidades" aceita apenas números inteiros e diferentes de zero(0)')
                        update_entryST()
    else:
        messagebox.showinfo('Erro na atualização da tabela.',
                            'Nenhum item selecionado'
                            '\nFavor, selecionar um item para fazer a atualização.')


def att_column_product(event=None):
    sale_price = stringvar_sale_t2.get()
    buy_price = stringvar_buy_t2.get()
    today = stringvar_today_t2.get()
    month = stringvar_month_t2.get()

    chk = True

    if cbx_table_t2.get() != '':
        column_values.clear()
        show_values(cbx_table_t2.get())

    if cbx_clm_t2.get() != '':
        if re.search('[a-zA-Z]+', f'{sale_price}') is None:
            if re.search('[,]+', f'{sale_price}'):
                sale_price = float(sale_price.replace(',', '.'))
        else:
            chk = False
            messagebox.showinfo('Erro na atualização do produto.',
                                'O campo "Preço de vendas", aceita apenas números decimais ou inteiros.')
            update_entryPROD()

        if re.search('[a-zA-Z]+', f'{buy_price}') is None:
            if re.search('[,]+', f'{buy_price}'):
                buy_price = float(buy_price.replace(',', '.'))
        else:
            chk = False
            messagebox.showinfo('Erro na atualização do produto.',
                                'O campo "Preço de compra", aceita apenas números decimais ou inteiros.')
            update_entryPROD()

        if len(today) > 0:
            if re.search('[a-zA-Z]+', f'{today}') is None:
                if today.isnumeric():
                    pass
                else:
                    messagebox.showinfo('Erro na atualização do produto.',
                                        'O campo "Vendas hoje", aceita apenas números inteiros.')
            else:
                messagebox.showinfo('Erro na atualização do produto.',
                                    'O campo "Vendas hoje", aceita apenas números inteiros.')
                update_entryPROD()

        if len(month) > 0:
            if re.search('[a-zA-Z]+', f'{month}') is None:
                if month.isnumeric():
                    pass
                else:
                    messagebox.showinfo('Erro na atualização do produto.',
                                        'O campo "Vendas totais", aceita apenas números inteiros.')
            else:
                messagebox.showinfo('Erro na atualização do produto.',
                                    'O campo "Vendas todais", aceita apenas números inteiros.')
                update_entryPROD()

        if chk:
            for i, n in enumerate(cbx_clm_t2['values']):
                if n == cbx_clm_t2.get():
                    update_columns_prod(cbx_table_t2.get(), stringvar_un_t2.get(), buy_price, sale_price,
                                        today, month, cbx_clm_t2.get())
    else:
        messagebox.showinfo('Erro na atualização do produto.',
                            'Nenhum item selecionado.'
                            '\nFavor, selecionar um item para fazer a atualização.')
    update_tree()


def del_ID(check=True):
    column_values.clear()
    temp = list()
    if check:
        show_values(cbx_table_t1.get())
        for i, n in enumerate(cbx_clm_t1['values']):
            if n == cbx_clm_t1.get():
                temp.append(column_values[i][0])
                # print(f'Index={i} / nome={n} / values={column_values[i]} / temp={temp}')
                for ID in temp:
                    # print(id)
                    delete_column(cbx_table_t1.get(), ID)
                temp.clear()

        stringvar_cod_t1.set('')
        stringvar_un_t1.set('')
        stringvar_cat_t1.set('')
        stringvar_dsc_t1.set('')
        cbx_clm_t1.set('')
    if not check:
        show_values(cbx_table_t2.get())
        for i, n in enumerate(cbx_clm_t2['values']):
            if n == cbx_clm_t2.get():
                temp.append(column_values[i][-1])
                # print(f'Index={i} / nome={n} / values={column_values[i]} / temp={temp}')
                for ID in temp:
                    delete_column(cbx_table_t2.get(), ID)
                temp.clear()
                arch = open('Recursos/Associação de Tabelas BD.txt', 'r')
                lines = arch.readlines()
                arch.close()
                arch = open('Recursos/Associação de Tabelas BD.txt', 'w')
                for line in lines:
                    # print(n)
                    # print(line.split())
                    if n in line.split()[0]:
                        pass
                    else:
                        arch.write(line)
                arch.close()

        stringvar_un_t2.set('')
        stringvar_buy_t2.set('')
        stringvar_sale_t2.set('')
        stringvar_today_t2.set('')
        stringvar_month_t2.set('')
        cbx_clm_t2.set('')

    save_data_base()
    update_tree()


def Drop_tables(table):
    if table != '-----':
        drop_table(table)
        cbx_app_del.delete(0, END)
        att_tables_product()
        att_tables_stock()
        tree.att_newList(cbx_table_t1.get())
        tree_.att_newList(cbx_table_t2.get(), False)
        update_cbxDel()
    else:
        messagebox.showinfo('Erro ao apagar tabela',
                            'Esté é um delimitador padrão para diferenciar as tabelas "Estoque" e "Produtos".'
                            '\nFavor escolher uma tabela válida.')
    cbx_app_del.set('')


def Update_sale():
    if cbx_table_t2.get() != '':
        column_values.clear()
        show_values(cbx_table_t2.get())
        if entry_SalC.get().isnumeric() and int(entry_SalC.get()) > 0:
            if len(entry_SalC.get()) > 0:
                for _ in column_values:
                    if _[0] == cbx_clm_t2.get():
                        result = _[1] - int(entry_SalC.get())
                        if result >= 0:
                            if chk_un():
                                update_column_un(cbx_table_t2.get(), cbx_clm_t2.get(), entry_SalC.get())
                                for _ in range(0, int(entry_SalC.get())):
                                    update_many_values('Recursos/Associação de Tabelas BD.txt', cbx_clm_t2.get())
                        else:
                            messagebox.showinfo('Erro ao cadastrar venda.',
                                                'O número de unidades é em estoque é menor que a quantidade de '
                                                'vendas inseridas')

            else:
                messagebox.showinfo('Erro ao cadastrar venda.',
                                    'Número de vendas não informado.'
                                    '\nFavor, inserir o número de vendas.')
        else:
            messagebox.showinfo('Erro ao cadastrar vendas.',
                                'O campo "Cadastrar vendas" aceita apenas números inteiros e diferente de 0(zero).'
                                '\nFavor, inserir apenas números inteiros.')
    else:
        messagebox.showinfo('Erro ao cadastrar venda.',
                            'Produto para cadastrar venda não selecionado.'
                            '\nFavor, selecionar um produto.')

    att_tables_product()
    att_tables_stock()
    update_entryPROD()
    update_tree()
    entry_SalC.delete(0, 'end')


def chk_un():
    arch = open('Recursos/Associação de Tabelas BD.txt', 'r')
    temp = list()
    out_stock = list()
    tables = list()
    for line in arch:
        temp.append(line)
    for i in temp:
        if cbx_clm_t2.get() in i:
            a = i.split()
            for idx, item in enumerate(a):
                if idx != 0:
                    tables.append(a[idx].split('/'))
    column_values.clear()
    for table in tables:
        show_values(table[0])
    for _ in column_values:
        result = _[3] - int(entry_SalC.get())
        if result < 0 or result == 0:
            out_stock.append(f'{_[2]} {_[3]}')
    arch.close()
    if len(out_stock) > 0:
        for item in out_stock:
            messagebox.showinfo(f'Erro ao cadastrar venda.',
                                f'O seguinte produto está com o estoque baixo: {item.split()[0]}'
                                f'\nFavor verificar.')
        return False
    return True


if __name__ == '__main__':
    app = App()
    app.mainloop()
