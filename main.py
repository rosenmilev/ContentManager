import tkinter as tk
from tkinter import ttk, messagebox
import pickle


class Item:
    def __init__(self, name, year, genre):
        self.name = name
        self.year = year
        self.genre = genre


class Movie(Item):
    def __init__(self, name, year, genre, director):
        super().__init__(name, year, genre)
        self.director = director


class Game(Item):
    def __init__(self, name, year, genre, studio):
        super().__init__(name, year, genre)
        self.studio = studio


class Book(Item):
    def __init__(self, name, year, genre, publisher):
        super().__init__(name, year, genre)
        self.publisher = publisher


class CollectionManager:
    def __init__(self, filename):
        self.filename = filename
        self.items = self.load_items()

    def add_item(self, item):
        self.items.append(item)
        self.save_items()

    def update_item(self, index, item):
        self.items[index] = item
        self.save_items()

    def delete_item(self, index):
        del self.items[index]
        self.save_items()

    def save_items(self):
        with open(self.filename, 'wb') as file:
            pickle.dump(self.items, file)

    def load_items(self):
        try:
            with open(self.filename, 'rb') as file:
                return pickle.load(file)
        except FileNotFoundError:
            return []


class CollectionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Collection Manager')
        self.manager = CollectionManager('database.pkl')
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.tabs = {}
        self.create_widgets()
        self.load_items()

    def create_widgets(self):
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label='File', menu=file_menu)
        file_menu.add_command(label='Exit', command=self.quit)

        main_frame = tk.Frame(self)
        main_frame.grid(sticky='nsew')
        self.configure_grid(self, 1, 1)

        search_frame = tk.Frame(main_frame)
        search_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        self.configure_grid(search_frame, 0, 1)

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.grid(row=0, column=0, padx=5, pady=5, sticky='news')
        search_frame.grid_columnconfigure(0, weight=1)

        search_button = ttk.Button(search_frame, text='Search', command=self.perform_search)
        search_button.grid(row=0, column=1, padx=5, pady=5)

        self.tab_control = ttk.Notebook(main_frame)
        self.tab_control.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        self.configure_grid(main_frame, 1, 1)

        for item_class, extra_label in [(Movie, 'Director'), (Game, 'Studio'), (Book, 'Publisher')]:
            self.create_tab(item_class, extra_label)

    def configure_grid(self, frame, row_weight, col_weight):
        frame.grid_rowconfigure(0, weight=row_weight)
        frame.grid_columnconfigure(0, weight=col_weight)

    def create_tab(self, item_class, extra_label):
        frame = ttk.Frame(self.tab_control)
        self.tab_control.add(frame, text=item_class.__name__ + 's')
        self.configure_grid(frame, 1, 1)

        listbox = tk.Listbox(frame)
        listbox.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        listbox.bind('<<ListboxSelect>>', lambda e, ic=item_class: self.on_select(e, ic, listbox))

        entry_frame = self.create_entry_frame(frame, item_class, extra_label)

        button_frame = tk.Frame(frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky='ew', padx=5, pady=5)

        add_button = ttk.Button(button_frame, text='Add', command=lambda: self.add_item(item_class, entry_frame))
        add_button.grid(row=0, column=0, padx=5, pady=5)

        update_button = ttk.Button(button_frame, text='Update',
                                   state='disabled', command=lambda: self.update_item(item_class, entry_frame))
        update_button.grid(row=0, column=1, padx=5, pady=5)

        delete_button = ttk.Button(button_frame, text='Delete', command=lambda: self.delete_item(listbox))
        delete_button.grid(row=0, column=2, padx=5, pady=5)

        self.tabs[item_class] = {
            'frame': frame,
            'listbox': listbox,
            'entries': entry_frame,
            'selected_index': None,
            'extra_label': extra_label.lower(),
            'update_button': update_button
        }

    def create_entry_frame(self, frame, item_class, extra_label):
        entry_frame = tk.Frame(frame)
        entry_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        frame.grid_columnconfigure(1, weight=1)

        entries = {}
        labels = ['Name', 'Year', 'Genre', extra_label]

        for idx, label in enumerate(labels):
            ttk.Label(entry_frame, text=label).grid(row=idx, column=0, padx=5, pady=2, sticky='w')
            if label == 'Year':
                year_values = [str(year) for year in range(1930, 2024)]
                entry = ttk.Combobox(entry_frame, values=year_values, state='readonly')

                entry.bind('<<ComboboxSelected>>', lambda e: self.enable_update_button(item_class))

            else:
                entry = ttk.Entry(entry_frame)
            entry.grid(row=idx, column=1, padx=5, pady=2, sticky='ew')
            entries[label.lower()] = entry
            entry_frame.grid_rowconfigure(idx, weight=1)
        return entries

    def enable_update_button(self, item_class):
        selected_index = self.tabs[item_class]['selected_index']
        if selected_index is not None:
            selected_item = self.manager.items[selected_index]
            entries = self.tabs[item_class]['entries']
            extra_label = self.tabs[item_class]['extra_label']

            if (entries['name'].get() != selected_item.name or
                    entries['year'].get() != str(selected_item.year) or
                    entries['genre'].get() != selected_item.genre or
                    entries[extra_label].get() != getattr(selected_item, extra_label)):
                self.tabs[item_class]['update_button'].config(state='normal')

    def on_select(self, event, item_class, listbox):
        selection = listbox.curselection()
        if selection:
            selected_index = selection[0]
            selected_item = listbox.get(selected_index)
            selected_name = selected_item.split(' (')[0]

            for index, item in enumerate(self.manager.items):
                if isinstance(item, item_class) and item.name == selected_name:
                    self.tabs[item_class]['selected_index'] = index
                    self.fill_fields(item, self.tabs[item_class]['entries'])
                    self.tabs[item_class]['update_button'].config(state='disabled')
                    for entry in self.tabs[item_class]['entries'].values():
                        entry.bind('<KeyRelease>', lambda e: self.enable_update_button(item_class))
                        if isinstance(entry, ttk.Combobox):
                            entry.bind('<<ComboboxSelected>>', lambda e: self.enable_update_button(item_class))

    def perform_search(self):
        search_query = self.search_var.get().lower()
        current_tab = self.tab_control.index(self.tab_control.select())
        item_class = [Movie, Game, Book][current_tab]
        listbox = self.tabs[item_class]['listbox']

        listbox.delete(0, tk.END)
        for item in self.manager.items:
            if isinstance(item, item_class) and search_query in item.name.lower():
                listbox.insert(tk.END, f'{item.name} ({item.year})')

    def fill_fields(self, item, entries):
        entries['name'].delete(0, tk.END)
        entries['name'].insert(0, item.name)
        entries['year'].set(str(item.year))
        entries['genre'].delete(0, tk.END)
        entries['genre'].insert(0, item.genre)

        specific_field = 'director' if isinstance(item, Movie) else 'studio' if isinstance(item, Game) else 'publisher'
        entries[specific_field].delete(0, tk.END)
        entries[specific_field].insert(0, getattr(item, specific_field))

    def clear_fields(self, item_class):
        entries = self.tabs[item_class]['entries']
        for entry in entries.values():
            if isinstance(entry, (ttk.Spinbox, ttk.Combobox)):
                entry.set('')
            else:
                entry.delete(0, tk.END)

    def add_item(self, item_class, entries):
        if not self.all_fields_filled(entries):
            messagebox.showwarning('Warning', 'All fields are required.')
            return

        item_data = {key: entry.get() for key, entry in entries.items()}
        new_item = item_class(**item_data)
        self.manager.add_item(new_item)
        self.load_items()
        self.clear_fields(item_class)

    def update_item(self, item_class, entries):
        if not self.all_fields_filled(entries):
            messagebox.showwarning('Warning', 'All fields are required.')
            return

        selected_index = self.tabs[item_class]['selected_index']
        if selected_index is not None and selected_index < len(self.manager.items):
            item_data = {key: (int(entry.get()) if key == 'year' else entry.get()) for key, entry in entries.items()}
            updated_item = item_class(**item_data)
            self.manager.update_item(selected_index, updated_item)
            self.load_items()
            self.clear_fields(item_class)
            self.tabs[item_class]['update_button'].config(state='disabled')
            self.tabs[item_class]['selected_index'] = None
        else:
            messagebox.showwarning('Error', 'Item no longer exists.')

    def delete_item(self, listbox):
        selection = listbox.curselection()
        if selection:
            selected_name = listbox.get(selection[0]).split(' (')[0]
            for index, item in enumerate(self.manager.items):
                if item.name == selected_name:
                    self.manager.delete_item(index)
                    break

            self.search_var.set('')
            self.load_items()

            current_tab = self.tab_control.index(self.tab_control.select())
            item_class = [Movie, Game, Book][current_tab]
            self.tabs[item_class]['selected_index'] = None
            self.clear_fields(item_class)

    def all_fields_filled(self, entries):
        return all(entry.get().strip() for entry in entries.values())

    def load_items(self):
        for item_class, tab_widgets in self.tabs.items():
            listbox = tab_widgets['listbox']
            listbox.delete(0, tk.END)
            for item in self.manager.items:
                if isinstance(item, item_class):
                    listbox.insert(tk.END, f'{item.name} ({item.year})')


if __name__ == '__main__':
    root = CollectionApp()
    root.mainloop()
