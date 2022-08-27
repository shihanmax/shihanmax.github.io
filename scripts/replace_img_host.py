import os


def replace_host(path):
    rec = []
    for f in os.listdir(path):
        if os.path.isdir(os.path.join(path, f)):
            replace_host(os.path.join(path, f))
        else:
            try:
                content = open(os.path.join(path, f), 'r').read()
                new_content = content.replace(
                    'http://qiniu.shihanmax.top/', 'http：//shihanmax.top:8009/?path=',
                )
                rep_path = path.replace("_posts", "_posts_new")
                if not os.path.exists(rep_path):
                    os.mkdir(rep_path)
                    
                with open(os.path.join(rep_path, f), "w") as fwt:
                    fwt.write(new_content)
                
            except Exception as e:
                rec.append(f)
                print(e)

    print(rec)
    
if __name__ == "__main__":
    replace_host('../_posts/')