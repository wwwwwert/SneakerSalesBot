### The meaning of the bot

Usually, people want to buy an item at a discount, but it is too exhausting to to visit the site and monitor interesting offers that suit them. I created a bot that independently monitors new discounts and notifies users who are interested in it.

### @SneakerSales_Bot
bot's telegram id: **@SneakerSales_Bot**

Thematic picture and description for the bot are used

The code is written using the telebot library. The first message from the user '/start' appears when the bot is started.
The bot welcomes and immediately offers to choose parameters (gender, size), or informs the user about his existing parameters. The standard multi-stage dialog of the bot with the user is implemented by storing the user_step (at what level of the dialog the user is) in the {id: step} dictionary. The user reports the model type and sizes.

The bot writes the user id to a text document at "model type"/"model type""size".txt in the sought_for_items folder. It also remembers user parameters in creating_users {id: user_parameters}, where user_parameters is an object of the corresponding simple class for convenient work with user parameters.
**Доступны команды**

/report - the user reports his comments to the bot, he writes them in report.txt

/edit - the user changes his parameters (almost the same as at the first start, only the bot asks again)

/help - informs about available commands

### Scrapping

**Preparing text documents before writing new data**

The **prepare_txt_files** function takes the location of the text document in which the last scrap is written (new) and
the location of the text document in which the previous scrap (old).

So, the function prepares these two files for writing:

     1) clears old
     2) transfers data from new to old
     3) clears new so that scrap can be written there
    
**Submit requests persistently**

Since sites are protected from this kind of activity, you have to send requests several times.
The **get_response** function will take a link and try to get a response with a fake user agent and my cookies pulled when loading brandshop. If an error 403 occurs, it sends the request again after 2 - 10 seconds. On error 404 - returns None.

**Data collection**

The 'shop name'_scrap functions will scrape data from the "SALES" section from all pages (the logic says to parse only the first page and watch updates on it, but the site constantly mixes products).
First, the corresponding text documents are prepared for writing the prepare_txt_files scrap.
Next, we persistently request a discount page.
The function pulls out the name of the model, a link to it, a link to a photo in acceptable quality, old and new prices, model type and available sizes. Runs **add_sneakers_scrap**, which adds data to the corresponding text document.


### Search for new discounts, notify users

The **find\_new\_items\_"shop name"** function iterates through the old and new shop scraps and transfers items that are only found in the new scrap into the new\_items\_'shop name'.txt file. Also, if the new and old scrap contains the same thing, but the new one has more of its size, then the thing will be transferred only with the new size.

The **notify\_about\_new\_items\_"shop name"** function simply reads the corresponding new_items document, extracts the item parameters from it and runs **notify\_about\_item** - the function notifies users (sends the available size and a link ) by id from a text document corresponding to the model type and size. Some manufacturers make half sizes, such as 42.5 EU. When such a product appears, users will be notified, expecting sizes 42 and 43. If the message could not be sent (the user turned off the bot), then its id will be deleted from the text document so as not to waste time on it next time (of course, the user will be able to restart bot and send data)

Since I want to check for new discounts and notify users at some intervals, I make a **regular\_update\_and\_notification** function that executes the script of scraping, searching for new things and notifying users. Using the schedule module, I implement periodic execution of regular\_update\_and\_notificatio with a frequency per day
