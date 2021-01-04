# coding = utf-8

from optparse import OptionParser
from optparse import OptionGroup



class ArgumentParser(object):

    def __init__(self, script_path):
        self.script_path = script_path
        self.options = self.parseArguments()


    def parseArguments(self):
        usage = 'Usage: %prog [options] arg1 arg2 ...'

        parser = OptionParser(usage,version='%prog 1.0')
        #通过OptionParser类创建parser实例,初始参数usage中的%prog等同于os.path.basename(sys.argv[0]),即
        #你当前所运行的脚本的名字，version参数用来显示当前脚本的版本。

        parser.add_option('-f','--file',
                        action='store',dest='file',
                        metavar='file',help='input filename')

        parser.add_option('--vv',
                        action='store_true',dest='show_level',default=False,
                        help='input level')

        parser.add_option('-p','--protocol',
                        action='store',dest='protocol',default='http',
                        help='http, ssh, telnet, FTP')

        parser.add_option('--thread',
                        action='store',dest='threads_Count',default=5,
                        help='input threadsCount')



        # group = OptionGroup(parser,'set scan-Options')
        # group.add_option('-D',action='store',dest='database_name',
        #                 help='Print debug information.')
        # group.add_option('-T',action='store',dest='table_name',
        #                 help='Print all SQL statements executed')
        # group.add_option('-C',action='store',dest='column_name',
        #                 help='Print every action done')
        # parser.add_option_group(group)

        #解析脚本输入的参数值，options是一个包含了option值的对象
        #args是一个位置参数的列表
        options, arguments = parser.parse_args()
        return options