PUSH_STRATEGY_JSON_FILENAMES = {
    "push_all": "push_all.json", #Alles wird gepusht, kein Critical CSS
    "push_all+criticial_css": "push_all_optimized.json", #Alles wird gepusht, + Critical CSS

    "push_critical": "push_critical.json", #Nur renderkritische/ATF Resourcen werden gepusht
    "push_critical+criticial_css": "push_critical_optimized.json", #Nur renderkritische/ATF Resourcen werden gepusht + Critical CSS (bzw. critical CSS zuerst)

    "no_push": "nopush.json",
    "no_push+criticial_css": "nopush_optimized.json"
}

AVAILABLE_SITES = [
    "aliexpress",
    "amazon",
    "apple",
    "bankofamerica",
    "bestbuy",
    "chase",
    "cnn",
    "craigslist",
    "ebay",
    "microsoft",
    "nytimes",
    "paypal",
    "reddit",
    "twitter",
    "walmart",
    "wellsfargo",
    "wikipedia",
    "yahoo",
    "yelp",
    "youtube"
]
