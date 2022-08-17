import os, hashlib, tkinter
from tkinter import filedialog
from time import time as tic
from functools import cache


MOVE = True
DELETE = True
ROOTONLY = True
FILEDIR = os.path.dirname(__file__)


class App:
    COLUMN_WIDTH = 25
    WRAP_LENGTH = 6 * COLUMN_WIDTH

    def __init__(self, title="Tkinter App", width=1200, height=800):
        self.root = tkinter.Tk()
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.display_label = None
        self.status_label = None

    def run(self):
        col, row = self.root.grid_size()
        self.Label("", row, 0)
        self.Label("", row+1, 0)
        self.display_label = App.Label(self, "<output here>", row + 2, 0, width=4)
        self.Label("", row + 3, 0)
        self.Label("", row + 4, 0)
        self.status_label = App.Label(self, "Ready", row + 5, 0, width=4)
        self.root.mainloop()

    def set_status(self, status):
        self.status_label.textvariable.set(status)
        self.status_label.update()

    def display(self, text):
        self.display_label.textvariable.set(text)
        self.display_label.update()

    def collect(self):
        result = dict()
        for key, value in self.__dict__.items():
            if isinstance(value, App.MyLabel) or isinstance(value, App.MyEntry):
                result[key] = value.textvariable.get()
        return result

    class MyLabel(tkinter.Label):
        def __init__(self, parent, text, row, col, width):
            self.textvariable = tkinter.StringVar(parent.root, text)
            super().__init__(parent.root, textvariable=self.textvariable,
                             wraplength=App.WRAP_LENGTH*width, width=App.COLUMN_WIDTH*width)
            self.grid(row=row, column=col, columnspan=width)

    class MyEntry(tkinter.Entry):
        def __init__(self, parent, text, row, col, width):
            self.parent = parent
            self.textvariable = tkinter.StringVar(parent.root, text)
            super().__init__(parent.root, textvariable=self.textvariable, width=App.COLUMN_WIDTH*width)
            self.grid(row=row,column=col, columnspan=width)

    class MyButton(tkinter.Button):
        def __init__(self, parent, text, row, col, width, function, output):
            self.parent = parent
            self.output = output
            if function is None:
                function = self.do_nothing
            self.function = function
            self.textvariable = tkinter.StringVar(parent.root, text)
            super().__init__(parent.root, textvariable=self.textvariable, width=App.COLUMN_WIDTH*width,
                             wraplength=App.WRAP_LENGTH*width, command=self.clicked)
            self.grid(row=row, column=col, columnspan=width)

        def do_nothing(self):
            print("Doing nothing...")

        def clicked(self):
            self.parent.set_status("Busy")
            text = self.function(self.parent)
            if self.output is not None:
                self.output.textvariable.set(text)
            self.parent.set_status("Ready")

    def Label(self, text, row, col, width=1):
        return App.MyLabel(self, text, row, col, width)

    def Entry(self, text, row, col, width=1):
        return App.MyEntry(self, text, row, col, width)

    def Button(self, text, row, col, width=1, function=None, output=None):
        return App.MyButton(self, text, row, col, width, function, output)

    def FolderDialog(self, text, row, col, width=1, output=None):
        def folder_dialog(self):
            return filedialog.askdirectory(initialdir=FILEDIR) + "/"
        return App.MyButton(self, text, row, col, width, folder_dialog, output)

    def FileDialog(self, text, row, col, width=1, output=None, filetypes=None):
        def file_dialog(self):
            return filedialog.askopenfile(initialdir=FILEDIR, filetypes=filetypes).name
        if filetypes is None:
            filetypes = [("Any File", "*")]
        return App.MyButton(self, text, row, col, width, file_dialog, output)


class Time:
    def __init__(self, time):
        self.time = time

    def __str__(self):
        time = self.time
        hours = time // 3600
        time = time % 3600
        minutes = time // 60
        time = time % 60
        seconds = time
        if hours > 0:
            return f"{Number(hours)} hr, {Number(minutes)} min, and {Number(seconds)} s"
        elif minutes > 0:
            return f"{Number(minutes)} min and {Number(seconds)} s"
        else:
            return f"{Number(seconds)} s"


class Number:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        if self.value < 1:
            return f"{round(self.value, 2)}"
        elif self.value < 10:
            return f"{round(self.value, 1)}"
        else:
            return f"{round(self.value)}"


class Bytes:
    KB = 1024
    MB = KB * KB
    GB = MB * KB
    TB = GB * KB

    def __init__(self, value):
        self.value = value

    def __add__(self, other):
        return Bytes(self.value + other.value)

    def __str__(self):
        size = self.value
        if size is None:
            return "n/a"
        elif size < Bytes.KB:
            return f"{Number(size)} Bytes"
        elif size < Bytes.MB:
            return f"{Number(size/Bytes.KB)} KB"
        elif size < Bytes.GB:
            return f"{Number(size/Bytes.MB)} MB"
        else:
            return f"{Number(size/Bytes.GB)} GB"


class File:
    music = {'mp3', 'wav'}
    videos = {'avi', 'mpeg', 'mpg', 'mp4', 'wmv', 'mov'}
    documents = {'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'pdf',
                 'gdoc', 'gsheet', 'gslides', 'rtf', 'csv'}
    pictures = {'jpg', 'jpeg', 'gif', 'tif', 'bmp', 'raw', 'tiff', 'png'}
    downloads = {'html', 'exe', 'zip'}

    def __init__(self, fulldir, root):
        self.root = root
        self.fulldir = u"" + fulldir
        self.reldir = fulldir.replace(root, "")
        self.filename = os.path.basename(self.reldir)
        self.folder = fulldir.replace(self.filename, '')
        self.ext = self.filename.split('.')[-1].lower()
        self.size = Bytes(os.path.getsize(fulldir))
        self.type = self.get_type()

    def __str__(self):
        return self.reldir

    @property
    @cache
    def hash(self):
        with open(self.fulldir, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    def get_type(self):
        if self.ext in self.documents:
            return "Documents"
        elif self.ext in self.pictures:
            return "Pictures"
        elif self.ext in self.music:
            return "Music"
        elif self.ext in self.videos:
            return "Videos"
        elif self.ext in self.downloads:
            return "Downloads"
        else:
            return None

    def is_organized(self):
        if self.type is not None:
            if ROOTONLY:
                return self.reldir.replace(self.filename, "") == os.path.join(self.type, "")
            else:
                return self.reldir.startswith(self.type)
        else:
            return True

    def organized_directory(self):
        identifier = 0
        new_dir = os.path.join(self.root, self.type, self.filename)
        while os.path.isfile(new_dir):
            identifier += 1
            new_dir = new_dir.split(".")[0] + f"__{identifier}.{self.ext}"
        return new_dir

    def move(self, new_file):
        if MOVE:
            os.rename(self.fulldir, new_file)

    def delete(self):
        if DELETE:
            os.remove(self.fulldir)


class Files:
    def __init__(self, file):
        self.files = [file]

    def __contains__(self, file):
        return file.hash in {f.hash for f in self.files}

    def __getitem__(self, file):
        return self.files[[f.hash for f in self.files].index(file.hash)]

    def __iter__(self):
        return iter([file.hash for file in self.files])

    def add(self, file):
        self.files += [file]


class Scanner:
    def __init__(self):
        self.root = None
        self.backup = None
        self.duplicates_file = None
        self.misplaced_file = None
        self.excluded = None
        self.min = None
        self.max = None

    @staticmethod
    def open(file, mode):
        return open(file, mode, encoding='utf-8')

    def collect(self, app):
        kwargs = app.collect()
        self.root = kwargs["root_folder"]
        self.backup = kwargs["backup_folder"]
        self.excluded = kwargs["extensions"].split(",")
        self.min = int(kwargs["min_size"])
        self.max = int(kwargs["max_size"])

    @staticmethod
    def exception(exception):
        print(f"A(n) {exception.__class__.__name__} Occured. So Sorry.")

    def scan_duplicates(self, app):
        self.collect(app)
        self.duplicates_file = f"{FILEDIR}/_duplicates.res"
        scanned_count = 0
        duplicate_count = 0
        start_time = tic()
        scanned_sizes = dict()
        scanned_bytes = Bytes(0)
        duplicate_bytes = Bytes(0)
        with self.open(self.duplicates_file, "w") as f:
            pass  # Clears File
        for root, _, files in os.walk(self.root):
            for file in files:
                try:
                    file = File(os.path.join(root, file), self.root)
                    size = file.size.value
                    if size is not None and file.ext not in self.excluded and self.min < size < self.max:
                        scanned_count += 1
                        scanned_bytes += file.size
                        if size in scanned_sizes:
                            scan = scanned_sizes[size]
                            if file in scan:
                                duplicate_count += 1
                                duplicate_bytes += Bytes(size)
                                with self.open(self.duplicates_file, 'a') as f:
                                    print(f"{file.reldir} is {scan[file].reldir}")
                                    f.write(f"{file.fulldir}\n")
                            else:
                                scan.add(file)
                        else:
                            scanned_sizes[size] = Files(file)

                    output = (f"Elapsed Time is {Time(tic() - start_time)}\n"
                              f"Python scanned {scanned_count} files totaling {scanned_bytes}\n"
                              f"and found {duplicate_count} duplicate files totaling {duplicate_bytes}...")
                    app.display(output)

                except Exception as exception:
                    self.exception(exception)

    def purge_duplicates(self, app):
        self.collect(app)
        if self.duplicates_file is None:
            app.display("No Duplicates File. Scan for Duplicates Files First.")
        else:
            deleted_bytes = Bytes(0)
            with self.open(self.duplicates_file, 'r') as f:
                files = f.read().strip().split('\n')
                if files[0] == "":
                    app.display("No files to delete.")
                else:
                    ans = input(f"Delete {len(files)} Files? (y/n)").lower()
                    if ans in {"y", "yes", "ok"}:
                        for file in files:
                            try:
                                file = File(file, self.root)
                                deleted_bytes += file.size
                                text = f"Deleting {file.reldir}"
                                print(text)
                                app.display(text)
                                file.delete()
                            except Exception as exception:
                                self.exception(exception)
                        app.display(f"Python deleted {len(files)} files and saved {deleted_bytes}!")
                    else:
                        app.display("Python did not delete anything. Have a nice day.")
            self.duplicates_file = None

    def scan_misplaced(self, app):
        self.collect(app)
        start_time = tic()
        scanned_count = 0
        misplaced_count = 0
        self.misplaced_file = os.path.join(FILEDIR, "misplaced.res")
        with self.open(self.misplaced_file, "w"):
            pass  # Clears File
        print(f"Python is scanning {self.root} for files in the wrong folders...")
        for root, _, files in os.walk(self.root):
            for file in files:
                scanned_count += 1
                try:
                    file = File(os.path.join(root, file), self.root)
                    if not file.is_organized():
                        misplaced_count += 1
                        with self.open(self.misplaced_file, "a") as f:
                            print(f"{file.fulldir} should be in {file.organized_directory()}")
                            f.write(f"{file.fulldir}\n")
                except Exception as exception:
                    self.exception(exception)

            output = (f"Elapsed Time is {Time(tic() - start_time)}\n"
                      f"Python scanned {scanned_count} files and found {misplaced_count} misplaced files...")
            app.display(output)

    def organize_files(self, app):
        self.collect(app)
        if self.misplaced_file is None:
            app.display("No Misplaced File. Scan for Misplaced Files First.")
        else:
            with self.open(self.misplaced_file, 'r') as f:
                files = f.read().strip().split('\n')
                if files[0] == "":
                    app.display("No files to move.")
                else:
                    ans = input(f"Move {len(files)} Files? (y/n)").lower()
                    if ans in {"y", "yes", "ok"}:
                        for old_file in files:
                            try:
                                file = File(old_file, self.root)
                                new_file = file.organized_directory()
                                text = f"Moving {old_file} to {new_file}"
                                print(text)
                                app.display(text)
                                file.move(new_file)
                            except Exception as exception:
                                self.exception(exception)
                        app.display(f"Python moved {len(files)} files!")
                    else:
                        app.display("Python did not move any files. Have a nice day.")
            self.misplaced_file = None

    def delete_empty_folders(self, app):
        self.collect(app)
        start_time = tic()
        empty_count = 0
        print(f"Python is scanning {self.root} for empty folders...")
        for root, dirs, files in os.walk(self.root, topdown=False):
            try:
                items = os.listdir(root)
                if not items:
                    empty_count += 1
                    print(f"Deleting empty folder: {root}")
                    os.rmdir(root)
            except Exception as exception:
                self.exception(exception)

            output = (f"Elapsed Time is {Time(tic() - start_time)}\n"
                      f"Python deleted {empty_count} empty folders...")
            app.display(output)

    def backup_files(self, app):
        self.collect(app)
        ans = input(f"Are you sure you want to sync {self.root} to {self.backup}? (y/n)")
        if ans.lower() in {"y", "yes"}:
            print("Backing up...")
            raise NotImplementedError


if __name__ == "__main__":
    scanner = Scanner()
    RESULTS_FILE = [("Result Files", "*.res")]

    app = App("My Backup Utility V1.0", 725, 450)
    app.Label("File Extensions to Exclude: ", 0, 0)
    app.extensions = app.Entry("", 0, 1, width=2)
    app.Label("e.g. txt, doc, xls", 0, 3)

    app.Label("Exclude Files Smaller Than: ", 1, 0)
    app.min_size = app.Entry("0", 1, 1, width=2)
    app.Label("Bytes", 1, 3)

    app.Label("Exclude Files Larger Than: ", 2, 0)
    app.max_size = app.Entry("10_000_000_000", 2, 1, width=2)
    app.Label("Bytes", 2, 3)

    app.root_folder = app.Label("<No Directory Selected>", 3, 0, width=4)
    app.FolderDialog("Browse to Root Directory", 4, 0, width=4, output=app.root_folder)
    app.Button("Scan Directory for Duplicates", 5, 0, width=4, function=scanner.scan_duplicates)

    app.Button("Delete Duplicate Files", 6, 0, width=4, function=scanner.purge_duplicates)

    app.Button("Scan Directory for Misplaced Files", 7, 0, width=4, function=scanner.scan_misplaced)
    app.Button("Organize Misplaced Files", 8, 0, width=4, function=scanner.organize_files)

    app.Button("Delete Empty Folders", 9, 0, width=4, function=scanner.delete_empty_folders)

    app.backup_folder = app.Label("<No Directory Selected>", 10, 0, width=4)
    app.FolderDialog("Browse to Backup Directory", 11, 0, width=4, output=app.backup_folder)
    app.Button("Sync Root to Backup", 12, 0, width=4, function=scanner.backup_files)

    app.run()
