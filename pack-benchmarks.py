import os


def main():
    os.system('tar cvf prp-benchmark-A.tar problem-class-A-*.tar.bz2')
    os.system('tar cvf prp-benchmark-B.tar problem-class-B-*.tar.bz2')
    os.system('tar cvf prp-benchmark-C.tar problem-class-C-*.tar.bz2')
    os.system('tar cvf prp-benchmark-D.tar problem-class-D-*.tar.bz2')
    os.system('tar cvf prp-benchmark-E.tar problem-class-E-*.tar.bz2')
    os.system('rm problem-class-*.tar.bz2')

    os.system('tar cvf smv-benchmark-A.tar class-A-*.smv')
    os.system('tar cvf smv-benchmark-B.tar class-B-*.smv')
    os.system('tar cvf smv-benchmark-C.tar class-C-*.smv')
    os.system('tar cvf smv-benchmark-D.tar class-D-*.smv')
    os.system('tar cvf smv-benchmark-E.tar class-E-*.smv')
    os.system('rm class-*.smv')

    os.system('tar cvf ispl-benchmark-A.tar class-A-*.ispl')
    os.system('tar cvf ispl-benchmark-B.tar class-B-*.ispl')
    os.system('tar cvf ispl-benchmark-C.tar class-C-*.ispl')
    os.system('tar cvf ispl-benchmark-D.tar class-D-*.ispl')
    os.system('tar cvf ispl-benchmark-E.tar class-E-*.ispl')
    os.system('rm class-*.ispl')


if __name__ == '__main__':
    main()
