# Automate WordPress with GPT-4-turbo and Python

This project automates a WordPress blog (making posts to the blog) with AI.
- It communicates with OpenAI's API (`gpt-4-turbo` model)
- Generates topic ideas for several configured categories
- Generates the blog post content for each topic idea generated. 
- Generates a thumbnail image for each topic (using `dall-e-3` model)
- Finally, it posts this generated content along with the featured thumbnail image to your blog by using WordPress' API.

## Clone project
```
cd $HOME
git clone https://github.com/teja156/wordpress-automation-GPT.git

cd wordpress-automation-GPT
```

## Configuring the .env file
Before running the script, you need to first configure all the variables in the .env file.
- `OPENAI_API_KEY` : Your OpenAI API key
- `WORDPRESS_DOMAIN` : Your WordPress hostname/domain (ex: techreader.io)
- `WORDPRESS_USERNAME` : Your WordPress username (ex: admin)
- `WORDPRESS_APPLICATION_PASSWORD` : Your WordPress Application password. Read the next section to learn how to get this.
- `CATEGORIES` : Coma separated categories that you want the AI to generate content about (ex: Programming Tutorials, Cybersecurity, etc).

## Setup Wordpress
- Download and Install Wordpress (https://wordpress.org/download/)
- Verify API is functional. Head over to `https://<your-hostname>/wp-json/wp/v2/users`. If you get a JSON output of the current users of your site, it means API is enabled (it is enabled by default).
- Create an Application Password: Go to your **Wordpress Admin Panel** -> **Users** -> **All Users** -> Click on your admin account and scroll down until you see "**Application Password**". Create a new application password and paste it into the .env file.

## Setup OpenAI API
- Create an OpenAI developer account (https://platform.openai.com/)
- Create a new project
- For your project, allow these models: `gpt-4-turbo` and `dall-e-3`
- Create an API key for your project and paste it into the .env file

## Setup Python Environment
The recommended Python version is `3.11.1`. If you have a different version of Python installed on your Server/VM, install `3.11.1` using `pyenv.run` by follow these steps:
- Download and execute `pyenv.run`
```
curl https://pyenv.run | bash
```
- Restart your shell
- Add this to your `~/.bashrc`
```
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv virtualenv-init -)"
```
- Source your updated `~/.bashrc`
```
source ~/.bashrc
```
- Install Python 3.11.1
```
mkdir -p $HOME/tmp
chmod 700 $HOME/tmp

TMPDIR=$HOME/tmp pyenv install 3.11.1
```
- List the installed Python versions. You should now see `3.11.1`
```
pyenv versions
```
- Make `3.11.1` the global Python version
```
pyenv global 3.11.1
```
- Verify that your Python version is 3.11.1
```
python -V

# Should print Python 3.11.1
```

> This project is untested on other Python versions, so run at your own risk.

## Run script as CronJob
You can run this script as CronJob so that it gets executed at regular time intervals. Each execution of the script will post **ONE** blog post to your WordPress blog. If you want to have 5 posts per day, then you would schedule it to run 5 times a day using CronJobs.

- Edit your user's crontab
```
crontab -e
```
- Go to the end of the file, and insert your CronJob command
```
0 02,06,10,14,18 * * * $HOME/wordpress-automation-GPT/run.sh
```
This cronjob will run at 0th minute of the hours 2am, 6am, 10am, 2pm, 6pm everday (it runs 5 times a day). You can configure this however you like. You can use this website (https://crontab.guru/) to customize your Cron schedule. 