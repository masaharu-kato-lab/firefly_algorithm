import argparse
import attrdict

class Test:
    pass

def main():

    obj = Test()
    obj.test = 'テスト'
    obj.hogehoge = 'ほげほげ'
    obj.fuga = 'ふが'
    obj.a = 1234
    obj.b = 5678
    obj.c = 9012

    print(obj)
    print(obj.__dict__)

    print('a:{a:>6} test:{test} b:{b} hogehoge:{hogehoge} fuga:{fuga} c:{c}'.format(**vars(obj)))
    

if __name__ == '__main__':
    main()
