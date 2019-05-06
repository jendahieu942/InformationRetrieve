#Project structure
```bash
  (IR)
    |___crawler
    |    |______crawler
    |    |       |______spiders
    |    |       |       |_____restaurant.py
    |    |       |
    |    |       |______items.py
    |    |       |______middlewares.py
    |    |       |______pipelines.py
    |    |       |______settings.py
    |    |
    |    |______mains.py
    |
    |___docs
    |    |______readme.md
    |
    |___sync
    |
    |___search
    |
    |___frontend
     
```

#How did i code this project

## Crawler

In the root folder start this command
`scrapy startproject crawler`

Make a `main.py` file in `crawler` folder
This is start point of crawler program 