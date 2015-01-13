__author__ = 'mpa'

import os, yaml

if __name__ == '__main__':
    template_file = open(os.path.join('/net/u/mpa/project/templates/template1', 'services.yaml'))
    template_yaml = template_file.read()
    template_dict = yaml.load(template_yaml)

    print template_dict.get('heat_template_version')

