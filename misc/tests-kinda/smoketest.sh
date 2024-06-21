set -e
python main.py init
python main.py load --fn=test.txt --group_tag="raw"
python main.py blocks --where="group_tag='raw'"
python main.py transform --transformation="sentence-split"
python main.py blocks
python main.py blocks --where="token_count = 5"
#python main.py dump --source=blocks --delimiter="\n**********************\n"