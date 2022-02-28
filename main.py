import requests
import json
from github import Github
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler
sched = BlockingScheduler()

def get_json_from_github():
    url = 'https://raw.githubusercontent.com/Saransh-Tiwari-2002/inshorts_json/main/inshorts.json'
    resp = requests.get(url)
    return json.loads(resp.text)

def push_to_github():
    g = Github('Enter Toekn here')
    print(g)
    repo = g.get_user().get_repo('inshorts_json')
    all_files = []
    contents = repo.get_contents("")
    print(contents)
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            file = file_content
            all_files.append(str(file).replace('ContentFile(path="','').replace('")',''))

    #print(all_files)
    file=open('inshorts_test.json', 'r', encoding='utf-8')
    content = file.read()

    # Upload to github
    #git_prefix = 'folder1/'
    git_file ='inshorts.json'
    if git_file in all_files:
        contents = repo.get_contents(git_file)
        repo.update_file(contents.path, "committing files", content, contents.sha, branch="main")
        print(git_file + ' UPDATED')
    else:
        repo.create_file(git_file, "committing files", content, branch="main")
        print(git_file + ' CREATED')

def fix_index(new_articles):
    try: test_data=get_json_from_github()
    except: test_data={}
    temp1={} 
    if(len(test_data.keys())>400): temp_range= 400
    else: temp_range=len(test_data.keys())
    for x in range(temp_range):
        temp={str(x+len(new_articles)):{'url':test_data.get(str(x)).get('url'), 'title':test_data.get(str(x)).get('title'), 'image':test_data.get(str(x)).get('image'), 'author_name':test_data.get(str(x)).get('author_name'), 'article_time':test_data.get(str(x)).get('article_time'), 'article_date':test_data.get(str(x)).get('article_date'), 'article_body':test_data.get(str(x)).get('article_body')}}
        temp1.update(temp)
    test=open('inshorts_test.json', 'w', encoding='utf-8')
    new_articles.update(temp1)
    json.dump(new_articles, test, ensure_ascii=False, indent=4)
    return True

def main():
    r=requests.get('https://www.inshorts.com/en/read')
    soup=BeautifulSoup(r.content, 'html.parser')
    count=0
    new_articles={}
    try: test_data=get_json_from_github()
    except: test_data={}
    for div in soup.findAll('div', {'class':'news-card z-depth-1'}):
        url=div.find('span', {'itemtype':'https://schema.org/WebPage'})['itemid']
        title=div.find('span', {'itemprop':'description'})['content']
        image=div.find('div', {'class':'news-card-image'})['style']
        image=image[image.find("'")+1: image.rfind("'")]
        article_body=div.find('div', {'itemprop':'articleBody'}).text
        author_name=div.find('span',{'class':'author'}).text
        article_date=div.find('span',{'class':'date'}).text
        article_time=div.find('span',{'class':'time'}).text

        flag=0
        temp={count:{'url':url, 'title':title, 'image':image, 'author_name':author_name, 'article_time':article_time, 'article_date':article_date, 'article_body':article_body}}
        for check in range(len(test_data)):
           if(test_data.get(str(check)).get('url') == url):
                flag=1
                break
        if(flag==0):  
            new_articles.update(temp)
            count+=1

    if(len(new_articles)):
        fix_index(new_articles)
        push_to_github()


@sched.scheduled_job('interval', minutes=6)
def timed_job():
   main()
#main()
sched.start()

