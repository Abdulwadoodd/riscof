from cerberus import Validator
import oyaml as yaml
from rips.schemaValidator import *
import common.utils
import logging
import sys
import os
import re

def extreaddefset():
    '''Function to set readonly in extensions field in misa'''
    global inp_yaml
    if inp_yaml['misa']['Extensions']['bitmask']['base'] > 0:
        return False
    else:
        return True

def sset():
    '''Function to check and set defaults for all fields which are dependent on 
        the presence of 'S' extension.'''
    global inp_yaml
    if 'S' in inp_yaml['ISA']:
        return True
    else:
        return False

def uset():
    '''Function to check and set defaults for all fields which are dependent on 
        the presence of 'U' extension.'''
    global inp_yaml
    if 'U' in inp_yaml['ISA']:
        return True
    else:
        return False

def nosset():
    '''Function to check and set defaults for all fields which are dependent on 
        the presence of 'S' extension and have a hardwired value of 0.'''
    global inp_yaml
    if 'S' not in inp_yaml['ISA']:
        return {'readonly':True,'hardwired':'0'}
    else:
        return {'readonly':False}
    
def nouset():
    '''Function to check and set defaults for all fields which are dependent on 
        the presence of 'U' extension and have a hardwired value of 0.'''
    global inp_yaml
    if 'U' not in inp_yaml['ISA']:
        return {'readonly':True,'hardwired':'0'}
    else:
        return {'readonly':False}

def upieset(doc):
    '''Function to check and set value for upie field in misa.'''
    global inp_yaml
    if 'U' not in inp_yaml['ISA']:
        return {'readonly':True,'hardwired':'0'}
    elif 'UPIE' not in doc.keys():
        return {'readonly':False}
    else:
        return doc['UPIE']

def uieset(doc):
    '''Function to check and set value for uie field in misa.'''
    global inp_yaml
    if 'U' not in inp_yaml['ISA']:
        return {'readonly':True,'hardwired':'0'}
    elif 'UIE' not in doc.keys():
        return {'readonly':False}
    else:
        return doc['UIE']

def twset():
    '''Function to check and set value for tw field in misa.'''
    global inp_yaml
    if 'S' not in inp_yaml['ISA'] and 'U' not in inp_yaml['ISA']:
        return {'readonly':True,'hardwired':'0'}
    else:
        return {'readonly':False}

def miedelegset():
    '''Function to set "implemented" value for mideleg regisrer.'''
    # return True
    global inp_yaml
    if 'U' not in inp_yaml['ISA']:
        return False
    elif (('U' in inp_yaml['ISA']) and not ('N' in inp_yaml['ISA'] or 'S' in inp_yaml['ISA'])):
        return False
    else:
        return True

def add_def_setters(schema_yaml):
    '''Function to set the default setters for various fields in the schema'''
    schema_yaml['misa']['schema']['Extensions']['schema']['readonly']['default_setter'] = lambda doc: extreaddefset()
    schema_yaml['mstatus']['schema']['SXL']['schema']['implemented']['default_setter'] = lambda doc: sset()
    schema_yaml['mstatus']['schema']['UXL']['schema']['implemented']['default_setter'] = lambda doc: uset()
    schema_yaml['mstatus']['schema']['TVM']['default_setter'] = lambda doc: nosset()
    schema_yaml['mstatus']['schema']['TSR']['default_setter'] = lambda doc: nosset()
    schema_yaml['mstatus']['schema']['MXR']['default_setter'] = lambda doc: nosset()
    schema_yaml['mstatus']['schema']['SUM']['default_setter'] = lambda doc: nosset()
    schema_yaml['mstatus']['schema']['SPP']['default_setter'] = lambda doc: nosset()
    schema_yaml['mstatus']['schema']['SPIE']['default_setter'] = lambda doc: nosset()
    schema_yaml['mstatus']['schema']['SIE']['default_setter'] = lambda doc: nosset()
    schema_yaml['mstatus']['schema']['UPIE']['default_setter'] = lambda doc: upieset(doc)
    schema_yaml['mstatus']['schema']['UIE']['default_setter'] = lambda doc: uieset(doc)
    schema_yaml['mstatus']['schema']['MPRV']['default_setter'] = lambda doc: nouset()
    schema_yaml['mstatus']['schema']['TW']['default_setter'] = lambda doc: twset()
    schema_yaml['mideleg']['schema']['implemented']['default_setter'] = lambda doc:miedelegset()
    schema_yaml['medeleg']['schema']['implemented']['default_setter'] = lambda doc:miedelegset()
    return schema_yaml

def main():
    global inp_yaml
    # Set up the parser
    parser = common.utils.rips_cmdline_args()
    args = parser.parse_args()

    # Set up the logger
    common.utils.setup_logging(args.verbose)
    logger = logging.getLogger()
    logger.handlers = []
    ch = logging.StreamHandler()
    ch.setFormatter(common.utils.ColoredFormatter())
    logger.addHandler(ch)

    logger.info('Running RIPS Checker on Input file')

    foo = args.input
    schema = args.schema
    """
      Read the input foo (yaml file) and validate with schema for feature values
      and constraints
    """
    inputfile = open(foo, 'r')
    schemafile = open(schema, 'r')
    # Load input YAML file
    logger.info('Loading input file: '+str(foo))
    inp_yaml = yaml.safe_load(inputfile)

    # instantiate validator
    logger.info('Load Schema '+str(schema))
    # yaml.add_path_resolver('!exset',"lambda doc: extreaddefset(doc)")
    schema_yaml = yaml.safe_load(schemafile)
    
    schema_yaml=add_def_setters(schema_yaml)
    validator = schemaValidator(schema_yaml)
    validator.allow_unknown = True
    normalized = validator.normalized(inp_yaml, schema_yaml)
    # print(normalized)
    # Perform Validation
    logger.info('Initiating Validation')
    valid=validator.validate(inp_yaml)
    
    # Print out errors
    if valid:
        logger.info('No Syntax errors in Input Yaml. :)')
    else:
        error_list = validator.errors
        logger.error(str(error_list))
        sys.exit(0)

    logger.info('Performing Additional Checks')

    file_name_split = foo.split('.')
    output_filename = file_name_split[0]+'_checked.'+file_name_split[1]
    outfile = open(output_filename, 'w')
    logger.info('Dumping out Normalized Checked YAML: '+output_filename)
    yaml.dump(normalized, outfile, default_flow_style=False, allow_unicode=True)


if __name__ == '__main__':
    main()

