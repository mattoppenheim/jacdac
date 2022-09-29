''' Convert Kicad footprint files from nightly-build v6.99 to stable build.
Run in the folder that you want the files to be converted in, or supply the path
to this folder at the command line.
need to convert e.g. (stroke (width 0.15) (type solid))  to (width 0.15)
(stroke (width 0.15) (type default)) to (width 0.15)
(stroke (width x.xx) (type abc*)) to (width x.xx)
(stroke (width x) (type abc*)) to (width x)

Removes tstamp tags - not necessary for functionality.
Adjusts version tag to a bogus date so that gets updated by kicad.

To run on multiple files:
find . -name '*.kicad_mod' -exec python convert_kicad_footprint.py {} \;
Matthew Oppenheim  28 Sep 2022 '''

import logging
import os
import re
import sys


# regex to find (stroke (width x.xx) (type abc*)) and match (width x.xx) to group 1
REGEX_STROKE = r'(?:\(stroke )(\(width [0-9]*\.?[0-9]*\))\s*(?:\(type [a-z]*\)\))'
# regex to find TSTAMP tags
REGEX_TSTAMP = r'\s{1}\(tstamp\s.{8}(?:\-.{4}){3}\-.{12}\)'
# regex to find version date
REGEX_VERSION = r'\(version\s[0-9]{8}\)'


logging.basicConfig(level=logging.DEBUG, format='%(message)s')


def apply_regex_to_file(input_filepath, output_filepath):
    ''' Apply a regex to each line of a file and write to an output file. '''
    open_output = open(output_filepath, 'w')
    with open(input_filepath, 'r') as open_input:
      for line in open_input:
        open_output.write(apply_regex_to_line(line))


def apply_regex_to_line(line):
    ''' Apply regex to line. '''
    # edit width tags
    line = re.sub(REGEX_STROKE, r'\1', line)
    # remove TSTAMP tags - cosmetic only
    line = re.sub(REGEX_TSTAMP, '', line)
    # put in spoof version so that it is updated with the current version of kicad
    line = re.sub(REGEX_VERSION, '(version 20100101)', line)
    return line


def check_file_exists(filepath):
  ''' Check if <filepath> exists. '''
  if os.path.exists(filepath):
    logging.debug('Found filepath: {}'.format(filepath))
    return True
  else:
    logging.debug('Filepath does not exist: {}'.format(filepath))
    return False


def create_output_directory(working_directory):
  ''' Create a directory called kicad_converted in working directory. '''
  output_directory = os.path.join(working_directory, 'kicad_converted')
  if not os.path.exists(output_directory):
    try:
      os.mkdir(output_directory)
    except OSError as e:
      exit_code('unable to make output directory {}\n{}'.format(output_directory, e))
  return output_directory


def create_output_filepath(input_filepath):
  ''' Create an output filepath. '''
  input_filename = os.path.basename(input_filepath)
  logging.debug('input_filename {}'.format(input_filename))
  input_directory = os.path.dirname(input_filepath)
  # append '_edited' to end of filename, prior to suffix
  # split_input_filename = input_filename.split('.')
  # split_input_filename[-2] = split_input_filename[-2] + '_edited'
  # output_filename = '.'.join(split_input_filename)
  output_directory = create_output_directory(input_directory)
  output_filepath = os.path.join(output_directory, input_filename)
  logging.debug('output_filepath {}'.format(output_filepath))
  return output_filepath


def exit_code(message):
    ''' exits '''
    logging.critical(message)
    logging.critical("exiting")
    raise SystemExit


def filepath(*args):
    ''' Return the filepath passed at startup. '''
    try:
        filepath = sys.argv[1]
    # if no args IndexError is raised
    except IndexError:
        filepath = str(input ("Enter filepath to work on: "))
    return filepath


def main(*args, **kwargs):
  logging.debug('\nstarting {}'.format(sys.argv[0])) #convert_nightly_footprints_to_stable')
  input_filepath = filepath(*args)
  logging.debug('input filepath: {}'.format(input_filepath))
  if not check_file_exists(input_filepath):
    exit_code('Filepath not found: {}'.format(input_filepath))
  output_filepath = create_output_filepath(input_filepath)
  apply_regex_to_file(input_filepath, output_filepath)


  logging.debug('done')

if __name__=='__main__':
  main()
