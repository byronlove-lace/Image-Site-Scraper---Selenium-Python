#Image File Downloader 
Image File Downloader is a CLI program that automatically downloads images from Imgur or Flickr.

##How It Works
1. Image File Downloader takes a user search query, the number of pictures and the site the user wants them from. 
2. To begin, IFD creates a local folder with query name to store images. 
3. IFD uses Selenium to create a windowless instance of Chrome that runs a search on the selected site. It checks the number of results (returns an error if 0; notes if results are less than requested images). 
4. IFD uses Selenium to scroll down to ensure that all results dynamically load before creating a list of the resulting image pages
5. For each page, it uses Selenium to interact with the elements (the dropdown menus, the buttons) and downloads the image. Resulting images are stored in the created folder.  


##Background
I made this project to familiarize myself with Selenium and browser automation.

##Challenges // Solutions
Some of the initial challenges related to learning the synax of Selenium and to dealing with the unpredictability realtime web-based software. The latter of these, I overcame through trial and error, using Selenium's various wait condition.

Another challenge was that search results load dynamically, that is, they load as the user scrolls down. To solve this I used Selenium's scroll function. This didn't work in the case of Flickr, so I used the downkey input to simulate a user clicking down on the keyboard, which solved the issue.

In general, Flickr proved more challenging to automate for than Imgur. This is because some images are not availible to download to get around this, gets the source of that image directly from the page and checks the file suffix. It then writes it to a buffer using iio and saves it like the others. 

