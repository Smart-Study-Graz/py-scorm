import os

def test():
    print(os.listdir(os.path.join(__file__, '..', 'data')))