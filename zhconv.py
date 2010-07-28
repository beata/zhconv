#!/usr/bin/python
#_*_ coding:UTF-8 _*_
#
# Convert file text between Traditional Chinese and Simplified Chinese
#
#  Author: Beata
#    Blog: http://blog.nahoya.com
#     URL: http://github.com/beata/zhconv
# License: http://creativecommons.org/licenses/by-sa/3.0/

import os.path, sys, shutil
from optparse import OptionParser
from progressBar import ProgressBarWidget, Bar, Percentage, ETA, ProgressBar

class BarLabel(ProgressBarWidget):
  def __init__(self, proc_text, done_text):
    ProgressBarWidget.__init__(self)
    self.proc_text = proc_text
    self.done_text = done_text
  def update(self, pbar):
    if pbar.percentage() < 100:
      return self.proc_text
    else:
      return self.done_text

class ZHConvertError(Exception):
  pass

class ZHConvert:

  VERSION = '0.2'

  def __init__(self, files, convertTo, override=False):
    '''
    files     - REQUIRED, list|str
                Files to be convert.
    convertTo - REQUIRED, str
                's2t' - convert Simplified Chinese to Traditional Chinese.
                't2s' - convert Traditional Chinese to Simplified Chinese.
    override  - OPTIONAL, boolean
                Update the file when complete the convertion?
    '''

    if type(files).__name__ == 'str':
      files = [files]

    if convertTo not in ['s2t', 't2s']:
      raise ZHConvertError('Please specified which format you want convert to.');

    exec('import '+convertTo+' as dic')

    self.convertTo = convertTo
    self.dict = dic

    if override:
      for filename in files:
        self.convert_save(filename)
    else:
      for filename in files:
        self.convert(filename)

  def convert(self, filename):
    f = open(filename)
    try:
      while True:
        line = f.readline()
        if not line: break
        print self.__parse(line)
    finally:
      f.close()

  def convert_save(self, filename):
    widgets = ['    ', Bar('#'), ' ', BarLabel('Parsing "%s" ....' % filename, 'Parsing "%s" Done' % filename), ' | ',Percentage(),' | ', ETA(), '    ']
    tmpname = filename + '.' + self.convertTo
    fr = open(filename)
    fw = open(tmpname, 'w')
    bar = ProgressBar(widgets=widgets, maxval=os.path.getsize(filename)).start()
    try:
      while True:
        line = fr.readline()
        if not line: break
        fw.write( self.__parse(line) )
        bar.update(fr.tell())

      shutil.move(tmpname, filename)
      bar.finish()
    finally:
      fr.close()
      fw.close()

  def __parse(self, line):
    # replace chars
    line = ''.join([self.dict.chars.get(c, c) for c in unicode(line, 'UTF8')])
    # replace phrase
    for key in self.dict.phrase:
      if key not in line: continue
      line = line.replace(key, self.dict.phrase[key])

    return line.encode('utf8')

if __name__ == '__main__':
  parser = OptionParser('usage: %prog [-t or -s] [options] files', version=ZHConvert.VERSION)

  parser.add_option('-t', '--traditional', dest='convertTo',\
      action='store_const', const='s2t', default='',\
      help='convert to Traditional Chinese')
  parser.add_option('-s', '--simplified', dest='convertTo',\
      action='store_const', const='t2s', default='',\
      help='convert to Simplified Chinese')

  parser.add_option('-w', '--write', dest='override',\
      action='store_true', default=False,\
      help='override the original file with the converted text')

  opt, args = parser.parse_args()

  if len(args) == 0:
    parser.print_usage()
    print 'Please specified the file you want convert to.'
    exit()

  try:
    ZHConvert(args, opt.convertTo, opt.override)
  except ZHConvertError, e:
    parser.print_usage()
    print '\n'.join(e.args)
    print '%s(%s) on "%s": %s' % (type(e).__name__, e.errno, e.filename, e.strerror)
  except KeyboardInterrupt:
    print 'KeyboardInterrupt'
  except Exception, e:
    sys.stderr.write('%s: %s\n' % (type(e).__name__, str(e)))
