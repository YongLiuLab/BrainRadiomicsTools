# coding=UTF-8
from backports import configparser as ConfigParser
class resini(object):
    def __init__(self, path):
        self.path = path
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.path)

    def write(self,value):
        if self.config.has_option('Segmentation Images', 'indexesToSegment'):
            self.config.set('Segmentation Images', 'indexesToSegment', value)
            # value = map(int,value)
            # self.config.set('Segmentation Images', 'indexesToSegment', value)
            self.config.write(open(self.path, 'w'))
            print ('写入ini',value)
        else:
            print ('parse ini fail')
