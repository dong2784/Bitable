from json import load, JSONDecodeError
from view.main_window import MainWindow

if __name__ == '__main__':
    try:
        with open('version.json') as f:
            version = load(f).get('version')
    except FileNotFoundError or JSONDecodeError:
        version = 'unknown'
    MainWindow.exec(version)
