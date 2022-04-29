import os
class config:
    staticAdd="main/statics/"
    staticSound=staticAdd+"sound/"
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    Model_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),"main/model")