import yaml

def test():
    with open('upload_deny_list.yaml', 'r') as f:
        deny_list = yaml.load(f, Loader=yaml.FullLoader)
    for i in deny_list.get('deny_ext'):
        print(i)

if __name__ == '__main__':
    test()
