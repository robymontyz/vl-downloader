"""
    PoliTO VL Downloader GUI

    GUI to download video-lessons from "Portale della didattica"
    of Politecnico di Torino. It uses vl_downloader modules.
    Written using TKinter library.

    :copyright: (c) 2016, robymontyz
    :license: BSD

    Permission to use, copy, modify, and distribute this software for any
    purpose with or without fee is hereby granted, provided that the above
    copyright notice and this permission notice appear in all copies.

    THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
    WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
    MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
    ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
    WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
    ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
    OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""


import os


import Tkinter
import tkMessageBox
import tkFileDialog


import vl_downloader as vl_dl


TITLE_FONT = ("Helvetica", 18, "bold")
SESSION = None
URLS = []
DL_PATH = os.path.expanduser('~' + 'Downloads')


class SampleApp(Tkinter.Tk):
    """
    Main app, windows container
    """

    def __init__(self, *args, **kwargs):
        Tkinter.Tk.__init__(self, *args, **kwargs)
        Tkinter.Tk.wm_title(self, 'PoliTO VL Downloader')

        w = 600  # width for the Tk root
        h = 500  # height for the Tk root

        # get screen width and height
        ws = Tkinter.Tk.winfo_screenwidth(self)  # width of the screen
        hs = Tkinter.Tk.winfo_screenheight(self)  # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)

        # set the dimensions of the screen
        # and where it is placed
        Tkinter.Tk.geometry(self, '%dx%d+%d+%d' % (w, h, x, y))

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = Tkinter.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (Login, LessonList, PageTwo):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("Login")

    def show_frame(self, page_name):
        # Show a frame for the given page name
        frame = self.frames[page_name]
        frame.tkraise()


class Login(Tkinter.Frame):
    """
    Starting page of the program. It is the login page.
    """

    def __init__(self, parent, controller):
        Tkinter.Frame.__init__(self, parent)
        self.controller = controller

        # ---Commands--- #
        def do_login(event=None):
            username = entry_user.get()
            password = entry_psw.get()

            global SESSION
            # Do the login
            SESSION = vl_dl.login(username, password)

            if SESSION is None:
                tkMessageBox.showerror(message="Username or password not correct!")
            else:
                # showinfo(message="Logged in!")
                controller.show_frame('LessonList')

        # TODO: "remind me" feature

        # ---Widgets---- #
        label_user = Tkinter.Label(self, text='Username')
        entry_user = Tkinter.Entry(self)
        label_psw = Tkinter.Label(self, text='Password')
        entry_psw = Tkinter.Entry(self, show='*')
        login_button = Tkinter.Button(self, text="Login", command=do_login)
        label_sign = Tkinter.Label(self, text='(c) 2016, robymontyz')

        # key bindings
        entry_user.bind('<Return>', do_login)
        entry_psw.bind('<Return>', do_login)
        login_button.bind('<Return>', do_login)

        # pack widgets
        label_user.pack()
        entry_user.pack()
        entry_user.focus()
        label_psw.pack()
        entry_psw.pack()
        login_button.pack()
        label_sign.pack(side=Tkinter.BOTTOM)


class LessonList(Tkinter.Frame):
    """
    Page that show all the lessons and you can select which one download.
    """

    def __init__(self, parent, controller):
        Tkinter.Frame.__init__(self, parent)
        self.controller = controller

        # ---Commands--- #
        def populate_with_lesson(event=None):
            # clear list
            lessons_list.delete(0, lessons_list.size())

            global URLS
            # Get the URLs of the video-lessons
            URLS = vl_dl.get_video_urls(SESSION, entry_link.get())
            i = 1
            for url in URLS:
                lesson_name = os.path.split(url)[-1][:-4]
                lessons_list.insert(i, lesson_name)
                i += 1

            # DEFAULT: selected all the lessons
            select_all_cb.config(state=Tkinter.NORMAL)
            select_all()

        def choose_dir():
            global DL_PATH
            DL_PATH = tkFileDialog.askdirectory()
            path.set(DL_PATH)

        def download_lessons(event=None):
            indexes = lessons_list.curselection()
            for i in indexes:
                vl_dl.download_video(SESSION, URLS[i], path.get())

        def select_all():
            if cb.get() == 1:
                for i in range(0, lessons_list.size()):
                    lessons_list.select_set(i)
            else:
                for i in range(0, lessons_list.size()):
                    lessons_list.select_clear(i)

        #def logout():
        # TODO: logout button

        # ---Widgets---- #
        label_link = Tkinter.Label(self, text='Insert first lesson url here:')
        entry_link = Tkinter.Entry(self)
        show_lessons_button = Tkinter.Button(self, text="Go", command=populate_with_lesson)

        lb_frame = Tkinter.Frame(self)
        scrollbar = Tkinter.Scrollbar(lb_frame)
        lessons_list = Tkinter.Listbox(lb_frame, selectmode=Tkinter.MULTIPLE, yscrollcommand=scrollbar.set)
        scrollbar.config(command=lessons_list.yview)
        cb = Tkinter.IntVar()
        cb.set(1)
        select_all_cb = Tkinter.Checkbutton(self, text='Select all', onvalue=1, offvalue=0,
                                            variable=cb, state=Tkinter.DISABLED, command=select_all)

        label_dl_dir = Tkinter.Label(self, text='Choose the download folder:')
        path = Tkinter.StringVar(value=DL_PATH)
        dir_frame = Tkinter.Frame(self)
        entry_dl_dir = Tkinter.Entry(dir_frame, textvariable=path)
        select_dir_button = Tkinter.Button(dir_frame, text='...', command=choose_dir)
        dl_button = Tkinter.Button(self, text='Download', command=download_lessons)

        #logout_button = Button(self, text='Logout', command=logout)

        # key bindings
        entry_link.bind('<Return>', populate_with_lesson)

        # pack widgets
        label_link.pack()
        entry_link.pack()
        entry_link.focus()
        show_lessons_button.pack()

        lb_frame.pack()
        scrollbar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
        lessons_list.pack()
        select_all_cb.pack()

        label_dl_dir.pack()
        dir_frame.pack()
        entry_dl_dir.grid(row=0, column=0)
        select_dir_button.grid(row=0, column=1)
        dl_button.pack()

        #logout_button.pack()


class PageTwo(Tkinter.Frame):
    # TODO: download manager page
    """
    Download manager page. It shows the progress of the downloads.
    """

    def __init__(self, parent, controller):
        Tkinter.Frame.__init__(self, parent)
        self.controller = controller
        label = Tkinter.Label(self, text="This is page 2", font=TITLE_FONT)
        label.pack(side="top", fill="x", pady=10)
        button = Tkinter.Button(self, text="Go to the start page", command=lambda: controller.show_frame("Login"))
        button.pack()


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
