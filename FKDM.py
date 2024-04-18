import os
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QWidget,QPushButton,QLineEdit,QVBoxLayout,QApplication,QMainWindow,QFileDialog,QProgressBar,QStatusBar,QDialog
import sys
from qtawesome import icon
import pycurl
import io
from fkdm.config.styles import global_styles
from fkdm.dialogs.settings import SettingsDialog
from fkdm.config import settings
from PyQt5.QtCore import QThread, pyqtSignal
from notifypy import Notify


kb = 1024

pycurl_custom_headers = [
    f"User-Agent: {settings.DEFAULT_USER_AGENT}",
]


notification = Notify()


class DownloadThread(QThread):
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str)


    def __init__(self,url,filename:str):
        super().__init__()
        self.url = url
        self.filename = filename
        self.total_bytes = None
        self.downloaded_bytes = 0

    
    def run(self):
        self.status_signal.emit("Download started")
        buffer  = io.BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL,self.url)
        c.setopt(c.WRITEDATA,buffer)
        #c.setopt(pycurl.WRITEFUNCTION,self.write_callback)
        c.setopt(pycurl.NOPROGRESS, 0)
        c.setopt(pycurl.PROGRESSFUNCTION, self.progress_function)
        fp= open(self.filename, "wb")
        c.setopt(pycurl.WRITEDATA, fp)

        try:
            c.perform()
            # buffer.seek(0)
            # data = buffer.read()
        except pycurl.error as e:
            self.status_signal.emit(f'Error: {e}')
        finally:
            c.close()

        
        # with open(self.filename,'wb') as f:
        #     f.write(data)
        #     f.close()
        notification.title = "Download Completed"
        notification.message = self.filename

        # Display the notification
        notification.send()
        os.system("open "+self.filename)
        self.status_signal.emit("Download Complete!")
        self.quit()

    def progress_function(self,download_t, download_d, upload_t, upload_d):
        percent = (download_d+0.00000000001)/(download_t+0.000000000001)*100
        self.progress_signal.emit(percent)
        total =  (download_t/1048576) 
        downloaded = (download_d/1048576)
        print("Total to download = " + str(total))
        print("Downloaded = "+str(downloaded))


    def write_callback(self,data):
        self.downloaded_bytes += len(data)
        if not self.total_bytes:
            self.total_bytes  = self.get_total_size()

        if self.total_bytes:
            progress = int((self.downloaded_bytes/self.total_bytes)*100)
            print(progress)
            print("Total to download = " + str(self.total_bytes))
            print("Downloaded = "+str(self.downloaded_bytes))
            self.progress_signal.emit(progress)

        return len(data)

    
    def get_total_size(self):
        """
            A function to retrieve the total size of the download from the server.

            Returns:
                int: The total size of the download in bytes, or None if unavailable.
        """
        c = pycurl.Curl()
        try:
            c.setopt(c.URL,self.url)
            c.setopt(c.NOBODY,1)
            c.perform()
            return c.getinfo(pycurl.CONTENT_LENGTH_DOWNLOAD)
        except pycurl.error:
            return None
        finally:
            c.close()

class FkdmApp(QMainWindow):


    def __init__(self) -> None:
        super().__init__()
        self.settings = QSettings("Fkdm","Fkdm")
        self.initUI()
        self.download_thread = DownloadThread(None, None)
        

    
    def initUI(self):
        self.setWindowTitle("Fkdm - Free yet simple and very fast downloader manager")
        self.setGeometry(100, 100, 600, 200)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # URL textfield
        main_layout = QVBoxLayout(main_widget)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter URL text...")
        self.setStyleSheet(global_styles)
        main_layout.addWidget(self.url_input)
        self.save_directory_input = QLineEdit()
        self.save_directory_input.setReadOnly(True)

        self.save_directory_input.setText(self.settings.value("save_location"))
        self.save_directory_input.setPlaceholderText("Choose save location...")
        main_layout.addWidget(self.save_directory_input)

        # create a button to select save location
        browse_button = QPushButton(icon('fa.folder-open',color='black'),'Browse',self)
        browse_button.clicked.connect(self.browse_location)
        main_layout.addWidget(browse_button)

        # create a button to handle download
        download_button = QPushButton(icon("fa.download",color="black"),"Download",self)
        download_button.clicked.connect(self.download_file)
        main_layout.addWidget(download_button)

        # add progress bar
        self.progress_bar = QProgressBar(self)
        main_layout.addWidget(self.progress_bar)
        
        # status
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    

    def show_settings(self):
        settings_dialog = SettingsDialog(self)
        settings_dialog.show()

    def get_valid_name(self,url):
        file_name = url.split("/")[-1]
        if '?' in file_name:
            file_name = file_name.split('?')[0]
        
        max_file_name_length = 255
        if len(file_name) > max_file_name_length:
            file_name = file_name[:max_file_name_length]
        
        return file_name
    

    def start_download(self, url, filename):
        self.progress_bar.setValue(0)
        self.download_thread.url = url
        self.download_thread.filename = filename
        self.download_thread.total_bytes = None
        self.download_thread.downloaded_bytes = 0
        self.download_thread.progress_signal.connect(self.update_progress)
        self.download_thread.status_signal.connect(self.update_status)
        self.download_thread.start()

    def update_progress(self, progress):
        self.progress_bar.setValue(progress)

    
    def update_status(self, message):
        # Implement status display (e.g., a label) based on your UI design
        pass

    def browse_location(self):
        options = QFileDialog.Options()
        folder_path = QFileDialog.getExistingDirectory(self,"select download location",options=options)
        if folder_path:
            self.save_directory_input.setText(folder_path)

    def download_file(self):
        print("Download button clicked")
        self.progress_bar.setValue(0)
        self.settings.setValue("save_location",self.save_directory_input.text())
        self.settings.sync()
        url = self.url_input.text()
        save_location = self.save_directory_input.text()
        # buffer = BytesIO()
        if not url:
            return
        # self.progress_bar.setValue(0)
        file_name = self.get_valid_name(url)
        file_path = os.path.join(save_location, file_name)
        filename = file_path
        self.start_download(url, filename)
    
    

def runApp():
    app = QApplication(sys.argv)
    fkdm = FkdmApp()
    fkdm.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    runApp()
