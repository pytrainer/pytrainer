def main():
    import pytrainer.lib.localization
    pytrainer.lib.localization.initialize_gettext()
    from pytrainer.main import pyTrainer
    pytrainer = pyTrainer()
