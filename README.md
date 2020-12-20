# LineChatBot
成大資工計算理論課程Project

## Description



## [Heroku](https://dashboard.heroku.com/)

* **requirement.txt**

    這個檔案是要告訴 Heroku 你的環境需要那些其他的套件`

* **[Procfile](https://devcenter.heroku.com/articles/procfile)**

    Procfile 這個檔案是要告訴 Heroku 要如何啟動這個 web app
    在 Heroku 裡，官方使用 [Gunicorn](http://gunicorn.org/) 來啟動 web server
    使用前須先安裝gunicorn套件：`pip install gunicorn`
    Procfile 檔案，基本使用方法如：`web gunicorn app_run:app`
    gunicorn相關可以參考[官方文件](https://devcenter.heroku.com/articles/python-gunicorn#adding-gunicorn-to-your-application)


* **runtime.txt**

    runtime.txt 檔案裡，只需要簡單的填入你想要指定的 python 版本，如果你不想指定 python 的版本，這個檔案可以忽略。


## 參考資料

* [官方文件](https://devcenter.heroku.com/articles/getting-started-with-python)
* [Deploy flask to heroku](https://github.com/twtrubiks/Deploying-Flask-To-Heroku)
* [line-bot-tutorial](https://github.com/twtrubiks/line-bot-tutorial)
