from distutils.core import setup
import py2exe

setup(windows=['QCMDAnalyser.py'],
      options={
          'py2exe': {
              'packages': ['matplotlib', 'PyQt5',  'numpy', 'scipy',   'mpl_toolkits'],
              'includes':['E:\Python\Lib\site-packages\scipy\special\_ufuncs.pyd']
          }
      }
      )