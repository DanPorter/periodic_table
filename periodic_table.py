"""
TKinter GUI to select element from Periodic table of elementsDans Element Properties.txt

Inspired by:
https://codereview.stackexchange.com/questions/272438/python-tkinter-periodic-table-of-chemical-elements
Thanks to: Thingamabobs and Reinderien
"""

import tkinter as tk

ELEMENT_FILE = 'Dans Element Properties.txt'

ALKALI_METALS = [1, 3, 11, 19, 37, 55, 87]
ALKALI_EARTH_METALS = [4, 12, 20, 38, 56, 88]
OTHER_METALS = [13, 31, 32, 49, 50, 51, 81, 82, 83, 84, 113, 114, 115, 116]
NON_METALS = [5, 6, 7, 8, 9, 14, 15, 16, 17, 33, 34, 35, 52, 53, 85, 117]
NOBEL_GASES = [2, 10, 18, 36, 54, 86, 118]
LIQUID = [35, 80]
GAS = [1, 2, 7, 8, 9, 10, 17, 18, 36, 54, 86]
SYNTHETIC = [43, 61]  # + > 92

# Colours taken from https://xdb.lbl.gov/Section1/Periodic_Table/X-ray_Elements.html
COLORS = {
    'alkali metals': '#cccccc',
    'alkali earth metals': '#a2cb69',
    'transition metals': '#fdfe6c',
    'other metals': '#f19bcc',
    'nonmetals': '#80cbcc',
    'noble gases': '#f6cc9b',
    'solid': 'black',
    'liquid': 'blue',
    'gas': 'red',
    'synthetic': 'grey',
}


def gen_colours(atomic_number):
    """Return background, forground colour"""
    background = COLORS['transition metals']
    foreground = COLORS['solid']
    if atomic_number in ALKALI_METALS:
        background = COLORS['alkali metals']
    elif atomic_number in ALKALI_EARTH_METALS:
        background = COLORS['alkali earth metals']
    elif atomic_number in OTHER_METALS:
        background = COLORS['other metals']
    elif atomic_number in NON_METALS:
        background = COLORS['nonmetals']
    elif atomic_number in NOBEL_GASES:
        background = COLORS['noble gases']
    if atomic_number in LIQUID:
        foreground = COLORS['liquid']
    elif atomic_number in GAS:
        foreground = COLORS['gas']
    elif atomic_number in SYNTHETIC or atomic_number > 92:
        foreground = COLORS['synthetic']
    return background, foreground


def gen_position(atomic_number, group, period):
    """Returns row and column"""
    row = period
    column = group
    if atomic_number in [57, 89]:
        column = 3
    elif 57 < atomic_number < 72:
        # Lanthanides
        row += 2
        column = atomic_number - 54
    elif 89 < atomic_number < 104:
        # Actinides
        row += 2
        column = atomic_number - 86
    return row, column


class Element:
    def __init__(self, element_dict):
        self.data = element_dict
        self.atomic_number = int(element_dict['Z'])
        self.symbol = element_dict['Element']
        self.name = element_dict['Name']
        self.group, self.period = int(element_dict['Group']), int(element_dict['Period'])
        self.weight = '%.2f' % float(element_dict['Weight'])
        self.row, self.column = gen_position(self.atomic_number, self.group, self.period)
        self.background, self.foreground = gen_colours(self.atomic_number)

    def gen_info(self):
        return '\n'.join(['%8s: %s' % (name, val) for name, val in self.data.items()])

    def __repr__(self):
        s = "Element('%s', '%s', '%s', '%s', '%s', '%s')"
        return s % (self.atomic_number, self.symbol, self.name, self.group, self.period, self.weight)

    def __str__(self):
        s = '%3s %2s %16s group=%2s, period=%2s, (%2s, %2s)'
        return s % (self.atomic_number, self.symbol, self.name, self.group, self.period, self.row, self.column)


# Load elements
def load_elements():
    """Return list of [Element]"""
    element_list = []
    with open(ELEMENT_FILE) as f:
        # skip header
        line = f.readline()
        while line.startswith('#'):
            line = f.readline()
        # column headers
        headers = line.split()
        for line in f.readlines():
            values = line.split()
            data = {name: value for name, value in zip(headers, values)}
            element_list += [Element(data)]
    return element_list


class ElementButton:
    BORDER = 3

    def __init__(self, parent: tk.Widget, placed_element: Element, info_widget: tk.Text) -> None:
        self.element = placed_element
        self.background = self.element.background
        self.info_widget = info_widget
        self.frame = frame = tk.Frame(
            parent, relief=tk.RAISED,
            name=f'frame_{self.element.symbol}',
            background=self.background,
            border=self.BORDER,
        )
        self.frame.grid_columnconfigure(1, weight=2)
        self.frame.grid(row=self.element.row, column=self.element.column, sticky=tk.EW)

        self.populate()

        frame.bind('<ButtonPress-1>', self.press)
        frame.bind('<ButtonRelease-1>', self.release)
        for child in frame.winfo_children():
            child.bindtags((frame,))

    def populate(self) -> None:
        prefix = f'label_{self.element.symbol}_'

        tk.Label(
            self.frame, name=prefix + 'number',
            text=self.element.atomic_number, background=self.background,
        ).grid(row=0, column=0, sticky=tk.NW)

        tk.Label(
            self.frame, name=prefix + 'mass',
            text=self.element.weight, background=self.background,
        ).grid(row=0, column=2, sticky=tk.NE)

        tk.Label(
            self.frame, name=prefix + 'symbol',
            text=self.element.symbol, font='bold', background=self.background,
            foreground=self.element.foreground,
        ).grid(row=1, column=0, sticky=tk.EW, columnspan=3)

        tk.Label(
            self.frame, name=prefix + 'name',
            text=self.element.name, background=self.background,
        ).grid(row=2, column=0, sticky=tk.EW, columnspan=3)

    def press(self, event: tk.Event) -> None:
        self.frame.configure(relief='sunken')

    def release(self, event: tk.Event) -> None:
        self.frame.configure(relief='raised')
        # print(self.element)
        #self.info_widget.set('%s' % self.element)
        self.info_widget.delete('1.0', tk.END)
        self.info_widget.insert('1.0', self.element.gen_info())


class PeriodTableGui:
    """
    TKinter GUI showing periodic table
    """

    def __init__(self):
        # Create Tk inter instance
        self.root = tk.Tk()
        self.root.wm_title('Periodic Table')
        # self.root.minsize(width=640, height=480)
        self.root.maxsize(width=self.root.winfo_screenwidth(), height=self.root.winfo_screenheight())
        # self.root.tk_setPalette(
        #     background=bkg,
        #     foreground=txtcol,
        #     activeBackground=opt_active,
        #     activeForeground=txtcol)
        self.root.title('Periodic Table of the Elements')

        frame = tk.Frame(self.root, name='grid_container')
        frame.pack_configure(fill=tk.BOTH)

        # --- Create element infobox ---
        info_frame = tk.LabelFrame(frame, text='Element', relief=tk.RIDGE)
        info_frame.grid(row=1, column=4, sticky=tk.EW, columnspan=8, rowspan=3)

        # Scrollbars
        scanx = tk.Scrollbar(info_frame, orient=tk.HORIZONTAL)
        scanx.pack(side=tk.BOTTOM, fill=tk.X)

        scany = tk.Scrollbar(info_frame)
        scany.pack(side=tk.RIGHT, fill=tk.Y)

        # Editable string box
        self.element_text = tk.Text(info_frame, font=['Courier', 12], width=60, height=10,
                                    wrap=tk.NONE, background='white')
        self.element_text.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        self.element_text.insert(tk.END, '')

        self.element_text.config(xscrollcommand=scanx.set, yscrollcommand=scany.set)
        scanx.config(command=self.element_text.xview)
        scany.config(command=self.element_text.yview)

        # --- Add elements ---
        elements = load_elements()
        for element in elements:
            ElementButton(frame, element, self.element_text)

        columns = {elm.column for elm in elements}
        for x in columns:
            frame.grid_columnconfigure(index=x, weight=1)

        self.root.mainloop()


if __name__ == '__main__':
    PeriodTableGui()

